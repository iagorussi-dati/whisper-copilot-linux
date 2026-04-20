"""Test: transcrição densa com muitas perguntas técnicas — search direto."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api import Api

# Transcrição densa: discovery técnica com MUITAS perguntas de pricing/specs
CHUNKS = [
    # Chunk 1: Infra atual + S3 + RDS
    [
        ("Consultor", "Bom, vamos mapear a infra de vocês. Me conta o que vocês têm hoje."),
        ("Cliente", "A gente tem 3 servidores on-premise, um Postgres com 500GB, e uns 2TB de arquivos estáticos que a gente guarda em NFS."),
        ("Consultor", "Pra esses 2TB de arquivos, S3 é o caminho. E pro Postgres, Aurora ou RDS."),
        ("Cliente", "Quanto custa o S3 pra 2TB? E qual classe eu uso? Porque metade desses arquivos a gente não acessa há mais de 6 meses."),
        ("Cliente", "E o Aurora PostgreSQL, qual o preço? Porque 500GB de banco não é pouco. E tem o custo de I/O também né?"),
        ("Consultor", "Vou te passar os números."),
    ],
    # Chunk 2: EKS + Lambda + API Gateway
    [
        ("Cliente", "Outra coisa, a gente tem 12 microserviços rodando em Docker. Quero saber se compensa EKS ou Lambda pra cada um."),
        ("Consultor", "Depende do padrão de uso. Serviços com tráfego constante ficam melhor no EKS, esporádicos no Lambda."),
        ("Cliente", "Qual o preço do EKS por cluster? E o Fargate por pod? Porque a gente tem picos de 500 requests por segundo."),
        ("Cliente", "E o API Gateway, quanto custa por milhão de requests? Porque a gente recebe uns 50 milhões de requests por mês."),
        ("Cliente", "Ah, e o Lambda, qual o limite de memória e timeout? Porque tem um serviço nosso que processa PDFs e demora uns 5 minutos."),
    ],
    # Chunk 3: Bedrock + OpenSearch + CloudFront
    [
        ("Cliente", "A gente quer implementar um chatbot interno com IA. Vi que tem o Bedrock. Quanto custa o Claude no Bedrock por token?"),
        ("Cliente", "E o Amazon Q, serve pra isso? Qual a diferença pro Bedrock?"),
        ("Consultor", "São coisas diferentes. Q é produto pronto, Bedrock é plataforma pra construir."),
        ("Cliente", "Entendi. E pra busca, a gente usa Elasticsearch on-premise. Qual o equivalente na AWS e quanto custa?"),
        ("Cliente", "E CDN? A gente precisa de CloudFront. Quanto custa pra 10TB de transferência por mês pro Brasil?"),
        ("Cliente", "Última coisa: WAF. A gente precisa de proteção contra DDoS. Quanto custa o AWS WAF e o Shield?"),
    ],
]

def run():
    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "assistente-objetivo.md")) as f:
        prompt = f.read()

    api = Api()
    all_responses = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            all_responses.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Consultor", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt,
        "suggestions_target": "Consultor", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": "research", "auto_response": True, "extra_context": "",
    }
    api.start_meeting(config)

    for i, chunk in enumerate(CHUNKS):
        print(f"\n{'='*60}")
        print(f"SNAPSHOT {i+1}/3")
        print(f"{'='*60}")

        for speaker, text in chunk:
            entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
            api._transcript.append(entry)
            api._chat_history.append({"event": "transcript", "data": entry})
            print(f"  📝 [{speaker}] {text[:80]}")

        prev = [r[:80] for r in all_responses]
        hint = f"\n\nJá respondido: {'; '.join(prev[-3:])}. NÃO repita." if prev else ""

        print(f"\n  ⏳ Gerando resposta (search direto)...")
        t0 = time.time()
        api._generate_snapshot_response(hint)
        for _ in range(30):
            time.sleep(1)
            if len(all_responses) > i:
                break
        elapsed = time.time() - t0

        if len(all_responses) > i:
            print(f"\n  🤖 RESPOSTA ({elapsed:.1f}s):\n")
            for line in all_responses[-1].split("\n"):
                if line.strip():
                    print(f"  {line}")
        else:
            print(f"  ❌ Sem resposta ({elapsed:.1f}s)")

    # Full context
    print(f"\n{'='*60}")
    print(f"FULL CONTEXT (Win+H)")
    print(f"{'='*60}")
    t0 = time.time()
    api._generate_fullcontext_response()
    for _ in range(30):
        time.sleep(1)
        if len(all_responses) > len(CHUNKS):
            break
    elapsed = time.time() - t0
    if len(all_responses) > len(CHUNKS):
        print(f"\n  🔍 RESPOSTA ({elapsed:.1f}s):\n")
        for line in all_responses[-1].split("\n"):
            if line.strip():
                print(f"  {line}")

    api._hotkey_stop.set()

    # Check coverage
    print(f"\n{'='*60}")
    print("COBERTURA DE PERGUNTAS")
    print(f"{'='*60}")
    all_text = " ".join(all_responses).lower()
    questions = [
        ("S3 pricing 2TB", ["s3", "2tb", "$0.02", "glacier", "armazenamento"]),
        ("Aurora PostgreSQL pricing", ["aurora", "postgres", "i/o", "rds"]),
        ("EKS pricing", ["eks", "cluster", "$0.10", "fargate"]),
        ("API Gateway pricing", ["api gateway", "milhão", "request", "$3.50", "$1.00"]),
        ("Lambda limites", ["lambda", "memória", "timeout", "15 min", "10gb", "10.240"]),
        ("Bedrock/Claude pricing", ["bedrock", "claude", "token", "$3", "$15"]),
        ("Amazon Q vs Bedrock", ["amazon q", "q business", "produto pronto", "plataforma"]),
        ("OpenSearch pricing", ["opensearch", "elasticsearch", "search"]),
        ("CloudFront 10TB Brasil", ["cloudfront", "cdn", "transferência", "10tb"]),
        ("WAF + Shield pricing", ["waf", "shield", "ddos", "proteção"]),
    ]
    covered = 0
    for label, keywords in questions:
        found = any(k in all_text for k in keywords)
        covered += found
        print(f"  {'✅' if found else '❌'} {label}")
    print(f"\n  Cobertura: {covered}/{len(questions)} ({covered*100//len(questions)}%)")


if __name__ == "__main__":
    run()
