"""Lote 5: 10 cenários extremos — stress test final."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

SCENARIOS = [
    # 41. Uma única palavra
    {"name": "41. Uma palavra só", "instruction": "", "transcripts": [("Pessoa1", "Oi.")]},
    # 42. Transcrição gigante — 15 falas
    {
        "name": "42. Transcrição longa — 15 falas",
        "instruction": "",
        "transcripts": [
            ("A", "Bom dia pessoal."), ("B", "Bom dia."), ("C", "Oi."),
            ("A", "Vamos começar pela pauta de hoje."),
            ("A", "Primeiro ponto: o lançamento do produto tá marcado pra dia 15."),
            ("B", "Eu acho que a gente não vai conseguir. Falta o módulo de pagamento."),
            ("C", "Eu terminei a integração com o gateway ontem."),
            ("B", "Sério? Então falta só o teste end-to-end."),
            ("A", "Ótimo. Quem pode fazer o teste?"),
            ("C", "Eu faço. Preciso de acesso ao ambiente de staging."),
            ("A", "Segundo ponto: o cliente pediu uma feature nova. Exportar relatório em PDF."),
            ("B", "Isso é simples. Uso uma lib e faço em 2 dias."),
            ("A", "Beleza. Terceiro ponto: a gente precisa contratar mais um dev."),
            ("B", "Concordo. Tamo sobrecarregado."),
            ("C", "Eu conheço alguém que tá procurando. Posso indicar."),
        ],
    },
    # 43. Idioma misturado (portunhol)
    {
        "name": "43. Portunhol",
        "instruction": "",
        "transcripts": [
            ("Pessoa1", "Hola, como estás?"),
            ("Pessoa2", "Bien, y tú? Tudo certo por aqui."),
            ("Pessoa1", "Necesito que me ayudes con el proyecto."),
            ("Pessoa2", "Claro, me manda los detalles por email."),
        ],
    },
    # 44. Conversa sobre morte/luto (sensível)
    {
        "name": "44. Tema sensível — luto",
        "instruction": "",
        "transcripts": [
            ("Colega", "Cara, meu avô faleceu semana passada."),
            ("Iago", "Poxa, sinto muito. Vocês eram próximos?"),
            ("Colega", "Muito. Ele me criou praticamente."),
        ],
    },
    # 45. Alguém mentindo/exagerando
    {
        "name": "45. Exagero óbvio",
        "instruction": "",
        "transcripts": [
            ("Colega", "Eu fiz 200 flexões hoje de manhã."),
            ("Iago", "200? Sério?"),
            ("Colega", "Sim, fácil. E depois corri 10km."),
            ("Iago", "Tu é o Superman então."),
        ],
    },
    # 46. Conversa técnica densa
    {
        "name": "46. Técnico denso — Kubernetes",
        "instruction": "",
        "transcripts": [
            ("Dev1", "O pod tá em CrashLoopBackOff. O liveness probe tá falhando."),
            ("Dev2", "Qual o endpoint do probe?"),
            ("Dev1", "Slash health. Mas o container demora 30 segundos pra subir e o probe começa em 10."),
            ("Dev2", "Aumenta o initialDelaySeconds pra 60."),
            ("Dev1", "Já tentei. Agora tá dando OOMKilled."),
            ("Dev2", "Então o limite de memória tá baixo. Quanto tá?"),
            ("Dev1", "256Mi."),
            ("Dev2", "Sobe pra 512Mi e vê se resolve."),
        ],
    },
    # 47. Conversa sobre jogo/game
    {
        "name": "47. Game — Elden Ring",
        "instruction": "",
        "transcripts": [
            ("Amigo", "Cara, eu morri pro Malenia 47 vezes."),
            ("Iago", "Só 47? Eu morri umas 100."),
            ("Amigo", "Qual build tu usou?"),
            ("Iago", "Sangramento com katana. Demora mas funciona."),
            ("Amigo", "Eu tô de mago. Ela desvia de tudo."),
        ],
    },
    # 48. Conversa sobre criança/filho
    {
        "name": "48. Filho — escola",
        "instruction": "",
        "transcripts": [
            ("Colega", "Meu filho não quer ir pra escola. Todo dia é uma briga."),
            ("Iago", "Quantos anos ele tem?"),
            ("Colega", "7. Diz que não gosta da professora."),
            ("Iago", "Já conversou com a professora?"),
            ("Colega", "Marquei reunião pra semana que vem."),
        ],
    },
    # 49. Conversa sobre notícia/atualidade
    {
        "name": "49. Notícia — terremoto",
        "instruction": "",
        "transcripts": [
            ("Colega", "Tu viu o terremoto no Japão?"),
            ("Iago", "Vi. 7.2 na escala Richter. Assustador."),
            ("Colega", "Eles são preparados pra isso mas mesmo assim teve estragos."),
            ("Iago", "Os prédios lá são feitos pra aguentar. Aqui no Brasil ia ser um desastre."),
        ],
    },
    # 50. Múltiplos snapshots — segundo snapshot da mesma conversa
    {
        "name": "50. Segundo snapshot — continuação",
        "instruction": "",
        "transcripts": [
            ("Iago", "Então, voltando ao assunto do deploy."),
            ("Colega", "Sim, eu testei e tá funcionando no staging."),
            ("Iago", "Beleza. Vou subir pra produção então."),
            ("Colega", "Espera, faz um backup antes."),
            ("Iago", "Boa. Vou fazer."),
        ],
    },
]

BAD_PATTERNS = [
    "analis", "identificação dos", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto", "dor aqui é",
    "tema novo é", "ponto central é", "vamos analisar",
    "baseado no contexto",
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
    print("LOTE 5 — 10 CENÁRIOS EXTREMOS (modo short)")
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
    print(f"\nTOTAL GERAL: {passed + 40}/50")
