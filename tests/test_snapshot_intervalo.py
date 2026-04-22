"""Teste: Snapshot intervalo — Abordagem A (tudo + instrução) vs B (só trecho).
5 intervalos com assuntos diferentes, verificar se responde só sobre o intervalo."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.llm import BedrockClient

bedrock = BedrockClient()

# Conversa com 5 assuntos distintos em sequência
CHUNKS = [
    # Chunk 1: Falando sobre férias
    ["[Iago] Cara, tô pensando em ir pra Floripa no feriado.",
     "[Colega] Bora! Vi um Airbnb barato perto da Joaquina.",
     "[Iago] Vamos de carro, umas 5 horas de Joinville."],
    # Chunk 2: Mudou pra futebol
    ["[Colega] Tu viu o jogo do Grêmio ontem? Perdeu de 3 a 0.",
     "[Iago] Vi. O Renato tem que sair. Time não marca.",
     "[Colega] O elenco tá fraco, não tem lateral direito."],
    # Chunk 3: Mudou pra trabalho
    ["[Iago] Mudando de assunto, preciso terminar o deploy até sexta.",
     "[Colega] Qual projeto?",
     "[Iago] O Whisper Copilot. Tá quase pronto, falta o build pro Windows.",
     "[Colega] Precisa de ajuda?"],
    # Chunk 4: Mudou pra comida
    ["[Colega] Vamos almoçar onde?",
     "[Iago] Aquele japonês novo. Dizem que o sashimi é fresco.",
     "[Colega] Mas é 80 conto o rodízio.",
     "[Iago] Racha no meio."],
    # Chunk 5: Mudou pra tecnologia
    ["[Iago] Tu já testou o Claude 4? Saiu semana passada.",
     "[Colega] Ainda não. Tá melhor que o 3.5?",
     "[Iago] Muito. Principalmente pra código. Mais rápido também.",
     "[Colega] Vou testar hoje."],
]

SYSTEM = "Você é um copiloto pessoal. Acompanha a conversa e ajuda no que for preciso.\nSem markdown, sem títulos, sem listas. Texto corrido.\nNão narre a conversa (não diga 'Pessoa 1 falou X'). Apenas contribua."


def build_full_context(chunks_so_far):
    """All transcripts up to this point."""
    lines = []
    for chunk in chunks_so_far:
        for line in chunk:
            lines.append(line)
    return "\n".join(lines)


def build_interval_only(chunk):
    """Only the current interval."""
    return "\n".join(chunk)


def test_approach_a(chunks_so_far, current_chunk, chunk_idx):
    """Abordagem A: manda tudo + instrui sobre o intervalo."""
    full = build_full_context(chunks_so_far)
    interval = build_interval_only(current_chunk)

    user_msg = (
        f"Conversa completa até agora:\n{full}\n\n"
        f"--- INTERVALO ATUAL (responda SOMENTE sobre isso) ---\n{interval}\n"
        f"--- FIM DO INTERVALO ---\n\n"
        f"Responda naturalmente APENAS sobre o que foi dito no INTERVALO ATUAL. "
        f"Não comente sobre assuntos anteriores. Não narre quem falou o quê."
    )
    t0 = time.time()
    resp = bedrock.call_raw(SYSTEM, user_msg, max_tokens=80)
    return resp.strip(), time.time() - t0


def test_approach_b(current_chunk, chunk_idx):
    """Abordagem B: manda só o trecho."""
    interval = build_interval_only(current_chunk)

    user_msg = (
        f"Conversa:\n{interval}\n\n"
        f"Responda naturalmente sobre o que acabou de ser dito. "
        f"Não narre quem falou o quê."
    )
    t0 = time.time()
    resp = bedrock.call_raw(SYSTEM, user_msg, max_tokens=80)
    return resp.strip(), time.time() - t0


TOPICS = ["férias/Floripa", "futebol/Grêmio", "trabalho/deploy", "comida/japonês", "tech/Claude 4"]

# Palavras-chave por assunto pra verificar se ficou no intervalo
KEYWORDS = [
    ["floripa", "airbnb", "joaquina", "carro", "joinville", "férias", "feriado"],
    ["grêmio", "renato", "futebol", "jogo", "lateral", "elenco", "perdeu"],
    ["deploy", "whisper", "windows", "build", "projeto", "sexta"],
    ["japonês", "sashimi", "rodízio", "almoç", "comer", "racha"],
    ["claude", "3.5", "código", "rápido", "testar", "ia"],
]

# Palavras dos outros assuntos (não deveria mencionar)
def other_keywords(idx):
    others = []
    for i, kw in enumerate(KEYWORDS):
        if i != idx:
            others.extend(kw[:3])  # top 3 de cada outro assunto
    return others


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: SNAPSHOT INTERVALO — A (tudo+instrução) vs B (só trecho)")
    print("=" * 70)

    for approach_name, test_fn_label in [("A (tudo + instrução)", "A"), ("B (só trecho)", "B")]:
        print(f"\n{'─'*70}")
        print(f"ABORDAGEM {approach_name}")
        print(f"{'─'*70}")

        passed = 0
        leaked = 0

        for i, chunk in enumerate(CHUNKS):
            if test_fn_label == "A":
                chunks_so_far = []
                for j in range(i + 1):
                    chunks_so_far.append(CHUNKS[j])
                resp, elapsed = test_approach_a(chunks_so_far, chunk, i)
            else:
                resp, elapsed = test_approach_b(chunk, i)

            resp_lower = resp.lower()

            # Check: resposta menciona o assunto correto?
            on_topic = any(k in resp_lower for k in KEYWORDS[i])

            # Check: resposta NÃO menciona outros assuntos?
            others = other_keywords(i)
            leaked_words = [w for w in others if w in resp_lower]
            no_leak = len(leaked_words) == 0

            # Check: não narra ("Pessoa 1 falou", "Iago disse")
            narrating = any(p in resp_lower for p in ["pessoa 1", "pessoa 2", "iago falou", "iago disse", "colega falou", "colega disse"])

            ok = on_topic and no_leak and not narrating
            if ok:
                passed += 1
            if leaked_words:
                leaked += 1

            status = "✅" if ok else "❌"
            print(f"\n  {status} Snapshot {i+1} — {TOPICS[i]} ({elapsed:.1f}s)")
            print(f"     {resp[:200]}")
            if not on_topic:
                print(f"     ⚠️ Não falou sobre {TOPICS[i]}")
            if leaked_words:
                print(f"     ⚠️ Vazou assuntos: {leaked_words}")
            if narrating:
                print(f"     ⚠️ Narrou a conversa")

        print(f"\n  RESULTADO {test_fn_label}: {passed}/5 no tópico | {leaked}/5 vazaram")

    # Test full context (Win+H) — deve falar de TUDO
    print(f"\n{'─'*70}")
    print("FULL CONTEXT (Win+H) — deve cobrir todos os assuntos")
    print(f"{'─'*70}")

    full = build_full_context(CHUNKS)
    user_msg = (
        f"Conversa completa:\n{full}\n\n"
        f"Dê uma visão geral da conversa toda. Pode repetir pontos importantes.\n"
        f"Sem markdown, sem títulos, sem listas."
    )
    t0 = time.time()
    resp = bedrock.call_raw(SYSTEM, user_msg, max_tokens=200)
    elapsed = time.time() - t0
    resp_lower = resp.lower()

    covered = 0
    for i, topic in enumerate(TOPICS):
        hit = any(k in resp_lower for k in KEYWORDS[i])
        if hit:
            covered += 1
        print(f"  {'✅' if hit else '❌'} {topic}")

    print(f"\n  Full context: {covered}/5 assuntos cobertos ({elapsed:.1f}s)")
    print(f"  {resp[:300]}")
