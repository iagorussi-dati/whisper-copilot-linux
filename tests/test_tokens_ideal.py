"""Teste: qual max_tokens ideal pra short que não corta mas não vira textão."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.llm import BedrockClient

bedrock = BedrockClient()

SYSTEM = "Você é um copiloto pessoal. Acompanha a conversa e ajuda no que for preciso.\nSem markdown, sem títulos, sem listas. Texto corrido.\nNão narre a conversa. Apenas contribua.\nSempre termine suas frases. Nunca pare no meio de uma frase."

# Cenário simples (1 assunto)
SIMPLE = "Tô pensando em ir pra Floripa no feriado. Vi Airbnb por 200 a diária."

# Cenário denso (4 assuntos)
DENSE = """O sistema tá lento, demora 10 segundos pra carregar.
O login falha quando tem mais de 100 usuários simultâneos.
O relatório de vendas tá com dados errados desde março.
E a integração com o ERP parou de funcionar ontem."""

# Cenário médio (2 assuntos)
MEDIUM = """Meu carro tá fazendo barulho estranho no motor.
E o chefe pediu pra entregar o relatório até amanhã."""

TOKENS = [80, 100, 120, 150]

if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: MAX_TOKENS IDEAL PRA SHORT")
    print("=" * 70)

    for label, text in [("Simples (1 assunto)", SIMPLE), ("Médio (2 assuntos)", MEDIUM), ("Denso (4 assuntos)", DENSE)]:
        print(f"\n{'─'*70}")
        print(f"📌 {label}")

        for tok in TOKENS:
            user_msg = f"Conversa:\n{text}\n\nResponda naturalmente. Não narre. Sempre termine suas frases."
            t0 = time.time()
            resp = bedrock.call_raw(SYSTEM, user_msg, max_tokens=tok)
            elapsed = time.time() - t0

            # Check if response ends mid-sentence
            stripped = resp.strip()
            ends_ok = stripped and stripped[-1] in '.!?"\'):'
            cut = "✅" if ends_ok else "❌ CORTOU"

            print(f"  {tok:3d} tok → {len(resp):3d} chars, {elapsed:.1f}s {cut}")
            print(f"         {resp[:200]}")
            if not ends_ok:
                print(f"         ...FINAL: '{stripped[-30:]}'")
