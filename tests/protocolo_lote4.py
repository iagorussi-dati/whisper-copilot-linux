"""Lote 4: Com instrução — usuário pede algo específico."""
from protocolo_runner import run_lote

SCENARIOS = [
    {"name": "Resume pra mim", "instruction": "resume o que falaram",
     "transcripts": [
         ("PM", "Sprint termina sexta. 3 tasks abertas."),
         ("PM", "Iago com V1, Bruno com TatiLab, Mari com testes."),
         ("PM", "Prioridade: V1 primeiro."),
     ]},
    {"name": "Me faz rir", "instruction": "faz uma piada sobre o que tão falando",
     "transcripts": [
         ("Colega", "O deploy de sexta deu ruim de novo."),
         ("Iago", "Quem fez deploy na sexta?"),
         ("Colega", "Eu."),
     ]},
    {"name": "Traduz pro inglês", "instruction": "traduz o que o cliente falou pro inglês",
     "transcripts": [
         ("Cliente", "Precisamos de escalabilidade automática e alta disponibilidade."),
         ("Cliente", "Orçamento de 50 mil por mês, prazo de 3 meses."),
     ]},
    {"name": "O que perguntar?", "instruction": "o que eu deveria perguntar agora?",
     "transcripts": [
         ("Cliente", "A gente tem 3 servidores on-premise e 500GB de Postgres."),
         ("Cliente", "Queremos migrar tudo pra AWS."),
     ]},
    {"name": "Me dá argumentos", "instruction": "me dá argumentos pra negociar aumento",
     "transcripts": [
         ("Chefe", "Sobre o aumento, a empresa não tá num momento bom."),
         ("Iago", "Entendo, mas assumi muito mais responsabilidade."),
         ("Chefe", "Sei, mas orçamento tá apertado."),
     ]},
    {"name": "Explica pra leigo", "instruction": "explica isso de forma simples",
     "transcripts": [
         ("Dev", "O pod tá em CrashLoopBackOff. Liveness probe falhando."),
         ("Dev", "Container demora 30s pra subir, probe começa em 10."),
     ]},
    {"name": "Qual a temperatura?", "instruction": "qual a temperatura que ele falou?",
     "extra": "Assistindo aula de culinária.",
     "transcripts": [
         ("Chef", "O forno tem que estar a 180 graus, pré-aquecido."),
         ("Chef", "Uns 40 minutos no forno."),
     ]},
    {"name": "O que ele quis dizer?", "instruction": "o que ele quis dizer com isso?",
     "extra": "Assistindo podcast tech.",
     "transcripts": [
         ("Convidado", "Kubernetes é overkill pra maioria das startups. Se tu tem 3 microserviços, roda num ECS."),
     ]},
    {"name": "O que anotar?", "instruction": "o que eu deveria anotar?",
     "extra": "Reunião de trabalho. Sou estagiário.",
     "transcripts": [
         ("Diretor", "Faturamento Q1: 2.3 milhões, 15% acima do target."),
         ("Diretor", "Maior crescimento: enterprise, 40% YoY."),
         ("Diretor", "Meta Q2: 2.8 milhões. Precisamos de 2 SDRs."),
     ]},
    {"name": "Fala como narrador", "instruction": "comenta como se fosse narrador de futebol",
     "transcripts": [
         ("Narrador", "Vini Jr recebe na ponta, corta pra dentro."),
         ("Narrador", "Chuta! Desviou na zaga, escanteio."),
     ]},
]

if __name__ == "__main__":
    run_lote("4. Com Instrução", SCENARIOS, mode="short", behavior="conversa")
