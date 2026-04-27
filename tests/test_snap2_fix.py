#!/usr/bin/env python3
"""Teste com o mesmo snapshot 2 do log real — contexto inteiro."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

# Exatamente o contexto do snapshot 2 do log (21 entradas, 4375 chars)
context = """[Gustavo Conti] e mergulhar bem nessa frente. E partindo dessa conversa, a gente já começar a desenhar cenários de resolução dessa frente. Daí, claro, é uma questão comercial, uma questão técnica também, que a gente vai direcionar junto com o Juliano. Tudo bem dessa forma?
[Juliano] Tá, tudo certo.
[Kyulin] Maravilha. Vou passar a palavra do Gustavo. Vamos aprofundar essas frentes, tá?
[Gustavo Conti] Você tem algum desenho de arquitetura, alguma coisa que mostre o que vocês estão usando ali para eu entender um pouco melhor até esse cenário ali de processo?
[Juliano] Sim, peraí. Na verdade não possuo, porque a gente começou a subir a infraestrutura aos poucos, né? E como é muito pouca coisa, realmente muito pouca coisa.
[Gustavo Conti] Vocês conseguem me mostrar, talvez? No painel mesmo?
[Juliano] Sim, só um segundo.
[Gustavo Conti] Hoje vocês não estão usando nenhum tipo de WAF, nem nada assim?
[Juliano] É, então no momento não. Essa foi realmente a dúvida se isso ia solucionar, né? Aqui atualmente, a gente tem duas instâncias, EC2, né? Essa instância do front-end é a que geralmente é atacada, tá? A gente fez algumas coisas que acabou resolvendo isso, mas como o projeto está bem no início. E a gente não viu ainda essa parte de scaling, né? Então, a ideia é usar um ECS para subir mais pods ali, ou talvez até um Kubernetes, né? Mas, por enquanto, estava realmente subindo na mão a instância.
[Juliano] que faz chamada na API da Amazon para subir isso aí, enfim. E daí o que acontecia basicamente era isso, né? A gente via que o CPU aqui, ele ia subindo. Aqui estava em 11%, a gente fez algumas ações ali que foi, por exemplo, fechar a porta do LB, a porta de LB de outbound, de saída, apontar que somente o security group do próprio instante do front-end seria o único ponto de saída. E daí com isso reduziu, parou de ocorrer o problema.
[Gustavo Conti] O front de vocês está escrito em qual linguagem?
[Juliano] Em Python. O back-end está em Python e a parte do front-end é em Next.js.
[Gustavo Conti] Qual a versão do Next que vocês estão usando?
[Juliano] o Next, se não me engano, é esse aqui, 16.2, então, assim, nosso medo até era de alguma coisa do tipo, ah, estou dando lá, NPM instalou em algum pacote, esse pacote que está instalando algo e, né, executando algum alérgico ali e tal, mas parece que não, assim, né, realmente no momento que a gente fechou a porta de saída que parou de ocorrer. Pelo que eu entendi, o pessoal explora essa porta 3000, né, que é do Node ali, enfim, e agora, o ponto é como que eles conseguem fazer uma execução de código remoto, assim, né, que era colocar o SH aqui dentro e ficar executando, executando, até tinham momentos que eu ia acessar a máquina, davam um, dava o meu atalho ali, enfim, né, pra acessar a máquina, via SSH, que eu só tenho liberado o meu IP aqui, né, e eu não tinha mais acesso, então, provavelmente, o que o pessoal fazia é ir ali, removia aquela chave de SSH, né, a chave pública ali, linha de acesso, e daí eu já não tinha mais a
[Juliano] a sua instância, então eu tinha que matar aquela instância e subir outra e tudo mais.
[Gustavo Conti] É,"""

print(f"Contexto: {len(context)} chars")
print(f"System prompt: {len(system)} chars\n")

# CHAMADA 1: classificação + pontos
t0 = time.time()
cm = (
    f"Analise a transcrição INTEIRA e responda QUATRO linhas, sem explicação, sem markdown:\n"
    f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta técnica ou dúvida que precisa resposta?)\n"
    f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT?)\n"
    f"PONTOS: Liste TODOS os assuntos técnicos discutidos — problemas, dúvidas, decisões, tecnologias. Foque no que é mais recente e relevante.\n"
    f"RESPOSTA: CURTA se tem 1 assunto, MÉDIA se tem 2, LONGA se tem 3+\n\n"
    f"Transcrição:\n{context}"
)
cr = client.call_raw("Responda EXATAMENTE 4 linhas.", cm, max_tokens=300).strip()
t1 = time.time() - t0
print(f"⏱️ CHAMADA 1: {t1:.2f}s ({len(context)} chars de contexto)")
print(f"🔍 Resultado:\n{cr}\n")

# Extrair pontos
clean = context
for l in cr.split("\n"):
    if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break
has_q = "SIM" in cr.split("\n")[0].upper()

# CHAMADA 2: web search + resposta
t0 = time.time()
qp = f"Query de busca em inglês, 8 palavras. Só a query.\n\nConversa: {clean[:300]}"
q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
q += " AWS 2026"
print(f"🔍 Search query: {q}")
sr = web_search(q, max_results=3)
sc = f"\n\nDados web (2026):\n{sr}" if len(sr) > 50 else ""
t_search = time.time() - t0

t0 = time.time()
resp_size = "MÉDIA"
for l in cr.split("\n"):
    if l.strip().upper().startswith("RESPOSTA:"): resp_size = l.split(":",1)[1].strip().upper(); break

msg = f"Pontos da conversa:\n{clean}\n\nResponda a dúvida técnica de forma objetiva. Tamanho: {resp_size}. Se LONGA, seja mais conciso em cada tema. NÃO adicione resumo no final.{sc}"
resp = client.call_raw(system, msg, max_tokens=5120)
t2 = time.time() - t0

print(f"\n⏱️ SEARCH: {t_search:.2f}s")
print(f"⏱️ CHAMADA 2: {t2:.2f}s")
print(f"⏱️ TOTAL: {t1 + t_search + t2:.2f}s\n")
print(f"📌 RESPOSTA ({len(resp)} chars):\n{resp}")

# Salvar
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-snap2-fix.md"), "w") as f:
    f.write(f"# Teste Snapshot 2 — Contexto inteiro ({len(context)} chars)\n\n")
    f.write(f"Tempos: Chamada1={t1:.2f}s Search={t_search:.2f}s Chamada2={t2:.2f}s Total={t1+t_search+t2:.2f}s\n\n")
    f.write(f"## Chamada 1\n{cr}\n\n## Pontos limpos\n{clean}\n\n## Resposta\n{resp}\n")
print(f"\n📄 Salvo em tests/resultado-snap2-fix.md")
