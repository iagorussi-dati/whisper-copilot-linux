#!/usr/bin/env python3
"""Simula os mesmos 3 snapshots do log real — agora com intervalo correto."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

previous = []

def snapshot(title, interval_text):
    """Simula snapshot com só o intervalo."""
    no_repeat = ""
    if previous:
        no_repeat = "\n\nJá respondido (NÃO repita):\n" + "\n".join(f"- {r[:80]}" for r in previous[-3:])

    # Chamada 1
    cm = (
        f"Analise a transcrição e responda TRÊS linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta direta do cliente?)\n"
        f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT?)\n"
        f"PONTOS: 2-4 frases com os pontos cruciais limpos\n\n"
        f"Transcrição: {interval_text[:600]}"
    )
    cr = client.call_raw("Responda EXATAMENTE 3 linhas.", cm, max_tokens=120).strip()
    has_q = "SIM" in cr.split("\n")[0].upper()
    has_comp = any("CONCORRENTE: SIM" in l.upper() for l in cr.split("\n"))
    clean = interval_text
    for l in cr.split("\n"):
        if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break

    q_instr = ""
    if has_q:
        q_instr = ("\n\nO cliente fez uma PERGUNTA direta. Depois das sugestões, adicione:\n"
                   "📌 Sobre [tema da pergunta]:\n[resposta objetiva 2-3 frases]\n"
                   "💬 \"frase pronta de como falar pro cliente\"")

    msg = (f"Pontos da conversa:\n{clean}\n\n"
           f"Contribua com sugestões úteis. Seja objetivo e curto. Não narre quem falou.{q_instr}{no_repeat}")

    resp = client.call_raw(system, msg, max_tokens=5120)
    previous.append(resp[:100])

    print(f"\n{'='*70}\n{title}\n{'='*70}")
    print(f"\n📝 INTERVALO (só o que foi falado desde o último snapshot):\n{interval_text}")
    print(f"\n🔍 CHAMADA 1:\n{cr}")
    print(f"Q={has_q} Comp={has_comp}")
    print(f"Pontos limpos: {clean}")
    print(f"\n📌 RESPOSTA:\n{resp}\n")
    return f"\n{'='*70}\n{title}\n{'='*70}\n\n📝 INTERVALO:\n{interval_text}\n\n🔍 CHAMADA 1:\n{cr}\nQ={has_q} Comp={has_comp}\nPontos: {clean}\n\n📌 RESPOSTA:\n{resp}\n"

results = []

# SNAP 1: tudo desde o início até o primeiro Win+D
# Inclui: apresentação + stack + necessidade de terceirizar + site de ingressos + orçamento com outra empresa
results.append(snapshot("SNAP 1 — Apresentação + stack + necessidade + concorrência",
"""É que eu posso conhecer um pouco mais sobre vocês, então eu sou o Reginaldo, trabalho aqui no setor de desenvolvimento, a Lara está aqui comigo, também trabalha no setor de desenvolvimento.
A gente hoje, além de desenvolver, a gente mantém também a estrutura na AWS. Aí que surgiu agora a necessidade de a gente terceirizar essa demanda da AWS pra gente poder focar mais na questão de desenvolvimento do produto.
Isso acaba no início eu tirava um bom tempo da gente, agora tá tirando muito mais tempo da gente porque a gente recentemente lançou um site de vendas de ingresso e a volatilidade é diferente.
Então a gente não consegue mais ficar com uma estrutura que não seja elástica, que não seja dinâmica, a gente está se virando por enquanto diminuindo, aumentando as instâncias de acordo com quando surgem eventos grandes.
Mas a gente hoje está num modo não muito profissional lá dentro da AWS. A gente tem só as instâncias do EC2 para cada serviço que a gente precisa.
Eu fiz um orçamento com uma empresa aqui de Joinville. E coincidentemente a AWS entrou em contato comigo e me indicou uma empresa de Blumenau também, a Nuve Me. Eles me mandaram um orçamento também.
Em paralelo a isso, eu estou buscando também uma consultoria em segurança da informação mais focada também para esse site de venda de ingressos.
O que eu preciso é o seguinte, eu preciso de uma empresa que faça para mim uma estruturação do meu ambiente, de uma maneira profissional, que nos ajude a mudar também para uma forma de trabalhar com containers. Que a gente hoje não trabalha com containers. E depois da sequência que continue sendo meu parceiro com um suporte mensal e sustentação."""))

# SNAP 2: intervalo entre snap 1 e snap 2
# Inclui: pergunta sobre suporte 24/7 + NOC + apresentação da empresa do cliente
results.append(snapshot("SNAP 2 — Suporte 24/7 + apresentação empresa cliente (totens, eventos, ingressos)",
"""Uma pergunta antes, só para mim não esquecer. Vocês têm algum cliente que vocês vão suporte 24 horas? 24 por 7?
Sim. A gente tem um NOC aqui. Então, a gente tem monitoramento 24 por 7 e depois tem o atendimento também dentro do plantão.
Hoje, todos os nossos ambientes sustentados, a gente trabalha muito de forma proativa. Então a gente consegue trabalhar antes de dar um problema. Mas quando dá a gente consegue trabalhar dessa forma atuando com o plantão.
Legal. Deixa eu só continuar que eu esqueci de falar um pouco da empresa.
Vocês atendem a Café Cultura? Ah, sim, aquele lá é nosso.
Nós trabalhamos inicialmente com um projeto de totens de autoatendimento. Depois nós começamos a atender eventos e desenvolvemos também um aplicativo que roda nessas Smart e PDV, que o garçom consegue vender os produtos pela própria maquininha.
E quando a gente entrou no setor de eventos, para complementar esse serviço a gente também lançou um site de vendas de ingressos."""))

# SNAP 3: intervalo entre snap 2 e snap 3
# Inclui: pânico com escalabilidade do site de ingressos
results.append(snapshot("SNAP 3 — Pânico com escalabilidade do site de ingressos",
"""Então, aí que esse site de vendas de ingresso que causou esse pânico, e gerou, não sei se acelerar com essa questão de reestruturação desse nosso ambiente lá na nuvem.
Justamente pelo quê? Porque se eu for no site agora, eu tenho cinco pessoas, daqui a pouco eu tenho 20, mas se lançar um evento com alta demanda, amanhã eu posso ter mil, duas mil, sabe?"""))

output = "# Teste Discovery — Mesmos snapshots do log real (com intervalo correto)\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-discovery-intervalo.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-discovery-intervalo.md")
