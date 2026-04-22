"""Bateria de testes: Copiloto Pessoal em vários cenários."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api import Api

SCENARIOS = [
    # 1. Daily standup
    {
        "name": "Daily — atualização de tarefas",
        "instruction": "Me ajuda com umas dicas pra daily",
        "transcripts": [
            ("Iago", "Essa tarefa aí de ajustes finais da V1, faltam algumas coisas mas muito pequenas, de meia hora pra ver, bem rápido mesmo."),
            ("Iago", "Preciso fazer também a criação dos usuários para as meninas da Bolshoi."),
            ("Iago", "E aí com relação ao app, consegui fazer funcionar pra Windows, criei o executável, só que ainda tenho que criar mais vezes pra ele funcionar certinho."),
            ("Gui", "Beleza, fechou. Mais alguma coisa?"),
            ("Iago", "Não, é isso. Vou focar nisso hoje."),
        ],
    },
    # 2. Daily — outro colega falando
    {
        "name": "Daily — colega apresentando blocker",
        "instruction": "Me dá umas sugestões do que falar",
        "transcripts": [
            ("Bruno", "Cara, eu não atualizei o ClickUp, mas eu estou trabalhando em uma nova frente. TatiLab, botei o nome dessa frente."),
            ("Bruno", "Basicamente estamos criando um repositório de demonstrações para o comercial. Tipo demos prontas pra mostrar pro cliente."),
            ("Gui", "Legal. E o que tá travando?"),
            ("Bruno", "O problema é que preciso de acesso ao ambiente de staging pra gravar as demos, e o Josimar tá de férias."),
            ("Gui", "Entendi. Alguém mais pode liberar?"),
        ],
    },
    # 3. Bate-papo sobre futebol
    {
        "name": "Futebol — conversa informal",
        "instruction": "",
        "transcripts": [
            ("Iago", "Cara, tu viu o jogo do Grêmio ontem? Que absurdo."),
            ("Colega", "Vi, mano. Três a zero no primeiro tempo, aí tomou a virada no segundo."),
            ("Iago", "O Renato tem que sair, não aguento mais. O time não marca, não corre."),
            ("Colega", "Mas o problema é o elenco, cara. Não tem lateral direito decente."),
            ("Iago", "É, mas o Renato insiste em escalar o Fabio que não joga nada."),
        ],
    },
    # 4. Podcast — discussão sobre IA
    {
        "name": "Podcast — debate sobre IA no trabalho",
        "instruction": "",
        "transcripts": [
            ("Host", "Então, a pergunta é: a IA vai substituir programadores?"),
            ("Convidado", "Olha, eu acho que não substitui, mas muda completamente o perfil. O programador que não usar IA vai ficar pra trás."),
            ("Host", "Mas e o junior? Porque hoje o junior aprende fazendo código básico. Se a IA faz isso, como ele aprende?"),
            ("Convidado", "Esse é o ponto. O junior vai ter que aprender a pensar em arquitetura mais cedo. Menos código braçal, mais design de sistema."),
            ("Host", "Interessante. E você acha que as empresas vão contratar menos?"),
            ("Convidado", "Não necessariamente menos, mas diferente. Vai precisar de gente que saiba orquestrar IA, não só escrever código."),
        ],
    },
    # 5. Reunião com cliente — pedido de ajuda
    {
        "name": "Reunião — cliente com problema",
        "instruction": "Me ajuda a responder o cliente",
        "transcripts": [
            ("Cliente", "A gente tá com um problema sério. O sistema caiu três vezes essa semana e a gente não sabe o que tá causando."),
            ("Cliente", "O pessoal de infra falou que pode ser memória, mas não tem certeza."),
            ("Iago", "Entendi. Vocês têm algum monitoramento hoje? CloudWatch, Datadog, alguma coisa?"),
            ("Cliente", "Tem CloudWatch mas ninguém olha. A gente não configurou alarmes."),
        ],
    },
    # 6. Conversa casual — pedindo piada
    {
        "name": "Casual — pedindo piada",
        "instruction": "Faz uma piada sobre o que tão falando",
        "transcripts": [
            ("Iago", "Cara, passei o dia inteiro debugando um erro que era uma vírgula faltando."),
            ("Colega", "Clássico. Eu uma vez perdi 4 horas porque tinha um espaço invisível no YAML."),
            ("Iago", "YAML é o capeta. Indentação errada e tudo explode."),
        ],
    },
    # 7. Transcrição real do log (daily do Iago)
    {
        "name": "Daily real — transcrição do log",
        "instruction": "Me dá umas dicas rápidas",
        "transcripts": [
            ("Iago", "Essa tarefa aí de ajustes finais da V1, faltam algumas coisas, mas muito pequenas, de meia hora pra ver, bem rápido mesmo."),
            ("Iago", "Preciso fazer também a criação dos usuários para as meninas da Bolshoi."),
            ("Iago", "E aí com relação ao app, consegui fazer funcionar pra Windows, criei o executável."),
            ("Gui", "Os usuários que vão precisar agora no primeiro momento, ou se a gente tiver um canal ali em comum com elas, talvez solicitarem."),
            ("Gui", "Se a gente tem notícias ali, é por onde eu ia pegar."),
            ("Iago", "Beleza, fechou Gui."),
            ("Bruno", "Cara, eu não atualizei o ClickUp, mas eu estou trabalhando em uma nova frente. TatiLab, botei o nome dessa frente."),
            ("Bruno", "Basicamente estamos criando um repositório de demonstrações para o comercial."),
            ("Iago", "Feito o aplicativo funcionar pra Windows, consegui fazer, deu tudo certo. Daí eu tinha que criar o executável, eu já criei no caso, só que eu ainda tenho que criar mais vezes pra ele funcionar certinho."),
        ],
    },
]

MODES = ["short", "full"]


def run_scenario(scenario, mode):
    api = Api()
    results = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "conversa-natural.md")) as f:
        prompt = f.read()

    instruction = scenario.get("instruction", "")
    extra = instruction if instruction else ""

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
    print("BATERIA DE TESTES — COPILOTO PESSOAL")
    print("=" * 70)

    all_results = []

    for scenario in SCENARIOS:
        print(f"\n{'─'*70}")
        print(f"📌 {scenario['name']}")
        if scenario.get("instruction"):
            print(f"   Instrução: \"{scenario['instruction']}\"")
        print(f"{'─'*70}")

        for mode in MODES:
            resp, elapsed = run_scenario(scenario, mode)
            label = "⚡ Curta" if mode == "short" else "💬 Normal"
            print(f"\n  {label} ({elapsed:.1f}s):")
            for line in resp.split("\n"):
                if line.strip():
                    print(f"    {line.strip()}")
            all_results.append({
                "scenario": scenario["name"],
                "mode": mode,
                "time": elapsed,
                "response": resp,
                "length": len(resp),
            })

    # Summary
    print(f"\n{'='*70}")
    print("RESUMO")
    print(f"{'='*70}")
    print(f"{'Cenário':<40} {'Modo':<8} {'Tempo':>6} {'Chars':>6}")
    print(f"{'─'*40} {'─'*8} {'─'*6} {'─'*6}")
    for r in all_results:
        print(f"{r['scenario'][:40]:<40} {r['mode']:<8} {r['time']:>5.1f}s {r['length']:>5}")

    times = [r["time"] for r in all_results]
    print(f"\nMédia: {sum(times)/len(times):.1f}s | Min: {min(times):.1f}s | Max: {max(times):.1f}s")
