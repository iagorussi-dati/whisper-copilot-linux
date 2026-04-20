"""Test runner for Whisper Copilot — simulates snapshot and full_context flows."""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api import Api

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_wav(name):
    path = os.path.join(FIXTURES, name)
    with open(path, "rb") as f:
        return f.read()


def run_test(name, chunks, system_prompt, behavior="sugestoes", response_mode="short"):
    """Run a test with given chunks simulating snapshots."""
    print(f"\n{'='*60}")
    print(f"TESTE: {name}")
    print(f"Chunks: {len(chunks)} | Behavior: {behavior} | Mode: {response_mode}")
    print(f"{'='*60}")

    api = Api()
    results = {"transcripts": [], "snapshot_responses": [], "fullcontext_response": None}

    def fake_emit(event, data):
        if event == "transcript":
            results["transcripts"].append(data)
            print(f"  📝 [{data['speaker']}] {data['text'][:80]}")
        elif event == "copilot_response" and data.get("response"):
            results["snapshot_responses"].append(data["response"])
            print(f"  🤖 {data['response'][:150]}")
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    # Start meeting
    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Iago", "participants": [],
        "groq_api_key": "", "custom_system_prompt": system_prompt,
        "behavior_prompt": system_prompt,
        "suggestions_target": "Iago", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": response_mode, "auto_response": True, "extra_context": "",
    }
    api.start_meeting(config)

    # Process each chunk as a snapshot
    for i, chunk_name in enumerate(chunks):
        print(f"\n--- Snapshot {i+1}/{len(chunks)}: {chunk_name} ---")
        wav = load_wav(chunk_name)
        t0 = time.time()

        # Transcribe (simulates _process_auto_chunk)
        api._process_auto_chunk(wav)

        # Build no-repeat hint
        prev = [e["data"]["response"][:100] for e in api._chat_history
                if e["event"] == "copilot_response" and e["data"].get("response")]
        hint = ""
        if prev:
            hint = f"\n\nVocê já sugeriu sobre: {'; '.join(prev[-5:])}. NÃO repita. Foque no que é NOVO neste trecho."

        # Generate snapshot response
        api._generate_snapshot_response(hint)
        time.sleep(1)  # wait for thread
        elapsed = time.time() - t0
        print(f"  ⏱️ {elapsed:.1f}s")

    # Full context
    print(f"\n--- Full Context (Win+H) ---")
    t0 = time.time()
    api._generate_fullcontext_response()
    time.sleep(1)
    elapsed = time.time() - t0
    results["fullcontext_response"] = results["snapshot_responses"][-1] if results["snapshot_responses"] else ""
    print(f"  ⏱️ {elapsed:.1f}s")

    api._hotkey_stop.set()
    return results


if __name__ == "__main__":
    # Load sugestoes prompt
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    with open(os.path.join(prompts_dir, "sugestoes.md")) as f:
        sugestoes_prompt = f.read()

    print("\n" + "="*60)
    print("TESTE 1: 4min-teste — 2 snapshots incrementais")
    print("="*60)
    r1 = run_test(
        "4min-teste (2 snapshots)",
        ["4min-chunk-0.wav", "4min-chunk-1.wav"],
        sugestoes_prompt,
    )

    print("\n" + "="*60)
    print("TESTE 2: Discovery — 4 snapshots incrementais + full context")
    print("="*60)
    r2 = run_test(
        "Discovery (4 snapshots + full)",
        ["discovery-chunk-0.wav", "discovery-chunk-1.wav",
         "discovery-chunk-2.wav", "discovery-chunk-3.wav"],
        sugestoes_prompt,
    )

    print("\n" + "="*60)
    print("TESTE 3: Migração AWS — arquivo inteiro + full context")
    print("="*60)
    r3 = run_test(
        "Migração AWS (inteiro)",
        ["call-migracao-aws.wav"],
        sugestoes_prompt,
    )

    # Summary
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    for name, r in [("4min", r1), ("Discovery", r2), ("AWS", r3)]:
        print(f"\n{name}:")
        print(f"  Transcrições: {len(r['transcripts'])}")
        print(f"  Respostas snapshot: {len(r['snapshot_responses'])}")
        for i, resp in enumerate(r["snapshot_responses"]):
            print(f"  Snapshot {i+1}: {resp[:120]}...")
