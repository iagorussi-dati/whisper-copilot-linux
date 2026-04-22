"""Lote 3: 10 cenários com instruções do usuário + contextos variados."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

SCENARIOS = [
    # 21. Instrução: "me faz rir"
    {
        "name": "21. Instrução: me faz rir",
        "instruction": "me faz rir com o que tão falando",
        "transcripts": [
            ("Colega", "O deploy de sexta deu ruim de novo."),
            ("Iago", "Quem foi o gênio que fez deploy na sexta?"),
            ("Colega", "Eu."),
        ],
    },
    # 22. Instrução: "resume pra mim"
    {
        "name": "22. Instrução: resume pra mim",
        "instruction": "resume o que falaram",
        "transcripts": [
            ("Gui", "Então, a sprint termina sexta. Temos 3 tasks abertas."),
            ("Gui", "O Iago tá com a V1, o Bruno com o TatiLab, e a Mari com os testes."),
            ("Gui", "Prioridade é fechar a V1 primeiro."),
            ("Gui", "Se sobrar tempo, a gente começa a sprint seguinte."),
        ],
    },
    # 23. Instrução: "traduz"
    {
        "name": "23. Instrução: traduz pro inglês",
        "instruction": "traduz o que ele falou pro inglês",
        "transcripts": [
            ("Cliente", "A gente precisa de uma solução que escale automaticamente e que tenha alta disponibilidade."),
            ("Cliente", "O orçamento é de 50 mil por mês e o prazo é 3 meses."),
        ],
    },
    # 24. Instrução: "o que eu deveria perguntar?"
    {
        "name": "24. Instrução: o que perguntar?",
        "instruction": "o que eu deveria perguntar agora?",
        "transcripts": [
            ("Entrevistador", "Me conta sobre um projeto desafiador que você fez."),
            ("Iago", "Eu criei um copiloto de reuniões em tempo real com IA."),
            ("Entrevistador", "Interessante. Quais tecnologias usou?"),
            ("Iago", "Groq Whisper pra transcrição, Bedrock pra IA, pywebview pra UI."),
        ],
    },
    # 25. Sem instrução — podcast sobre investimentos
    {
        "name": "25. Podcast investimentos",
        "instruction": "",
        "transcripts": [
            ("Host", "Então, renda fixa ou renda variável em 2026?"),
            ("Convidado", "Com a Selic a 14%, renda fixa tá pagando muito bem. CDB de banco médio tá dando 120% do CDI."),
            ("Host", "Mas e quem quer mais risco?"),
            ("Convidado", "Aí tem FIIs que tão descontados. Alguns pagando 1% ao mês de dividendo."),
        ],
    },
    # 26. Sem instrução — casal discutindo destino de férias
    {
        "name": "26. Casal — férias",
        "instruction": "",
        "transcripts": [
            ("Ela", "Eu quero ir pra praia. Tô precisando descansar."),
            ("Ele", "Mas a gente foi pra praia no último feriado. Que tal serra?"),
            ("Ela", "Serra é frio demais. E não tem nada pra fazer."),
            ("Ele", "Tem vinícola, trilha, fondue..."),
            ("Ela", "Tá, me convenceu no fondue."),
        ],
    },
    # 27. Instrução: "me dá argumentos"
    {
        "name": "27. Instrução: argumentos pra negociação",
        "instruction": "me dá argumentos pra eu negociar",
        "transcripts": [
            ("Chefe", "Iago, sobre o aumento, a empresa não tá num momento bom pra isso."),
            ("Iago", "Entendo, mas eu assumi muito mais responsabilidade nos últimos meses."),
            ("Chefe", "Eu sei, mas o orçamento tá apertado."),
        ],
    },
    # 28. Conversa técnica — debug ao vivo
    {
        "name": "28. Debug ao vivo",
        "instruction": "",
        "transcripts": [
            ("Iago", "O erro tá dando 502 Bad Gateway no nginx."),
            ("Colega", "Já olhou se o backend tá rodando?"),
            ("Iago", "Tá rodando, mas o log mostra timeout na conexão com o banco."),
            ("Colega", "Pode ser o pool de conexões cheio. Quantas conexões ativas tem?"),
            ("Iago", "Deixa eu ver... 50 ativas, limite é 50."),
        ],
    },
    # 29. Conversa sobre pet
    {
        "name": "29. Conversa sobre cachorro",
        "instruction": "",
        "transcripts": [
            ("Amigo", "Meu cachorro comeu meu fone de ouvido."),
            ("Iago", "De novo? Ele já comeu quantos?"),
            ("Amigo", "Esse é o terceiro. Acho que ele gosta do gosto da borracha."),
            ("Iago", "Compra um fone bluetooth e guarda no alto."),
            ("Amigo", "Ele pula na mesa."),
        ],
    },
    # 30. Instrução específica — "fala como se fosse o Galvão Bueno"
    {
        "name": "30. Instrução: fala como Galvão Bueno",
        "instruction": "comenta como se fosse o Galvão Bueno narrando",
        "transcripts": [
            ("Narrador", "E o Vini Jr recebe na ponta esquerda, corta pra dentro."),
            ("Narrador", "Chuta! Desviou na zaga e a bola vai pra escanteio."),
        ],
    },
]

BAD_PATTERNS = [
    "analis", "identificação", "participantes", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto", "dor aqui",
    "tema novo", "ponto central", "vamos analisar",
    "identificação dos", "baseado no contexto",
]


def run_one(scenario, mode="short"):
    api = Api()
    results = []
    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})
    api._emit = fake_emit

    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "conversa-natural.md")) as f:
        prompt = f.read()

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt, "behavior_template": "conversa",
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": mode, "auto_response": True,
        "extra_context": scenario.get("instruction", ""),
    }
    api.start_meeting(config)

    for speaker, text in scenario["transcripts"]:
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
    print("LOTE 3 — 10 CENÁRIOS COM INSTRUÇÕES (modo short)")
    print("=" * 70)

    passed = 0
    failed = 0

    for s in SCENARIOS:
        resp, elapsed = run_one(s, "short")
        resp_lower = resp.lower()
        issues = [p for p in BAD_PATTERNS if p in resp_lower]
        ok = len(issues) == 0
        if ok:
            passed += 1
        else:
            failed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {s['name']} ({elapsed:.1f}s)")
        preview = resp[:300].replace("\n", " ")
        print(f"   {preview}")
        if issues:
            print(f"   ⚠️ Padrões robóticos: {issues}")

    print(f"\n{'='*70}")
    print(f"RESULTADO: {passed}/10 passaram | {failed}/10 falharam")
    print(f"{'='*70}")
