#!/usr/bin/env python3
"""Teste das 4 abordagens de latência — mesmo cenário, mesma reunião."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

# Pre-warm
client.call_raw(system, "Aguarde.", max_tokens=10)
print("Cache warmed ✅\n")

# Chunks de 1 minuto (simulando transcrição real)
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

# Último pedaço (30s após último chunk)
last_30s = "[Juliano] Conseguimos passar volume de usuários, produtos, transações pra mensurar máquinas."

# Contexto completo (como seria sem otimização)
full_context = "\n".join(chunks) + "\n" + last_30s

temas = ['System Manager','deploy','GitHub','Next.js','build','CodePipeline','VPN','Bastion','subnet','Virginia','custo','Terraform','WAF','incentivo','budget','CloudWatch']

def check_coverage(text):
    cobertos = [t for t in temas if t.lower() in text.lower()]
    return len(cobertos), len(temas), cobertos

results = []

# ═══════════════════════════════════════════════════════════
print("="*60)
print("ABORDAGEM 0: ATUAL (sem otimização)")
print("="*60)
t0 = time.time()
# Chamada 1: classifica + resume
cr = client.call_raw("Sem markdown.", f"CLASSIFICAÇÃO: SIM ou NAO\nCONCORRENTE: SIM ou NAO\nCONTEXTO: Resuma cobrindo todos os assuntos. Foque na dor.\nRESPOSTA: CURTA/MÉDIA/LONGA\n\nTranscrição:\n{full_context}", max_tokens=5120).strip()
t_c1 = time.time() - t0
clean = full_context
for l in cr.split("\n"):
    s = l.strip().replace("*","").replace("#","").strip()
    if s.upper().startswith("CONTEXTO:"):
        rest = s.split(":",1)[1].strip()
        if rest: clean = rest
        break
t0 = time.time()
resp = client.call_raw(system, f"Contexto:\n{clean}\n\nResponda curto e objetivo focado na dor.", max_tokens=5120)
t_c2 = time.time() - t0
cov = check_coverage(clean)
total = t_c1 + t_c2
print(f"C1={t_c1:.1f}s C2={t_c2:.1f}s Total={total:.1f}s | Cobertura={cov[0]}/{cov[1]} | Ctx={len(clean)}chars")
results.append(f"ATUAL: C1={t_c1:.1f}s C2={t_c2:.1f}s Total={total:.1f}s Cobertura={cov[0]}/{cov[1]} Ctx={len(clean)}chars")

# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ABORDAGEM 1: ROLLING SUMMARY (resumo incremental a cada chunk)")
print("="*60)
rolling = ""
t_chunks_total = 0
for i, chunk in enumerate(chunks):
    t0 = time.time()
    rolling = client.call_raw(
        "Atualize o resumo. Sem markdown. Só o resumo atualizado.",
        f"Resumo atual: {rolling if rolling else 'vazio'}\nNova transcrição: {chunk}\n\nAtualize o resumo incluindo os novos pontos. Mantenha tudo que já tinha. Foque na dor do cliente.",
        max_tokens=500
    ).strip()
    t_chunk = time.time() - t0
    t_chunks_total += t_chunk
    print(f"  Chunk {i+1}: {t_chunk:.1f}s | Resumo: {len(rolling)}chars")

# Snapshot: resumo + últimos 30s
t0 = time.time()
snap_ctx = f"{rolling}\nÚltimo trecho: {last_30s}"
resp = client.call_raw(system, f"Contexto:\n{snap_ctx}\n\nResponda curto e objetivo focado na dor.", max_tokens=5120)
t_snap = time.time() - t0
cov = check_coverage(rolling)
print(f"\nSnapshot: {t_snap:.1f}s | Chunks total: {t_chunks_total:.1f}s ({t_chunks_total/len(chunks):.1f}s/chunk)")
print(f"Cobertura={cov[0]}/{cov[1]} | Resumo={len(rolling)}chars")
results.append(f"ROLLING: Snap={t_snap:.1f}s ChunksTotal={t_chunks_total:.1f}s ({t_chunks_total/len(chunks):.1f}s/chunk) Cobertura={cov[0]}/{cov[1]} Resumo={len(rolling)}chars")

# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ABORDAGEM 3: PRÉ-PROCESSAMENTO LOCAL (keywords)")
print("="*60)
import re
keywords_acc = set()
for chunk in chunks:
    # Extrai palavras-chave simples
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*|[A-Z]{2,}|[a-z]+\s(?:de|do|da|pra|pro)\s[a-z]+', chunk)
    keywords_acc.update(w.strip() for w in words if len(w) > 3)

local_ctx = ", ".join(sorted(keywords_acc)[:30])
t0 = time.time()
# Chamada 1: classifica com keywords
cr = client.call_raw("Sem markdown.", f"CLASSIFICAÇÃO: SIM ou NAO\nCONCORRENTE: SIM ou NAO\nCONTEXTO: Resuma baseado nestas keywords: {local_ctx}. E neste último trecho: {last_30s}\nRESPOSTA: CURTA/MÉDIA/LONGA", max_tokens=5120).strip()
t_c1 = time.time() - t0
clean = local_ctx
for l in cr.split("\n"):
    s = l.strip().replace("*","").replace("#","").strip()
    if s.upper().startswith("CONTEXTO:"):
        rest = s.split(":",1)[1].strip()
        if rest: clean = rest
        break
t0 = time.time()
resp = client.call_raw(system, f"Contexto:\n{clean}\n\nResponda curto e objetivo.", max_tokens=5120)
t_c2 = time.time() - t0
cov = check_coverage(clean)
total = t_c1 + t_c2
print(f"C1={t_c1:.1f}s C2={t_c2:.1f}s Total={total:.1f}s | Cobertura={cov[0]}/{cov[1]} | Ctx={len(clean)}chars")
results.append(f"LOCAL: C1={t_c1:.1f}s C2={t_c2:.1f}s Total={total:.1f}s Cobertura={cov[0]}/{cov[1]} Ctx={len(clean)}chars")

# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ABORDAGEM 4: HÍBRIDA (rolling summary + snapshot rápido)")
print("="*60)
# Reutiliza o rolling summary já calculado
t0 = time.time()
resp = client.call_raw(system, f"Contexto do cliente (resumo acumulado):\n{rolling}\n\nÚltimo trecho: {last_30s}\n\nDê uma resposta curta e objetiva focada na dor do cliente. 📌 + 💬.", max_tokens=5120)
t_snap2 = time.time() - t0
cov = check_coverage(rolling)
print(f"Snapshot: {t_snap2:.1f}s (resumo já pronto) | Cobertura={cov[0]}/{cov[1]}")
results.append(f"HÍBRIDA: Snap={t_snap2:.1f}s (resumo pronto) Cobertura={cov[0]}/{cov[1]}")

# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("RESUMO FINAL")
print("="*60)
for r in results:
    print(f"  {r}")

with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-abordagens-latencia.md"), "w") as f:
    f.write("# Teste Abordagens de Latência\n\n")
    f.write(f"Cenário: 9 chunks de 1min + snapshot no final\n{len(temas)} temas pra cobrir\n\n")
    for r in results:
        f.write(f"- {r}\n")
    f.write(f"\nRolling summary final ({len(rolling)} chars):\n{rolling}\n")
print(f"\n📄 Salvo em tests/resultado-abordagens-latencia.md")
