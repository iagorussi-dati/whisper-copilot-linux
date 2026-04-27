#!/usr/bin/env python3
"""Testes de integração do fluxo completo — rodar após qualquer mudança."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()
passed = 0
failed = 0
errors = []

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        errors.append(f"{name}: {detail}")
        print(f"  ❌ {name} — {detail}")

# ═══════════════════════════════════════════════════════════
print("\n1. CARREGAMENTO DE TEMPLATES")
# ═══════════════════════════════════════════════════════════
base = os.path.expanduser("~/whisper-copilot-lite-linux/prompts")

discovery = open(f"{base}/discovery-dati.md").read()
test("Discovery carrega", len(discovery) > 5000, f"got {len(discovery)} chars")

tecnico = open(f"{base}/assistente-objetivo.md").read()
test("Consultor Técnico carrega", len(tecnico) > 5000, f"got {len(tecnico)} chars")

sugestoes = open(f"{base}/sugestoes.md").read()
test("Sugestões carrega", len(sugestoes) > 50, f"got {len(sugestoes)} chars")

# ═══════════════════════════════════════════════════════════
print("\n2. CLASSIFICAÇÃO (Chamada 1)")
# ═══════════════════════════════════════════════════════════
def classify(ctx):
    cm = (
        f"Analise a transcrição e responda TRÊS linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta direta do cliente?)\n"
        f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT?)\n"
        f"PONTOS: 2-4 frases com os pontos cruciais limpos\n\n"
        f"Transcrição: {ctx[:600]}"
    )
    return client.call_raw("Responda EXATAMENTE 3 linhas.", cm, max_tokens=120).strip()

# Pergunta direta
r = classify("Quanto custa o Amazon Q Business depois dos 60 dias?")
test("Pergunta direta → SIM", "SIM" in r.split("\n")[0].upper(), r.split("\n")[0])

# Sem pergunta
r = classify("A gente tem Elastic Beanstalk pro back-end, Aurora como banco, OpenSearch pra pesquisa.")
test("Sem pergunta → NAO", "SIM" not in r.split("\n")[0].upper(), r.split("\n")[0])

# Concorrente
r = classify("Nós já estamos usando o Gemini com o Google Drive pra buscar documentos.")
has_comp = any("CONCORRENTE: SIM" in l.upper() or "CONCORRENTE:SIM" in l.upper() for l in r.split("\n"))
test("Concorrente Gemini → SIM", has_comp, r)

# Sem concorrente
r = classify("A gente usa EC2, S3, Lambda na AWS.")
has_comp = any("CONCORRENTE: SIM" in l.upper() for l in r.split("\n"))
test("Sem concorrente → NAO", not has_comp, r)

# Pontos extraídos
r = classify("Temos um Redis local que não está ativo. Talvez seria pra cache.")
has_points = any(l.strip().upper().startswith("PONTOS:") and len(l.split(":",1)[1].strip()) > 10 for l in r.split("\n"))
test("Pontos extraídos não vazios", has_points, r)

# ═══════════════════════════════════════════════════════════
print("\n3. SNAPSHOT DISCOVERY")
# ═══════════════════════════════════════════════════════════

# Com pergunta
msg = "Pontos:\nCliente pergunta sobre custo do Amazon Q Business após 60 dias.\n\nContribua com sugestões úteis.\n\nO cliente fez uma PERGUNTA direta. Depois das sugestões, adicione:\n📌 Sobre [tema]:\n[resposta]\n💬 \"frase\""
resp = client.call_raw(discovery, msg, max_tokens=5120)
test("Discovery com pergunta → tem 📌", "📌" in resp, resp[:100])
test("Discovery com pergunta → tem 💬", "💬" in resp, resp[:100])

# Sem pergunta
msg = "Pontos:\nMineradora de Curitiba, usa AWS, iniciando em IA.\n\nContribua com sugestões úteis. Não narre quem falou."
resp = client.call_raw(discovery, msg, max_tokens=5120)
test("Discovery sem pergunta → tem sugestões", "💡" in resp or "✅" in resp, resp[:100])

# Não corta
test("Discovery não corta", not resp.endswith("...") and len(resp) > 50, f"ends with: ...{resp[-30:]}")

# ═══════════════════════════════════════════════════════════
print("\n4. SNAPSHOT CONSULTOR TÉCNICO")
# ═══════════════════════════════════════════════════════════

# Com pergunta
msg = "Pontos:\nPergunta sobre tempo de execução do Lambda e limite de 15 minutos.\n\nResponda a dúvida técnica de forma objetiva. Tamanho: CURTA."
resp = client.call_raw(tecnico, msg, max_tokens=5120)
test("Técnico com pergunta → tem 📌", "📌" in resp, resp[:100])
test("Técnico com pergunta → tem 💬", "💬" in resp, resp[:100])

# Sem pergunta
msg = "Pontos:\nCliente usa Beanstalk, Aurora, OpenSearch.\n\nSem pergunta técnica. Contexto em 1-2 frases + 3 perguntas pro consultor.\n📌 [contexto]\n💬 Perguntas:\n- \"1\"\n- \"2\"\n- \"3\""
resp = client.call_raw(tecnico, msg, max_tokens=5120)
test("Técnico sem pergunta → sugere perguntas", "?" in resp, resp[:100])

# ═══════════════════════════════════════════════════════════
print("\n5. INTERVALO DE CHECKPOINT")
# ═══════════════════════════════════════════════════════════

# Snap 1
ctx1 = "Precisamos terceirizar a AWS pra focar no desenvolvimento. Temos só EC2."
msg1 = f"Pontos:\n{ctx1}\n\nContribua com sugestões úteis."
resp1 = client.call_raw(discovery, msg1, max_tokens=5120)

# Snap 2 — intervalo diferente, com no_repeat
ctx2 = "O site de ingressos tem picos de 5 a 2000 pessoas. Precisamos de auto-scaling."
msg2 = f"Pontos:\n{ctx2}\n\nContribua com sugestões úteis.\n\nJá respondido (NÃO repita):\n- {resp1[:80]}"
resp2 = client.call_raw(discovery, msg2, max_tokens=5120)

# Snap 2 não deve falar de terceirizar (era do snap 1)
test("Snap 2 foca no intervalo (escalabilidade)", "escal" in resp2.lower() or "pico" in resp2.lower() or "auto" in resp2.lower(), resp2[:150])
test("Snap 2 não repete snap 1", "terceirizar" not in resp2.lower()[:200], resp2[:200])

# ═══════════════════════════════════════════════════════════
print("\n6. FULLCONTEXT")
# ═══════════════════════════════════════════════════════════

full = "Somos mineradora. Usamos EC2. Precisamos terceirizar. Site de ingressos com picos. Já usamos Gemini. Billing R$3k no cartão."
msg = (f"Conversa completa:\n{full}\n\nAnalise a conversa toda e identifique os principais temas.\n"
       f"Para cada tema, gere sugestões separadas.\nNo final, liste próximos passos.\nSeja objetivo.")
resp = client.call_raw(discovery, msg, max_tokens=5120)
test("Fullcontext → tem múltiplos temas", resp.count("📌") >= 2 or resp.count("####") >= 2 or resp.count("💡") >= 3, f"📌={resp.count('📌')} 💡={resp.count('💡')}")
test("Fullcontext → tem próximos passos", "próximo" in resp.lower() or "passo" in resp.lower() or "✅" in resp, resp[-200:])
test("Fullcontext não corta", len(resp) > 100, f"{len(resp)} chars")

# ═══════════════════════════════════════════════════════════
print("\n7. WEB SEARCH")
# ═══════════════════════════════════════════════════════════

# Query limpa
qp = "Responda APENAS query de busca em inglês, 8 palavras. Só a query.\n\nConversa: Nós usamos Gemini com Google Drive pra buscar documentos."
q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
test("Query limpa (não transcrição crua)", len(q) < 80 and "###" not in q, q)

# Search retorna resultados
sr = web_search(q + " AWS 2026", max_results=3)
test("Web search retorna resultados", len(sr) > 50, f"{len(sr)} chars")

# ═══════════════════════════════════════════════════════════
print("\n8. CACHE")
# ═══════════════════════════════════════════════════════════

# Primeira chamada (cache write)
resp1 = client.call_raw(discovery, "Teste de cache.", max_tokens=10)
test("Cache: primeira chamada funciona", len(resp1) > 0, resp1)

# Segunda chamada (cache read — deve ser mais rápida)
t0 = time.time()
resp2 = client.call_raw(discovery, "Teste de cache 2.", max_tokens=10)
t1 = time.time() - t0
test("Cache: segunda chamada funciona", len(resp2) > 0, resp2)
test("Cache: segunda chamada < 3s", t1 < 3, f"{t1:.2f}s")

# ═══════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"RESULTADO: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.0f}%)")
if errors:
    print(f"\nERROS ({len(errors)}):")
    for e in errors:
        print(f"  ❌ {e}")
print(f"{'='*60}")
