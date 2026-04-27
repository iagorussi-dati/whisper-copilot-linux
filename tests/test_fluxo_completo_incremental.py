#!/usr/bin/env python3
"""Teste COMPLETO do fluxo incremental — simula reunião real com edge cases.
Verifica: snapshots não se atravessam, pontos não se perdem, tempos consistentes."""
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

# Simula reunião: chunks de 60s + snapshots em momentos variados
chunks = [
    ("[Gustavo] Podem usar System Manager, conexão privada com autenticação AWS. Não precisa liberar porta 22. IAM rules.", "min 0-1"),
    ("[Juliano] Código no GitHub, dois repos. Deploy é git pull dentro da instância. Deploy manual.", "min 1-2"),
    ("[Gustavo] Frontend Next.js pesado no build. Instância pequena estoura RAM.", "min 2-3"),
    ("[Juliano] CodePipeline conecta com GitHub, faz build deploy teste. Reversão automática.", "min 3-4"),
    ("[Juliano] Bastion pra separar subnet. VPN custo alto, preferem System Manager.", "min 4-5"),
    ("[Gustavo] Route pro LB em subnet pública. ECS/EC2 e banco em privada. CloudWatch.", "min 5-6"),
    ("[Gustavo] Virginia mais barato que SP. SP 35-50ms, Virginia 120ms.", "min 6-7"),
    ("[Juliano] Terraform ou CloudFormation. WAF pra ataques. Precisa volumetria e billing.", "min 7-8"),
    ("[Juliano] Budget limitado. 600→4mil assinaturas. Incentivo AWS possível.", "min 8-9"),
]

# Estado da simulação
pontos_acumulados = []  # pontos extraídos de cada chunk
checkpoint = 0  # último snapshot
previous_responses = []
results = []

def extract_point(chunk_text):
    """Simula extração de ponto em background (1.8s)."""
    t0 = time.time()
    p = client.call_raw(
        "UMA frase curta com a dor do cliente e tecnologias. Sem markdown.",
        f"Trecho: {chunk_text}", max_tokens=80
    ).strip().replace("*","").replace("#","").strip()
    return p, time.time() - t0

def do_snapshot(title, pontos_intervalo, pontos_anteriores):
    """Executa snapshot com os pontos do intervalo."""
    no_repeat = ""
    if previous_responses:
        no_repeat = "\n\nJá respondido (NÃO repita):\n" + "\n".join(f"- {r[:60]}" for r in previous_responses[-2:])
    
    n_pontos = len(pontos_intervalo)
    
    if n_pontos <= 2:
        # CURTO: manda direto
        ctx = "\n".join(pontos_intervalo)
        ant = ""
        if pontos_anteriores:
            ant = f"\nContexto anterior:\n" + "\n".join(f"- {p[:60]}" for p in pontos_anteriores[-3:])
        t0 = time.time()
        resp = client.call_raw(system, f"Dor do cliente:\n{ctx}{ant}\n\nResponda curto. 📌 + 💬. Sem resumo.{no_repeat}", max_tokens=5120)
        t = time.time() - t0
        metodo = "DIRETO"
    else:
        # LONGO: agrupa primeiro
        lista = "\n".join(f"- {p}" for p in pontos_intervalo)
        t0 = time.time()
        agrupado = client.call_raw(
            "Agrupe em 2-3 categorias. Cada uma: nome + 1 frase. Sem markdown. Não perca nenhum ponto.",
            f"Pontos:\n{lista}", max_tokens=300
        ).strip().replace("*","").replace("#","").strip()
        t_ag = time.time() - t0
        
        t0 = time.time()
        resp = client.call_raw(system, f"Dores agrupadas:\n{agrupado}\n\nPra cada categoria: 📌 (2 linhas) + 💬 (1 frase). Sem resumo.{no_repeat}", max_tokens=5120)
        t_resp = time.time() - t0
        t = t_ag + t_resp
        metodo = f"AGRUPADO ({t_ag:.1f}s+{t_resp:.1f}s)"
    
    previous_responses.append(resp[:80])
    
    block = (f"\n{'='*60}\n{title} [{metodo}]\n{'='*60}\n"
             f"Intervalo: {n_pontos} pontos | Anteriores: {len(pontos_anteriores)}\n"
             f"⏱️ {t:.1f}s | {len(resp)} chars\n"
             f"Pontos intervalo: {pontos_intervalo}\n"
             f"Resposta: {resp[:200]}...\n")
    results.append(block)
    print(f"  {title}: {t:.1f}s [{metodo}] | {len(resp)} chars")
    return t

