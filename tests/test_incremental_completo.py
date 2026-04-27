#!/usr/bin/env python3
"""Teste abordagem incremental — snapshots curtos, médios e longos na reunião Defin."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()
client.call_raw(system, "Aguarde.", max_tokens=10)
print("Cache warmed ✅\n")

# Chunks de 1 minuto da reunião Defin (9 chunks)
chunks = [
    "[Gustavo] Podem usar System Manager, conexão privada com autenticação AWS. Não precisa liberar porta 22. IAM rules, tranquilo.",
    "[Juliano] Código no GitHub, dois repos. Deploy é git pull dentro da instância. Só pra teste. Deploy hoje bem manual.",
    "[Gustavo] Frontend Next.js pesado no build. Instância pequena estoura RAM. Fazemos build local e upload.",
    "[Juliano] CodePipeline conecta com GitHub, faz build deploy teste. Se causar indisponibilidade reverte. Custo 1,5 dólar.",
    "[Juliano] Interessante Bastion, separar subnet pra reduzir área de ataque. Vocês indicam VPN? VPN gera custo alto, não recomendamos.",
    "[Gustavo] Route joga pro LB em subnet pública. ECS/EC2 e banco em subnet privada. CI/CD com CodePipeline. CloudWatch.",
    "[Gustavo] Recomendando Virginia. SP mais caro, quase dobro. SP 35-50ms, Virginia 120ms. Migrar pra reduzir custo.",
    "[Juliano] Terraform ou CloudFormation. WAF pra ataques. Preciso volumetria e billing atual. Incentivo AWS possível.",
    "[Juliano] Budget limitado. 600 assinaturas início próximo ano, 4 mil final. Movimentação financeira grande.",
]

# Fase 1: Extrair pontos incrementais (simula background a cada 60s)
print("FASE 1: Extração incremental de pontos (background)")
print("="*60)
pontos = []
t_extract_total = 0
for i, chunk in enumerate(chunks):
    t0 = time.time()
    p = client.call_raw(
        "UMA frase curta com a dor do cliente e tecnologias citadas. Sem markdown.",
        f"Trecho: {chunk}",
        max_tokens=80
    ).strip().replace("*","").replace("#","").strip()
    t_c = time.time() - t0
    t_extract_total += t_c
    pontos.append(p)
    print(f"  Chunk {i+1}: {t_c:.1f}s | {p[:90]}")

print(f"\nTotal extração: {t_extract_total:.1f}s ({t_extract_total/len(chunks):.1f}s/chunk)")

results = []

def do_snapshot(title, ponto_intervalo, pontos_anteriores=None):
    """Simula snapshot: manda ponto do intervalo + contexto anterior opcional."""
    ctx_anterior = ""
    if pontos_anteriores:
        ctx_anterior = f"\nContexto anterior da reunião:\n" + "\n".join(f"- {p}" for p in pontos_anteriores)
    
    t0 = time.time()
    msg = f"Dor do cliente agora:\n{ponto_intervalo}{ctx_anterior}\n\nResponda curto focado na dor. 📌 + 💬. Sem resumo."
    resp = client.call_raw(system, msg, max_tokens=5120)
    t = time.time() - t0
    
    block = (f"\n{'='*60}\n{title}\n{'='*60}\n"
             f"\n📝 PONTO DO INTERVALO:\n{ponto_intervalo}\n"
             f"\n📋 CONTEXTO ANTERIOR: {len(pontos_anteriores or [])} pontos ({len(ctx_anterior)} chars)\n"
             f"\n⏱️ TEMPO: {t:.1f}s | Input: {len(msg)} chars\n"
             f"\n📌 RESPOSTA ({len(resp)} chars):\n{resp}\n")
    results.append(block)
    print(f"  {title}: {t:.1f}s | {len(resp)} chars")
    return t

# ═══════════════════════════════════════════════════════════
print("\n\nFASE 2: SNAPSHOTS CURTOS (1 chunk = ~1 min)")
print("="*60)
t1 = do_snapshot("CURTO 1 — Só chunk 1 (System Manager)", pontos[0])
t2 = do_snapshot("CURTO 2 — Só chunk 4 (CodePipeline)", pontos[3], pontos[:3])
t3 = do_snapshot("CURTO 3 — Só chunk 7 (Virginia)", pontos[6], pontos[:6])

# ═══════════════════════════════════════════════════════════
print("\n\nFASE 3: SNAPSHOTS MÉDIOS (3 chunks = ~3 min)")
print("="*60)
medio1 = "\n".join(pontos[0:3])
t4 = do_snapshot("MÉDIO 1 — Chunks 1-3 (SSM + deploy + Next.js)", medio1)
medio2 = "\n".join(pontos[3:6])
t5 = do_snapshot("MÉDIO 2 — Chunks 4-6 (CodePipeline + VPN + topologia)", medio2, pontos[:3])
medio3 = "\n".join(pontos[6:9])
t6 = do_snapshot("MÉDIO 3 — Chunks 7-9 (Virginia + WAF + budget)", medio3, pontos[:6])

# ═══════════════════════════════════════════════════════════
print("\n\nFASE 4: SNAPSHOT LONGO (todos os 9 chunks = ~9 min)")
print("="*60)
longo = "\n".join(pontos)
t7 = do_snapshot("LONGO — Todos os 9 chunks", longo)

# ═══════════════════════════════════════════════════════════
print("\n\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"Extração: {t_extract_total/len(chunks):.1f}s/chunk (background)")
print(f"Curto (1 chunk):  {(t1+t2+t3)/3:.1f}s média")
print(f"Médio (3 chunks): {(t4+t5+t6)/3:.1f}s média")
print(f"Longo (9 chunks): {t7:.1f}s")

output = "# Teste Abordagem Incremental — Curto/Médio/Longo\n\n"
output += f"Extração: {t_extract_total/len(chunks):.1f}s/chunk\n"
output += f"Curto: {(t1+t2+t3)/3:.1f}s média | Médio: {(t4+t5+t6)/3:.1f}s média | Longo: {t7:.1f}s\n\n"
output += "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-incremental-completo.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-incremental-completo.md")
