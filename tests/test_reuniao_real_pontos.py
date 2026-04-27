#!/usr/bin/env python3
"""Teste nos mesmos snapshots da reunião real — chamada 2 recebe SÓ pontos resumidos."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

snaps = [
    ("SNAP 1 — SSM, IAM, Security Group, deploy manual",
     "[Gustavo] E aí vocês fazem porta SSH. Ou podem usar System Manager, conexão privada com autenticação AWS. Não precisa liberar Security Group porta 22.\n[Juliano] Ok. Acessa via navegador?\n[Gustavo] Ou navegador ou CLI.\n[Juliano] Interessante. Vi que tinha que criar outros recursos.\n[Gustavo] Sim, IAM rules, é tranquilo. Tudo reflete na forma de deploy, hoje bem manual. Teria que evoluir essa parte primeiro."),

    ("SNAP 2 — GitHub, deploy manual, git pull",
     "[Juliano] Código no GitHub?\n[Gustavo] Sim, dois repos, back e front.\n[Juliano] Deploy, acessam instância e sobem?\n[Gustavo] Hoje é git pull dentro da instância, baixa alterações, aplica migrações. Só pra teste."),

    ("SNAP 3 — Next.js build estoura RAM, CodePipeline",
     "[Gustavo] Frontend Next.js, pesado no build. Instância pequena estoura RAM. Fazemos build local e upload. Ideal seria Docker multi-stage.\n[Juliano] CodePipeline conecta com GitHub, branch produção, faz build deploy teste. Se causar indisponibilidade reverte. Só paga tempo da máquina. Custo 1,5 dólar."),

    ("SNAP 4 — VPN vs SSM, Bastion, segurança",
     "[Juliano] Interessante Bastion, separar subnet pra reduzir área de ataque. Vocês indicam VPN pra acessar banco e instâncias?\n[Gustavo] VPN gera custo alto, não recomendamos. Usamos System Manager. Arquitetura seria assim."),

    ("SNAP 5 — Topologia rede, CodePipeline, CloudWatch",
     "[Gustavo] Route joga pro load balancer em subnet pública. Só LB e NAT na pública. ECS/EC2 e banco em subnet privada.\n[Juliano] CI/CD com CodePipeline e CodeBuild. Observabilidade com CloudWatch. Vocês usam?\n[Gustavo] Eu uso em outra empresa."),

    ("SNAP 6 — São Paulo vs Virginia, custo, latência",
     "[Gustavo] Recomendando Virginia. Vocês usam SP. Compliance específico?\n[Juliano] Mais por delay. SP mais caro, quase dobro.\n[Gustavo] SP 35-50ms, Virginia 120ms.\n[Juliano] Migrar pra Virginia pra reduzir custo. RDS lá mais barato."),

    ("SNAP 7 — Terraform, WAF, estimativa custo",
     "[Juliano] Usam Terraform?\n[Gustavo] Depende do cliente. Terraform ou CloudFormation. Adiciona horas. Adicionaria WAF pra ataques, SQL injection, regras gerenciadas AWS.\n[Juliano] Com esses recursos, estimativa de preço mensal. Reservar instâncias. Preciso volumetria. Projeto migração Virginia. Preciso billing atual."),

    ("SNAP 8 — Incentivos AWS, subsídio, créditos",
     "[Kyulin] Ver se consegue incentivo AWS.\n[Gustavo] AWS pode subsidiar projeto, total ou parcial. Meu papel levar case pra AWS buscar incentivo. Pode ser pra pagar projeto ou créditos.\n[Juliano] Entendi. Caminho é esse. Estou mais confortável."),

    ("SNAP 9 — Crescimento, volumetria, budget",
     "[Juliano] Budget limitado. Plataforma vai ter 600 assinaturas início próximo ano, 4 mil final. Movimentação financeira grande. Conseguimos passar volume usuários, produtos, transações pra mensurar máquinas."),
]

results = []
for title, ctx in snaps:
    # CHAMADA 1: classificação + pontos
    t0 = time.time()
    cm = (
        f"Analise a transcrição INTEIRA e responda QUATRO linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO\nCONCORRENTE: SIM ou NAO\n"
        f"PONTOS: Liste TODOS os assuntos técnicos — problemas, dúvidas, decisões, tecnologias.\n"
        f"RESPOSTA: CURTA/MÉDIA/LONGA\n\nTranscrição:\n{ctx}"
    )
    cr = client.call_raw("4 linhas exatas.", cm, max_tokens=300).strip()
    t_c1 = time.time() - t0

    has_q = "SIM" in cr.split("\n")[0].upper()
    clean = ctx  # fallback
    for l in cr.split("\n"):
        stripped = l.strip().replace("*","").replace("#","").strip()
        if stripped.upper().startswith("PONTOS:") or stripped.upper().startswith("PONTOS "):
            clean = stripped.split(":",1)[1].strip() if ":" in stripped else stripped[7:].strip()
            break
    fallback = clean == ctx

    # CHAMADA 2: resposta com SÓ os pontos
    t0 = time.time()
    if not has_q:
        msg = f"Pontos da conversa:\n{clean}\n\nSem pergunta técnica. Contexto em 1-2 frases + 3 perguntas pro consultor. Seja curto e objetivo."
    else:
        msg = f"Pontos da conversa:\n{clean}\n\nResponda cada ponto de forma objetiva e curta. Máximo 3 linhas por ponto no 📌 e 2 frases no 💬. Foque nos pontos fortes. Sem resumo no final."
    resp = client.call_raw(system, msg, max_tokens=5120)
    t_c2 = time.time() - t0

    block = (
        f"\n{'='*70}\n{title}\n{'='*70}\n\n"
        f"📝 TRANSCRIÇÃO ({len(ctx)} chars):\n{ctx}\n\n"
        f"⏱️ CHAMADA 1: {t_c1:.2f}s\n"
        f"🔍 Classificação:\n{cr}\n"
        f"{'⚠️ FALLBACK: pontos não extraídos, usando contexto inteiro' if fallback else f'✅ Pontos extraídos ({len(clean)} chars): {clean}'}\n\n"
        f"⏱️ CHAMADA 2: {t_c2:.2f}s | Input: {len(clean)} chars\n"
        f"⏱️ TOTAL: {t_c1+t_c2:.2f}s\n\n"
        f"📌 RESPOSTA ({len(resp)} chars):\n{resp}\n"
    )
    results.append(block)
    status = "⚠️FALLBACK" if fallback else "✅"
    print(f"{status} {title[:50]}... C1={t_c1:.1f}s C2={t_c2:.1f}s Total={t_c1+t_c2:.1f}s Points={len(clean)}chars")

output = "# Teste Reunião Real — Pontos Resumidos na Chamada 2\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-reuniao-real-pontos.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-reuniao-real-pontos.md")
