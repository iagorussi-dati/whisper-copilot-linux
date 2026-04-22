"""Lote 6: Respeito ao tamanho — mesmo cenário nos 3 modos."""
from protocolo_runner import run_one, score_response

# Mesmo cenário pra todos
T = [
    ("PM", "Sprint termina sexta. Temos 3 tasks abertas."),
    ("PM", "Iago com V1, Bruno com TatiLab, Mari com testes."),
    ("PM", "Prioridade é fechar a V1 primeiro."),
    ("PM", "Se sobrar tempo, começa a sprint seguinte."),
    ("Dev", "A migração do banco tá travada. Preciso de acesso ao staging."),
]

SCENARIOS_BASE = [
    {"name": "Sprint planning", "transcripts": T, "extra": "Reunião de sprint."},
    {"name": "Futebol", "extra": "Jogo no YouTube.", "transcripts": [
        ("Narrador", "Vini Jr recebe, corta, chuta! Desviou, escanteio."),
        ("Comentarista", "O Real tá aberto atrás. Linha alta demais."),
        ("Comentarista", "O Vini tá tentando resolver sozinho."),
    ]},
    {"name": "Debug técnico", "transcripts": [
        ("Dev", "Erro 502 no nginx. Backend rodando mas timeout no banco."),
        ("Dev", "Pool de conexões: 50 ativas, limite 50."),
        ("Dev", "Precisa aumentar ou tem leak."),
    ]},
]

MODES = ["short", "full", "research"]

if __name__ == "__main__":
    print("=" * 70)
    print("LOTE 6: RESPEITO AO TAMANHO")
    print("=" * 70)

    passed = 0
    total = 0
    all_sizes = []

    for s in SCENARIOS_BASE:
        print(f"\n{'─'*70}")
        print(f"📌 {s['name']}")
        sizes = {}

        for mode in MODES:
            resp, elapsed = run_one(s["transcripts"], mode=mode, extra_context=s.get("extra", ""))
            sc = score_response(resp, mode, elapsed)
            sizes[mode] = sc["chars"]
            total += 1
            if sc["passed"]:
                passed += 1

            status = "✅" if sc["passed"] else "❌"
            print(f"  {status} {mode:8s} → {sc['chars']:4d} chars, {sc['lines']:2d} lines, {elapsed:.1f}s")
            if sc["issues"]:
                print(f"     ⚠️ {sc['issues']}")

        # Check ordering: short < full < research
        order_ok = sizes.get("short", 0) <= sizes.get("full", 0) <= sizes.get("research", 0)
        total += 1
        if order_ok:
            passed += 1
            print(f"  ✅ Ordem: short({sizes['short']}) ≤ full({sizes['full']}) ≤ research({sizes['research']})")
        else:
            print(f"  ❌ Ordem ERRADA: short({sizes['short']}) / full({sizes['full']}) / research({sizes['research']})")

        all_sizes.append(sizes)

    # Extra: test that short is actually short (< 400 chars average)
    avg_short = sum(s["short"] for s in all_sizes) / len(all_sizes)
    avg_full = sum(s["full"] for s in all_sizes) / len(all_sizes)
    avg_research = sum(s["research"] for s in all_sizes) / len(all_sizes)

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/{total}")
    print(f"  Média short:    {avg_short:.0f} chars")
    print(f"  Média full:     {avg_full:.0f} chars")
    print(f"  Média research: {avg_research:.0f} chars")
