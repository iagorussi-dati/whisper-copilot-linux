# Testes de Integração — Whisper Copilot

## Objetivo
Garantir que o fluxo completo funciona após qualquer mudança. Rodar com:
```bash
cd ~/whisper-copilot-lite-linux && python tests/test_fluxo.py
```

## O que cobre

### 1. Carregamento de Templates
- Discovery carrega e tem >5000 chars
- Consultor Técnico carrega e tem >5000 chars
- Sugestões carrega

### 2. Classificação (Chamada 1)
- Pergunta direta → SIM
- Sem pergunta → NAO
- Concorrente mencionado → CONCORRENTE: SIM
- Sem concorrente → CONCORRENTE: NAO
- Pontos extraídos não vazios

### 3. Snapshot Discovery (Chamada 2)
- Com pergunta → responde com 📌 + 💬
- Sem pergunta → sugere perguntas
- Concorrente → diferencia com fatos
- Não corta (termina com frase completa)

### 4. Snapshot Consultor Técnico
- Com pergunta → 📌 dado + 💬 como falar
- Sem pergunta → sugere 3 perguntas
- Concorrente → web search + diferenciação
- Não corta

### 5. Intervalo de Checkpoint
- Snapshot 1 recebe contexto completo
- Snapshot 2 recebe SÓ intervalo desde snap 1
- Snap 2 não repete conteúdo do snap 1

### 6. Fullcontext
- Pega conversa toda
- Separa por temas/categorias
- Tem próximos passos no final
- Não corta

### 7. Web Search
- Query gerada é limpa (não transcrição crua)
- Concorrente → query inclui comparação
- Resultados > 50 chars

### 8. Cache
- Pre-warm funciona
- Chamadas seguintes usam cache (cache read > 0)

## Histórico de Atualizações

| Data | Mudança | Teste adicionado |
|---|---|---|
| 2026-04-24 | Classificação SIM/NAO | Seção 2 |
| 2026-04-24 | Detecção de concorrente | Seção 2 |
| 2026-04-24 | Web search com query inteligente | Seção 7 |
| 2026-04-24 | Pontos cruciais na chamada 1 | Seção 2 |
| 2026-04-24 | Duas chamadas pro consultor técnico | Seção 4 |
| 2026-04-27 | Duas chamadas pra discovery/sugestões | Seção 3 |
| 2026-04-27 | Intervalo de checkpoint (não contexto completo) | Seção 5 |
| 2026-04-27 | Pre-warm com _raw_system_prompt | Seção 8 |
| 2026-04-27 | cachePoint no Bedrock | Seção 8 |
| 2026-04-27 | Tokens livres (5120 max) | Seção 3, 4, 6 |
