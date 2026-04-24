#!/usr/bin/env python3
"""Teste v4: classificação + pontos cruciais → resposta com contexto limpo."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

# Transcrições RUIDOSAS (como vem do Groq de verdade)
tests = [
    ("RUIDOSA 1 — experiência AWS (sem pergunta)",
     "Conheço ali a parte de...\nVou ver a conversa.\nCristiano?\nNossa, desculpa, eu estava falando e estava no múdico.\nEu já tenho de quatro a cinco anos de experiência com a AWS,\neu já tenho\nconhecimento ali da parte\nde computação\nde EC2, de install\nde lambda\nconheço ali a parte\nde cloud front\nde\na parte de\nagora fugiu o nome\nrapaz\nda parte de arquivos lá\ndo S3"),

    ("RUIDOSA 2 — migração Google→AWS com pergunta",
     "S3.\nS3.\nJá tem mais uma boa base, né?\nTenho, né?\nEu estava dando uma olhada no terraform\nque vocês mandaram pra gente\npra fazer migração... se a gente fosse\numa migração pra AWS, tá?\nE existem alguns serviços que eles funcionam de forma\nbem diferente entre a Google e a AWS.\nUm dos maiores\nexemplos aqui é o próprio\nCloud Functions\ne os run services que vocês têm ali.\nPara eu conseguir decidir entre um serviço e outro,\ne isso vai acontecer em mais alguns outros casos que eu anotei,\neu preciso de fazer algumas perguntas,\npor isso que eu vou fazer esses questionamentos.\nEssa é sobre os runtimes, as functions.\nQual é o tempo de execução médio entre elas?\nExiste alguma suprência?"),

    ("RUIDOSA 3 — Redis + jobs (mista)",
     "ou Redis Local?\nA gente tem um Redis Local\naqui, só que eu vou\nser bem sincero contigo, eu ainda\nnão descobri\no real motivo. Talvez\nseria para um serviço de cache,\nmas não está ativo\natualmente.\nAh, beleza.\nTá bom.\nAcho que daí a gente vai para um Lambda, né?\nQuanto aos jobs ali,\nvocês precisam de algum job,\nalguma coisa que rode em background?\nTem alguma necessidade de sidecar?"),

    ("RUIDOSA 4 — Gemini e privacidade (da reunião Caltech)",
     "Nós já estamos usando o Gemini com o Google Drive pra buscar documentos.\nO que foi tratado em tal situação, ele busca e traz.\nIsso já estamos utilizando.\nEsses documentos já estão lá no Drive.\nSe você sobe os dados no próprio Gemini ele usa para retreinar modelos, isso se torna público.\nNós já temos um caminhão de informação lá no Drive.\nQuero ver quanto foi faturado em tal data,\nquem é meu melhor cliente, meu melhor fornecedor."),
]

results = []
for title, ctx in tests:
    # Chamada 1: classificação + pontos cruciais
    classify_msg = (
        f"Analise a transcrição abaixo e faça DUAS coisas:\n"
        f"1. CLASSIFICAÇÃO: SIM ou NAO — tem pergunta técnica? (pergunta = pede informação, expressa dúvida como 'não sei se', 'será que', 'tem como'. Afirmação/descrição = NAO)\n"
        f"2. PONTOS CRUCIAIS: Extraia os pontos mais importantes em 2-4 frases limpas e objetivas. Remova ruído (repetições, hesitações). Foque em: dúvidas, tecnologias mencionadas, problemas, decisões.\n\n"
        f"Formato EXATO (sem markdown):\n"
        f"CLASSIFICAÇÃO: SIM ou NAO\n"
        f"PONTOS: texto limpo\n\n"
        f"Transcrição: {ctx[:600]}"
    )
    classify_result = client.call_raw("Classifique e extraia pontos cruciais.", classify_msg, max_tokens=150).strip()
    has_q = "SIM" in classify_result.split("\n")[0].upper()
    clean_ctx = ctx
    for line in classify_result.split("\n"):
        if line.strip().upper().startswith("PONTOS:"):
            clean_ctx = line.split(":", 1)[1].strip()
            break

    # Query + search
    sc = ""
    if has_q:
        qp = f"Responda APENAS com uma query de busca em inglês, máximo 8 palavras. Só a query. Se não houver tema técnico, responda: NONE\n\nConversa: {clean_ctx[:300]}"
        query = client.call_raw("Responda APENAS a query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
        if query and "NONE" not in query.upper():
            query += " AWS 2026"
            sr = web_search(query, max_results=3)
            if len(sr) > 50:
                sc = f"\n\nDados atualizados da web (2026) — USE APENAS se relevantes:\n{sr}"

    # Chamada 2: resposta com contexto limpo
    if not has_q:
        msg = f"Pontos da conversa:\n{clean_ctx}\n\nNão há pergunta técnica. Reconheça o contexto em 1-2 frases e sugira 3 perguntas pro consultor fazer.\nFormato:\n📌 [contexto]\n\n💬 Perguntas pra fazer:\n- \"pergunta 1\"\n- \"pergunta 2\"\n- \"pergunta 3\"{sc}"
    else:
        msg = f"Pontos da conversa:\n{clean_ctx}\n\nResponda a dúvida técnica de forma objetiva.{sc}"

    resp = client.call_raw(system, msg, max_tokens=300)

    r = f"\n{'='*60}\n{title}\n{'='*60}\n\n🔍 CHAMADA 1 (classificação + pontos):\n{classify_result}\n\n📝 CONTEXTO LIMPO ENVIADO PRA CHAMADA 2:\n{clean_ctx}\n\n📌 RESPOSTA FINAL:\n{resp}\n"
    results.append(r)
    print(r)

with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-iterativo-v4.md"), "w") as f:
    f.write("# Teste v4 — Classificação + Pontos Cruciais\n\n" + "\n".join(results))
print("Salvo em tests/resultado-iterativo-v4.md")
