"""Teste: chat com instrução — não deve narrar, deve responder direto."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

NARRATION_PATTERNS = [
    "pessoa 1", "pessoa 2", "participante", "foi mencionado",
    "foi dito que", "na conversa,", "o usuário perguntou",
    "responda essa pergunta", "a pergunta do usuário",
]

SCENARIOS = [
    # Podcast mágica/entretenimento
    {"name": "Podcast mágica — qual é o truque?",
     "instruction": "qual é a mágica do dado?",
     "transcripts": [
         ("Pessoa 1", "E eu fiquei feliz que não só o nosso vídeo deu bom."),
         ("Pessoa 2", "É, então, eu..."),
         ("Pessoa 1", "Isso que eu fico feliz, tá ligado?"),
         ("Pessoa 2", "A galera pirou na mágica do dado, né?"),
         ("Pessoa 1", "Aí eu falei, mano, vou fazer de novo no próximo vídeo."),
     ]},
    # Podcast história de vida
    {"name": "Podcast vida — como ele começou?",
     "instruction": "como ele começou a carreira?",
     "transcripts": [
         ("Pessoa 1", "Eu trabalhava da manhã até de madrugada. Pra receber 50 conto de diária."),
         ("Pessoa 2", "E lá ia vários empresários de futebol."),
         ("Pessoa 1", "Na época eu já tava querendo cantar, mas também queria jogar bola."),
         ("Pessoa 1", "Aí eu falei pro cara, me dá uma chance aí."),
         ("Pessoa 2", "E o cara falou, faz um DVD que eu te levo pra gravar."),
     ]},
    # Podcast tech
    {"name": "Podcast tech — o que é Kubernetes?",
     "instruction": "explica o que é Kubernetes de forma simples",
     "transcripts": [
         ("Host", "Então o Kubernetes é overkill pra maioria das startups?"),
         ("Convidado", "Total. Se tu tem 3 microserviços, roda num ECS."),
         ("Convidado", "Kubernetes é pra quando tu tem 50 serviços e precisa de auto-scaling granular."),
     ]},
    # Podcast futebol
    {"name": "Podcast futebol — quem jogou melhor?",
     "instruction": "quem jogou melhor no jogo?",
     "transcripts": [
         ("Narrador", "Vini Jr recebe na esquerda, corta pra dentro, chuta!"),
         ("Comentarista", "O Vini tá tentando resolver sozinho. Precisa tocar mais."),
         ("Narrador", "Bellingham recebe, toca pro Rodrygo. Rodrygo finaliza, gol!"),
         ("Comentarista", "Que jogada coletiva. Bellingham e Rodrygo combinaram perfeitamente."),
     ]},
    # Podcast investimentos
    {"name": "Podcast investimentos — onde investir?",
     "instruction": "onde ele recomenda investir?",
     "transcripts": [
         ("Host", "Renda fixa ou variável em 2026?"),
         ("Convidado", "Com a Selic a 14%, renda fixa tá pagando muito bem."),
         ("Convidado", "CDB de banco médio tá dando 120% do CDI."),
         ("Host", "E quem quer mais risco?"),
         ("Convidado", "FIIs descontados. Alguns pagando 1% ao mês."),
     ]},
    # Podcast comédia
    {"name": "Podcast comédia — qual a piada?",
     "instruction": "qual foi a piada?",
     "transcripts": [
         ("Comediante", "Aí o cara chega no bar e pede uma cerveja."),
         ("Comediante", "O garçom fala: a gente só tem água."),
         ("Comediante", "O cara: então me vê uma água com gás, pelo menos parece cerveja."),
         ("Host", "Mano, essa é boa demais."),
     ]},
    # Podcast ciência
    {"name": "Podcast ciência — como funciona?",
     "instruction": "como funciona o buraco negro?",
     "transcripts": [
         ("Cientista", "Um buraco negro é uma região do espaço onde a gravidade é tão forte que nada escapa."),
         ("Cientista", "Nem a luz consegue sair. Por isso é negro."),
         ("Host", "E o que acontece se alguém cair num?"),
         ("Cientista", "Espaguetificação. Seu corpo seria esticado como um espaguete."),
     ]},
    # Entrevista emprego
    {"name": "Entrevista — qual o salário?",
     "instruction": "qual salário ele ofereceu?",
     "transcripts": [
         ("Entrevistador", "A faixa salarial pra essa posição é entre 8 e 12 mil."),
         ("Entrevistador", "Depende da experiência e do resultado da avaliação técnica."),
         ("Iago", "Entendi. E tem benefícios?"),
         ("Entrevistador", "Plano de saúde, VR de 40 reais por dia, e home office 3 dias."),
     ]},
    # Aula online
    {"name": "Aula — qual a fórmula?",
     "instruction": "qual a fórmula que ele explicou?",
     "transcripts": [
         ("Professor", "A fórmula de Bhaskara é x igual a menos b mais ou menos raiz de b ao quadrado menos 4ac, tudo dividido por 2a."),
         ("Professor", "Ela serve pra resolver equações do segundo grau."),
         ("Aluno", "E quando o delta é negativo?"),
         ("Professor", "Não tem raiz real. A parábola não toca o eixo x."),
     ]},
    # Podcast random — pergunta vaga
    {"name": "Podcast random — do que eles tão falando?",
     "instruction": "do que eles tão falando?",
     "transcripts": [
         ("Pessoa 1", "Mano, aquele lugar é insano. A vista de cima é surreal."),
         ("Pessoa 2", "Eu fui ano passado. Fiquei 3 dias e não queria voltar."),
         ("Pessoa 1", "O pôr do sol de lá é o mais bonito que eu já vi."),
         ("Pessoa 2", "E a comida? Mano, o peixe fresco de lá é outro nível."),
     ]},
]


def run_chat_with_instruction(scenario):
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
        "response_mode": "short", "auto_response": False, "extra_context": "",
    }
    api.start_meeting(config)

    for speaker, text in scenario["transcripts"]:
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        api._transcript.append(entry)
        api._chat_history.append({"event": "transcript", "data": entry})

    t0 = time.time()
    api.submit_recording(scenario["instruction"])
    for _ in range(25):
        time.sleep(1)
        if results:
            break
    elapsed = time.time() - t0
    api._hotkey_stop.set()
    return results[-1] if results else "❌ Sem resposta", elapsed


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: CHAT COM INSTRUÇÃO — NÃO NARRAR")
    print("=" * 70)

    passed = 0
    for s in SCENARIOS:
        resp, elapsed = run_chat_with_instruction(s)
        resp_lower = resp.lower()

        narrations = [p for p in NARRATION_PATTERNS if p in resp_lower]
        ok = len(narrations) == 0 and not resp.startswith("❌")

        if ok:
            passed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {s['name']} ({elapsed:.1f}s)")
        print(f"   📝 \"{s['instruction']}\"")
        print(f"   🤖 {resp[:250]}")
        if narrations:
            print(f"   ⚠️ NARROU: {narrations}")

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/10")
