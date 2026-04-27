#!/usr/bin/env python3
"""Teste Discovery com contexto de dor — reunião GoTotem (muitos chars)."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

previous = []

def snap(title, ctx):
    no_repeat = ""
    if previous:
        no_repeat = "\n\nJá respondido (NÃO repita):\n" + "\n".join(f"- {r[:80]}" for r in previous[-3:])

    t0 = time.time()
    cm = (f"Responda TRÊS linhas, sem markdown:\n"
          f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta direta do cliente?)\n"
          f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT?)\n"
          f"CONTEXTO: Resuma a situação do cliente em 2-3 frases objetivas. Foque na DOR — qual o problema, o que precisa, o que está tentando resolver.\n\n"
          f"Transcrição:\n{ctx}")
    cr = client.call_raw("3 linhas exatas.", cm, max_tokens=300).strip()
    t_c1 = time.time() - t0

    has_q = "SIM" in cr.split("\n")[0].upper()
    has_comp = any("CONCORRENTE: SIM" in l.upper() for l in cr.split("\n"))
    clean = ctx
    for l in cr.split("\n"):
        s = l.strip().replace("*","").replace("#","").strip()
        if s.upper().startswith("CONTEXTO:") or s.upper().startswith("PONTOS:"):
            clean = s.split(":",1)[1].strip()
            break
    fallback = clean == ctx

    q_instr = ""
    if has_q:
        q_instr = "\n\nO cliente fez uma PERGUNTA. Depois das sugestões, adicione: 📌 Sobre [tema]: [resposta] 💬 \"frase\""
    comp_instr = " Mencionou concorrente — diferencie AWS com fatos." if has_comp else ""

    t0 = time.time()
    msg = f"Contexto do cliente:\n{clean}\n\nDê sugestões curtas e objetivas focadas na dor do cliente.{comp_instr}{q_instr}{no_repeat}"
    resp = client.call_raw(system, msg, max_tokens=5120)
    t_c2 = time.time() - t0

    previous.append(resp[:80])
    fb = "⚠️FALLBACK" if fallback else "✅"
    print(f"{fb} {title[:50]}... C1={t_c1:.1f}s C2={t_c2:.1f}s Total={t_c1+t_c2:.1f}s Ctx={len(clean)}chars")
    return (f"\n{'='*70}\n{title}\n{'='*70}\n\n"
            f"📝 TRANSCRIÇÃO ({len(ctx)} chars):\n{ctx[:200]}...\n\n"
            f"⏱️ C1={t_c1:.2f}s | C2={t_c2:.2f}s | Total={t_c1+t_c2:.2f}s\n"
            f"🔍 CHAMADA 1:\n{cr}\n"
            f"{'⚠️ FALLBACK' if fallback else f'✅ Contexto ({len(clean)} chars): {clean}'}\n\n"
            f"📌 RESPOSTA ({len(resp)} chars):\n{resp}\n")

results = []

results.append(snap("SNAP 1 — Totem autoatendimento, produto, ticket médio",
"Esse é o nosso produto de totem de autoatendimento. A gente desenvolve tanto a parte de software que é o aplicativo Android, quanto a parte de hardware. A gente oferece a solução completa. O principal objetivo é agilizar o atendimento e aumentar o ticket médio, fazer com que o cliente compre mais. Porque quando você chega num atendente no caixa dificilmente ele vai te oferecer novos produtos. E o totem está ali o tempo todo oferecendo."))

results.append(snap("SNAP 2 — Sugestões manuais no totem, produto acaba, esquece configurar",
"No nosso sistema hoje, o dono do estabelecimento tem que entrar manualmente e configurar que se comprar esse item ele ofereça uma Coca. É tudo manual. Às vezes o estabelecimento não faz, esquece de fazer, ou o produto acabou. Então o que a gente está pensando com IA: primeiro uma IA especializada no cardápio que consiga fazer sugestões automáticas pro cliente. Considerando o cadastro dele, disponibilidade do produto, combinações óbvias, clima, região."))

results.append(snap("SNAP 3 — Pedido por voz sem tocar na tela",
"O segundo ponto é permitir que o cliente faça o pedido sem tocar na tela, por voz. Que converse com quem está fazendo o pedido. Como se fosse no drive-thru. O totem vai trazer as sugestões na tela e tu vai dar o ok. Pode fazer manualmente e fazer por voz sem ter que tocar na tela."))

results.append(snap("SNAP 4 — Concorrente Google/Gemini já mandou proposta",
"Eu já conversei com uma parceira do Google, o Google fez link com o parceiro deles. Ele já me mandou escopo inicial usando as ferramentas do Google, Gemini e outras ferramentas. Já me mandaram a proposta de preço. E como a AWS também tem, e como vocês agora são nosso parceiro com a AWS, perguntei se vocês tinham essa especialidade."))

results.append(snap("SNAP 5 — Acesso a dados, banco centralizado, histórico de pedidos",
"Eu tenho o banco de dados centralizado onde estão todos os cardápios e todos os pedidos. Então você também tem a informação de histórico de pedidos, o que cada pessoa comprou com que, quais foram os adicionais. Já tem uma base ali de conhecimento que a gente pode utilizar pra que a IA já possa sugerir com base nesse conhecimento."))

results.append(snap("SNAP 6 — Orçamento embrionário, não urgente mas inevitável, faseamento",
"Vocês têm orçamento pré-estabelecido pra esse projeto? Está muito embrionário. A gente começou a conversar com empresas agora, 1 semana, 2 semanas. Não tem noção nenhuma de quanto custa. Não é projeto urgente. É projeto que a gente está pesquisando, mas é inevitável. É uma modernização do nosso produto que a gente enxerga como inevitável. Dá pra dividir em 2 projetos: fase 1 sugestões inteligentes, fase 2 voz."))

output = "# Teste Discovery GoTotem — Contexto de Dor\n\n6 snapshots, prompt discovery-dati.md\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-discovery-gototem-dor.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-discovery-gototem-dor.md")
