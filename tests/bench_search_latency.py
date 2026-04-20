"""Benchmark: comparar latência de web search vs Bedrock Tool Use vs direto."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.llm.bedrock import BedrockClient
from backend.search import web_search

bedrock = BedrockClient()

QUERY = "Quanto custa o Amazon Q Business por usuário em 2026?"

# ── 1. Abordagem atual: Bedrock decide + web search separado ──
def test_current():
    t0 = time.time()
    # Step 1: Bedrock decide se precisa pesquisar
    check = bedrock.call_raw("Responda apenas SIM ou NAO.", 
        f"Pergunta: {QUERY}\nVocê precisa pesquisar na internet? Responda APENAS 'SIM: query' ou 'NAO'.", 
        max_tokens=30)
    t_check = time.time() - t0
    
    # Step 2: Web search
    t1 = time.time()
    results = web_search("Amazon Q Business pricing 2026", max_results=3)
    t_search = time.time() - t1
    
    # Step 3: Bedrock responde com contexto
    t2 = time.time()
    answer = bedrock.call_raw(
        "Responda com dados de pricing atualizados. Seja direto.",
        f"Pergunta: {QUERY}\n\nDados da web:\n{results}\n\nResponda com preços exatos.",
        max_tokens=200
    )
    t_answer = time.time() - t2
    
    total = time.time() - t0
    return {
        "method": "Atual (check + search + resposta)",
        "t_check": t_check, "t_search": t_search, "t_answer": t_answer,
        "total": total, "answer": answer[:200]
    }

# ── 2. Bedrock Tool Use ──
def test_tool_use():
    import json
    t0 = time.time()
    
    # Reuse bedrock client (already has auth)
    client = bedrock._client
    model_id = bedrock.model_id
    
    tool_config = {
        "tools": [{
            "toolSpec": {
                "name": "web_search",
                "description": "Search the web for current pricing, specs, or technical data about AWS services.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            }
        }]
    }
    
    tool_config = {
        "tools": [{
            "toolSpec": {
                "name": "web_search",
                "description": "Search the web for current pricing, specs, or technical data about AWS services.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            }
        }]
    }
    
    messages = [{"role": "user", "content": [{"text": QUERY}]}]
    
    # Step 1: Bedrock call with tool
    t1 = time.time()
    r = client.converse(
        modelId=model_id,
        messages=messages,
        toolConfig=tool_config,
        system=[{"text": "Você é um consultor técnico AWS. Use web_search para dados atualizados de pricing."}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.3}
    )
    t_first = time.time() - t1
    
    output = r["output"]["message"]
    
    # Check if tool use requested
    tool_calls = [b for b in output["content"] if "toolUse" in b]
    
    t_search = 0
    t_second = 0
    if tool_calls:
        tool = tool_calls[0]["toolUse"]
        query = tool["input"].get("query", QUERY)
        
        # Step 2: Execute search
        t2 = time.time()
        search_results = web_search(query, max_results=3)
        t_search = time.time() - t2
        
        # Step 3: Send results back
        messages.append(output)
        messages.append({
            "role": "user",
            "content": [{"toolResult": {
                "toolUseId": tool["toolUseId"],
                "content": [{"text": search_results}]
            }}]
        })
        
        t3 = time.time()
        r2 = client.converse(
            modelId=model_id,
            messages=messages,
            toolConfig=tool_config,
            system=[{"text": "Responda com dados de pricing. Seja direto."}],
            inferenceConfig={"maxTokens": 200, "temperature": 0.3}
        )
        t_second = time.time() - t3
        answer = r2["output"]["message"]["content"][0]["text"]
    else:
        answer = output["content"][0].get("text", "No tool use")
    
    total = time.time() - t0
    return {
        "method": "Tool Use (Bedrock decide + executa)",
        "t_first": t_first, "t_search": t_search, "t_second": t_second,
        "total": total, "answer": answer[:200]
    }

# ── 3. Direto sem search (baseline) ──
def test_no_search():
    t0 = time.time()
    answer = bedrock.call_raw(
        "Responda com dados de pricing AWS. Seja direto.",
        QUERY,
        max_tokens=200
    )
    total = time.time() - t0
    return {"method": "Sem search (modelo puro)", "total": total, "answer": answer[:200]}

# ── 4. Search direto sem check ──
def test_search_direct():
    t0 = time.time()
    
    t1 = time.time()
    results = web_search("Amazon Q Business pricing 2026", max_results=3)
    t_search = time.time() - t1
    
    t2 = time.time()
    answer = bedrock.call_raw(
        "Responda com dados de pricing. Seja direto.",
        f"Pergunta: {QUERY}\n\nDados da web:\n{results}\n\nResponda com preços exatos.",
        max_tokens=200
    )
    t_answer = time.time() - t2
    
    total = time.time() - t0
    return {
        "method": "Search direto (sem check)",
        "t_search": t_search, "t_answer": t_answer,
        "total": total, "answer": answer[:200]
    }


if __name__ == "__main__":
    print("="*60)
    print(f"BENCHMARK: Latência de abordagens de pricing")
    print(f"Query: {QUERY}")
    print("="*60)
    
    tests = [
        ("Sem search", test_no_search),
        ("Search direto", test_search_direct),
        ("Atual (3 steps)", test_current),
        ("Tool Use", test_tool_use),
    ]
    
    all_results = []
    for name, fn in tests:
        print(f"\n--- {name} ---")
        try:
            r = fn()
            all_results.append(r)
            print(f"  ⏱️  Total: {r['total']:.1f}s")
            for k, v in r.items():
                if k.startswith("t_") and isinstance(v, float):
                    print(f"     {k}: {v:.2f}s")
            print(f"  📝 {r['answer'][:150]}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            import traceback; traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("RESUMO")
    print(f"{'='*60}")
    for r in all_results:
        print(f"  {r['total']:5.1f}s  {r['method']}")
