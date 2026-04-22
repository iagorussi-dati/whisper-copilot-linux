"""Lote 2: Edge Cases — situações incomuns."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Silêncio — 1 palavra", "transcripts": [("Pessoa", "Tá.")]},
    {"name": "Transcrição com ruído", "transcripts": [
        ("Pessoa1", "Então a gente vai... [inaudível] ...na terça."),
        ("Pessoa2", "Tá, mas o... como é que chama... o relatório."),
        ("Pessoa1", "Ah sim, eu mando amanhã."),
    ]},
    {"name": "Inglês puro", "transcripts": [
        ("John", "The deployment failed again. Third time this week."),
        ("Sarah", "Did you check the logs? Might be a memory issue."),
        ("John", "Yeah, OOM killed. Need to bump the limits."),
    ]},
    {"name": "Portunhol", "transcripts": [
        ("Pessoa1", "Hola, necesito ayuda con el proyecto."),
        ("Pessoa2", "Claro, me manda os detalhes por email."),
        ("Pessoa1", "Bueno, te mando ahora mismo."),
    ]},
    {"name": "Monólogo — pensando alto", "transcripts": [
        ("Iago", "Preciso terminar isso até sexta."),
        ("Iago", "Se fizer backend primeiro, frontend fica mais fácil."),
        ("Iago", "Ou será que mostro pro cliente antes?"),
        ("Iago", "Não, melhor backend. Se tiver bug, frontend não adianta."),
    ]},
    {"name": "Conversa desconectada", "transcripts": [
        ("P1", "Gatos são melhores que cachorros."),
        ("P2", "Ontem comi o melhor hambúrguer da vida."),
        ("P1", "Meu vizinho reforma a casa às 7 da manhã."),
        ("P2", "Preciso trocar o pneu do carro."),
    ]},
    {"name": "Transcrição longa — 15 falas", "transcripts": [
        ("A", "Bom dia."), ("B", "Bom dia."), ("C", "Oi."),
        ("A", "Lançamento dia 15."), ("B", "Não vamos conseguir. Falta pagamento."),
        ("C", "Terminei integração ontem."), ("B", "Sério? Falta teste E2E."),
        ("A", "Quem faz?"), ("C", "Eu faço. Preciso de staging."),
        ("A", "Segundo ponto: PDF export."), ("B", "Simples, 2 dias."),
        ("A", "Terceiro: contratar dev."), ("B", "Concordo, tamo sobrecarregado."),
        ("C", "Conheço alguém."), ("A", "Manda o contato."),
    ]},
    {"name": "Só música/ruído", "transcripts": [
        ("Audio", "la la la na na na"),
        ("Audio", "tum tum tum pá"),
    ]},
    {"name": "Repetição — mesma frase", "transcripts": [
        ("Pessoa", "Tá me ouvindo?"),
        ("Pessoa", "Tá me ouvindo?"),
        ("Pessoa", "Alô? Tá me ouvindo?"),
    ]},
    {"name": "Números e siglas", "transcripts": [
        ("Dev", "O erro é HTTP 502 no endpoint /api/v2/users."),
        ("Dev", "O pod tá com 256Mi de RAM e 0.5 vCPU."),
        ("Dev", "Precisa subir pra 512Mi e 1 vCPU."),
    ]},
]

if __name__ == "__main__":
    run_lote("2. Edge Cases", SCENARIOS, mode="short", behavior="conversa")
