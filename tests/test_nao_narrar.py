"""Teste: copiloto NÃO deve narrar quem falou o quê."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from protocolo_runner import run_one

NARRATION_PATTERNS = [
    "pessoa 1 falou", "pessoa 2 falou", "pessoa 1 disse", "pessoa 2 disse",
    "pessoa 1 mencionou", "pessoa 2 mencionou",
    "iago falou", "iago disse", "iago mencionou",
    "colega falou", "colega disse", "colega mencionou",
    "narrador falou", "comentarista falou",
    "foi dito que", "foi mencionado que",
    "o primeiro falou", "o segundo falou",
    "um deles falou", "um deles disse",
    "na conversa, pessoa", "na conversa, iago",
]

SCENARIOS = [
    {"name": "Podcast futebol com speakers",
     "transcripts": [
         ("Narrador", "Autoriza o árbitro, tá rolando."),
         ("Comentarista", "O Arbeloa tem mais derrotas que o Xabi Alonso."),
         ("Comentarista", "Ele não deve ficar, pensando na reformulação do Florentino."),
         ("Narrador", "Vini Jr recebe, corta, chuta! Escanteio."),
     ]},
    {"name": "Daily com nomes",
     "transcripts": [
         ("Gui", "Bom dia. Iago, como tá?"),
         ("Iago", "Terminei a V1, falta deploy."),
         ("Bruno", "Travei no staging."),
         ("Gui", "Prioridade é deploy da V1."),
     ]},
    {"name": "Reunião com cliente",
     "transcripts": [
         ("Cliente", "O sistema caiu 3 vezes essa semana."),
         ("Cliente", "O pessoal de infra acha que é memória."),
         ("Iago", "Vocês têm monitoramento?"),
         ("Cliente", "Tem CloudWatch mas ninguém olha."),
     ]},
    {"name": "Entrevista com Pessoa 1/2",
     "transcripts": [
         ("Pessoa 1", "Eu jogava quando era menorzinho, lá na minha quebrada."),
         ("Pessoa 2", "Mano, aqui é a Arena da Morte."),
         ("Pessoa 1", "Nós entravamos lá, saímos no soco."),
         ("Pessoa 2", "Que loucura, e como era o campo?"),
     ]},
    {"name": "Podcast tech com Host/Convidado",
     "transcripts": [
         ("Host", "A IA vai substituir programadores?"),
         ("Convidado", "Não substitui, mas muda o perfil."),
         ("Host", "E o junior?"),
         ("Convidado", "Vai ter que aprender arquitetura mais cedo."),
     ]},
    {"name": "Bate-papo 3 pessoas",
     "transcripts": [
         ("Amigo1", "Tu viu o jogo ontem?"),
         ("Amigo2", "Vi, que absurdo. 3 a 0 no primeiro tempo."),
         ("Iago", "O Renato tem que sair."),
         ("Amigo1", "Concordo. O elenco tá fraco."),
         ("Amigo2", "Mas o problema é tático."),
     ]},
    {"name": "Reunião formal com Diretor",
     "transcripts": [
         ("Diretor", "Faturamento Q1 foi 2.3 milhões."),
         ("Diretor", "Maior crescimento no enterprise, 40% YoY."),
         ("Gerente", "Meta Q2 é 2.8 milhões."),
         ("Diretor", "Precisamos de 2 SDRs."),
     ]},
    {"name": "Conversa com speakers genéricos",
     "transcripts": [
         ("CONVERSA", "Então a gente vai na terça."),
         ("CONVERSA", "Tá, mas o relatório do mês passado."),
         ("CONVERSA", "Ah sim, eu mando amanhã."),
     ]},
    {"name": "Stream com streamer",
     "transcripts": [
         ("Streamer", "Vou de AWP no meio."),
         ("Streamer", "Peguei dois! Ace incoming?"),
         ("Streamer", "Não, morri pro cara de pistola."),
     ]},
    {"name": "Discovery com Reginaldo",
     "transcripts": [
         ("Reginaldo", "A gente tem 3 servidores on-premise."),
         ("Consultor", "Quanto vocês gastam hoje?"),
         ("Reginaldo", "Uns 15 mil por mês."),
         ("Reginaldo", "E o site de ingressos tem picos absurdos."),
     ]},
]

if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: COPILOTO NÃO DEVE NARRAR")
    print("=" * 70)

    passed = 0
    for s in SCENARIOS:
        resp, elapsed = run_one(s["transcripts"], mode="short", behavior="conversa")
        resp_lower = resp.lower()

        narrations = [p for p in NARRATION_PATTERNS if p in resp_lower]
        ok = len(narrations) == 0

        if ok:
            passed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {s['name']} ({elapsed:.1f}s)")
        print(f"   {resp[:200]}")
        if narrations:
            print(f"   ⚠️ NARROU: {narrations}")

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/10")
