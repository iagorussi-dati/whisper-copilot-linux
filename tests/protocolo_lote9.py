"""Lote 9: Snapshot incremental — 3 snapshots sequenciais, não repetir."""
from protocolo_runner import run_one, score_response
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

CONVERSATIONS = [
    {
        "name": "Discovery comercial",
        "behavior": "sugestoes",
        "chunks": [
            [("Cliente", "A gente tem 3 servidores on-premise. Tá ficando caro."),
             ("Consultor", "Entendi. Quanto vocês gastam hoje?"),
             ("Cliente", "Uns 15 mil por mês com data center.")],
            [("Cliente", "E a gente tem picos absurdos no site de ingressos."),
             ("Cliente", "5 pessoas num minuto, 2000 no outro."),
             ("Consultor", "Escalabilidade automática resolve.")],
            [("Cliente", "E segurança? Já tivemos ataque DDoS ano passado."),
             ("Cliente", "Ficamos fora 6 horas."),
             ("Consultor", "Vamos incluir WAF e Shield.")],
        ],
    },
    {
        "name": "Daily standup",
        "behavior": "conversa",
        "chunks": [
            [("Gui", "Bom dia. Iago?"), ("Iago", "Terminei V1, falta deploy."),
             ("Gui", "Bruno?"), ("Bruno", "Travei no staging.")],
            [("Mari", "Terminei testes, 95% cobertura."),
             ("Josimar", "Tô revisando PR do Bruno."),
             ("Gui", "Prioridade: deploy V1.")],
            [("Gui", "Mais alguma coisa?"),
             ("Bruno", "Preciso de acesso ao staging urgente."),
             ("Iago", "Posso ajudar o Bruno com isso.")],
        ],
    },
]


def run_incremental(conv):
    api = Api()
    all_responses = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            all_responses.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    pmap = {"sugestoes": "sugestoes.md", "conversa": "conversa-natural.md"}
    with open(os.path.join(prompts_dir, pmap[conv["behavior"]])) as f:
        prompt = f.read()

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt, "behavior_template": conv["behavior"],
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": "short", "auto_response": True, "extra_context": "",
    }
    api.start_meeting(config)

    for i, chunk in enumerate(conv["chunks"]):
        for speaker, text in chunk:
            entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
            api._transcript.append(entry)
            api._chat_history.append({"event": "transcript", "data": entry})

        prev = [r[:80] for r in all_responses]
        hint = f"\n\nJá respondido: {'; '.join(prev[-3:])}. NÃO repita." if prev else ""

        t0 = time.time()
        api._generate_snapshot_response(hint)
        for _ in range(20):
            time.sleep(1)
            if len(all_responses) > i:
                break
        elapsed = time.time() - t0

        resp = all_responses[-1] if len(all_responses) > i else "❌"
        print(f"  Snapshot {i+1} ({elapsed:.1f}s): {resp[:200].replace(chr(10), ' ')}")

    api._hotkey_stop.set()
    return all_responses


if __name__ == "__main__":
    print("=" * 70)
    print("LOTE 9: SNAPSHOT INCREMENTAL")
    print("=" * 70)

    passed = 0
    total = 0

    for conv in CONVERSATIONS:
        print(f"\n{'─'*70}")
        print(f"📌 {conv['name']} ({conv['behavior']})")

        responses = run_incremental(conv)

        # Check: each snapshot should NOT repeat previous
        for i in range(1, len(responses)):
            total += 1
            prev_words = set(responses[i-1].lower().split())
            curr_words = set(responses[i].lower().split())
            overlap = len(prev_words & curr_words) / max(len(curr_words), 1)
            no_repeat = overlap < 0.5  # less than 50% word overlap
            if no_repeat:
                passed += 1
                print(f"  ✅ Snapshot {i+1} não repetiu ({overlap:.0%} overlap)")
            else:
                print(f"  ❌ Snapshot {i+1} repetiu demais ({overlap:.0%} overlap)")

        # Check: responses exist
        for i, r in enumerate(responses):
            total += 1
            if r and not r.startswith("❌"):
                passed += 1
            else:
                print(f"  ❌ Snapshot {i+1} sem resposta")

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/{total}")
