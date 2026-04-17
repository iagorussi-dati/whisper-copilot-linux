# Whisper Copilot Lite — Benchmarks e Arquitetura v1

## Modos de Operação

### Modo Sugestões
- Transcrição automática a cada X minutos
- A cada chunk: Groq transcreve → Bedrock identifica speakers + gera sugestões
- Sugestões aparecem no painel principal (sem popup)
- Espaço/SUPER+Espaço = força transcrição + sugestão agora
- Formatação controlada pelo app (emoji + frase curta)
- Opções: curtas (3 sugestões, 256 tokens) ou completas (10 sugestões, 1024 tokens)

### Modo Copiloto
- Transcrição automática a cada X minutos (só speakers, acumula contexto)
- Espaço/SUPER+Espaço = abre chat flutuante
- Usuário digita instrução ou Enter vazio
- Respostas em texto corrido natural
- Chat persistente com histórico

## Benchmarks de Latência

### Groq Whisper (transcrição)
| Métrica | Valor |
|---|---|
| Modelo | whisper-large-v3-turbo |
| Tempo por chunk 60s | 1.0-1.4s |
| Total 5min (6 chunks) | 6.6s |
| Rate limit (free) | 20 req/min |

### Bedrock Nova 2 Pro (speaker ID por chunk)
| Métrica | Valor |
|---|---|
| Tempo por chunk | 2-8s |
| Total 6 chunks | 19-45s |
| Cache hit system prompt | sim (após warm) |
| Roda em background | sim (usuário não espera) |

### Bedrock Nova 2 Pro (chat final — o que o usuário espera)
| Cenário | TTFT | Total |
|---|---|---|
| 3 sugestões (256 tok) | 0.8s | 1.4-1.9s |
| 5 sugestões (512 tok) | 0.8s | 1.9-2.5s |
| 10 sugestões (1024 tok) | 0.8s | 2.3-3.4s |
| Copiloto texto livre (512 tok) | 0.8s | 4-6s |
| Copiloto instrução (256 tok) | 0.7s | 1.5-2.0s |

### Abordagens testadas (chat final)
| Abordagem | Chat final | Custo total |
|---|---|---|
| A. Baseline (single-turn) | 11.37s | 30.59s |
| B. Prompt cache | 15.33s | 48.60s |
| C. Tudo no final | 19.18s | 19.18s |
| D. Contexto acumulativo | 10.75s | 52.12s |
| E. Multi-turn | 6.86s | 47.58s |
| F. Multi-turn + resumo | 13.09s | 69.53s |
| **G. Streaming + maxTokens** | **1.4-3.4s** | **~20s** |

**Vencedor: Streaming + maxTokens controlado (G)**
- TTFT ~0.8s consistente
- Total depende de quantos tokens gera
- Cache do system prompt funciona

### Insight principal
O gargalo NÃO é processamento do contexto (TTFT ~0.8s sempre).
O gargalo é GERAÇÃO de tokens. Controlar maxTokens = controlar latência.

## Estimativa de Custos

### Groq Whisper
| Uso | Preço |
|---|---|
| Free tier | 20 req/min, suficiente para chunks de 60s |
| Pago | $0.04/hora de áudio |
| Reunião 30min (30 chunks) | ~$0.02 |
| 4 reuniões/dia, 20 dias/mês | ~R$10/mês |

### Bedrock Nova 2 Pro
| Uso | Input | Output |
|---|---|---|
| Preço | $0.80/1M tokens | $3.20/1M tokens |
| Speaker ID por chunk (~500 tok in, ~300 tok out) | $0.0004 | $0.001 |
| Chat final (~2000 tok in, ~200 tok out) | $0.0016 | $0.0006 |
| Reunião 30min (30 chunks + 5 chats) | ~$0.05 | ~$0.04 |
| 4 reuniões/dia, 20 dias/mês | ~R$40-60/mês |

### Otimizações de custo
1. **Cache do system prompt**: reduz input tokens em ~30% (já implementado)
2. **maxTokens baixo**: menos output tokens = menos custo + mais rápido
3. **Modo sugestões curtas**: 256 tok vs 4096 tok = ~16x menos output
4. **Chunks maiores (2min)**: metade das chamadas de speaker ID
5. **Skip chunks silenciosos**: não enviar chunks sem áudio

## Arquitetura do Pipeline

```
[Áudio] → [Groq Whisper] → texto bruto
                              ↓
                    [Bedrock speaker ID] → [Speaker] Texto
                              ↓
                    acumula em _transcript
                              ↓
              [Usuário aperta botão]
                              ↓
                    flush áudio restante → Groq → Bedrock speaker ID
                              ↓
                    [Chat / Sugestões]
                    ├── Modo Sugestões: APP_FORMAT + maxTokens controlado
                    └── Modo Copiloto: texto livre + clean_md fallback
                              ↓
                    [Bedrock streaming] → resposta incremental
```

## System Prompts

### Regra: system prompt = contexto/comportamento, NÃO formato
- Formato de sugestão é injetado pelo app (APP_FORMAT_SUGGESTION)
- Modo copiloto: app injeta "responda em texto corrido"
- clean_md() como fallback para remover markdown residual

### Templates disponíveis
- Discovery Comercial (Dati): vendas, Problem Canvas, 5W2H
- Consultor Técnico: arquitetura AWS, trade-offs, requisitos não-funcionais
- Piadas e Humor
- Copiloto de Vendas
- Custom (upload .md/.txt)
