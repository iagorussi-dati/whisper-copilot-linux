"""Lote 2: 10 cenários mais difíceis — edge cases de naturalidade."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

SCENARIOS = [
    # 11. Silêncio quase total — pouca informação
    {
        "name": "11. Quase silêncio — frase solta",
        "transcripts": [
            ("Pessoa1", "Tá."),
            ("Pessoa2", "Uhum."),
            ("Pessoa1", "Beleza então."),
        ],
    },
    # 12. Conversa em inglês
    {
        "name": "12. Conversa em inglês",
        "transcripts": [
            ("John", "Hey, did you see the new release?"),
            ("Sarah", "Yeah, it looks great. The performance improvements are insane."),
            ("John", "I'm worried about the breaking changes though."),
            ("Sarah", "True, we should test before upgrading."),
        ],
    },
    # 13. Alguém falando sozinho (monólogo)
    {
        "name": "13. Monólogo — pessoa pensando alto",
        "transcripts": [
            ("Iago", "Então, eu preciso terminar isso até sexta."),
            ("Iago", "Mas se eu fizer a parte do backend primeiro, o frontend fica mais fácil."),
            ("Iago", "Ou será que eu faço o frontend primeiro pra mostrar pro cliente?"),
            ("Iago", "Não, melhor backend. Se o backend tiver bug, o frontend não adianta."),
        ],
    },
    # 14. Conversa com muitas gírias
    {
        "name": "14. Gírias pesadas",
        "transcripts": [
            ("Amigo", "Mano, aquele rolê ontem foi brabo demais."),
            ("Iago", "Demais, cara. O DJ mandou muito, tava insano."),
            ("Amigo", "E aquela mina que chegou lá? Mó gata."),
            ("Iago", "Qual? A de cabelo cacheado? Ela é da firma do Léo."),
        ],
    },
    # 15. Reunião chata — alguém enrolando
    {
        "name": "15. Reunião chata — enrolação",
        "transcripts": [
            ("Gerente", "Então, como eu estava dizendo, a gente precisa alinhar as expectativas do projeto."),
            ("Gerente", "Porque, veja bem, o stakeholder principal tem uma visão que nem sempre converge com o que a gente tá entregando."),
            ("Gerente", "E aí a gente precisa fazer um realinhamento estratégico pra garantir que todos estejam na mesma página."),
            ("Gerente", "Vou marcar uma reunião pra discutir isso melhor."),
        ],
    },
    # 16. Alguém pedindo ajuda com código
    {
        "name": "16. Pedindo ajuda com código",
        "transcripts": [
            ("Colega", "Iago, tu sabe como faz pra pegar o último elemento de uma lista em Python?"),
            ("Iago", "lista[-1]."),
            ("Colega", "Ah, verdade. E se a lista tiver vazia?"),
            ("Iago", "Aí dá IndexError. Tem que checar antes ou usar try/except."),
        ],
    },
    # 17. Conversa sobre música
    {
        "name": "17. Música — recomendação",
        "transcripts": [
            ("Amigo", "Tu ouve o quê?"),
            ("Iago", "Ultimamente tô ouvindo muito lo-fi pra trabalhar. E tu?"),
            ("Amigo", "Eu tô numa vibe de rock alternativo. Arctic Monkeys, Tame Impala."),
            ("Iago", "Tame Impala é muito bom. Currents é um álbum perfeito."),
            ("Amigo", "Sim! Let It Happen é uma das melhores músicas que eu já ouvi."),
        ],
    },
    # 18. Alguém reclamando do trabalho
    {
        "name": "18. Reclamação do trabalho",
        "transcripts": [
            ("Colega", "Cara, tô de saco cheio. Terceira vez que mudam o escopo do projeto."),
            ("Iago", "Sei como é. Aqui também tão mudando tudo toda hora."),
            ("Colega", "E o pior é que ninguém avisa. Tu descobre quando já tá fazendo errado."),
            ("Iago", "Foda. Pelo menos tu tem autonomia pra decidir como fazer?"),
            ("Colega", "Mais ou menos. O gerente quer aprovar tudo."),
        ],
    },
    # 19. Conversa sobre comida/restaurante
    {
        "name": "19. Restaurante — onde comer",
        "transcripts": [
            ("Iago", "Vamos almoçar onde hoje?"),
            ("Colega", "Aquele japonês novo na esquina. Tu já foi?"),
            ("Iago", "Não, mas vi que o preço é salgado. 80 conto o rodízio."),
            ("Colega", "Mas dizem que vale a pena. O sashimi é fresco."),
            ("Iago", "Bora então. Mas se for ruim tu paga."),
        ],
    },
    # 20. Transcrição com erro/ruído — frases cortadas
    {
        "name": "20. Transcrição com ruído/erros",
        "transcripts": [
            ("Pessoa1", "Então a gente vai... [inaudível] ...na terça."),
            ("Pessoa2", "Tá, mas o... como é que chama... o relatório."),
            ("Pessoa1", "Isso, o relatório do... do mês passado."),
            ("Pessoa2", "Ah sim, eu mando amanhã. Pode ser?"),
        ],
    },
]

BAD_PATTERNS = [
    "analis", "identificação", "participantes", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto", "dor aqui",
    "tema novo", "ponto central", "em resumo", "vamos analisar",
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
        "response_mode": mode, "auto_response": True, "extra_context": "",
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
    print("LOTE 2 — 10 CENÁRIOS DIFÍCEIS (modo short)")
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
        preview = resp[:250].replace("\n", " ")
        print(f"   {preview}")
        if issues:
            print(f"   ⚠️ Padrões robóticos: {issues}")

    print(f"\n{'='*70}")
    print(f"RESULTADO: {passed}/10 passaram | {failed}/10 falharam")
    print(f"{'='*70}")
