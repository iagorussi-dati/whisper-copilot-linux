"""Teste rápido: transcrição do podcast futebol/música — verificar tamanho short."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from protocolo_runner import run_one, score_response

CHUNKS = [
    [
        ("Pessoa", "Eu jogava quando era menorzinho, lá na minha quebração eu jogava."),
        ("Pessoa", "Mano, aqui é a Arena da Morte aqui, que nós chamava."),
        ("Pessoa", "Mano, nós entravamos lá, saímos no soco, mano."),
        ("Pessoa", "Então, tipo, já é uma parte da minha vida que eu gosto muito."),
    ],
    [
        ("Pessoa", "De terra, por causa da quadra, na escola."),
        ("Pessoa", "Família que tinha lá também, entendeu?"),
        ("Pessoa", "Onde tinha futebol de areia, que tinha um campinho de areia lá na cidade, nós jogávamos também."),
        ("Pessoa", "Eu trabalhava da manhã até de madrugada."),
    ],
    [
        ("Pessoa", "O dia todo ralando. Pra receber quanta diária? 50 conto."),
        ("Pessoa", "E lá ia vários empresários de futebol."),
        ("Pessoa", "Na época eu já tava querendo cantar, mas só que eu já tinha querendo jogar bola."),
        ("Pessoa", "Aí eu falei, bom, vou pedir uma oportunidade, vai que de repente os caras me descobrem."),
    ],
    [
        ("Pessoa", "Umas paradinhas que inspiravam muito, né?"),
        ("Pessoa", "Aí eu falei, bom, vou pedir uma oportunidade."),
        ("Pessoa", "Ah, você era carudo também, né?"),
        ("Pessoa", "É, eu falei pro cara, mano, me dá uma chance aí."),
        ("Pessoa", "Aí o cara falou, faz um DVD aí que eu te levo pra gravar."),
    ],
]

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE: Podcast futebol/música — modo SHORT (80 tok)")
    print("=" * 60)

    for i, chunk in enumerate(CHUNKS):
        resp, elapsed = run_one(chunk, mode="short", behavior="conversa",
                                extra_context="Assistindo podcast/entrevista no YouTube.")
        sc = score_response(resp, "short", elapsed)
        print(f"\nSnapshot {i+1} ({elapsed:.1f}s, {len(resp)} chars, {sc['lines']} lines):")
        print(f"  {resp}")
        if sc["issues"]:
            print(f"  ⚠️ {sc['issues']}")
