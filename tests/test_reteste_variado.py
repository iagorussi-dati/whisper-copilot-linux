"""Reteste: cenários variados com contexto extra — confirmar consistência."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

TESTS = [
    # YouTube: podcast de tecnologia
    {
        "name": "YouTube: podcast tech",
        "extra": "Estou assistindo um podcast de tecnologia no YouTube.",
        "instruction": "o que ele quis dizer com isso?",
        "transcripts": [
            ("Host", "Então o Kubernetes é overkill pra maioria das startups?"),
            ("Convidado", "Total. Se tu tem 3 microserviços, roda num ECS ou até num EC2 com Docker Compose. Kubernetes é pra quando tu tem 50 serviços e precisa de auto-scaling granular."),
        ],
    },
    # YouTube: live de coding
    {
        "name": "YouTube: live coding",
        "extra": "Estou assistindo uma live de programação no YouTube.",
        "instruction": "",
        "transcripts": [
            ("Streamer", "Então galera, vou refatorar esse componente React. Tá com 500 linhas, precisa quebrar."),
            ("Streamer", "Primeiro vou extrair o hook customizado. Toda essa lógica de fetch vai pra um useQuery."),
            ("Streamer", "Pronto, agora o componente ficou com 200 linhas. Muito melhor."),
        ],
    },
    # Reunião de trabalho — alguém apresentando
    {
        "name": "Reunião: apresentação de resultados",
        "extra": "Estou numa reunião de trabalho. Sou estagiário.",
        "instruction": "o que eu deveria anotar?",
        "transcripts": [
            ("Diretor", "O faturamento do Q1 foi 2.3 milhões, 15% acima do target."),
            ("Diretor", "O maior crescimento foi no segmento enterprise, 40% year over year."),
            ("Diretor", "Pra Q2 a meta é 2.8 milhões. Vamos precisar de mais 2 SDRs."),
        ],
    },
    # YouTube: aula de culinária
    {
        "name": "YouTube: aula de culinária",
        "extra": "Estou assistindo uma aula de culinária no YouTube.",
        "instruction": "qual a temperatura que ele falou?",
        "transcripts": [
            ("Chef", "O segredo do risoto é o caldo quente. Nunca coloque caldo frio."),
            ("Chef", "Vai adicionando concha por concha, mexendo sempre."),
            ("Chef", "O fogo tem que ser médio, uns 160 graus se for no forno."),
            ("Chef", "E no final, manteiga e parmesão. Isso que dá a cremosidade."),
        ],
    },
    # Call com cliente gringo
    {
        "name": "Call com cliente em inglês",
        "extra": "Estou numa call com um cliente americano. Me ajuda a entender.",
        "instruction": "o que ele tá pedindo?",
        "transcripts": [
            ("Client", "We need the API to support pagination and filtering by date range."),
            ("Client", "Also, the response time should be under 200ms for the search endpoint."),
            ("Client", "Can you guys deliver this by end of sprint?"),
        ],
    },
    # YouTube: documentário
    {
        "name": "YouTube: documentário natureza",
        "extra": "Estou assistindo um documentário sobre oceanos no YouTube.",
        "instruction": "",
        "transcripts": [
            ("Narrador", "As baleias jubarte viajam mais de 8 mil quilômetros por ano."),
            ("Narrador", "Elas saem das águas geladas da Antártica e vão até o nordeste do Brasil pra se reproduzir."),
            ("Narrador", "O canto das baleias pode ser ouvido a mais de 30 quilômetros de distância."),
        ],
    },
    # Twitch: stream de game
    {
        "name": "Twitch: stream de Valorant",
        "extra": "Estou assistindo uma stream de Valorant na Twitch.",
        "instruction": "ele jogou bem nesse round?",
        "transcripts": [
            ("Streamer", "Vou de Jett nesse mapa. Dash pro site A."),
            ("Streamer", "Peguei o primeiro, headshot. Segundo tá no canto, smoke e dash."),
            ("Streamer", "Ace! Cinco kills no round. Chat tá maluco."),
        ],
    },
    # Spotify: podcast de história
    {
        "name": "Podcast: história do Brasil",
        "extra": "Estou ouvindo um podcast sobre história do Brasil.",
        "instruction": "resume o que ele falou",
        "transcripts": [
            ("Historiador", "A proclamação da República em 1889 não foi um movimento popular."),
            ("Historiador", "Foi um golpe militar liderado pelo Marechal Deodoro da Fonseca."),
            ("Historiador", "O povo assistiu bestializado, como disse Aristides Lobo. Ninguém entendeu o que estava acontecendo."),
        ],
    },
]

BAD_PATTERNS = [
    "analis", "identificação dos", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto",
    "baseado no contexto", "vamos analisar", "ponto central é",
]


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

    extra = test["extra"]
    if test.get("instruction"):
        extra += f"\n{test['instruction']}"

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

    for speaker, text in test["transcripts"]:
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
    print("RETESTE: 8 CENÁRIOS VARIADOS COM CONTEXTO EXTRA")
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
        print(f"   📋 Contexto: {t['extra'][:60]}")
        if t.get("instruction"):
            print(f"   📝 Instrução: \"{t['instruction']}\"")
        for line in resp[:300].split("\n"):
            if line.strip():
                print(f"   {line.strip()}")
        if issues:
            print(f"   ⚠️ Padrões robóticos: {issues}")

    print(f"\n{'='*70}")
    print(f"RESULTADO: {passed}/8 passaram | {failed}/8 falharam")
    print(f"{'='*70}")
