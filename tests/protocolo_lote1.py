"""Lote 1: Happy Path — cenários comuns do dia a dia."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Daily standup", "extra": "Estou numa daily do time.",
     "transcripts": [
         ("Gui", "Bom dia. Iago, como tá?"),
         ("Iago", "Terminei a V1, só falta deploy."),
         ("Gui", "Beleza. Bruno?"),
         ("Bruno", "Tô com o TatiLab, travei no acesso ao staging."),
         ("Gui", "Prioridade é deploy da V1."),
     ]},
    {"name": "Reunião de sprint", "extra": "Reunião de planejamento de sprint.",
     "transcripts": [
         ("PM", "Temos 15 pontos de capacidade essa sprint."),
         ("PM", "As tasks prioritárias são: migração do banco, testes E2E, e o fix do login."),
         ("Dev", "A migração sozinha já são uns 8 pontos."),
         ("PM", "Então vamos priorizar migração e login. Testes ficam pra próxima."),
     ]},
    {"name": "1:1 com gestor", "extra": "1:1 com meu gestor.",
     "transcripts": [
         ("Gestor", "Como tu tá se sentindo no time?"),
         ("Iago", "Bem, tô gostando. Mas queria mais autonomia nos projetos."),
         ("Gestor", "Entendo. Vou te dar o lead do próximo projeto."),
     ]},
    {"name": "Sync rápido", "extra": "",
     "transcripts": [
         ("Colega", "Iago, tu já subiu o PR?"),
         ("Iago", "Subi agora. Tá pronto pra review."),
         ("Colega", "Beleza, vou olhar depois do almoço."),
     ]},
    {"name": "Bate-papo almoço", "extra": "",
     "transcripts": [
         ("Colega", "Vamos no japonês hoje?"),
         ("Iago", "Bora. Mas tá caro lá."),
         ("Colega", "Dizem que vale a pena. Sashimi fresco."),
         ("Iago", "Fechou. Se for ruim tu paga."),
     ]},
    {"name": "YouTube podcast tech", "extra": "Assistindo podcast de tech no YouTube.",
     "transcripts": [
         ("Host", "Qual linguagem aprender em 2026?"),
         ("Convidado", "Python continua dominando. Mas Rust tá crescendo muito em infra."),
         ("Host", "E JavaScript?"),
         ("Convidado", "Não vai morrer nunca. Mas TypeScript é o padrão agora."),
     ]},
    {"name": "Stream Twitch", "extra": "Assistindo stream de CS2 na Twitch.",
     "transcripts": [
         ("Streamer", "Vou de AWP no meio. Se der errado a culpa é do chat."),
         ("Streamer", "Peguei dois! Ace incoming?"),
         ("Streamer", "Não, morri pro cara de pistola. Vergonha."),
     ]},
    {"name": "Reunião com cliente", "extra": "Reunião com cliente.",
     "transcripts": [
         ("Cliente", "A gente precisa que o sistema aguente 10 mil usuários simultâneos."),
         ("Iago", "Entendi. Hoje vocês têm quantos?"),
         ("Cliente", "Uns 2 mil no pico. Mas vai crescer rápido."),
     ]},
    {"name": "Conversa sobre série", "extra": "",
     "transcripts": [
         ("Amigo", "Terminei Severance. Que série doida."),
         ("Iago", "Tô no episódio 3. Sem spoiler."),
         ("Amigo", "Relaxa. Mas prepara a cabeça."),
     ]},
    {"name": "Planejamento viagem", "extra": "",
     "transcripts": [
         ("Amigo", "Bora pra Floripa no feriado?"),
         ("Iago", "Bora. Vi Airbnb por 200 a diária."),
         ("Amigo", "Fecha. Vamos de carro?"),
         ("Iago", "Sim, 5 horas de Joinville."),
     ]},
]

if __name__ == "__main__":
    run_lote("1. Happy Path", SCENARIOS, mode="short", behavior="conversa")
