"""Lote 8: Consultor Técnico AWS — web search + dados técnicos."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Preço S3", "transcripts": [
        ("Cliente", "Quanto custa o S3 pra 2TB de dados?"),
        ("Consultor", "Vou verificar."),
    ]},
    {"name": "Preço Aurora", "transcripts": [
        ("Cliente", "E o Aurora PostgreSQL? Quanto custa pra 500GB?"),
    ]},
    {"name": "EKS vs Lambda", "transcripts": [
        ("Cliente", "Compensa mais EKS ou Lambda pra 12 microserviços?"),
        ("Consultor", "Depende do padrão de uso."),
        ("Cliente", "A gente tem picos de 500 req/s."),
    ]},
    {"name": "Preço API Gateway", "transcripts": [
        ("Cliente", "Quanto custa o API Gateway pra 50 milhões de requests por mês?"),
    ]},
    {"name": "Limites Lambda", "transcripts": [
        ("Cliente", "Qual o limite de memória e timeout do Lambda?"),
        ("Cliente", "Tenho um serviço que processa PDFs e demora 5 minutos."),
    ]},
    {"name": "Bedrock pricing", "transcripts": [
        ("Cliente", "Quanto custa o Claude no Bedrock por token?"),
    ]},
    {"name": "CloudFront Brasil", "transcripts": [
        ("Cliente", "Quanto custa CloudFront pra 10TB de transferência pro Brasil?"),
    ]},
    {"name": "WAF + Shield", "transcripts": [
        ("Cliente", "Preciso de proteção DDoS. Quanto custa WAF e Shield?"),
    ]},
    {"name": "OpenSearch vs Elasticsearch", "transcripts": [
        ("Cliente", "A gente usa Elasticsearch on-premise. Qual o equivalente na AWS?"),
        ("Cliente", "Quanto custa?"),
    ]},
    {"name": "Comparação regiões", "transcripts": [
        ("Cliente", "Compensa usar Norte da Virgínia ou São Paulo?"),
        ("Cliente", "A gente precisa de baixa latência pro Brasil."),
    ]},
]

if __name__ == "__main__":
    run_lote("8. Consultor Técnico AWS", SCENARIOS, mode="research", behavior="assistente")
