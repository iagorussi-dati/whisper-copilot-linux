"""Protocolo de Testes — Runner completo com scorecard."""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

BAD_PATTERNS = [
    "vamos analisar", "analisando o trecho", "identificação dos participantes",
    "trecho mais recente", "contexto da conversa",
    "vou acompanhar como copiloto", "baseado no contexto",
    "ponto central é", "tema novo é", "dor aqui é",
]

SIZE_LIMITS = {
    "short": {"max_chars": 600, "max_lines": 8},
    "full": {"max_chars": 1500, "max_lines": 20},
    "research": {"max_chars": 3000, "max_lines": 40},
}

TIME_LIMITS = {"short": 6, "full": 8, "research": 10, "research_search": 15}


def score_response(resp, mode, elapsed, had_instruction=False, instruction=""):
    """Score a response across 5 dimensions. Returns dict with scores and issues."""
    r = resp.lower()
    lines = [l for l in resp.split("\n") if l.strip()]
    issues = []

    # Naturalidade (25%)
    bad = [p for p in BAD_PATTERNS if p in r]
    nat_score = 5 if not bad else (2 if len(bad) > 2 else 3)
    if bad:
        issues.append(f"Padrões robóticos: {bad}")

    # Concisão (15%)
    lim = SIZE_LIMITS.get(mode, SIZE_LIMITS["short"])
    chars_ok = len(resp) <= lim["max_chars"]
    lines_ok = len(lines) <= lim["max_lines"]
    con_score = 5 if chars_ok and lines_ok else (3 if chars_ok or lines_ok else 1)
    if not chars_ok:
        issues.append(f"Chars: {len(resp)} > {lim['max_chars']}")
    if not lines_ok:
        issues.append(f"Lines: {len(lines)} > {lim['max_lines']}")

    # Latência
    t_lim = TIME_LIMITS.get(mode, 6)
    lat_ok = elapsed <= t_lim
    lat_score = 5 if elapsed <= t_lim * 0.7 else (4 if lat_ok else 2)
    if not lat_ok:
        issues.append(f"Latência: {elapsed:.1f}s > {t_lim}s")

    # Segurança (10%)
    seg_score = 5
    if "identificação dos participantes" in r or "lista de participantes" in r:
        seg_score = 1
        issues.append("Listou participantes")
    if resp.strip() == "" or resp.startswith("❌"):
        seg_score = 1
        issues.append("Sem resposta")

    return {
        "naturalidade": nat_score,
        "concisao": con_score,
        "latencia": lat_score,
        "seguranca": seg_score,
        "issues": issues,
        "chars": len(resp),
        "lines": len(lines),
        "elapsed": elapsed,
        "passed": nat_score >= 4 and con_score >= 3 and seg_score >= 4,
    }


def run_one(transcripts, mode="short", behavior="conversa", extra_context="",
            instruction="", auto_response=True):
    api = Api()
    results = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    prompt_map = {
        "conversa": "conversa-natural.md",
        "sugestoes": "sugestoes.md",
        "assistente": "assistente-objetivo.md",
        "pesquisa": "pesquisa.md",
    }
    prompt_file = prompt_map.get(behavior, "conversa-natural.md")
    with open(os.path.join(prompts_dir, prompt_file)) as f:
        prompt = f.read()

    full_extra = extra_context
    if instruction:
        full_extra += f"\n{instruction}" if full_extra else instruction

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt, "behavior_template": behavior,
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": mode, "auto_response": auto_response,
        "extra_context": full_extra,
    }
    api.start_meeting(config)

    for speaker, text in transcripts:
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        api._transcript.append(entry)
        api._chat_history.append({"event": "transcript", "data": entry})

    t0 = time.time()
    api._generate_snapshot_response("")
    for _ in range(25):
        time.sleep(1)
        if results:
            break
    elapsed = time.time() - t0
    api._hotkey_stop.set()
    return results[-1] if results else "❌ Sem resposta", elapsed


def run_lote(name, scenarios, mode="short", behavior="conversa"):
    print(f"\n{'='*70}")
    print(f"LOTE: {name} (mode={mode}, behavior={behavior})")
    print(f"{'='*70}")

    passed = 0
    total_scores = {"naturalidade": 0, "concisao": 0, "latencia": 0, "seguranca": 0}

    for s in scenarios:
        resp, elapsed = run_one(
            s["transcripts"], mode=mode, behavior=behavior,
            extra_context=s.get("extra", ""),
            instruction=s.get("instruction", ""),
        )
        sc = score_response(resp, mode, elapsed, instruction=s.get("instruction", ""))

        for k in total_scores:
            total_scores[k] += sc[k]

        if sc["passed"]:
            passed += 1

        status = "✅" if sc["passed"] else "❌"
        print(f"\n{status} {s['name']} ({sc['elapsed']:.1f}s, {sc['chars']}ch, {sc['lines']}ln)")
        print(f"   {resp[:250].replace(chr(10), ' ')}")
        if sc["issues"]:
            print(f"   ⚠️ {sc['issues']}")

    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/{len(scenarios)}")
    for k, v in total_scores.items():
        avg = v / len(scenarios)
        print(f"  {k}: {avg:.1f}/5")
    return passed, len(scenarios)
