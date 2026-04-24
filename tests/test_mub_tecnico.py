#!/usr/bin/env python3
"""10 snapshots na reunião MUB (Conti) — fluxo completo do consultor técnico."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from backend.search import web_search
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

def snapshot(title, ctx):
    # Chamada 1: classificação + concorrente + pontos
    cm = (
        f"Analise a transcrição e responda TRÊS linhas, sem explicação, sem markdown:\n"
        f"CLASSIFICAÇÃO: SIM ou NAO (tem pergunta técnica ou dúvida que precisa resposta?)\n"
        f"CONCORRENTE: SIM ou NAO (menciona Google, Gemini, Azure, Heroku, Oracle, ChatGPT ou qualquer serviço que NÃO seja AWS?)\n"
        f"PONTOS: 2-4 frases com os pontos cruciais limpos\n\n"
        f"Transcrição: {ctx[:600]}"
    )
    cr = client.call_raw("Responda EXATAMENTE 3 linhas no formato pedido. Sem markdown.", cm, max_tokens=120).strip()
    has_q = "SIM" in cr.split("\n")[0].upper()
    has_comp = any("CONCORRENTE: SIM" in l.upper() or "CONCORRENTE:SIM" in l.upper() for l in cr.split("\n"))
    clean = ctx
    for l in cr.split("\n"):
        if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break

    # Web search se pergunta ou concorrente
    sc = ""
    if has_q or has_comp:
        qp = f"Responda APENAS query de busca em inglês, 8 palavras. Só a query.\n\nConversa: {clean[:300]}"
        q = client.call_raw("Query.", qp, max_tokens=20).strip().strip('"').strip("'").strip("`").split("\n")[0]
        if q and "NONE" not in q.upper():
            q += (" vs AWS privacy security 2026" if has_comp else " AWS 2026")
            sr = web_search(q, max_results=3)
            if len(sr) > 50: sc = f"\n\nDados da web (2026) — USE na resposta:\n{sr}"

    # Chamada 2: resposta
    if not has_q:
        msg = f"Pontos:\n{clean}\n\nSem pergunta técnica. Contexto em 1-2 frases + 3 perguntas pro consultor.\n📌 [contexto]\n💬 Perguntas:\n- \"1\"\n- \"2\"\n- \"3\"{sc}"
    else:
        extra = " IMPORTANTE: mencionou concorrente — diferencie AWS com FATOS da web." if has_comp else ""
        msg = f"Pontos:\n{clean}\n\nResponda objetivamente.{extra}{sc}"
    resp = client.call_raw(system, msg, max_tokens=300)
    return f"\n{'='*70}\n{title}\n{'='*70}\n\n📝 TRANSCRIÇÃO:\n{ctx}\n\n🔍 CHAMADA 1:\n{cr}\nQ={has_q} Comp={has_comp}\nPontos limpos: {clean}\n\n📌 RESPOSTA:\n{resp}\n"

results = []
results.append(snapshot("SNAP 1 — Kevin descreve stack: Beanstalk, Aurora, OpenSearch, DynamoDB",
"A gente tem o Elastic Beanstalk fazendo a orquestração do back-end. Nós usamos o Aurora como serviço do banco. A gente tem um outro banco rodando no OpenSearch, que é pra pesquisa. E o DynamoDB em alguns casos, mas muito poucos."))

results.append(snapshot("SNAP 2 — Clientes exigem RTO/RPO melhor, não tem formalizado",
"Os clientes estavam exigindo uma RTO RPO maior, melhor. A gente não tem exatamente formalizado isso, o meu chefe pediu pra gente ter documentado o RTO, RPO, pra poder apresentar, porque os clientes acabam pedindo sempre."))

results.append(snapshot("SNAP 3 — Duplicar infra em outra região faz sentido?",
"A gente pode pensar em um ambiente duplicado em outra região, geraria um RTO RPO muito melhor. Só que isso também dobraria o custo. Duplicar a infra seria um passo mais ousado para a situação atual. Não faria sentido."))

results.append(snapshot("SNAP 4 — Como funciona failover multi-região na prática?",
"Só de curioso mesmo, como é que funciona na prática? Porque vai ser dois load balancers em locais separados, mas quem que faz esse meio do caminho entre os dois? Vocês usam Route 53? Lá tem uma opção de usar ele como failover."))

results.append(snapshot("SNAP 5 — Cliente quer infra exclusiva, banco separado, acesso restrito",
"Teve um cliente que levantou a mão dizendo que queria uma infraestrutura pra ele. Eles queriam uma infra exclusiva deles, o banco deles, o back-end deles. Tudo duplicado para atender somente um cliente. E eles queriam que fosse acessível somente da rede deles. Não sei nem se isso é viável."))

results.append(snapshot("SNAP 6 — Conta separada por cliente, estrutura de contas",
"Vocês teriam que ter uma infra pronta. Talvez eu usaria até uma conta separada só pra esse cliente. Vocês têm estrutura de contas hoje? Não, hoje é uma só. Vocês conseguem ter uma estrutura de contas, uma conta de produção, uma de homologação, uma de desenvolvimento. O login entre elas pode ser único."))

results.append(snapshot("SNAP 7 — Deploy cross-account com CodePipeline",
"A gente usa o CodePipeline para fazer deploy. A gente conseguiria do mesmo modo plugar ali a branch master e plugar as duas infraestruturas e fazer funcionar? Contas diferentes é uma excelente pergunta. Tenho certeza, eu vou checar isso."))

results.append(snapshot("SNAP 8 — Auto-scaling lento no Beanstalk, 30 min pra subir máquina",
"A gente tem uma dor hoje que é a demora do auto scaling. A gente tem o auto scaling com Elastic Beanstalk que é cerca de meia hora até uma máquina subir e começar a rodar. O que acaba às vezes caindo fora do ar do sistema. A sugestão que vocês deram era migrar para o Fargate."))

results.append(snapshot("SNAP 9 — Monolito no Fargate vale a pena?",
"A gente tem um grande monolito. Normalmente quando tem um grande monolito não tem dentro da EC2, não tem muitos microserviços, traz tanta vantagem, o custo-benefício acaba não mudando tanto. Mas mesmo assim o auto-scaling não seria mais rápido por ser uma imagem já pronta, já buildada?"))

results.append(snapshot("SNAP 10 — Acesso SSH no Fargate pra troubleshooting urgente",
"Às vezes acontece algum erro e eu preciso urgentemente resolver, o build demora 30 minutos, eu vou lá, conecto na máquina e ajusto manual o código. Ao momento que a gente virar pra Fargate, é possível fazer uma conexão com as máquinas que estão rodando ou não tem esse acesso?"))

output = "# Teste Consultor Técnico — Reunião MUB (Conti)\n\nPrompt: assistente-objetivo.md\n10 snapshots com fluxo completo (classificação + pontos + web search + resposta)\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-mub-tecnico.md"), "w") as f:
    f.write(output)
print(f"\n📄 Salvo em tests/resultado-mub-tecnico.md ({len(results)} snapshots)")
