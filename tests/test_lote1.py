"""Lote 1: 10 cenários diversos — testar naturalidade do Copiloto Pessoal."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

SCENARIOS = [
    # 1. Narração de futebol ao vivo (o que falhou antes)
    {
        "name": "1. Narração futebol ao vivo",
        "instruction": "",
        "transcripts": [
            ("Narrador", "Autoriza o árbitro, tá rolando na tela do Disney Plus."),
            ("Comentarista", "Mas o Arbeloa em bem menos jogos já tem mais derrotas do que teve o Xabi Alonso na sua passagem pelo Real Madrid."),
            ("Comentarista", "Ele não deve ficar né, pensando nessa reformulação que pensa o Florentino Pérez."),
            ("Narrador", "Blanco, aí o capitão do Alavés já faz o lançamento às costas, é boa a bola, já ganhando a marcação."),
        ],
    },
    # 2. Fofoca de escritório
    {
        "name": "2. Fofoca de escritório",
        "instruction": "",
        "transcripts": [
            ("Colega", "Tu viu que o Marcos pediu demissão?"),
            ("Iago", "Sério? Quando?"),
            ("Colega", "Ontem. Parece que ele recebeu uma proposta de uma startup pagando o dobro."),
            ("Iago", "Caramba. E o chefe já sabe?"),
            ("Colega", "Sabe, e tá puto. Falou que não vai cobrir."),
        ],
    },
    # 3. Alguém explicando receita de bolo
    {
        "name": "3. Receita de bolo",
        "instruction": "",
        "transcripts": [
            ("Mãe", "Então, primeiro tu bate as claras em neve bem firme."),
            ("Mãe", "Depois mistura a gema com o açúcar e vai adicionando a farinha aos poucos."),
            ("Mãe", "O segredo é não bater demais senão o bolo fica solado."),
            ("Iago", "E o forno, que temperatura?"),
            ("Mãe", "180 graus, pré-aquecido. Uns 40 minutos."),
        ],
    },
    # 4. Discussão sobre série de TV
    {
        "name": "4. Série de TV — spoiler",
        "instruction": "",
        "transcripts": [
            ("Amigo", "Cara, terminei The Last of Us ontem. Que final."),
            ("Iago", "Não me dá spoiler, tô no episódio 5 ainda."),
            ("Amigo", "Relaxa, não vou falar nada. Mas prepara o emocional."),
            ("Iago", "Tá me assustando. É pior que o episódio 3?"),
            ("Amigo", "Diferente. Mas igualmente pesado."),
        ],
    },
    # 5. Planejamento de viagem
    {
        "name": "5. Planejamento de viagem",
        "instruction": "",
        "transcripts": [
            ("Iago", "Tô pensando em ir pra Floripa no feriado. Tu vai?"),
            ("Amigo", "Quero ir sim. Mas tá caro demais hotel lá."),
            ("Iago", "Vi um Airbnb perto da Joaquina por 200 a diária. Racha no meio."),
            ("Amigo", "Fecha. E transporte? Tu vai de carro?"),
            ("Iago", "Acho que sim, umas 5 horas de Joinville."),
        ],
    },
    # 6. Reclamação de internet
    {
        "name": "6. Reclamação de internet lenta",
        "instruction": "",
        "transcripts": [
            ("Iago", "Mano, minha internet tá uma merda hoje. Caiu 3 vezes na call."),
            ("Colega", "A minha também tá ruim. Acho que é a operadora."),
            ("Iago", "Vou ligar lá e reclamar. Pago 200 conto por mês pra isso."),
            ("Colega", "Troca pra fibra da outra operadora. Eu troquei e nunca mais tive problema."),
        ],
    },
    # 7. Conversa sobre academia/treino
    {
        "name": "7. Treino na academia",
        "instruction": "",
        "transcripts": [
            ("Iago", "Comecei a fazer supino inclinado com halteres. Tô sentindo muito mais o peitoral."),
            ("Amigo", "Quantos quilos?"),
            ("Iago", "16 cada lado. Tô subindo devagar."),
            ("Amigo", "Boa. Eu prefiro o supino reto com barra, mas inclinado com halter é muito bom pra parte superior."),
            ("Iago", "É, e o ombro não dói tanto quanto na barra."),
        ],
    },
    # 8. Alguém contando história engraçada
    {
        "name": "8. História engraçada",
        "instruction": "",
        "transcripts": [
            ("Colega", "Cara, ontem eu fui no mercado e esqueci a carteira no carro."),
            ("Colega", "Aí eu voltei pro carro, peguei a carteira, voltei pro mercado e esqueci o que ia comprar."),
            ("Colega", "Fiquei 10 minutos andando nos corredores tentando lembrar."),
            ("Iago", "E lembrou?"),
            ("Colega", "Não. Comprei um monte de besteira e quando cheguei em casa lembrei: era leite."),
        ],
    },
    # 9. Discussão política leve
    {
        "name": "9. Discussão sobre economia",
        "instruction": "",
        "transcripts": [
            ("Colega", "O dólar subiu de novo. Tá quase 6 reais."),
            ("Iago", "É foda. Meu teclado que eu queria comprar era 400 reais, agora tá 600."),
            ("Colega", "Tudo importado tá absurdo. Até comida tá cara."),
            ("Iago", "O arroz dobrou de preço em dois anos."),
        ],
    },
    # 10. Conversa completamente aleatória/desconectada
    {
        "name": "10. Conversa desconectada/aleatória",
        "instruction": "",
        "transcripts": [
            ("Pessoa1", "Eu acho que gatos são melhores que cachorros."),
            ("Pessoa2", "Ontem eu comi o melhor hambúrguer da minha vida."),
            ("Pessoa1", "Meu vizinho tá reformando a casa às 7 da manhã."),
            ("Pessoa2", "Tu já assistiu aquele documentário sobre polvos?"),
            ("Pessoa1", "Preciso trocar o pneu do carro."),
        ],
    },
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


# Critérios de avaliação
BAD_PATTERNS = [
    "analis",           # "analisando", "análise"
    "identificação",
    "participantes",
    "trecho mais recente",
    "contexto da conversa",
    "vou acompanhar como copiloto",
    "dor aqui",
    "tema novo",
    "ponto central",
    "em resumo",
    "vamos analisar",
]


if __name__ == "__main__":
    print("=" * 70)
    print("LOTE 1 — 10 CENÁRIOS DIVERSOS (modo short)")
    print("=" * 70)

    passed = 0
    failed = 0

    for s in SCENARIOS:
        resp, elapsed = run_one(s, "short")
        resp_lower = resp.lower()

        # Check for robotic patterns
        issues = [p for p in BAD_PATTERNS if p in resp_lower]
        ok = len(issues) == 0
        if ok:
            passed += 1
        else:
            failed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {s['name']} ({elapsed:.1f}s)")
        # Show first 200 chars
        preview = resp[:200].replace("\n", " ")
        print(f"   {preview}")
        if issues:
            print(f"   ⚠️ Padrões robóticos: {issues}")

    print(f"\n{'='*70}")
    print(f"RESULTADO: {passed}/10 passaram | {failed}/10 falharam")
    print(f"{'='*70}")
