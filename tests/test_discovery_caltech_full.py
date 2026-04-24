#!/usr/bin/env python3
"""Bateria de testes: snapshots Win+D + fullcontext Win+H na reunião Caltech."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

results = []

# ── SNAPSHOTS Win+D ──
snapshots = [
    ("SNAPSHOT 1 — Cliente é mineradora, pesquisando IA sem foco, usa DataSul e planilhas",
     """[3:31] Naor: Somos uma mineradora da região de Curitiba, parte de suco alcooleiro, fertilizantes, caldolumita. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA.
[4:59] Naor: É novo pra gente. Estamos pesquisando pra ver onde pode nos auxiliar. Não tem um ponto específico.
[6:47] Carlos: Hoje a gente trabalha com o DataSul. Na parte de conferência, trabalhamos com planilhas."""),

    ("SNAPSHOT 2 — Contabilidade usa planilhas pra conferência, TI é pequeno",
     """[5:50] Naor: O Paulo é do time de TI, desenvolvedor. O Abner é do setor de melhoria contínua. O Carlos é da contabilidade.
[6:47] Carlos: Hoje a gente trabalha com o nosso sistema interno, o DataSul. Na parte de conferência, trabalhamos com planilhas. Fazemos lançamento da nota e conferência à base de planilhas."""),

    ("SNAPSHOT 3 — Cliente pergunta se IA roda local, diretoria prefere on-prem por dados sensíveis",
     """[20:14] Naor: Essa IA da Amazon roda somente em nuvem, direto na AWS, ou a gente conseguiria rodar localmente com servidor nosso?
[20:46] Naor: É que eu fiz essa pergunta mais na questão de tratar dados sensíveis. A diretoria tem preferência de rodar localmente."""),

    ("SNAPSHOT 4 — Cliente quer entender como conectar ERP on-prem com AWS",
     """[23:23] Naor: Como funcionaria? O serviço da Amazon estaria conectado aqui, quero saber como faria a comunicação pra ler nossas informações locais, as que estão no ERP, não as públicas da internet.
[25:06] Naor: As informações principais estão dentro do ERP, o DataSul."""),

    ("SNAPSHOT 5 — Cliente já usa Gemini com Google Drive e está satisfeito",
     """[31:43] Naor: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. O que foi tratado em tal situação, ele busca e traz. Isso já estamos utilizando.
[32:14] Naor: Esses documentos já estão lá no Drive.
[33:25] Naor: Nós já temos um caminhão de informação lá no Drive. Quero ver quanto foi faturado em tal data, quem é meu melhor cliente, meu melhor fornecedor."""),

    ("SNAPSHOT 6 — Cliente acha 60 dias pouco pra construir APIs e precisa falar com gerente",
     """[33:43] Naor: Só que pra isso a gente vai construir APIs de conexão. Talvez nesses 60 dias seja muito trabalhoso pra gente construir as APIs e testar.
[27:19] Naor: Vou conversar com a nossa gerente, que não pôde participar hoje. Não posso passar uma definição agora sem autorização dela.
[35:45] Naor: Entendi. Vou conversar com a gerente e tendo parecer dela a gente volta a conversar."""),

    ("SNAPSHOT 7 — Cliente pede case real, quer ver exemplo concreto",
     """[28:45] Naor: Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso. Pra o nosso querer aqui, ver alguma coisa que dá pra fazer.
[30:05] Naor: Vocês já implementaram isso em outro lugar?"""),
]

for title, ctx in snapshots:
    user_msg = f"Conversa:\n{ctx}\n\nContribua com sugestões úteis pro comercial. Não narre quem falou. Responda direto. Sem markdown, sem títulos."
    resp = client.call_raw(system, user_msg, max_tokens=250)
    results.append(f"\n{'='*80}\n{title}\n{'='*80}\n\n{resp}\n")
    print(f"✅ {title[:60]}...")

# ── FULLCONTEXT Win+H (conversa toda) ──
full_ctx = """[3:31] Naor: Somos uma mineradora da região de Curitiba, parte de suco alcooleiro, fertilizantes, caldolumita. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA.
[4:29] Naor: Temos um aplicativo de frete, o site, mas de forma geral é esse o tipo de serviço que consumimos na AWS.
[4:59] Naor: É novo pra gente. Estamos pesquisando pra ver onde pode nos auxiliar. Não tem um ponto específico.
[5:50] Naor: O Paulo é do time de TI, desenvolvedor. O Abner é do setor de melhoria contínua. O Carlos é da contabilidade.
[6:47] Carlos: Hoje a gente trabalha com o DataSul. Na parte de conferência, trabalhamos com planilhas. Fazemos lançamento da nota e conferência à base de planilhas.
[7:28] Danilo (Dati): Hoje a AWS, vocês fazem pagamento por cartão ou por boleto?
[20:14] Naor: Essa IA da Amazon roda somente em nuvem ou a gente conseguiria rodar localmente? É pela questão de dados sensíveis. A diretoria tem preferência de rodar localmente.
[23:23] Naor: Como funcionaria a comunicação pra ler nossas informações locais, as que estão no ERP, não as públicas da internet?
[25:06] Naor: As informações principais estão dentro do ERP, o DataSul. Tem uma automatização sendo desenvolvida pra lançamento de notas fiscais usando o Gemini buscando do Google Drive.
[27:19] Naor: Vou conversar com a nossa gerente, que não pôde participar hoje. Não posso passar uma definição agora sem autorização dela.
[28:45] Naor: Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso.
[31:43] Naor: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. Isso já estamos utilizando.
[33:43] Naor: Pra construir APIs de conexão, talvez nesses 60 dias seja muito trabalhoso.
[35:45] Naor: Vou conversar com a gerente e tendo parecer dela a gente volta a conversar."""

fullctx_prompt = (
    f"Conversa completa:\n{full_ctx}\n\n"
    f"Analise a conversa toda e identifique os principais temas que surgiram.\n"
    f"Para cada tema, gere sugestões no formato abaixo.\n\n"
    f"FORMATO OBRIGATÓRIO:\n"
    f"**[EMOJI] Título do tema específico da conversa**\n"
    f"*Contexto: resuma em 1-2 frases o que foi falado sobre esse tema, referenciando o que o cliente disse.*\n\n"
    f"💡/⚠️/🔴/✅ \"Frase pronta que o comercial pode falar\"\n"
    f"(3-4 sugestões por tema)\n\n"
    f"No último bloco, sempre coloque:\n"
    f"**✅ Próximos passos**\n"
    f"✅ \"Resumo do que ficou combinado e o que cada um vai fazer\"\n\n"
    f"REGRAS:\n"
    f"- Os temas vêm da conversa, não são categorias fixas\n"
    f"- O contexto em itálico deve ser específico, referenciando o que o cliente falou\n"
    f"- As sugestões devem ser frases prontas que o comercial pode falar diretamente\n"
    f"- Não narre a conversa, não diga 'o cliente falou X' nas sugestões\n"
    f"- Tom natural e coloquial"
)

resp = client.call_raw(system, fullctx_prompt, max_tokens=600)
results.append(f"\n{'='*80}\nFULLCONTEXT Win+H — CONVERSA TODA\n{'='*80}\n\n{resp}\n")
print("✅ FULLCONTEXT Win+H")

# Salvar resultado
output = "# Teste Discovery Dati — Reunião Caltech\n\nPrompt: discovery-dati.md (41 situações)\nReunião: Caltech mineradora, Amazon Q Business\n\n" + "\n".join(results)
with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-caltech.md"), "w") as f:
    f.write(output)
print(f"\n📄 Resultado salvo em tests/resultado-caltech.md")
