"""Teste: Snapshot com múltiplos assuntos no mesmo intervalo + cenários densos."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.llm import BedrockClient

bedrock = BedrockClient()

SYSTEM = "Você é um copiloto pessoal. Acompanha a conversa e ajuda no que for preciso.\nSem markdown, sem títulos, sem listas. Texto corrido.\nNão narre a conversa (não diga 'Pessoa 1 falou X'). Apenas contribua."

# 10 cenários com intervalos complexos
TESTS = [
    {
        "name": "1. Intervalo com 2 assuntos (viagem + dinheiro)",
        "interval": [
            "Tô pensando em ir pra Europa em dezembro.",
            "Mas o dólar tá 6 reais, vai sair caro demais.",
            "Vi passagem pra Lisboa por 3 mil ida e volta.",
            "Meu cartão tá no limite, vou ter que parcelar.",
        ],
        "must_mention": ["europa", "lisboa", "passagem", "dólar", "caro", "parcel"],
    },
    {
        "name": "2. Intervalo com 3 assuntos (carro + saúde + trabalho)",
        "interval": [
            "Meu carro tá fazendo um barulho estranho no motor.",
            "E tô com dor nas costas faz uma semana, preciso ir no médico.",
            "Ah, e o chefe pediu pra entregar o relatório até amanhã.",
        ],
        "must_mention": ["carro", "motor", "costas", "médico", "relatório", "amanhã"],
    },
    {
        "name": "3. Reunião densa — cliente fala de 4 problemas",
        "interval": [
            "O sistema tá lento, demora 10 segundos pra carregar.",
            "O login falha quando tem mais de 100 usuários simultâneos.",
            "O relatório de vendas tá com dados errados desde março.",
            "E a integração com o ERP parou de funcionar ontem.",
        ],
        "must_mention": ["lento", "login", "relatório", "erp", "integração"],
    },
    {
        "name": "4. Podcast — host muda de assunto rápido",
        "interval": [
            "Então, sobre IA generativa, o mercado vai triplicar até 2027.",
            "Mudando de assunto, o que você acha do trabalho remoto?",
            "Eu acho que híbrido é o futuro. 3 dias no escritório.",
            "E sobre cripto, Bitcoin bateu 100 mil dólares.",
        ],
        "must_mention": ["ia", "remoto", "híbrido", "bitcoin", "cripto"],
    },
    {
        "name": "5. Daily caótica — todo mundo fala ao mesmo tempo",
        "interval": [
            "Eu terminei o frontend ontem.",
            "O banco tá dando timeout.",
            "Alguém viu o email do cliente?",
            "Preciso de review no meu PR.",
            "O staging tá fora do ar.",
            "Quem vai fazer o deploy hoje?",
        ],
        "must_mention": ["frontend", "banco", "timeout", "email", "pr", "staging", "deploy"],
    },
    {
        "name": "6. Conversa informal — pula entre 3 assuntos",
        "interval": [
            "Cara, o show do Coldplay foi incrível.",
            "Tu viu que o preço da gasolina subiu de novo?",
            "Meu gato fugiu ontem e voltou hoje de manhã.",
        ],
        "must_mention": ["coldplay", "show", "gasolina", "gato", "fugiu"],
    },
    {
        "name": "7. Entrevista técnica — várias perguntas",
        "interval": [
            "Me explica a diferença entre SQL e NoSQL.",
            "E quando usar microserviços vs monolito?",
            "Qual sua experiência com CI/CD?",
            "Como você lida com code review?",
        ],
        "must_mention": ["sql", "nosql", "microserviço", "monolito", "ci/cd", "review"],
    },
    {
        "name": "8. Notícias misturadas",
        "interval": [
            "O terremoto no Japão foi 7.2 na escala Richter.",
            "A seleção brasileira perdeu pra Argentina de novo.",
            "SpaceX lançou mais 60 satélites Starlink.",
        ],
        "must_mention": ["terremoto", "japão", "seleção", "argentina", "spacex", "starlink"],
    },
    {
        "name": "9. Planejamento complexo — evento da empresa",
        "interval": [
            "O evento é dia 15 no hotel Ibis.",
            "Precisamos de 50 cadeiras e 10 mesas.",
            "O buffet custa 80 reais por pessoa, são 120 convidados.",
            "O DJ cobra 2 mil pela noite.",
            "Falta confirmar o estacionamento.",
        ],
        "must_mention": ["evento", "hotel", "cadeira", "buffet", "dj", "estacionamento"],
    },
    {
        "name": "10. Debug ao vivo — múltiplos erros",
        "interval": [
            "O nginx tá dando 502.",
            "O Redis tá com memória cheia, 100% usado.",
            "Tem um memory leak no serviço de notificações.",
            "E o certificado SSL expira amanhã.",
        ],
        "must_mention": ["nginx", "502", "redis", "memória", "leak", "ssl", "certificado"],
    },
]


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: MÚLTIPLOS ASSUNTOS NO MESMO INTERVALO (abordagem B)")
    print("=" * 70)

    passed = 0
    narrated = 0

    for t in TESTS:
        interval_text = "\n".join(t["interval"])
        user_msg = (
            f"Conversa:\n{interval_text}\n\n"
            f"Responda naturalmente sobre o que acabou de ser dito. "
            f"Não narre quem falou o quê."
        )
        t0 = time.time()
        resp = bedrock.call_raw(SYSTEM, user_msg, max_tokens=120)
        elapsed = time.time() - t0
        resp_lower = resp.lower()

        # Check coverage
        hits = [k for k in t["must_mention"] if k in resp_lower]
        coverage = len(hits) / len(t["must_mention"])

        # Check narration
        is_narrating = any(p in resp_lower for p in [
            "pessoa 1", "pessoa 2", "falou que", "disse que", "mencionou que",
            "primeiro ponto", "segundo ponto", "terceiro ponto",
        ])
        if is_narrating:
            narrated += 1

        ok = coverage >= 0.4 and not is_narrating  # at least 40% of topics covered
        if ok:
            passed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {t['name']} ({elapsed:.1f}s, {coverage:.0%} cobertura)")
        print(f"   {resp[:250]}")
        if is_narrating:
            print(f"   ⚠️ Narrou a conversa")
        if coverage < 0.4:
            print(f"   ⚠️ Cobertura baixa: {hits}")

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/10 | Narrou: {narrated}/10")
