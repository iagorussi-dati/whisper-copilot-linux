#!/usr/bin/env python3
"""Teste consultor técnico COM web search — foco em Gemini, Q Business, custos."""
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

tests = [
    ("1 — Gemini usa dados pra retreinar? (com web search)",
     "Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. Isso já estamos utilizando.",
     "gemini google AI data privacy policy retreinar modelos 2026"),

    ("2 — Amazon Q Business suporta áudio? (com web search)",
     "Eu consigo enviar mensagens de áudio ou fazer uma conversação por áudio ou é somente texto?",
     "Amazon Q Business audio video support features 2026"),

    ("3 — Quanto custa o Amazon Q Business? (com web search)",
     "E o Q Business em si, quanto custa depois dos 60 dias?",
     "Amazon Q Business pricing cost per user 2026"),

    ("4 — Q Business conecta com Google Drive? (com web search)",
     "Construir APIs pode ser trabalhoso em 60 dias. O Q Business conecta direto com Google Drive?",
     "Amazon Q Business Google Drive connector integration 2026"),

    ("5 — Q Business vs Gemini segurança de dados (com web search)",
     "Nós já usamos Gemini com Google Drive. Qual a diferença de segurança entre Gemini e Q Business?",
     "Amazon Q Business vs Google Gemini data privacy security comparison 2026"),
]

for title, ctx, query in tests:
    print(f"🔍 Pesquisando: {query[:60]}...")
    search_results = web_search(query, max_results=3)
    print(f"   📄 {len(search_results)} chars de resultado")
    
    user_msg = (
        f"Conversa:\n{ctx}\n\n"
        f"Dados atualizados da web (2026) — USE esses dados na resposta, priorize informações atualizadas:\n{search_results}\n\n"
        f"Responda a dúvida técnica de forma objetiva. Sem markdown, sem títulos."
    )
    
    resp = client.call_raw(system, user_msg, max_tokens=400)
    results.append(f"\n{'='*80}\n{title}\n{'='*80}\n\n🔍 Query: {query}\n📄 Search results ({len(search_results)} chars):\n{search_results[:500]}...\n\n📌 RESPOSTA DO COPILOTO:\n{resp}\n")
    print(f"✅ {title[:60]}...")

output = "# Teste Consultor Técnico COM Web Search — Caltech\n\n" + "\n".join(results)
path = os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-caltech-tecnico-websearch.md")
with open(path, "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-caltech-tecnico-websearch.md")
