#!/usr/bin/env python3
"""Bateria COMPLEXA de classificação — perguntas escondidas, mistas, ambíguas."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()

cases = [
    # PERGUNTAS ESCONDIDAS (esperado: SIM)
    ("A gente tem um Redis local aqui, só que eu vou ser bem sincero contigo, eu ainda não descobri o real motivo. Talvez seria para um serviço de cache, mas não está ativo atualmente. Não sei se vale a pena manter ou tirar.", "SIM"),
    ("A gente tá pensando em sair do Beanstalk, mas não sei se compensa o esforço de migrar tudo pro Fargate agora ou se a gente espera.", "SIM"),
    ("O pessoal da diretoria quer que a gente rode tudo local por causa de dados sensíveis, mas eu não sei se isso é viável com os serviços da AWS.", "SIM"),
    ("A gente usa o Gemini com o Google Drive e funciona bem, mas me preocupa essa questão de privacidade dos dados.", "SIM"),
    ("Eu tentei usar a calculadora da AWS pra estimar o custo e ficou 18 mil por mês, achei absurdo, não sei se fiz a conta certa.", "SIM"),
    ("A gente tem o ERP DataSul on-prem e queria conectar com alguma coisa na nuvem, mas não faço ideia de como isso funcionaria.", "SIM"),
    ("Nosso deploy demora 30 minutos e quando dá pico o sistema cai porque o auto-scaling não acompanha, tá complicado.", "SIM"),
    ("A gente precisa atender um cliente que quer infra exclusiva, banco separado, tudo isolado, e eu não sei nem se isso é viável.", "SIM"),
    
    # SEM PERGUNTA — só contexto/afirmação (esperado: NAO)
    ("Eu já tenho uns 5 anos de experiência com AWS, trabalho com EC2, Lambda, S3, CloudFront. A gente usa bastante.", "NAO"),
    ("A gente tem Elastic Beanstalk, Aurora, OpenSearch e DynamoDB. Tudo rodando na mesma conta.", "NAO"),
    ("Somos uma mineradora de Curitiba, temos alguns serviços na AWS e estamos começando a olhar pra IA.", "NAO"),
    ("O Carlos é da contabilidade, o Paulo é dev, o Abner é de melhoria contínua. A gente trabalha com DataSul e planilhas.", "NAO"),
    ("A gente já usa Gemini com Google Drive pra buscar documentos. Funciona bem pra gente.", "NAO"),
    ("Nosso billing na AWS tá em torno de 8 mil dólares por mês, pagamos no cartão.", "NAO"),
    ("A gente tem duas empresas, BR Condos e a SCD, são CNPJs diferentes, coisas totalmente separadas.", "NAO"),
    ("O Thiago é nosso diretor, ele que aprova os projetos. Se ele topar a gente segue.", "NAO"),
    
    # MISTAS — contexto + pergunta escondida (esperado: SIM)
    ("A gente tem tudo rodando em duas VPS, Docker, Postgres, Redis, Minio. Tá funcionando mas eu sei que não escala. Será que vale a pena migrar agora ou esperar ter mais clientes?", "SIM"),
    ("Nosso sistema é um monolito em Python que consome muita memória, uns 2GB só parado. Os workers do Celery travam quando entra muita coisa na fila. Tem algum jeito de resolver isso sem refatorar tudo?", "SIM"),
    ("A gente fez uma POC de IA mas ela respondeu tudo errado, regra de três, um monte de erro. Desligamos. Será que com a AWS seria diferente?", "SIM"),
    ("Eu tenho 25 clientes, o BI atualiza a cada 15 minutos, mas às vezes o serviço cai e eu nem fico sabendo. O cliente que me avisa. Tem como monitorar isso de algum jeito?", "SIM"),
    
    # MISTAS — parece pergunta mas é afirmação (esperado: NAO)
    ("A gente decidiu que vai manter o ERP on-prem e só levar o BI pra nuvem. Já conversamos internamente e é isso.", "NAO"),
    ("Vou conversar com a gerente e te retorno. Não posso decidir nada sem ela.", "NAO"),
    ("A gente já testou o Gemini e gostou. Vamos continuar com ele por enquanto.", "NAO"),
    ("O pessoal da AWS já veio aqui, mandou documentação, mas a gente acabou não implementando.", "NAO"),
    
    # PERGUNTAS DIRETAS CLARAS (esperado: SIM)
    ("Quanto custa o ElastiCache pra um nó pequeno?", "SIM"),
    ("O Lambda suporta execução de mais de 15 minutos?", "SIM"),
    ("Dá pra usar o Cognito só pro MFA sem migrar os usuários?", "SIM"),
    ("Vocês conseguem fazer a migração em quanto tempo?", "SIM"),
]

prompt_template = "A conversa abaixo contém uma PERGUNTA TÉCNICA direta do cliente? Uma pergunta técnica é quando o cliente PEDE informação, faz uma PERGUNTA explícita (com ? ou pedindo explicação), ou expressa uma DÚVIDA que precisa de resposta técnica (ex: 'não sei se vale a pena', 'não faço ideia de como', 'será que', 'tem como', 'não sei se é viável'). Se o cliente apenas DESCREVE algo, AFIRMA uma decisão já tomada, ou INFORMA algo sem pedir resposta, NÃO é pergunta. Responda APENAS: SIM ou NAO\n\nConversa: {ctx}"

correct = 0
errors = []
results = []
for ctx, expected in cases:
    msg = prompt_template.format(ctx=ctx)
    raw = client.call_raw("Classifique.", msg, max_tokens=5).strip().upper()
    got = "SIM" if "SIM" in raw else "NAO"
    ok = got == expected
    if ok: correct += 1
    else: errors.append((ctx[:80], expected, got))
    icon = "✅" if ok else "❌"
    line = f"{icon} Esperado={expected} Got={got} | {ctx[:80]}..."
    results.append(line)
    print(line)

pct = correct / len(cases) * 100
print(f"\n{'='*60}")
print(f"RESULTADO: {correct}/{len(cases)} = {pct:.0f}%")
if errors:
    print(f"\nERROS ({len(errors)}):")
    for ctx, exp, got in errors:
        print(f"  {ctx}... (esperado={exp}, got={got})")
print(f"{'='*60}")

with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-classificacao-v2.md"), "w") as f:
    f.write(f"# Teste Classificação COMPLEXA — {correct}/{len(cases)} = {pct:.0f}%\n\n")
    f.write(f"30 casos: perguntas escondidas, mistas, ambíguas, afirmações\n\n")
    f.write("\n".join(results))
    f.write(f"\n\n## Resultado: {correct}/{len(cases)} = {pct:.0f}%\n")
    if errors:
        f.write(f"\n## Erros ({len(errors)}):\n")
        for ctx, exp, got in errors:
            f.write(f"- {ctx}... (esperado={exp}, got={got})\n")
