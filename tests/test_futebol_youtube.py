"""Teste: transmissão de futebol do YouTube — Copiloto Pessoal com instruções."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

# Transcrição real do log — narração de futebol espanhol
TRANSCRIPTS = [
    ("Narrador", "Autoriza o árbitro, tá rolando na tela do Disney Plus."),
    ("Comentarista", "Mas o Arbeloa em bem menos jogos já tem mais derrotas do que teve o Xabi Alonso na sua passagem pelo Real Madrid."),
    ("Comentarista", "Ele não deve ficar né, pensando nessa reformulação que pensa o Florentino Pérez."),
    ("Narrador", "Blanco, aí o capitão do Alavés já faz o lançamento às costas."),
    ("Narrador", "É boa a bola, já ganhando a marcação, o Angel Pérez."),
    ("Narrador", "Pérez faz o cruzamento, a bola passa por todo mundo."),
    ("Comentarista", "O Real Madrid tá muito aberto atrás. Essa linha defensiva tá alta demais."),
    ("Narrador", "Bola com o Bellingham agora, toca pro Vini Jr na ponta esquerda."),
    ("Narrador", "Vini corta pra dentro, chuta! Desviou na zaga, escanteio."),
    ("Comentarista", "O Vini tá tentando resolver sozinho. Precisa tocar mais."),
    ("Narrador", "Escanteio cobrado, Rüdiger sobe, cabeceia pra fora."),
    ("Comentarista", "O Alavés tá surpreendendo. Tá jogando sem medo."),
]

# Cenários com instruções diferentes
TESTS = [
    {
        "name": "Sem instrução — só acompanhando",
        "instruction": "",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: quem tá jogando melhor?",
        "instruction": "quem tá jogando melhor?",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: faz um comentário engraçado",
        "instruction": "faz um comentário engraçado sobre o jogo",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: como tá o Real Madrid?",
        "instruction": "como tá o Real Madrid nesse jogo?",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: o Vini Jr tá bem?",
        "instruction": "o Vini Jr tá jogando bem?",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: quem é o Arbeloa?",
        "instruction": "quem é o Arbeloa que eles falaram?",
        "slices": TRANSCRIPTS[:3],  # só o começo
    },
    {
        "name": "Instrução: previsão do resultado",
        "instruction": "qual tua previsão pro resultado?",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Snapshot parcial — só narração (sem comentário)",
        "instruction": "",
        "slices": [t for t in TRANSCRIPTS if t[0] == "Narrador"],
    },
    {
        "name": "Instrução: explica a tática do Alavés",
        "instruction": "explica a tática do Alavés",
        "slices": TRANSCRIPTS,
    },
    {
        "name": "Instrução: me conta o que tá acontecendo (leigo)",
        "instruction": "me explica o que tá acontecendo como se eu não entendesse de futebol",
        "slices": TRANSCRIPTS,
    },
]

BAD_PATTERNS = [
    "analis", "identificação dos", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto",
    "baseado no contexto", "vamos analisar", "ponto central é",
]

EXTRA_CONTEXT = "Estou assistindo uma transmissão de futebol ao vivo pelo YouTube. Real Madrid x Alavés, La Liga."


def run_one(test, mode="short"):
    api = Api()
    results = []
    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})
    api._emit = fake_emit

    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "conversa-natural.md")) as f:
        prompt = f.read()

    instruction = test.get("instruction", "")
    extra = EXTRA_CONTEXT
    if instruction:
        extra += f"\n{instruction}"

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt, "behavior_template": "conversa",
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": mode, "auto_response": True,
        "extra_context": extra,
    }
    api.start_meeting(config)

    for speaker, text in test["slices"]:
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        api._transcript.append(entry)
        api._chat_history.append({"event": "transcript", "data": entry})

    t0 = time.time()
    api._generate_snapshot_response("")
    for _ in range(20):
        time.sleep(1)
        if results:
            break
    elapsed = time.time() - t0
    api._hotkey_stop.set()
    return results[-1] if results else "❌ Sem resposta", elapsed


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: TRANSMISSÃO FUTEBOL YOUTUBE — 10 cenários")
    print(f"Contexto: {EXTRA_CONTEXT}")
    print("=" * 70)

    passed = 0
    failed = 0

    for t in TESTS:
        resp, elapsed = run_one(t, "short")
        resp_lower = resp.lower()
        issues = [p for p in BAD_PATTERNS if p in resp_lower]
        ok = len(issues) == 0
        if ok:
            passed += 1
        else:
            failed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {t['name']} ({elapsed:.1f}s)")
        if t.get("instruction"):
            print(f"   📝 Instrução: \"{t['instruction']}\"")
        for line in resp[:350].split("\n"):
            if line.strip():
                print(f"   {line.strip()}")
        if issues:
            print(f"   ⚠️ Padrões robóticos: {issues}")

    print(f"\n{'='*70}")
    print(f"RESULTADO: {passed}/10 passaram | {failed}/10 falharam")
    print(f"{'='*70}")
