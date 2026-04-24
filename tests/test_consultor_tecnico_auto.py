#!/usr/bin/env python3
"""Teste AUTOMÁTICO consultor técnico — sem instrução, só system prompt + contexto.
O copiloto tem que identificar sozinho o que responder."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/consultor-tecnico.md")) as f:
    system = f.read()

results = []

# Simula exatamente como o código faz: pega o contexto, faz web search, manda pro modelo
# SEM NENHUMA INSTRUÇÃO EXTRA — só "Conversa:\n{ctx}" igual o snapshot real
def snapshot(title, ctx):
    # Web search automático (como o código faz)
    query = ctx[:120] + " AWS pricing specs 2026"
    print(f"🔍 Pesquisando: {query[:70]}...")
    sr = web_search(query, max_results=3)
    
    # Exatamente como o _generate_snapshot_response faz
    user_msg = (
        f"Conversa:\n{ctx}\n\n"
        f"Contribua com algo útil sobre o que foi dito. Não narre quem falou o quê. Não diga 'Pessoa 1 falou' ou 'Foi mencionado que'. Apenas responda."
        f"\n\nDados atualizados da web (2026) — USE esses dados na resposta, priorize informações atualizadas:\n{sr}"
    )
    
    resp = client.call_raw(system, user_msg, max_tokens=350)
    results.append(f"\n{'='*80}\n{title}\n{'='*80}\n\nRESPOSTA:\n{resp}\n")
    print(f"✅ {title[:60]}...")

# 10 snapshots simulando Win+D em momentos-chave — SEM INSTRUÇÃO
snapshot("SNAP 1 — Cliente explica que é mineradora, usa DataSul, planilhas, pesquisando IA",
"""[3:31] Naor: Somos uma mineradora da região de Curitiba, parte de suco alcooleiro, fertilizantes. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA. Não tem um ponto específico.
[6:47] Carlos: Hoje a gente trabalha com o DataSul. Na parte de conferência, trabalhamos com planilhas.""")

snapshot("SNAP 2 — Cliente pergunta se Q Business roda local (dados sensíveis)",
"""[20:14] Naor: Essa IA da Amazon roda somente em nuvem, direto na AWS, ou a gente conseguiria rodar localmente com servidor nosso?
[20:46] Naor: É que eu fiz essa pergunta mais na questão de tratar dados sensíveis. A diretoria tem preferência de rodar localmente.""")

snapshot("SNAP 3 — Cliente pergunta se aceita áudio",
"""[21:43] Naor: Eu consigo enviar mensagens de áudio ou fazer uma conversação por áudio ou é somente texto?""")

snapshot("SNAP 4 — Cliente não entende como conectar com ERP on-prem",
"""[23:23] Naor: Como funcionaria? O serviço da Amazon estaria conectado aqui, quero saber como faria a comunicação pra ler nossas informações locais, as que estão no ERP, não as públicas da internet. Pra mim não ficou bem claro.
[25:06] Naor: As informações principais estão dentro do ERP, o DataSul.""")

snapshot("SNAP 5 — Cliente fala que já usa Gemini com Google Drive",
"""[31:43] Naor: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. O que foi tratado em tal situação, ele busca e traz. Isso já estamos utilizando.
[32:14] Naor: Esses documentos já estão lá no Drive.
[33:25] Naor: Nós já temos um caminhão de informação lá no Drive. Quero ver quanto foi faturado em tal data, quem é meu melhor cliente, meu melhor fornecedor.""")

snapshot("SNAP 6 — Alguém da Dati menciona que Gemini retreina com dados",
"""[31:43] Naor: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos.
[32:37] Guilherme (Dati): Se você sobe os dados no próprio Gemini ele usa para retreinar modelos, isso se torna público.
[33:25] Naor: Nós já temos um caminhão de informação lá no Drive.""")

snapshot("SNAP 7 — Cliente acha 60 dias pouco pra APIs",
"""[33:43] Naor: Só que pra isso a gente vai construir APIs de conexão. Talvez nesses 60 dias seja muito trabalhoso pra gente construir as APIs e testar.
[34:16] Guilherme (Dati): Hoje o Amazon Q Business tem conexão nativa com Google Drive, OneDrive. Não precisaria de API pra isso.""")

snapshot("SNAP 8 — Cliente quer saber custo do Q Business",
"""[15:01] Naor: E o Q Business em si, quanto custa depois dos 60 dias?""")

snapshot("SNAP 9 — Cliente confuso, acha reunião corrida, quer exemplo real",
"""[28:00] Naor: Pra ser sincero, achei um pouco corrida essa reunião. Não fico bem nítido como utilizar isso.
[28:45] Naor: Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso.""")

snapshot("SNAP 10 — Cliente precisa falar com gerente antes de decidir",
"""[27:19] Naor: Vou conversar com a nossa gerente, que não pôde participar hoje. Não posso passar uma definição agora sem autorização dela.
[35:45] Naor: Entendi. Vou conversar com a gerente e tendo parecer dela a gente volta a conversar.""")

# FULLCONTEXT — conversa toda, sem instrução extra além do formato do fullcontext
print("\n🔍 Pesquisando fullcontext...")
full_ctx = """[3:31] Naor: Somos uma mineradora da região de Curitiba. Temos serviços na Amazon, iniciando em IA. Não tem ponto específico.
[6:47] Carlos: Trabalhamos com DataSul. Conferência com planilhas.
[20:14] Naor: Essa IA roda só em nuvem ou localmente? Dados sensíveis. Diretoria prefere local.
[21:43] Naor: Consigo enviar áudio ou só texto?
[23:23] Naor: Como funciona a comunicação pra ler informações locais no ERP? Não ficou claro.
[25:06] Naor: Informações principais no ERP DataSul. Automatização com Gemini e Google Drive.
[28:00] Naor: Achei corrida a reunião. Não fico nítido como utilizar.
[31:43] Naor: Já usamos Gemini com Google Drive pra buscar documentos.
[32:37] Guilherme (Dati): Se sobe dados no Gemini ele usa pra retreinar modelos, se torna público.
[33:43] Naor: Construir APIs pode ser trabalhoso em 60 dias.
[34:16] Guilherme (Dati): Q Business tem conexão nativa com Google Drive. Não precisa API.
[35:45] Naor: Vou conversar com a gerente e volto."""

sr = web_search(full_ctx[:120] + " Amazon Q Business Gemini privacy pricing 2026", max_results=5)
fullctx_msg = (
    f"Conversa completa:\n{full_ctx}\n\n"
    f"Analise a conversa toda e identifique as principais dúvidas técnicas que surgiram.\n"
    f"Para cada dúvida, dê a resposta técnica objetiva (📌) e 3 formas de falar pro cliente (💬).\n"
    f"Identifique problemas que o cliente pode não ter percebido.\n"
    f"No final, liste os próximos passos técnicos."
    f"\n\nDados atualizados da web (2026) — USE esses dados na resposta, priorize informações atualizadas:\n{sr}"
)
resp = client.call_raw(system, fullctx_msg, max_tokens=1500)
results.append(f"\n{'='*80}\nFULLCONTEXT — CONVERSA TODA (automático)\n{'='*80}\n\nRESPOSTA:\n{resp}\n")
print("✅ FULLCONTEXT")

# Salvar
output = "# Teste AUTOMÁTICO Consultor Técnico — Reunião Caltech\n\nModo: automático, sem instrução específica\nWeb search: ativado em todos os snapshots\nPrompt: consultor-tecnico.md\n\n" + "\n".join(results)
path = os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-caltech-tecnico-auto.md")
with open(path, "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-caltech-tecnico-auto.md")
