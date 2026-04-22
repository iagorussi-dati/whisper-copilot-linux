"""Lote 3: Sem instrução — auto_response=true, copiloto decide sozinho."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Daily — sem instrução", "extra": "Estou numa daily.",
     "transcripts": [
         ("Gui", "Iago, como tá?"), ("Iago", "Terminei a V1."),
         ("Gui", "Bruno?"), ("Bruno", "Travei no staging."),
     ]},
    {"name": "Futebol — sem instrução", "extra": "Assistindo jogo no YouTube.",
     "transcripts": [
         ("Narrador", "Vini Jr recebe na esquerda, corta pra dentro, chuta!"),
         ("Narrador", "Desviou na zaga, escanteio."),
         ("Comentarista", "O Vini tá tentando resolver sozinho."),
     ]},
    {"name": "Podcast — sem instrução", "extra": "Ouvindo podcast.",
     "transcripts": [
         ("Host", "A IA vai substituir programadores?"),
         ("Convidado", "Não substitui, mas muda o perfil. Quem não usar IA fica pra trás."),
     ]},
    {"name": "Reunião cliente — sem instrução", "extra": "Reunião com cliente.",
     "transcripts": [
         ("Cliente", "O sistema caiu 3 vezes essa semana."),
         ("Cliente", "O pessoal de infra acha que é memória."),
         ("Iago", "Vocês têm monitoramento?"),
         ("Cliente", "Tem CloudWatch mas ninguém olha."),
     ]},
    {"name": "Bate-papo — sem instrução", "extra": "",
     "transcripts": [
         ("Colega", "Meu cachorro comeu meu fone."),
         ("Iago", "De novo? Quantos já foram?"),
         ("Colega", "Terceiro. Acho que gosta de borracha."),
     ]},
    {"name": "Aula online — sem instrução", "extra": "Assistindo aula online.",
     "transcripts": [
         ("Professor", "O conceito de overfitting é quando o modelo decora os dados."),
         ("Professor", "Pra evitar: regularização, dropout, mais dados."),
         ("Aluno", "Qual a mais usada?"),
         ("Professor", "Dropout e early stopping."),
     ]},
    {"name": "Entrevista — sem instrução", "extra": "Estou numa entrevista de emprego.",
     "transcripts": [
         ("Entrevistador", "Me conta sobre um projeto desafiador."),
         ("Iago", "Criei um copiloto de reuniões com IA em tempo real."),
         ("Entrevistador", "Quais tecnologias?"),
         ("Iago", "Groq Whisper, Bedrock, pywebview."),
     ]},
    {"name": "Documentário — sem instrução", "extra": "Assistindo documentário.",
     "transcripts": [
         ("Narrador", "As baleias jubarte viajam 8 mil km por ano."),
         ("Narrador", "Saem da Antártica e vão até o nordeste do Brasil."),
     ]},
    {"name": "Debate político — sem instrução", "extra": "",
     "transcripts": [
         ("Pessoa1", "O dólar subiu de novo. Quase 6 reais."),
         ("Pessoa2", "Tudo importado tá absurdo."),
         ("Pessoa1", "O arroz dobrou de preço em dois anos."),
     ]},
    {"name": "Silêncio total — sem instrução", "extra": "",
     "transcripts": [("Pessoa", "Uhum."), ("Pessoa", "Tá.")]},
]

if __name__ == "__main__":
    run_lote("3. Sem Instrução", SCENARIOS, mode="short", behavior="conversa")
