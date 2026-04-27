#!/usr/bin/env python3
"""3 fullcontext (Win+H) em momentos diferentes da reunião GoTotem."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

def fullcontext(title, ctx):
    sr = ""
    qp = f"Query em inglês, 8 palavras.\n\nConversa: {ctx[:300]}"
    q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
    if q and "NONE" not in q.upper():
        q += " AWS 2026"
        sr_raw = web_search(q, max_results=3)
        if len(sr_raw) > 50: sr = f"\n\nDados web (2026):\n{sr_raw}"

    msg = (
        f"Conversa completa:\n{ctx}\n\n"
        f"Analise a conversa toda e identifique os principais temas que surgiram.\n"
        f"Para cada tema, gere sugestões separadas por categoria.\n"
        f"Se o cliente fez perguntas, responda cada uma com 📌 + 💬.\n"
        f"Identifique problemas que o cliente pode não ter percebido.\n"
        f"No final, liste próximos passos.\n"
        f"Seja objetivo e curto em cada tema. Não adicione resumo ou conclusão extra."
        f"{sr}"
    )
    resp = client.call_raw(system, msg, max_tokens=5120)
    print(f"✅ {title} ({len(resp)} chars)")
    return f"\n{'='*70}\n{title}\n{'='*70}\n\n📝 CONTEXTO ATÉ AQUI:\n{ctx[:200]}...\n\n📌 RESPOSTA ({len(resp)} chars):\n{resp}\n"

results = []

# FULLCONTEXT 1 — após ~5 minutos (apresentação + necessidade)
results.append(fullcontext("FULLCONTEXT 1 — Após 5min (apresentação + necessidade)",
"""Reginaldo: Eu sou o Reginaldo, trabalho no setor de desenvolvimento, a Lara está comigo também.
A gente hoje além de desenvolver mantém a estrutura na AWS. Surgiu a necessidade de terceirizar essa demanda pra focar no desenvolvimento do produto.
No início tirava um bom tempo, agora tá tirando muito mais porque lançamos um site de vendas de ingresso e a volatilidade é diferente.
A gente não consegue mais ficar com uma estrutura que não seja elástica. Estamos nos virando aumentando e diminuindo instâncias EC2.
A gente está num modo não muito profissional na AWS. Só tem instâncias EC2 pra cada serviço.
Fiz orçamento com uma empresa de Joinville. A AWS me indicou a Nuve Me de Blumenau também.
Estou buscando consultoria em segurança da informação pro site de ingressos.
Preciso de uma empresa que estruture meu ambiente profissionalmente, ajude a migrar pra containers, e depois continue como parceiro com suporte mensal e sustentação."""))

# FULLCONTEXT 2 — após ~12 minutos (tudo acima + suporte 24/7 + empresa + escalabilidade)
results.append(fullcontext("FULLCONTEXT 2 — Após 12min (+ suporte + empresa + escalabilidade)",
"""Reginaldo: Eu sou o Reginaldo, trabalho no setor de desenvolvimento, a Lara está comigo também.
A gente hoje além de desenvolver mantém a estrutura na AWS. Surgiu a necessidade de terceirizar essa demanda pra focar no desenvolvimento do produto.
No início tirava um bom tempo, agora tá tirando muito mais porque lançamos um site de vendas de ingresso e a volatilidade é diferente.
A gente não consegue mais ficar com uma estrutura que não seja elástica. Estamos nos virando aumentando e diminuindo instâncias EC2.
A gente está num modo não muito profissional na AWS. Só tem instâncias EC2 pra cada serviço.
Fiz orçamento com uma empresa de Joinville. A AWS me indicou a Nuve Me de Blumenau também.
Estou buscando consultoria em segurança da informação pro site de ingressos.
Preciso de uma empresa que estruture meu ambiente profissionalmente, ajude a migrar pra containers, e depois continue como parceiro com suporte mensal e sustentação.
Reginaldo: Vocês têm algum cliente que vocês dão suporte 24 horas? 24 por 7?
Rafaela: Sim, temos NOC com monitoramento 24/7 e plantão. Trabalhamos de forma proativa.
Reginaldo: Nós trabalhamos com totens de autoatendimento. Atendemos a Café Cultura. Depois entramos em eventos e desenvolvemos app pra Smart PDV. E lançamos o site de vendas de ingressos.
Reginaldo: Esse site de ingressos causou pânico. Se eu for no site agora tenho 5 pessoas, daqui a pouco 20, mas se lançar evento com alta demanda posso ter mil, duas mil.
Rafaela: Vocês têm algum plano de contingência pra esses picos?
Reginaldo: Não, a gente vai na mão mesmo. Aumenta instância, diminui instância."""))

# FULLCONTEXT 3 — após ~19 minutos (tudo + orçamento + timeline + próximos passos)
results.append(fullcontext("FULLCONTEXT 3 — Final da reunião (~19min, tudo)",
"""Reginaldo: Eu sou o Reginaldo, trabalho no setor de desenvolvimento, a Lara está comigo também.
A gente hoje além de desenvolver mantém a estrutura na AWS. Surgiu a necessidade de terceirizar essa demanda pra focar no desenvolvimento do produto.
No início tirava um bom tempo, agora tá tirando muito mais porque lançamos um site de vendas de ingresso e a volatilidade é diferente.
A gente não consegue mais ficar com uma estrutura que não seja elástica. Estamos nos virando aumentando e diminuindo instâncias EC2.
A gente está num modo não muito profissional na AWS. Só tem instâncias EC2 pra cada serviço.
Fiz orçamento com uma empresa de Joinville. A AWS me indicou a Nuve Me de Blumenau também.
Estou buscando consultoria em segurança da informação pro site de ingressos.
Preciso de uma empresa que estruture meu ambiente profissionalmente, ajude a migrar pra containers, e depois continue como parceiro com suporte mensal e sustentação.
Reginaldo: Vocês têm algum cliente que vocês dão suporte 24 horas? 24 por 7?
Rafaela: Sim, temos NOC com monitoramento 24/7 e plantão. Trabalhamos de forma proativa.
Reginaldo: Nós trabalhamos com totens de autoatendimento. Atendemos a Café Cultura. Depois entramos em eventos e desenvolvemos app pra Smart PDV. E lançamos o site de vendas de ingressos.
Reginaldo: Esse site de ingressos causou pânico. Se eu for no site agora tenho 5 pessoas, daqui a pouco 20, mas se lançar evento com alta demanda posso ter mil, duas mil.
Rafaela: Vocês têm algum plano de contingência pra esses picos?
Reginaldo: Não, a gente vai na mão mesmo. Aumenta instância, diminui instância.
Rafaela: Qual é o billing de vocês hoje na AWS?
Reginaldo: Uns 3 mil reais por mês. Pagamos no cartão.
Rafaela: E orçamento pra esse projeto de reestruturação, vocês têm?
Reginaldo: Não temos definido. Estamos comparando propostas. A empresa de Joinville mandou uma proposta de 45 mil pro projeto.
Rafaela: E timeline, quando vocês precisam disso pronto?
Reginaldo: O mais rápido possível. Temos um evento grande em 2 meses e precisa estar rodando antes.
Rafaela: Entendi. Vou preparar uma proposta com escopo, custo e timeline pra vocês compararem."""))

output = "# Teste Fullcontext Discovery — 3 momentos da reunião\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-discovery-fullcontext.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-discovery-fullcontext.md")
