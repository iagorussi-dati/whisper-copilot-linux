"""Lote 5: Contexto extra — campo de configuração influencia resposta."""
from protocolo_runner import run_lote

T = [("Dev", "O deploy falhou. Erro 502."), ("Dev", "Logs mostram timeout no banco."), ("Dev", "Pool de conexões cheio.")]

SCENARIOS = [
    {"name": "Contexto: daily", "extra": "Estou numa daily do time.", "transcripts": T},
    {"name": "Contexto: sou estagiário", "extra": "Sou estagiário, não entendo muito.", "transcripts": T},
    {"name": "Contexto: sou senior", "extra": "Sou dev senior, quero resposta técnica.", "transcripts": T},
    {"name": "Contexto: entrevista", "extra": "Estou numa entrevista de emprego.", "transcripts": [
        ("Entrevistador", "Como você lida com pressão?"),
        ("Iago", "Eu priorizo as tarefas e foco no que é mais urgente."),
    ]},
    {"name": "Contexto: YouTube futebol", "extra": "Assistindo jogo de futebol no YouTube.", "transcripts": [
        ("Narrador", "Gol! Bellingham marca de cabeça!"),
        ("Comentarista", "Que jogada ensaiada. Cruzamento perfeito do Vini."),
    ]},
    {"name": "Contexto: podcast história", "extra": "Ouvindo podcast sobre história do Brasil.", "transcripts": [
        ("Historiador", "A proclamação da República foi um golpe militar."),
        ("Historiador", "O povo assistiu sem entender o que acontecia."),
    ]},
    {"name": "Contexto: cliente não técnico", "extra": "O cliente não entende de tecnologia.", "transcripts": [
        ("Cliente", "O site tá lento. O que tá acontecendo?"),
        ("Iago", "Pode ser o servidor sobrecarregado."),
    ]},
    {"name": "Contexto: apresentação pro chefe", "extra": "Estou apresentando resultados pro diretor.", "transcripts": [
        ("Iago", "O projeto reduziu o tempo de deploy de 2 horas pra 15 minutos."),
        ("Diretor", "Quanto isso economiza por mês?"),
    ]},
    {"name": "Contexto: Twitch Valorant", "extra": "Assistindo stream de Valorant na Twitch.", "transcripts": [
        ("Streamer", "Ace! Cinco kills no round."),
        ("Streamer", "Chat tá maluco. Vou de Jett de novo."),
    ]},
    {"name": "Contexto: aula culinária", "extra": "Assistindo aula de culinária no YouTube.", "transcripts": [
        ("Chef", "O segredo do risoto é o caldo quente. Nunca coloque frio."),
        ("Chef", "Manteiga e parmesão no final. Isso dá a cremosidade."),
    ]},
]

if __name__ == "__main__":
    run_lote("5. Contexto Extra", SCENARIOS, mode="short", behavior="conversa")
