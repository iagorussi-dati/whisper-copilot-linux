"""Lote 4: 10 cenários no modo full — verificar se mantém naturalidade com respostas maiores."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

SCENARIOS = [
    # 31. Daily com vários participantes
    {
        "name": "31. Daily 5 pessoas",
        "instruction": "me dá dicas do que falar",
        "transcripts": [
            ("Gui", "Bom dia pessoal. Vamos começar. Iago, como tá?"),
            ("Iago", "Tô bem. Terminei a V1 ontem, só falta deploy."),
            ("Bruno", "Eu tô com o TatiLab, mas travei no acesso ao staging."),
            ("Mari", "Eu terminei os testes unitários, 95% de cobertura."),
            ("Josimar", "Eu tô revisando o PR do Bruno. Tem uns pontos pra ajustar."),
            ("Gui", "Beleza. Prioridade é o deploy da V1 do Iago."),
        ],
    },
    # 32. Podcast longo sobre startups
    {
        "name": "32. Podcast startups",
        "instruction": "",
        "transcripts": [
            ("Host", "Então, qual o maior erro que fundadores cometem?"),
            ("Convidado", "Construir sem validar. O cara gasta 6 meses desenvolvendo e ninguém quer usar."),
            ("Host", "E como validar rápido?"),
            ("Convidado", "Landing page, lista de espera, conversa com 10 potenciais clientes. Se ninguém se interessa, pivota."),
            ("Host", "E sobre funding? Quando buscar investimento?"),
            ("Convidado", "Só depois de ter tração. Investidor quer ver números, não ideias."),
        ],
    },
    # 33. Briga de casal sobre dinheiro
    {
        "name": "33. Casal — dinheiro",
        "instruction": "",
        "transcripts": [
            ("Ela", "Tu gastou 500 reais em jogo de novo?"),
            ("Ele", "Não foi 500, foi 300. E era promoção."),
            ("Ela", "Promoção? A gente tá devendo o cartão e tu comprando jogo."),
            ("Ele", "Eu trabalho o mês inteiro, posso gastar um pouco comigo."),
            ("Ela", "Pode, mas não quando a gente tá no vermelho."),
        ],
    },
    # 34. Aula/palestra sobre machine learning
    {
        "name": "34. Palestra ML",
        "instruction": "",
        "transcripts": [
            ("Professor", "O conceito de overfitting é quando o modelo aprende demais os dados de treino."),
            ("Professor", "Ele decora em vez de generalizar. Aí quando vem dado novo, ele erra."),
            ("Aluno", "E como a gente evita isso?"),
            ("Professor", "Regularização, dropout, mais dados, cross-validation. Tem várias técnicas."),
            ("Aluno", "Qual a mais usada na prática?"),
            ("Professor", "Dropout em redes neurais e early stopping. São simples e funcionam bem."),
        ],
    },
    # 35. Conversa sobre mudança de cidade
    {
        "name": "35. Mudança de cidade",
        "instruction": "",
        "transcripts": [
            ("Iago", "Tô pensando em me mudar pra Floripa."),
            ("Amigo", "Sério? Por quê?"),
            ("Iago", "Qualidade de vida. Praia, clima, e tem bastante empresa de tech lá."),
            ("Amigo", "Mas o custo de vida lá tá absurdo. Aluguel no centro é 3 mil."),
            ("Iago", "É, mas se eu trabalhar remoto, posso morar mais longe."),
            ("Amigo", "Campeche, Ribeirão da Ilha... Tem opções boas e mais baratas."),
        ],
    },
    # 36. Conversa sobre filme
    {
        "name": "36. Filme — Oppenheimer",
        "instruction": "",
        "transcripts": [
            ("Amigo", "Tu viu Oppenheimer?"),
            ("Iago", "Vi. 3 horas de filme mas não senti o tempo passar."),
            ("Amigo", "O Cillian Murphy mereceu o Oscar. Que atuação."),
            ("Iago", "E a cena do julgamento? Pesadíssima."),
            ("Amigo", "O Nolan é gênio. Conseguiu fazer um filme sobre física nuclear ser emocionante."),
        ],
    },
    # 37. Instrução: "me ajuda a explicar"
    {
        "name": "37. Instrução: explicar pra leigo",
        "instruction": "me ajuda a explicar isso de forma simples",
        "transcripts": [
            ("Iago", "Então, basicamente o que a gente faz é pegar o áudio da reunião, mandar pra uma IA que transcreve, depois outra IA analisa e dá sugestões em tempo real."),
            ("Cliente", "Mas como assim IA? É tipo o ChatGPT?"),
            ("Iago", "Mais ou menos. É parecido mas focado em reuniões."),
        ],
    },
    # 38. Conversa sobre carro
    {
        "name": "38. Carro — trocar ou não",
        "instruction": "",
        "transcripts": [
            ("Iago", "Meu carro tá com 120 mil km. Tô pensando em trocar."),
            ("Amigo", "Qual é?"),
            ("Iago", "Polo 2019. Tá bom ainda mas o seguro tá caro."),
            ("Amigo", "Troca por um HB20 novo. Seguro é mais barato e o carro é bom."),
            ("Iago", "Mas eu gosto do Polo. Talvez só faça a revisão e segure mais um ano."),
        ],
    },
    # 39. Conversa sobre saúde
    {
        "name": "39. Saúde — dor nas costas",
        "instruction": "",
        "transcripts": [
            ("Iago", "Cara, tô com uma dor nas costas faz uma semana."),
            ("Colega", "Tu fica sentado o dia inteiro né? Postura."),
            ("Iago", "É, e minha cadeira é ruim."),
            ("Colega", "Investe numa cadeira boa. Faz diferença demais."),
            ("Iago", "Qual tu usa?"),
            ("Colega", "ThunderX3. Não é a melhor mas é boa pro preço."),
        ],
    },
    # 40. Conversa sobre clima/tempo
    {
        "name": "40. Clima — chuva",
        "instruction": "",
        "transcripts": [
            ("Colega", "Tá chovendo muito aí?"),
            ("Iago", "Demais. Alagou a rua aqui."),
            ("Colega", "Aqui também. Meu vizinho perdeu o carro."),
            ("Iago", "Sério? Que merda. Seguro cobre?"),
            ("Colega", "Acho que sim, mas demora meses pra pagar."),
        ],
    },
]

BAD_PATTERNS = [
    "analis", "identificação dos", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto", "dor aqui é",
    "tema novo é", "ponto central é", "vamos analisar",
    "baseado no contexto",
]


def run_one(scenario, mode="full"):
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
    print("LOTE 4 — 10 CENÁRIOS MODO FULL")
    print("=" * 70)

    passed = 0
    failed = 0

    for s in SCENARIOS:
        resp, elapsed = run_one(s, "full")
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
