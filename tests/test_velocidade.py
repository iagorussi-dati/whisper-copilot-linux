#!/usr/bin/env python3
"""Teste de alternativas pra reduzir tempo de resposta — meta: <10s."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()

# Mesmo contexto do snap2 (3131 chars, 21 entradas)
context = """[Gustavo Conti] e mergulhar bem nessa frente. E partindo dessa conversa, a gente já começar a desenhar cenários de resolução dessa frente.
[Gustavo Conti] Você tem algum desenho de arquitetura?
[Juliano] Não possuo, a gente começou a subir a infraestrutura aos poucos.
[Gustavo Conti] Hoje vocês não estão usando nenhum tipo de WAF, nem nada assim?
[Juliano] Não. Essa instância do front-end é a que geralmente é atacada. A gente tem duas instâncias EC2. A ideia é usar ECS ou Kubernetes. Mas por enquanto subindo na mão.
[Juliano] O CPU ia subindo. Fechamos a porta de LB de outbound, apontamos que somente o security group do front-end seria o único ponto de saída. Parou de ocorrer.
[Gustavo Conti] O front está em qual linguagem?
[Juliano] Back-end em Python, front-end em Next.js 16.2.
[Juliano] O pessoal explora a porta 3000 do Node. Conseguem fazer execução de código remoto, colocam SH dentro e ficam executando. Removiam a chave SSH e eu perdia acesso. Tinha que matar a instância e subir outra."""

print(f"Contexto: {len(context)} chars\n")

# ── ALT 1: Chamada 1 faz resumo, chamada 2 recebe só pontos ──
print("="*60)
print("ALT 1: Chamada 2 recebe SÓ os pontos da chamada 1")
print("="*60)
t0 = time.time()
cm = (
    f"Analise a transcrição INTEIRA e responda QUATRO linhas:\n"
    f"CLASSIFICAÇÃO: SIM ou NAO\n"
    f"CONCORRENTE: SIM ou NAO\n"
    f"PONTOS: Liste TODOS os assuntos técnicos — problemas, dúvidas, tecnologias.\n"
    f"RESPOSTA: CURTA/MÉDIA/LONGA\n\n"
    f"Transcrição:\n{context}"
)
cr = client.call_raw("4 linhas.", cm, max_tokens=300).strip()
t_c1 = time.time() - t0
clean = context
for l in cr.split("\n"):
    if l.strip().upper().startswith("PONTOS:"): clean = l.split(":",1)[1].strip(); break
print(f"Chamada 1: {t_c1:.2f}s → {cr}")
print(f"Pontos: {clean}\n")

t0 = time.time()
msg = f"Pontos da conversa:\n{clean}\n\nResponda cada ponto de forma objetiva. Máximo 3 linhas por ponto no 📌 e 2 frases no 💬. Sem resumo no final."
resp = client.call_raw(system, msg, max_tokens=5120)
t_c2 = time.time() - t0
print(f"Chamada 2: {t_c2:.2f}s ({len(resp)} chars)")
print(f"TOTAL: {t_c1+t_c2:.2f}s")
print(f"Resposta:\n{resp[:500]}...\n")

# ── ALT 2: Instrução mais agressiva de tamanho ──
print("="*60)
print("ALT 2: Instrução agressiva — 2 linhas por ponto máximo")
print("="*60)
t0 = time.time()
msg = f"Pontos da conversa:\n{clean}\n\nResponda TODOS os pontos. Máximo 2 linhas por ponto. Formato: 📌 [ponto]: resposta curta. 💬 \"frase pro cliente\". Sem explicação extra."
resp = client.call_raw(system, msg, max_tokens=5120)
t_c2b = time.time() - t0
print(f"Chamada 2: {t_c2b:.2f}s ({len(resp)} chars)")
print(f"TOTAL: {t_c1+t_c2b:.2f}s")
print(f"Resposta:\n{resp[:500]}...\n")

# ── ALT 3: Chamada 1 já gera a resposta resumida (1 chamada só) ──
print("="*60)
print("ALT 3: UMA chamada só — classifica + responde junto")
print("="*60)
t0 = time.time()
msg = (
    f"Transcrição de reunião técnica:\n{context}\n\n"
    f"Analise e responda de forma objetiva. Para cada assunto técnico identificado:\n"
    f"📌 [assunto]: resposta em 2-3 linhas\n"
    f"💬 \"frase pronta pro consultor falar\"\n\n"
    f"Seja conciso. Sem resumo no final."
)
resp = client.call_raw(system, msg, max_tokens=5120)
t_single = time.time() - t0
print(f"UMA chamada: {t_single:.2f}s ({len(resp)} chars)")
print(f"Resposta:\n{resp[:500]}...\n")

# ── RESUMO ──
print("="*60)
print("RESUMO")
print("="*60)
print(f"ALT 1 (pontos → chamada 2):     {t_c1+t_c2:.2f}s")
print(f"ALT 2 (instrução agressiva):     {t_c1+t_c2b:.2f}s")
print(f"ALT 3 (uma chamada só):          {t_single:.2f}s")

with open(os.path.expanduser("~/whisper-copilot-lite-linux/tests/resultado-alternativas-velocidade.md"), "w") as f:
    f.write(f"# Teste Alternativas de Velocidade\n\nContexto: {len(context)} chars\n\n")
    f.write(f"| Alt | Tempo | Chars |\n|---|---|---|\n")
    f.write(f"| 1 (pontos→chamada2) | {t_c1+t_c2:.2f}s | — |\n")
    f.write(f"| 2 (instrução agressiva) | {t_c1+t_c2b:.2f}s | — |\n")
    f.write(f"| 3 (uma chamada só) | {t_single:.2f}s | {len(resp)} |\n")
print(f"\n📄 Salvo em tests/resultado-alternativas-velocidade.md")
