# Proposta: Strands Agents — Tool Use Nativo

## Objetivo
Testar se o Bedrock com tool use (via Strands SDK) gera respostas melhores que o fluxo manual atual, deixando o modelo decidir sozinho quando pesquisar.

## O que muda

### Hoje (fluxo manual)
```
Transcrição → Regex detecta keywords → Busca DuckDuckGo → Bedrock gera resposta
```
- Decisão de buscar é hardcoded (lista de keywords: "azure", "google", "?", "como", etc)
- Se o modelo achar que precisa pesquisar algo que não está na lista, não pesquisa
- 2 chamadas ao Bedrock (1 pra checar se busca, 1 pra responder)

### Proposta (Strands Agent com tools)
```
Transcrição → Agent recebe tools disponíveis → Modelo decide sozinho → Resposta
```
- Modelo decide autonomamente quando usar cada tool
- Pode chamar múltiplas tools na mesma resposta
- 1 chamada ao Agent (internamente 2 round-trips ao Bedrock)

## Tools propostas

### 1. web_search (já existe)
```python
@tool
def web_search(query: str) -> str:
    """Pesquisa informações atualizadas na web. Use para:
    - Comparar AWS com concorrentes
    - Buscar preços e specs atualizados
    - Verificar informações que o cliente mencionou"""
    from backend.search import web_search as ws
    return ws(query, max_results=3)
```

### 2. aws_docs_search (nova — grátis)
```python
@tool
def aws_docs_search(query: str) -> str:
    """Pesquisa documentação oficial da AWS. Use para:
    - Detalhes técnicos de serviços AWS
    - Preços e limites
    - Best practices e arquiteturas"""
    from backend.search import web_search as ws
    return ws(f"site:docs.aws.amazon.com {query}", max_results=3)
```

## Implementação mínima (teste)

```python
# pip install strands-agents strands-agents-tools
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

copilot = Agent(
    model=model,
    system_prompt=system_prompt,  # mesmo prompt atual
    tools=[web_search, aws_docs_search]
)

# Em vez de toda a lógica manual de _generate_snapshot_response:
result = copilot(f"Transcrição do trecho:\n{pontos}\n\nGere sugestões.")
```

## Custos
- **Strands SDK**: grátis (open source)
- **Bedrock**: mesmo custo (~$0.80/1M tokens). Tool use adiciona ~1 round-trip extra quando usa tool.
- **Web search**: R$0 (DuckDuckGo continua grátis)
- **Estimativa**: +R$2-5/mês no máximo

## O que testar
1. Criar um `backend/agent.py` com o Agent Strands
2. Rodar os mesmos cenários dos testes existentes (transcrições em `transcricoes/`)
3. Comparar:
   - Quando o modelo decide pesquisar vs quando o regex decide
   - Qualidade das respostas com/sem tool use
   - Latência (espera-se similar ou melhor)
4. Documentar em `tests/resultado-strands-agent.md`

## Decisão
- Se as respostas forem significativamente melhores → migrar `_generate_snapshot_response` pra usar Agent
- Se forem similares → manter fluxo manual (mais simples, menos dependências)
- Independente do resultado, a tool `aws_docs_search` pode ser adicionada ao fluxo atual sem Strands

## Próximo passo (sem Strands)
Melhoria rápida que pode ser feita já: trocar a query de web search pra priorizar docs AWS:
```python
# Antes
query = "AWS vs Azure 2026"
# Depois  
query = "site:aws.amazon.com OR site:docs.aws.amazon.com AWS vs Azure"
```
