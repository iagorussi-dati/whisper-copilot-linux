#!/usr/bin/env python3
"""Bateria de 50 testes — encontrar instrução que mantém resposta curta e consistente."""
import os, sys, time
sys.path.insert(0, os.path.expanduser("~/whisper-copilot-lite-linux"))
from backend.llm.bedrock import BedrockClient
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/whisper-copilot-lite-linux/.env"))
client = BedrockClient()
with open(os.path.expanduser("~/whisper-copilot-lite-linux/prompts/assistente-objetivo.md")) as f:
    system = f.read()
client.call_raw(system, "Aguarde.", max_tokens=10)

# 10 pontos variados pra testar
test_points = [
    "Segurança: evitar porta 22 exposta, usar System Manager com IAM",
    "Deploy manual via git pull no GitHub, ineficiente",
    "Build Next.js estoura RAM em instância pequena",
    "CodePipeline pra CI/CD com GitHub, reversão automática. Custo 1,5 dólar",
    "VPN custo alto, preferem System Manager. Bastion pra separar subnet",
    "Virginia mais barato que SP, quase metade. Latência 120ms vs 35-50ms",
    "Terraform ou CloudFormation pra IaC. WAF pra ataques SQL injection",
    "Budget limitado. 600→4mil assinaturas. Incentivo AWS possível",
    "Topologia: LB em subnet pública, ECS/EC2 e banco em privada. CloudWatch",
    "Cliente precisa de volumetria e billing atual pra estimar custos de migração",
]

# Instruções candidatas
instructions = {
    "v1_atual": "Responda curto focado na dor. 📌 + 💬. Sem resumo.",
    "v2_limite": "Responda em EXATAMENTE 3-5 linhas. 📌 (2 linhas máximo) + 💬 (1 frase). NADA MAIS.",
    "v3_formato": "Formato EXATO:\n📌 [resposta técnica em 2 linhas]\n💬 \"[1 frase pro cliente]\"\nNADA além disso. Sem título, sem explicação extra.",
    "v4_direto": "📌 2 linhas técnicas + 💬 1 frase pro cliente. PARE após a frase do 💬.",
    "v5_stop": "Responda APENAS:\n📌 [máximo 2 linhas]\n💬 \"[máximo 1 frase]\"\nPARE AQUI. Não adicione mais nada.",
}

print("Testando 5 instruções x 10 pontos = 50 testes\n")

for inst_name, inst in instructions.items():
    times = []
    chars_list = []
    over_10s = 0
    over_2000 = 0
    
    print(f"\n{'='*60}")
    print(f"INSTRUÇÃO: {inst_name}")
    print(f"{'='*60}")
    
    for i, ponto in enumerate(test_points):
        t0 = time.time()
        resp = client.call_raw(system, f"Dor do cliente:\n{ponto}\n\n{inst}", max_tokens=5120)
        t = time.time() - t0
        times.append(t)
        chars_list.append(len(resp))
        if t > 10: over_10s += 1
        if len(resp) > 2000: over_2000 += 1
        status = "✅" if t < 10 and len(resp) < 2000 else "❌"
        print(f"  {status} P{i+1}: {t:.1f}s | {len(resp)}chars | {resp[:60].replace(chr(10),' ')}...")
    
    avg_t = sum(times) / len(times)
    avg_c = sum(chars_list) / len(chars_list)
    success = len([1 for t, c in zip(times, chars_list) if t < 10 and c < 2000])
    print(f"\n  📊 Média: {avg_t:.1f}s | {avg_c:.0f}chars | >10s: {over_10s} | >2000chars: {over_2000} | Sucesso: {success}/10 ({success*10}%)")

print("\n\nFIM DOS TESTES")
