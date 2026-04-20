# Teste 01 — Reunião Discovery Conti/Renata x Altomax

## Resultado Geral
O copiloto atuou bem na identificação de riscos e geração de sugestões durante a reunião de discovery comercial. Porém, os prompts e o fluxo de snapshot precisam de ajustes significativos.

## O que funcionou
- Identificação de speakers pela IA (Bedrock)
- Transcrição em tempo real via Groq Whisper
- Sugestões com emojis de prioridade (🔴 ⚠️ 💡 ✅)
- Análise baseada em Problem Canvas e 5W2H
- Resumo final com análise crítica detalhada

## Problemas Identificados

### 1. Modo Sugestões — Tom errado
**Problema:** As sugestões vêm como instruções genéricas ("Renata, pergunte X"). Deveria soar como se fosse a própria pessoa fazendo a pergunta naturalmente.

**Atual:**
> 🔴 "Renata, exija imediatamente de Pessoa 1 o nome e cargo exato do decisor de custos"

**Esperado:**
> 🔴 "Vocês estão usando o Forecast pra isso?"
> ⚠️ "Pode me explicar melhor a situação do projeto de vocês?"
> 💡 "Quem seria o responsável técnico pra gente alinhar a implementação?"

**Ação:** Reescrever o prompt `sugestoes.md` para que as sugestões sejam frases prontas que a pessoa pode falar diretamente, como se fosse ela perguntando.

### 2. Fluxo de Snapshot (SUPER+D) — Contexto parcial
**Problema atual:** O snapshot pega todo o áudio acumulado desde o início da gravação ou desde o último snapshot. Não há distinção entre "quero sugestão pro trecho atual" e "quero análise do contexto inteiro".

**Comportamento desejado:**
- **SUPER+D (Snapshot):** Pega o contexto desde o último SUPER+D (ou início se for o primeiro). O Bedrock responde com sugestões rápidas baseadas nesse trecho. Depois continua gravando. Se apertar SUPER+D de novo, pega só o trecho novo (do último SUPER+D até agora), mas mantém o tom da conversa.
- **Novo atalho (SUPER+F ou outro):** Snapshot do contexto INTEIRO da sessão. O Bedrock analisa toda a transcrição acumulada e dá sugestões/análise mais profunda baseada na conversa completa.

**Ação:** Implementar dois tipos de snapshot:
1. `snapshot` (SUPER+D) — trecho incremental, sugestões rápidas
2. `full_snapshot` (novo atalho) — contexto completo, análise profunda

### 3. Modo Sugestões — Deve responder perguntas do cliente
**Problema:** Quando o cliente (alvo) faz uma pergunta pertinente, o copiloto deveria sugerir uma resposta, não apenas gerar mais perguntas.

**Exemplo:** Se o cliente pergunta "Vocês trabalham com Amazon Q?", o copiloto deveria sugerir:
> ✅ "Sim, trabalhamos! Inclusive temos cases de implementação em empresas do mesmo segmento."

**Ação:** Ajustar o prompt para que o copiloto identifique perguntas do cliente e sugira respostas prontas.

## Próximos Passos
- [ ] Reescrever `prompts/sugestoes.md` com tom de pergunta natural
- [ ] Implementar `full_snapshot` com novo atalho global
- [ ] Ajustar prompt pra responder perguntas do cliente/alvo
- [ ] Testar novamente com gravação real
