#!/usr/bin/env python3
"""Teste iterativo — mesmos trechos da reunião real, até ficar decente."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

print(f"System prompt: {len(system)} chars")

def test_snapshot(title, ctx):
    # 1. Gerar query
    qp = f"Responda APENAS com uma query de busca em inglês, máximo 8 palavras. Sem explicação, sem markdown, sem análise. Só a query.\nSe não houver tema técnico, responda: NONE\n\nConversa: {ctx[:300]}"
    query = client.call_raw("Responda APENAS a query de busca, nada mais.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
    
    search_context = ""
    if query and "NONE" not in query.upper():
        query += " AWS 2026"
        print(f"  🔍 Query: {query}")
        sr = web_search(query, max_results=3)
        if len(sr) > 50:
            search_context = f"\n\nDados atualizados da web (2026) — USE esses dados na resposta APENAS se forem relevantes:\n{sr}"
            print(f"  📄 Search: {len(sr)} chars")
    
    user_msg = (
        f"Conversa:\n{ctx}\n\n"
        f"Contribua com algo útil sobre o que foi dito. Não narre quem falou o quê. Apenas responda."
        f"{search_context}"
    )
    
    resp = client.call_raw(system, user_msg, max_tokens=350)
    print(f"\n{'='*60}\n{title}\n{'='*60}\n\n{resp}\n")
    return resp

# Mesmos trechos da reunião real
test_snapshot("SNAP 1 — Cliente fala experiência AWS (EC2, Lambda, CloudFront, S3)",
"""Eu já tenho de quatro a cinco anos de experiência com a AWS, eu já tenho conhecimento ali da parte de computação de EC2, de Elastic Beanstalk, de Lambda, conheço ali a parte de CloudFront, de S3.""")

test_snapshot("SNAP 2 — Migração Google→AWS, Cloud Functions vs Lambda, tempo de execução",
"""Eu estava dando uma olhada no Terraform que vocês mandaram pra gente pra fazer migração pra AWS. E existem alguns serviços que funcionam de forma bem diferente entre a Google e a AWS. Um dos maiores exemplos é o próprio Cloud Functions e os Cloud Run que vocês têm ali. Pra eu conseguir decidir entre um serviço e outro, preciso fazer algumas perguntas. Qual é o tempo de execução médio das functions? Existe alguma que demora mais de 15 minutos?""")

test_snapshot("SNAP 3 — Redis local sem uso claro",
"""A gente tem um Redis local aqui, só que eu vou ser bem sincero contigo, eu ainda não descobri o real motivo. Talvez seria para um serviço de cache, mas não está ativo atualmente.""")

test_snapshot("SNAP 4 — Sidecar e jobs",
"""Quanto aos jobs ali, vocês precisam de algum job que rode em background? Tem alguma necessidade de sidecar? Tipo algum serviço que precise rodar junto com a aplicação principal?""")
