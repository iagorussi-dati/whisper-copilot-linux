#!/usr/bin/env python3
"""Teste consultor técnico com transcrição Caltech — foco em Gemini, Q Business, Drive."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/consultor-tecnico.md")) as f:
    system = f.read()

results = []
suffix = "\n\nResponda a dúvida técnica de forma objetiva. Sem markdown, sem títulos."

snaps = [
    ("1 — Cliente pergunta se Q Business roda local ou só nuvem (dados sensíveis)",
     """[20:14] Naor: Essa IA da Amazon roda somente em nuvem, direto na AWS, ou a gente conseguiria rodar localmente com servidor nosso?
[20:46] Naor: É que eu fiz essa pergunta mais na questão de tratar dados sensíveis. A diretoria tem preferência de rodar localmente."""),

    ("2 — Cliente pergunta se Q Business aceita áudio",
     """[21:43] Naor: Eu consigo enviar mensagens de áudio ou fazer uma conversação por áudio ou é somente texto?"""),

    ("3 — Cliente não entende como Q Business conecta com ERP on-prem (DataSul)",
     """[23:23] Naor: Como funcionaria? O serviço da Amazon estaria conectado aqui, quero saber como faria a comunicação pra ler nossas informações locais, as que estão no ERP, não as públicas da internet. Pra mim não ficou bem claro.
[25:06] Naor: As informações principais estão dentro do ERP, o DataSul."""),

    ("4 — Cliente já usa Gemini com Google Drive e está satisfeito",
     """[31:43] Naor: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. O que foi tratado em tal situação, ele busca e traz. Isso já estamos utilizando.
[32:14] Naor: Esses documentos já estão lá no Drive.
[32:37] Guilherme (Dati): Se você sobe os dados no próprio Gemini ele usa para retreinar modelos, isso se torna público.
[33:25] Naor: Nós já temos um caminhão de informação lá no Drive. Quero ver quanto foi faturado em tal data, quem é meu melhor cliente, meu melhor fornecedor."""),

    ("5 — Cliente acha 60 dias pouco pra construir APIs de conexão",
     """[33:43] Naor: Só que pra isso a gente vai construir APIs de conexão. Talvez nesses 60 dias seja muito trabalhoso pra gente construir as APIs e testar.
[34:16] Guilherme (Dati): Hoje o Amazon Q Business tem conexão nativa com Google Drive, OneDrive. Não precisaria de API pra isso. Só pra ERPs mais nichados."""),

    ("6 — Cliente quer saber quanto custa o Q Business",
     """[15:01] Naor: E a consultoria, como é feito em relação a custo? E o Q Business em si, quanto custa depois dos 60 dias?"""),

    ("7 — Cliente confuso sobre o que Q Business realmente faz",
     """[28:00] Naor: Pra ser sincero, achei um pouco corrida essa reunião. Não fico bem nítido como utilizar isso.
[28:45] Naor: Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso."""),

    ("8 — FULLCONTEXT — conversa toda",
     """[3:31] Naor: Somos uma mineradora da região de Curitiba. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA. Não tem um ponto específico.
[6:47] Carlos: Hoje a gente trabalha com o DataSul. Na parte de conferência, trabalhamos com planilhas.
[20:14] Naor: Essa IA da Amazon roda somente em nuvem ou localmente? Dados sensíveis. Diretoria prefere local.
[21:43] Naor: Eu consigo enviar áudio ou é somente texto?
[23:23] Naor: Como funcionaria a comunicação pra ler nossas informações locais no ERP? Não ficou claro.
[25:06] Naor: Informações principais estão no ERP DataSul. Tem automatização com Gemini e Google Drive.
[28:00] Naor: Achei corrida a reunião. Não fico nítido como utilizar isso.
[31:43] Naor: Já estamos usando Gemini com Google Drive pra buscar documentos.
[32:37] Guilherme (Dati): Se sobe dados no Gemini ele usa pra retreinar modelos, se torna público.
[33:43] Naor: Construir APIs pode ser trabalhoso em 60 dias.
[34:16] Guilherme (Dati): Q Business tem conexão nativa com Google Drive. Não precisa API.
[35:45] Naor: Vou conversar com a gerente e volto."""),
]

for title, ctx in snaps:
    is_full = "FULLCONTEXT" in title
    if is_full:
        user_msg = (
            f"Conversa completa:\n{ctx}\n\n"
            f"Analise a conversa toda e identifique as principais dúvidas técnicas que surgiram.\n"
            f"Para cada dúvida, dê a resposta técnica objetiva (📌) e 3 formas de falar pro cliente (💬).\n"
            f"Identifique problemas que o cliente pode não ter percebido (ex: segurança do Gemini).\n"
            f"No final, liste os próximos passos técnicos."
        )
        tok = 1200
    else:
        user_msg = f"Conversa:\n{ctx}{suffix}"
        tok = 300
    
    resp = client.call_raw(system, user_msg, max_tokens=tok)
    results.append(f"\n{'='*80}\n{title}\n{'='*80}\n\n{resp}\n")
    print(f"✅ {title[:70]}...")

output = "# Teste Consultor Técnico — Reunião Caltech\n\nPrompt: consultor-tecnico.md\n8 testes (7 snapshots + 1 fullcontext)\n\n" + "\n".join(results)
path = os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-caltech-tecnico.md")
with open(path, "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-caltech-tecnico.md")
