#!/usr/bin/env python3
"""Bateria de 20 testes de classificação SIM/NAO — precisa 90%+ de acerto."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()

# (texto, esperado)
cases = [
    # COM PERGUNTA (esperado: SIM)
    ("Qual é o tempo de execução médio das functions? Existe alguma que demora mais de 15 minutos?", "SIM"),
    ("Quanto custa o Amazon Q Business depois dos 60 dias?", "SIM"),
    ("O Amazon Q Business suporta áudio ou só texto?", "SIM"),
    ("Como funciona a comunicação pra ler informações locais no ERP?", "SIM"),
    ("Vocês já implementaram isso em outro lugar?", "SIM"),
    ("Essa IA roda somente em nuvem ou a gente consegue rodar localmente?", "SIM"),
    ("Eu consigo fazer deploy cross-account com CodePipeline?", "SIM"),
    ("Qual a diferença de custo entre EC2 e Fargate pra esse cenário?", "SIM"),
    ("O Cognito suporta MFA obrigatório com usuário e senha?", "SIM"),
    ("Tem como a gente ter uma infra exclusiva pra um cliente só?", "SIM"),
    # SEM PERGUNTA (esperado: NAO)
    ("Eu já tenho de quatro a cinco anos de experiência com a AWS, conheço EC2, Lambda, CloudFront, S3.", "NAO"),
    ("A gente tem Elastic Beanstalk pro back-end, Aurora como banco, OpenSearch pra pesquisa e DynamoDB.", "NAO"),
    ("A gente tem um Redis local aqui, só que não está ativo atualmente. Talvez seria pra cache.", "NAO"),
    ("Nós somos uma mineradora da região de Curitiba, temos alguns serviços rodando na Amazon.", "NAO"),
    ("Hoje a gente trabalha com o DataSul. Na parte de conferência, trabalhamos com planilhas.", "NAO"),
    ("A gente já está usando o Gemini com o Google Drive pra buscar documentos.", "NAO"),
    ("O Paulo é do time de TI, desenvolvedor. O Abner é do setor de melhoria contínua.", "NAO"),
    ("A gente tem o aplicativo de frete, o site, mas de forma geral é esse o tipo de serviço que consumimos.", "NAO"),
    ("Nós estamos iniciando na parte de IA. É novo pra gente. Não tem um ponto específico.", "NAO"),
    ("A diretoria tem preferência de rodar localmente por questão de dados sensíveis.", "NAO"),
]

prompt_template = "A conversa abaixo contém uma PERGUNTA TÉCNICA direta do cliente? Uma pergunta técnica é quando o cliente PEDE informação, faz uma PERGUNTA explícita (com ? ou pedindo explicação). Se o cliente apenas DESCREVE algo ou AFIRMA algo, NÃO é pergunta. Responda APENAS: SIM ou NAO\n\nConversa: {ctx}"

correct = 0
results = []
for ctx, expected in cases:
    msg = prompt_template.format(ctx=ctx)
    raw = client.call_raw("Classifique.", msg, max_tokens=5).strip().upper()
    # Normalizar
    got = "SIM" if "SIM" in raw else "NAO"
    ok = got == expected
    if ok: correct += 1
    icon = "✅" if ok else "❌"
    line = f"{icon} Esperado={expected} Got={got} | {ctx[:80]}..."
    results.append(line)
    print(line)

pct = correct / len(cases) * 100
print(f"\n{'='*60}")
print(f"RESULTADO: {correct}/{len(cases)} = {pct:.0f}%")
print(f"{'='*60}")

with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-classificacao.md"), "w") as f:
    f.write(f"# Teste Classificação SIM/NAO — {correct}/{len(cases)} = {pct:.0f}%\n\n")
    f.write("\n".join(results))
    f.write(f"\n\n## Resultado: {correct}/{len(cases)} = {pct:.0f}%\n")
