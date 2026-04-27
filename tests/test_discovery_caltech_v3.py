#!/usr/bin/env python3
"""Teste Discovery — snapshots sequenciais + fullcontext na reunião Caltech."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

previous = []

def snapshot(title, ctx):
    no_repeat = ""
    if previous:
        no_repeat = "\n\nJá respondido (NÃO repita):\n" + "\n".join(f"- {r[:80]}" for r in previous[-3:])

    # Chamada 1: classificação + pontos
    cm = (
        f"Analise a transcrição e responda TRÊS linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta direta do cliente?)\n"
        f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT?)\n"
        f"PONTOS: 2-4 frases com os pontos cruciais limpos\n\n"
        f"Transcrição: {ctx[:600]}"
    )
    cr = client.call_raw("Responda EXATAMENTE 3 linhas.", cm, max_tokens=120).strip()
    has_q = "SIM" in cr.split("\n")[0].upper()
    has_comp = any("CONCORRENTE: SIM" in l.upper() for l in cr.split("\n"))
    clean = ctx
    for l in cr.split("\n"):
        if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break

    # Web search se concorrente
    sc = ""
    if has_comp:
        from backend.search import web_search
        qp = f"Query de busca em inglês, 8 palavras. Só a query.\n\nConversa: {clean[:300]}"
        q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
        if q and "NONE" not in q.upper():
            q += " vs AWS privacy security 2026"
            sr = web_search(q, max_results=3)
            if len(sr) > 50: sc = f"\n\nDados web (2026) — USE sobre diferenças com concorrentes:\n{sr}"

    q_instr = ""
    if has_q:
        q_instr = ("\n\nO cliente fez uma PERGUNTA direta. Depois das sugestões, adicione:\n"
                   "📌 Sobre [tema da pergunta]:\n[resposta objetiva 2-3 frases]\n"
                   "💬 \"frase pronta de como falar pro cliente\"")
    comp_instr = " O cliente mencionou concorrente — diferencie AWS com fatos, sem atacar." if has_comp else ""

    msg = (f"Pontos da conversa:\n{clean}\n\n"
           f"Contribua com sugestões úteis. Seja objetivo e curto. Não narre quem falou.{comp_instr}{q_instr}{no_repeat}{sc}")

    resp = client.call_raw(system, msg, max_tokens=5120)
    previous.append(resp[:100])
    return f"\n{'='*70}\n{title}\n{'='*70}\n\n📝 TRANSCRIÇÃO:\n{ctx}\n\n🔍 CHAMADA 1:\n{cr}\nQ={has_q} Comp={has_comp}\nPontos: {clean}\n\n📌 RESPOSTA:\n{resp}\n"

results = []

results.append(snapshot("SNAP 1 — Mineradora, pesquisando IA, sem foco",
"Somos uma mineradora da região de Curitiba, parte de suco alcooleiro, fertilizantes. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA. Não tem um ponto específico. O Paulo é do time de TI, desenvolvedor. O Abner é do setor de melhoria contínua. O Carlos é da contabilidade."))

results.append(snapshot("SNAP 2 — Contabilidade usa DataSul e planilhas",
"Hoje a gente trabalha com o nosso sistema interno, o DataSul. Na parte de conferência, trabalhamos com planilhas. Fazemos lançamento da nota e conferência à base de planilhas."))

results.append(snapshot("SNAP 3 — Q Business roda local? Dados sensíveis",
"Essa IA da Amazon roda somente em nuvem, direto na AWS, ou a gente conseguiria rodar localmente com servidor nosso? É que eu fiz essa pergunta mais na questão de tratar dados sensíveis. A diretoria tem preferência de rodar localmente."))

results.append(snapshot("SNAP 4 — Já usa Gemini com Google Drive + privacidade",
"Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. O que foi tratado em tal situação, ele busca e traz. Isso já estamos utilizando. Esses documentos já estão lá no Drive. Se você sobe os dados no próprio Gemini ele usa para retreinar modelos, isso se torna público."))

results.append(snapshot("SNAP 5 — Como conectar ERP on-prem + 60 dias pouco pra APIs",
"Como funcionaria? O serviço da Amazon estaria conectado aqui, quero saber como faria a comunicação pra ler nossas informações locais, as que estão no ERP. Pra mim não ficou bem claro. As informações principais estão dentro do ERP, o DataSul. Só que pra isso a gente vai construir APIs de conexão. Talvez nesses 60 dias seja muito trabalhoso."))

results.append(snapshot("SNAP 6 — Quer case real + precisa falar com gerente",
"Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso. Pra o nosso querer aqui, ver alguma coisa que dá pra fazer. Vocês já implementaram isso em outro lugar? Vou conversar com a nossa gerente, que não pôde participar hoje. Não posso passar uma definição agora sem autorização dela."))

# FULLCONTEXT
full = """Somos uma mineradora da região de Curitiba. Temos serviços na Amazon, iniciando em IA. Não tem ponto específico.
Trabalhamos com DataSul. Conferência com planilhas.
Essa IA roda só em nuvem ou localmente? Dados sensíveis. Diretoria prefere local.
Consigo enviar áudio ou só texto?
Como funciona a comunicação pra ler informações locais no ERP? Não ficou claro.
Informações principais no ERP DataSul. Automatização com Gemini e Google Drive.
Achei corrida a reunião. Não fico nítido como utilizar.
Já usamos Gemini com Google Drive pra buscar documentos.
Se sobe dados no Gemini ele usa pra retreinar modelos, se torna público.
Construir APIs pode ser trabalhoso em 60 dias.
Q Business tem conexão nativa com Google Drive. Não precisa API.
Vou conversar com a gerente e volto."""

# Fullcontext com web search
sr = ""
qp = f"Query em inglês, 8 palavras.\n\nConversa: {full[:300]}"
q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
if q and "NONE" not in q.upper():
    q += " Amazon Q Business Gemini privacy 2026"
    sr_raw = web_search(q, max_results=3)
    if len(sr_raw) > 50: sr = f"\n\nDados web (2026):\n{sr_raw}"

fullctx_msg = (
    f"Conversa completa:\n{full}\n\n"
    f"Analise a conversa toda e identifique os principais temas que surgiram.\n"
    f"Para cada tema, gere sugestões separadas por categoria.\n"
    f"Se o cliente fez perguntas, responda cada uma com 📌 + 💬.\n"
    f"Identifique problemas que o cliente pode não ter percebido.\n"
    f"No final, liste próximos passos.\n"
    f"Seja objetivo e curto em cada tema. Não adicione resumo ou conclusão extra."
    f"{sr}"
)
resp = client.call_raw(system, fullctx_msg, max_tokens=5120)
results.append(f"\n{'='*70}\nFULLCONTEXT — CONVERSA TODA\n{'='*70}\n\nRESPOSTA:\n{resp}\n")
print("✅ FULLCONTEXT")

output = "# Teste Discovery — Reunião Caltech\n\n6 snapshots + 1 fullcontext\nPrompt: discovery-dati.md\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-discovery-caltech.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-discovery-caltech.md")
