"""Test: verifica se o copiloto identifica dúvidas do cliente no meio de uma transcrição
e responde ao mesmo tempo que sugere perguntas."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api import Api

# Transcrição simulada com dúvidas do cliente misturadas
FAKE_TRANSCRIPTS = [
    # Bloco 1: contexto normal
    ("Consultor", "Bom, Reginaldo, a ideia é migrar toda a infraestrutura de vocês pra AWS. A gente vai usar EKS pra orquestrar os containers."),
    ("Reginaldo", "Legal, faz sentido. Hoje a gente tá com tudo on-premise e tá ficando caro manter."),
    ("Consultor", "Exato. E pra armazenamento a gente vai usar S3 pra guardar os arquivos estáticos, backups, logs."),
    
    # DÚVIDA DO CLIENTE sobre S3
    ("Reginaldo", "Ah, sobre o S3, eu tenho uma dúvida. Qual classe de armazenamento do S3 é a mais rentável? Porque a gente tem muitos dados que quase nunca acessa."),
    
    # Bloco 2: conversa continua
    ("Consultor", "Boa pergunta. Vou te explicar depois em detalhe. Mas voltando, pra banco de dados a gente pensou em usar Aurora."),
    ("Reginaldo", "Aurora é compatível com Postgres né? Porque a gente usa Postgres hoje."),
    ("Consultor", "Sim, totalmente compatível. E tem auto-scaling."),
    
    # DÚVIDA DO CLIENTE sobre custos
    ("Reginaldo", "E outra coisa, quanto mais ou menos a gente vai gastar por mês com essa infraestrutura toda? Porque hoje a gente gasta uns 15 mil com o data center."),
    
    # Bloco 3: mais contexto
    ("Consultor", "A gente vai fazer uma estimativa detalhada. Mas com reserved instances e savings plans dá pra otimizar bastante."),
    ("Reginaldo", "Entendi. E o deploy, como funciona? Hoje a gente faz tudo manual, sobe no servidor via SSH."),
    ("Consultor", "Na AWS a gente vai automatizar com CI/CD. CodePipeline ou GitHub Actions."),
    
    # DÚVIDA TÉCNICA do cliente
    ("Reginaldo", "Mas e se der problema no deploy, tem como fazer rollback rápido? Porque já aconteceu da gente subir uma versão com bug e demorar horas pra voltar."),
]


def run():
    api = Api()
    results = []

    def fake_emit(event, data):
        if event == "copilot_response" and data.get("response"):
            results.append(data["response"])
        api._chat_history.append({"event": event, "data": data})

    api._emit = fake_emit

    # Load prompt
    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "sugestoes.md")) as f:
        prompt = f.read()

    config = {
        "mic_device_id": "none", "monitor_device_id": "none", "chunk_seconds": 60,
        "my_name": "Consultor", "participants": [],
        "groq_api_key": "", "custom_system_prompt": prompt,
        "behavior_prompt": prompt,
        "suggestions_target": "Consultor", "global_hotkey": "", "snapshot_hotkey": "",
        "response_mode": "full", "auto_response": True, "extra_context": "",
    }
    api.start_meeting(config)

    # Inject fake transcripts directly (skip Groq, test only Bedrock response)
    for speaker, text in FAKE_TRANSCRIPTS:
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        api._transcript.append(entry)
        api._chat_history.append({"event": "transcript", "data": entry})
        print(f"  📝 [{speaker}] {text[:80]}")

    print(f"\n--- Gerando resposta (snapshot) ---")
    t0 = time.time()
    api._generate_snapshot_response("")
    time.sleep(5)  # wait for thread
    elapsed = time.time() - t0

    if results:
        print(f"\n🤖 RESPOSTA ({elapsed:.1f}s):\n")
        print(results[-1])
    else:
        print("❌ Sem resposta")

    # Now test full context
    print(f"\n--- Gerando resposta (full context) ---")
    t0 = time.time()
    api._generate_fullcontext_response()
    time.sleep(5)
    elapsed = time.time() - t0

    if len(results) > 1:
        print(f"\n🔍 FULL CONTEXT ({elapsed:.1f}s):\n")
        print(results[-1])

    api._hotkey_stop.set()

    # Analyze
    print("\n" + "="*60)
    print("ANÁLISE")
    print("="*60)
    
    all_text = " ".join(results).lower()
    checks = [
        ("Identificou dúvida S3 (classe rentável)", any(w in all_text for w in ["glacier", "s3", "classe", "armazenamento", "rentável", "infrequent", "acessa pouco"])),
        ("Identificou dúvida custos (15 mil)", any(w in all_text for w in ["custo", "15", "gast", "reserv", "savings", "estimativa"])),
        ("Identificou dúvida rollback/deploy", any(w in all_text for w in ["rollback", "deploy", "versão", "bug", "voltar", "ci/cd", "blue", "green", "canary"])),
        ("Tem sugestões de pergunta (tom correto)", any(c in all_text for c in ["?", "vocês"])),
        ("Respondeu alguma dúvida (não só perguntou)", any(w in all_text for w in ["glacier", "infrequent", "rollback", "blue/green", "canary", "reserved", "savings"])),
    ]
    
    for label, passed in checks:
        print(f"  {'✅' if passed else '❌'} {label}")


if __name__ == "__main__":
    run()
