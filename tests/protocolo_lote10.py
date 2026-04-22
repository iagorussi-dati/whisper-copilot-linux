"""Lote 10: Full context Win+H — visão geral após vários snapshots."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from backend.api import Api

CONVERSATIONS = [
    {"name": "Discovery completa", "behavior": "sugestoes", "transcripts": [
        ("Consultor", "Me conta sobre a infra de vocês."),
        ("Cliente", "3 servidores on-premise, Postgres 500GB, 2TB de arquivos."),
        ("Consultor", "Quanto gastam hoje?"), ("Cliente", "15 mil por mês."),
        ("Cliente", "O site de ingressos tem picos absurdos."),
        ("Consultor", "Escalabilidade automática resolve."),
        ("Cliente", "E segurança? Já tivemos DDoS."),
        ("Cliente", "Ficamos fora 6 horas."),
        ("Consultor", "Vamos incluir WAF e Shield."),
        ("Cliente", "Quando vocês conseguem começar?"),
    ]},
    {"name": "Daily completa", "behavior": "conversa", "transcripts": [
        ("Gui", "Bom dia. Iago?"), ("Iago", "Terminei V1, falta deploy."),
        ("Bruno", "Travei no staging."), ("Mari", "Testes 95% cobertura."),
        ("Josimar", "Revisando PR do Bruno."), ("Gui", "Prioridade: deploy V1."),
        ("Bruno", "Preciso de acesso urgente."), ("Iago", "Posso ajudar o Bruno."),
        ("Gui", "Beleza. Mais alguma coisa?"), ("Mari", "Não, é isso."),
    ]},
    {"name": "Podcast tech", "behavior": "conversa", "extra": "Podcast de tecnologia.",
     "transcripts": [
        ("Host", "A IA vai substituir programadores?"),
        ("Convidado", "Não substitui, mas muda o perfil."),
        ("Host", "E o junior?"), ("Convidado", "Vai ter que aprender arquitetura mais cedo."),
        ("Host", "Empresas vão contratar menos?"),
        ("Convidado", "Diferente, não menos. Precisa de quem orquestre IA."),
    ]},
    {"name": "Reunião cliente problema", "behavior": "conversa",
     "extra": "Reunião com cliente.", "transcripts": [
        ("Cliente", "Sistema caiu 3 vezes essa semana."),
        ("Cliente", "Infra acha que é memória."),
        ("Iago", "Vocês têm monitoramento?"),
        ("Cliente", "CloudWatch mas ninguém olha."),
        ("Iago", "Vamos configurar alarmes."),
        ("Cliente", "Quanto tempo pra resolver?"),
    ]},
    {"name": "Futebol completo", "behavior": "conversa",
     "extra": "Jogo Real Madrid x Alavés no YouTube.", "transcripts": [
        ("Narrador", "Autoriza o árbitro, tá rolando."),
        ("Comentarista", "Arbeloa tem mais derrotas que Xabi Alonso."),
        ("Narrador", "Vini Jr recebe, corta, chuta! Escanteio."),
        ("Comentarista", "Vini tá tentando resolver sozinho."),
        ("Narrador", "Rüdiger cabeceia pra fora."),
        ("Comentarista", "Alavés tá surpreendendo."),
    ]},
]


def run_fullcontext(conv):
    api = Api()
    results = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    pmap = {"sugestoes": "sugestoes.md", "conversa": "conversa-natural.md"}
    with open(os.path.join(prompts_dir, pmap[conv["behavior"]])) as f:
        prompt = f.read()

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt, "behavior_template": conv["behavior"],
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": "full", "auto_response": True,
        "extra_context": conv.get("extra", ""),
    }
    api.start_meeting(config)

    for speaker, text in conv["transcripts"]:
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        api._transcript.append(entry)
        api._chat_history.append({"event": "transcript", "data": entry})

    t0 = time.time()
    api._generate_fullcontext_response()
    for _ in range(20):
        time.sleep(1)
        if results:
            break
    elapsed = time.time() - t0
    api._hotkey_stop.set()
    return results[-1] if results else "❌", elapsed


if __name__ == "__main__":
    print("=" * 70)
    print("LOTE 10: FULL CONTEXT (Win+H)")
    print("=" * 70)

    from protocolo_runner import BAD_PATTERNS
    passed = 0

    for conv in CONVERSATIONS:
        resp, elapsed = run_fullcontext(conv)
        r = resp.lower()
        bad = [p for p in BAD_PATTERNS if p in r]
        ok = len(bad) == 0 and resp and not resp.startswith("❌")

        # Full context CAN be more analytical, but still no robotic patterns
        if ok:
            passed += 1

        status = "✅" if ok else "❌"
        print(f"\n{status} {conv['name']} ({elapsed:.1f}s, {len(resp)}ch)")
        print(f"   {resp[:300].replace(chr(10), ' ')}")
        if bad:
            print(f"   ⚠️ Padrões: {bad}")

    # Double each as snapshot vs fullcontext comparison
    print(f"\n{'─'*70}")
    print(f"RESULTADO: {passed}/{len(CONVERSATIONS)}")

    # Run same conversations as snapshot for comparison
    print(f"\n{'─'*70}")
    print("COMPARAÇÃO: Snapshot vs Full Context")
    for conv in CONVERSATIONS[:2]:
        from protocolo_runner import run_one
        snap_resp, snap_t = run_one(conv["transcripts"][-3:], mode="short", behavior=conv["behavior"])
        fc_resp, fc_t = run_fullcontext(conv)
        snap_ok = len(snap_resp) < len(fc_resp)
        print(f"\n  {conv['name']}:")
        print(f"    Snapshot: {len(snap_resp)}ch ({snap_t:.1f}s)")
        print(f"    Full ctx: {len(fc_resp)}ch ({fc_t:.1f}s)")
        print(f"    {'✅' if snap_ok else '⚠️'} Snapshot < Full context: {snap_ok}")
        passed += 1 if snap_ok else 0

    total = len(CONVERSATIONS) + 2
    print(f"\n{'─'*70}")
    print(f"RESULTADO FINAL: {passed}/{total}")
