"""Test: copiloto técnico de pré-vendas com web search.
Simula cliente perguntando preços e specs durante call."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api import Api

SCENARIOS = [
    {
        "name": "Cliente pergunta preço do Amazon Q",
        "transcripts": [
            ("Consultor", "Então pra parte de busca interna e assistente de IA, a gente pode usar o Amazon Q Business."),
            ("Cliente", "Interessante. Mas quanto custa o Amazon Q Business? Porque a gente tem uns 200 funcionários que usariam."),
            ("Consultor", "Deixa eu verificar o pricing atualizado pra te passar."),
        ],
    },
    {
        "name": "Cliente pergunta sobre Bedrock pricing",
        "transcripts": [
            ("Consultor", "Pra parte de IA generativa, a gente usa o Amazon Bedrock com Claude ou Nova."),
            ("Cliente", "E qual o preço do Bedrock? Tipo, por token ou por request? Porque a gente vai ter um volume alto de chamadas."),
            ("Consultor", "Vou te dar os números exatos."),
        ],
    },
    {
        "name": "Cliente pergunta spec técnica do EKS",
        "transcripts": [
            ("Consultor", "A infraestrutura vai rodar em EKS com Fargate pra não precisar gerenciar nodes."),
            ("Cliente", "Qual o limite de pods por node no EKS com Fargate? E tem alguma limitação de CPU e memória por pod?"),
            ("Consultor", "Boa pergunta, deixa eu confirmar os limites atuais."),
        ],
    },
    {
        "name": "Mix: sugestão técnica + dúvida de preço",
        "transcripts": [
            ("Consultor", "Pra observabilidade a gente vai usar CloudWatch com X-Ray."),
            ("Cliente", "Tá, mas a gente já usa Datadog. Compensa trocar pro CloudWatch? E quanto custa o CloudWatch pra um ambiente com 50 serviços?"),
            ("Consultor", "É uma boa comparação. Deixa eu ver os números."),
            ("Cliente", "E outra coisa, vocês recomendam usar o Graviton pras instâncias? Vi que é mais barato mas não sei se compensa."),
        ],
    },
]


def run():
    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "assistente-objetivo.md")) as f:
        prompt = f.read()

    for scenario in SCENARIOS:
        print(f"\n{'='*60}")
        print(f"CENÁRIO: {scenario['name']}")
        print(f"{'='*60}")

        api = Api()
        results = []

        def fake_emit(event, data):
            if event == "copilot_response" and data.get("response"):
                results.append(data["response"])
            api._chat_history.append({"event": event, "data": data})

        api._emit = fake_emit

        config = {
            "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
            "my_name": "Consultor", "participants": [],
            "groq_api_key": "", "custom_system_prompt": prompt,
            "behavior_prompt": prompt,
            "suggestions_target": "Consultor", "global_hotkey": "", "snapshot_hotkey": "",
            "response_mode": "full", "auto_response": True, "extra_context": "",
        }
        api.start_meeting(config)

        for speaker, text in scenario["transcripts"]:
            entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
            api._transcript.append(entry)
            api._chat_history.append({"event": "transcript", "data": entry})
            print(f"  📝 [{speaker}] {text[:80]}")

        print(f"\n  ⏳ Gerando resposta (com web search se necessário)...")
        t0 = time.time()
        api._generate_snapshot_response("")
        # Wait for response
        for _ in range(30):
            time.sleep(1)
            if results:
                break
        elapsed = time.time() - t0

        if results:
            print(f"\n  🤖 RESPOSTA ({elapsed:.1f}s):\n")
            for line in results[-1].split("\n"):
                print(f"  {line}")
        else:
            print(f"  ❌ Sem resposta após {elapsed:.1f}s")

        api._hotkey_stop.set()
        print()


if __name__ == "__main__":
    run()
