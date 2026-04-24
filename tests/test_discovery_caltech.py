#!/usr/bin/env python3
"""Simulate Win+D snapshots on Caltech transcription using discovery-dati.md prompt."""
import sys, os
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))

client = BedrockClient()

with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/discovery-dati.md")) as f:
    system = f.read()

# 4 snapshots simulando Win+D em momentos-chave
snapshots = [
    {
        "momento": "Cliente explica que é mineradora, tem pouco na AWS, está pesquisando IA sem foco específico",
        "contexto": """[3:31] Naor Barbosa: Nós fomos localizados por vocês na semana passada. Como estamos nesse movimento de IA, resolvi que seria interessante conversar. Somos uma mineradora da região de Curitiba, parte de suco alcooleiro, fertilizantes, caldolumita. Temos alguns serviços rodando na Amazon e estamos iniciando na parte de IA.
[4:29] Naor Barbosa: Temos um aplicativo de frete, o site, mas de forma geral é esse o tipo de serviço que consumimos na AWS.
[4:59] Naor Barbosa: Na verdade estamos ingressando com IA. É novo pra gente. Estamos pesquisando pra ver onde pode nos auxiliar. Não tem um ponto específico que estamos procurando.
[5:50] Naor Barbosa: O Paulo é do time de TI, desenvolvedor. O Abner é do setor de melhoria contínua. O Carlos é da contabilidade, está pesquisando bastante também.
[6:47] Carlos Ribas: Hoje a gente trabalha com o nosso sistema interno, o DataSul. Na parte de conferência, trabalhamos com planilhas. Fazemos lançamento da nota e conferência à base de planilhas."""
    },
    {
        "momento": "Cliente pergunta se a IA roda local — preocupação com dados sensíveis e preferência da diretoria",
        "contexto": """[20:14] Naor Barbosa: Essa IA da Amazon roda somente em nuvem, direto na AWS, ou a gente conseguiria rodar localmente com servidor nosso?
[20:46] Naor Barbosa: É que eu fiz essa pergunta mais na questão de tratar dados sensíveis. A diretoria tem preferência de rodar localmente."""
    },
    {
        "momento": "Cliente quer saber como conectar com ERP on-prem (DataSul) e menciona que já usa Gemini com Google Drive",
        "contexto": """[23:23] Naor Barbosa: Como funcionaria? O serviço da Amazon estaria conectado aqui, quero saber como faria a comunicação pra ler nossas informações locais, as que estão no ERP, não as públicas da internet.
[25:06] Naor Barbosa: As informações principais estão dentro do ERP, o DataSul. Tem uma automatização sendo desenvolvida pra lançamento de notas fiscais usando o Gemini buscando do Google Drive.
[31:43] Naor Barbosa: Nós já estamos usando o Gemini com o Google Drive pra buscar documentos. O que foi tratado em tal situação, ele busca e traz."""
    },
    {
        "momento": "Cliente pede case real, diz que precisa falar com gerente, e acha que 60 dias pode ser pouco pra construir APIs",
        "contexto": """[28:45] Naor Barbosa: Seria interessante ter um exemplo real. A gente fez isso, é capaz de fazer isso. Pra o nosso querer aqui, ver alguma coisa que dá pra fazer.
[30:05] Naor Barbosa: Vocês já implementaram isso em outro lugar?
[33:43] Naor Barbosa: Quem é meu melhor cliente, meu melhor fornecedor — já vai buscar. Só que pra isso a gente vai construir APIs de conexão. Talvez nesses 60 dias seja muito trabalhoso pra gente construir as APIs e testar.
[35:45] Naor Barbosa: Entendi. Vou conversar com a gerente e tendo parecer dela a gente volta a conversar marcando próximo passo."""
    }
]

for i, snap in enumerate(snapshots, 1):
    print(f"\n{'='*80}")
    print(f"SNAPSHOT {i} — {snap['momento']}")
    print(f"{'='*80}\n")
    
    user_msg = f"Conversa:\n{snap['contexto']}\n\nContribua com sugestões úteis pro comercial. Não narre quem falou. Responda direto."
    
    result = client.call_raw(system, user_msg, max_tokens=250)
    print(result)
    print()
