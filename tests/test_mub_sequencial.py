#!/usr/bin/env python3
"""Teste de snapshots SEQUENCIAIS com checkpoints — simula reunião real.
Cada snapshot recebe só o intervalo desde o último checkpoint.
Testa: não repetir, cobrir todos os assuntos, separar temas."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

# Simula intervalos de checkpoint da reunião MUB
# Cada bloco = o que foi falado ENTRE dois Win+D
intervals = [
    ("CHECKPOINT 1 [0:00-3:00] — Apresentação + stack + RTO/RPO",
     "Kevin, o ponto focal aqui vai ser sobre backup, definir melhor o RTO e RPO de vocês. "
     "Você consegue me dar uma descrição do que vocês estão usando hoje? "
     "A gente tem o Elastic Beanstalk fazendo a orquestração do back-end. Usamos o Aurora como banco. "
     "Tem um OpenSearch pra pesquisa. E o DynamoDB em alguns casos. "
     "Os clientes estavam exigindo um RTO RPO melhor. A gente não tem formalizado isso, "
     "o chefe pediu pra documentar o RTO RPO pra apresentar pros clientes."),

    ("CHECKPOINT 2 [3:00-6:00] — Multi-região + failover + custo",
     "A gente pode pensar em ambiente duplicado em outra região, geraria RTO RPO muito melhor. "
     "Só que dobraria o custo. Duplicar a infra seria um passo ousado demais. "
     "Só de curioso, como funciona na prática? Dois load balancers em locais separados, "
     "quem faz o meio do caminho? Vocês usam Route 53? "
     "Lá tem opção de failover. Se detectar que o load balancer de uma região não tá funcionando, joga pra outra."),

    ("CHECKPOINT 3 [6:00-9:00] — Infra exclusiva por cliente + estrutura de contas",
     "Teve um cliente que quer infraestrutura exclusiva. Banco deles, back-end deles. "
     "Tudo duplicado pra atender só um cliente. Acessível somente da rede deles. "
     "Não sei se é viável. Vocês teriam que ter uma conta separada só pra esse cliente. "
     "Vocês têm estrutura de contas? Não, hoje é uma só. "
     "Vocês conseguem ter uma conta de produção, uma de homologação, uma de dev. "
     "Login único entre elas. Billing unificado. Mas gera custo maior de infra."),

    ("CHECKPOINT 4 [9:00-13:00] — MSP/billing + deploy cross-account + Terraform",
     "Vocês têm MSP com a Dati? Não, só billing via boleto. "
     "Se fosse só billing, pra gente não muda nada mesmo com mais contas. "
     "A gente usa CodePipeline pra deploy. Conseguiria plugar a branch master "
     "nas duas infraestruturas e fazer funcionar? Contas diferentes? "
     "Vou checar isso. Não sei se tá em Terraform. Precisaria checar."),

    ("CHECKPOINT 5 [13:00-20:00] — Auto-scaling lento + Beanstalk→Fargate + monolito",
     "A gente tem uma dor que é a demora do auto scaling. "
     "Elastic Beanstalk leva meia hora até uma máquina subir. "
     "Às vezes cai fora do ar. A sugestão era migrar pro Fargate. "
     "Mas a gente tem um grande monolito. Quando tem monolito grande, "
     "o custo-benefício do Fargate não muda tanto. "
     "Mas o auto-scaling não seria mais rápido por ser imagem já buildada? "
     "Normalmente sim, mas depende do tamanho da aplicação. "
     "Às vezes o problema não é só o build, é o Beanstalk arrumando configuração. "
     "E no Fargate, consigo acessar a máquina pra troubleshooting urgente? "
     "O build demora 30 minutos e às vezes preciso corrigir na mão."),
]

previous_responses = []

def run_snapshot(title, ctx, prev_responses):
    no_repeat = ""
    if prev_responses:
        no_repeat = "\n\nJá respondido anteriormente (NÃO repita):\n" + "\n".join(f"- {r[:80]}" for r in prev_responses[-3:])

    # Chamada 1: classificação + pontos
    cm = (
        f"Analise a transcrição e responda TRÊS linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO\n"
        f"CONCORRENTE: SIM ou NAO\n"
        f"PONTOS: Liste TODOS os temas/assuntos distintos do trecho em frases separadas\n\n"
        f"Transcrição: {ctx[:600]}"
    )
    cr = client.call_raw("Responda EXATAMENTE 3 linhas.", cm, max_tokens=150).strip()
    has_q = "SIM" in cr.split("\n")[0].upper()
    has_comp = any("CONCORRENTE: SIM" in l.upper() for l in cr.split("\n"))
    clean = ctx
    for l in cr.split("\n"):
        if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break

    # Web search se pergunta
    sc = ""
    if has_q:
        qp = f"Query de busca em inglês, 8 palavras. Só a query.\n\nConversa: {clean[:300]}"
        q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
        if q and "NONE" not in q.upper():
            q += " AWS 2026"
            sr = web_search(q, max_results=2)
            if len(sr) > 50: sc = f"\n\nDados web (2026):\n{sr}"

    # Chamada 2
    if not has_q:
        msg = f"Pontos:\n{clean}\n\nSem pergunta. Contexto + 3 perguntas pro consultor.{no_repeat}{sc}"
    else:
        msg = f"Pontos:\n{clean}\n\nResponda TODOS os temas/dúvidas identificados de forma objetiva. Se tem mais de um assunto, responda cada um separadamente.{no_repeat}{sc}"
    resp = client.call_raw(system, msg, max_tokens=400)
    return cr, clean, resp

results = []
for title, ctx in intervals:
    cr, clean, resp = run_snapshot(title, ctx, previous_responses)
    previous_responses.append(resp[:100])
    
    block = (
        f"\n{'='*70}\n{title}\n{'='*70}\n\n"
        f"📝 TRANSCRIÇÃO DO INTERVALO:\n{ctx}\n\n"
        f"🔍 CHAMADA 1 (classificação + pontos):\n{cr}\n\n"
        f"📋 PONTOS EXTRAÍDOS:\n{clean}\n\n"
        f"📌 RESPOSTA:\n{resp}\n"
    )
    results.append(block)
    print(f"✅ {title[:60]}...")

output = (
    "# Teste Snapshots SEQUENCIAIS — Reunião MUB\n\n"
    "Simula checkpoints reais: cada snapshot recebe só o intervalo desde o último.\n"
    "Testa: não repetir, cobrir todos os assuntos, separar temas.\n\n"
    + "\n".join(results)
)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-mub-sequencial.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-mub-sequencial.md")
