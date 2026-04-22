"""Lote 7: Modo Sugestões — frases prontas, tom correto."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Discovery — cliente fala de infra", "transcripts": [
        ("Consultor", "Então, me conta sobre a infra de vocês."),
        ("Cliente", "A gente tem 3 servidores on-premise, Postgres com 500GB, e 2TB de arquivos."),
        ("Consultor", "Pra esses arquivos, S3 é o caminho."),
    ]},
    {"name": "Discovery — cliente tem dúvida", "transcripts": [
        ("Cliente", "Qual classe de S3 é mais barata? Porque metade dos arquivos a gente não acessa."),
        ("Consultor", "Vou te passar os detalhes."),
    ]},
    {"name": "Reunião — cliente reclama de custo", "transcripts": [
        ("Cliente", "A gente gasta 15 mil por mês com data center. Tá caro demais."),
        ("Consultor", "Entendo. Na AWS dá pra otimizar bastante."),
        ("Cliente", "Mas quanto vai custar na AWS?"),
    ]},
    {"name": "Reunião — cliente fala de picos", "transcripts": [
        ("Cliente", "O site de ingressos tem picos absurdos. 5 pessoas num minuto, 2000 no outro."),
        ("Consultor", "Escalabilidade automática resolve isso."),
        ("Cliente", "Mas como funciona na prática?"),
    ]},
    {"name": "Negociação — cliente hesita", "transcripts": [
        ("Cliente", "Gostei da proposta, mas preciso pensar."),
        ("Cliente", "O preço tá um pouco acima do que eu esperava."),
        ("Consultor", "Entendo. O que seria um valor confortável?"),
    ]},
    {"name": "Discovery — dor de deploy", "transcripts": [
        ("Cliente", "Hoje a gente faz deploy manual. SSH no servidor, sobe os arquivos."),
        ("Cliente", "Já aconteceu de subir versão com bug e demorar horas pra voltar."),
    ]},
    {"name": "Reunião — cliente pergunta sobre segurança", "transcripts": [
        ("Cliente", "E segurança? A gente precisa de proteção contra DDoS."),
        ("Cliente", "Já tivemos ataque ano passado e ficamos fora 6 horas."),
    ]},
    {"name": "Discovery — múltiplos serviços", "transcripts": [
        ("Cliente", "A gente tem 12 microserviços em Docker."),
        ("Cliente", "Quero saber se compensa EKS ou Lambda pra cada um."),
        ("Consultor", "Depende do padrão de uso."),
    ]},
    {"name": "Reunião — cliente quer chatbot", "transcripts": [
        ("Cliente", "Queremos implementar um chatbot interno com IA."),
        ("Cliente", "Vi que tem o Bedrock. Serve pra isso?"),
    ]},
    {"name": "Fechamento — próximos passos", "transcripts": [
        ("Consultor", "Então, resumindo: migração de infra, CI/CD, e monitoramento."),
        ("Cliente", "Isso. Quando vocês conseguem começar?"),
        ("Consultor", "Podemos iniciar semana que vem com o assessment."),
    ]},
]

if __name__ == "__main__":
    run_lote("7. Sugestões", SCENARIOS, mode="short", behavior="sugestoes")