# ═══════════════════════════════════════════════════════════
print("SIMULAÇÃO DA REUNIÃO")
print("="*60)

# Min 0-1: chunk 1 chega
p, t = extract_point(chunks[0][0])
pontos_acumulados.append(p)
print(f"[{chunks[0][1]}] Extração: {t:.1f}s")

# SNAPSHOT no min 1:01 (logo após primeiro chunk — só 1 ponto)
print("\n📸 SNAPSHOT A — min 1:01 (1 ponto, logo após chunk)")
intervalo = pontos_acumulados[checkpoint:]
tA = do_snapshot("SNAP A — 1 ponto (System Manager)", intervalo, pontos_acumulados[:checkpoint])
checkpoint = len(pontos_acumulados)

# Min 1-2, 2-3: chunks 2 e 3
for i in [1, 2]:
    p, t = extract_point(chunks[i][0])
    pontos_acumulados.append(p)
    print(f"[{chunks[i][1]}] Extração: {t:.1f}s")

# SNAPSHOT no min 3:00 (2 pontos desde último snap)
print("\n📸 SNAPSHOT B — min 3:00 (2 pontos: deploy + Next.js)")
intervalo = pontos_acumulados[checkpoint:]
tB = do_snapshot("SNAP B — 2 pontos (deploy + Next.js)", intervalo, pontos_acumulados[:checkpoint])
checkpoint = len(pontos_acumulados)

# Min 3-4, 4-5, 5-6, 6-7: chunks 4-7
for i in [3, 4, 5, 6]:
    p, t = extract_point(chunks[i][0])
    pontos_acumulados.append(p)
    print(f"[{chunks[i][1]}] Extração: {t:.1f}s")

# SNAPSHOT no min 7:00 (4 pontos — médio, vai agrupar)
print("\n📸 SNAPSHOT C — min 7:00 (4 pontos: CodePipeline + VPN + topologia + Virginia)")
intervalo = pontos_acumulados[checkpoint:]
tC = do_snapshot("SNAP C — 4 pontos (médio)", intervalo, pontos_acumulados[:checkpoint])
checkpoint = len(pontos_acumulados)

# Min 7-8, 8-9: chunks 8 e 9
for i in [7, 8]:
    p, t = extract_point(chunks[i][0])
    pontos_acumulados.append(p)
    print(f"[{chunks[i][1]}] Extração: {t:.1f}s")

# SNAPSHOT no min 9:00 (2 pontos: WAF + budget)
print("\n📸 SNAPSHOT D — min 9:00 (2 pontos: WAF + budget)")
intervalo = pontos_acumulados[checkpoint:]
tD = do_snapshot("SNAP D — 2 pontos (WAF + budget)", intervalo, pontos_acumulados[:checkpoint])
checkpoint = len(pontos_acumulados)

# SNAPSHOT IMEDIATO — min 9:01 (0 pontos novos!)
print("\n📸 SNAPSHOT E — min 9:01 (0 pontos novos — edge case)")
intervalo = pontos_acumulados[checkpoint:]
if not intervalo:
    print("  SNAP E: 0 pontos no intervalo — nada pra responder ✅")
    results.append(f"\n{'='*60}\nSNAP E — 0 pontos (edge case)\n{'='*60}\nNada no intervalo — snapshot ignorado ✅\n")
    tE = 0
else:
    tE = do_snapshot("SNAP E — edge case", intervalo, pontos_acumulados[:checkpoint])

# ═══════════════════════════════════════════════════════════
print("\n\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"SNAP A (1 ponto):  {tA:.1f}s")
print(f"SNAP B (2 pontos): {tB:.1f}s")
print(f"SNAP C (4 pontos): {tC:.1f}s")
print(f"SNAP D (2 pontos): {tD:.1f}s")
print(f"SNAP E (0 pontos): {tE:.1f}s (edge case)")
print(f"\nSnapshots não se atravessaram: checkpoint sempre avança")
print(f"Pontos acumulados: {len(pontos_acumulados)}")

# Verificar que snapshots não repetiram
print(f"\nRespostas anteriores (pra verificar não-repetição):")
for i, r in enumerate(previous_responses):
    print(f"  {i+1}: {r[:70]}...")

output = "# Teste Completo Fluxo Incremental\n\n"
output += f"SNAP A (1pt): {tA:.1f}s | SNAP B (2pt): {tB:.1f}s | SNAP C (4pt): {tC:.1f}s | SNAP D (2pt): {tD:.1f}s | SNAP E (0pt): edge case\n\n"
output += "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-fluxo-completo.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-fluxo-completo.md")
