# Protocolo de Testes — Whisper Copilot

## Quando usar
Toda vez que o Iago pedir "testes", "teste completo", ou "roda os testes", seguir este protocolo.

## Estrutura: mínimo 110 testes

### Lotes de 10, rodar um por vez, analisar, ajustar se necessário, depois seguir.

---

## Categorias obrigatórias (10 testes cada = 11 categorias)

### 1. Naturalidade básica (10)
Cenários do dia a dia: daily, fofoca, receita, viagem, reclamação, treino, piada, clima, comida, história engraçada.
- Critério: zero padrões robóticos ("analisando", "identificação dos participantes", "trecho mais recente", "contexto da conversa", "ponto central", "vamos analisar", "baseado no contexto")

### 2. Edge cases (10)
Silêncio (1 palavra), inglês, monólogo, gírias, reunião chata, código, música, reclamação de trabalho, transcrição com ruído, conversa desconectada.
- Critério: não quebrar, não inventar, não entrar em modo analista

### 3. Sem instrução — auto_response=true (10)
Copiloto responde sozinho após snapshot, sem o usuário digitar nada.
Cenários variados: daily, futebol, podcast, reunião, bate-papo.
- Critério: resposta útil e natural mesmo sem instrução, não ficar perdido

### 4. Com instrução — auto_response=false (10)
Usuário digita instrução após snapshot: "me faz rir", "resume", "traduz", "o que perguntar?", "me dá argumentos", "fala como X", "explica pra leigo", etc.
- Critério: seguir a instrução, manter tom natural, não ignorar o que foi pedido

### 5. Modo full (10)
Mesmos cenários dos lotes 1-4 mas no modo full (300 tokens).
- Critério: resposta mais completa mas ainda natural, sem virar relatório

### 6. Transmissões/YouTube/Twitch (10)
Futebol, podcast tech, live coding, documentário, game stream, aula, etc. Sempre com contexto extra definido.
- Critério: entender que é uma transmissão, comentar naturalmente

### 7. Respeito ao tamanho de resposta (10)
Testar os 3 modos com o MESMO cenário e verificar:
- **short** (150 tokens): resposta curta, 2-4 frases, < 400 chars
- **full** (300 tokens): resposta média, 4-8 frases, < 800 chars
- **research** (600 tokens): resposta longa, detalhada, < 1500 chars
- Critério: short < full < research em tamanho. Short não pode ser um textão.

### 8. Modo Sugestões (10)
Testar com prompt de sugestões: frases prontas, tom de pergunta, emoji + frase.
- Critério: formato correto (emoji + frase entre aspas), não repetir entre snapshots

### 9. Consultor Técnico AWS (10)
Testar com prompt técnico + web search: preços, specs, comparações.
- Critério: dados da web, resposta técnica, web search ativado

### 10. Snapshot incremental (10)
Simular 3-4 snapshots sequenciais da mesma conversa.
- Critério: cada snapshot foca no trecho novo, não repete sugestões anteriores

### 11. Full context Win+H (10)
Após vários snapshots, testar o full context.
- Critério: visão geral da conversa toda, pode repetir pontos-chave, mais analítico que snapshot

---

## Critérios de aprovação por teste

### Naturalidade (automático)
Verificar ausência de padrões robóticos:
```python
BAD_PATTERNS = [
    "analis", "identificação dos", "trecho mais recente",
    "contexto da conversa", "vou acompanhar como copiloto",
    "baseado no contexto", "vamos analisar", "ponto central é",
    "tema novo é", "dor aqui é",
]
```

### Tamanho (automático)
```python
LIMITS = {
    "short": {"max_chars": 600, "max_lines": 8},
    "full": {"max_chars": 1500, "max_lines": 20},
    "research": {"max_chars": 3000, "max_lines": 40},
}
```

### Coerência (automático + manual)
- Resposta faz sentido com a transcrição?
- Seguiu a instrução do usuário?
- Tom adequado ao contexto (informal/formal)?
- Não inventou informação que não estava na transcrição?

### Latência
- short: < 6s
- full: < 8s
- research (sem search): < 10s
- research (com search): < 15s

---

## Formato de saída

Cada lote imprime:
```
✅ Nome do cenário (Xs)
   Resposta resumida...

❌ Nome do cenário (Xs)
   Resposta resumida...
   ⚠️ Problema: [descrição]
```

No final:
```
RESULTADO: X/10 passaram | Y/10 falharam
```

Total geral no final de todos os lotes:
```
TOTAL: X/110 passaram
Naturalidade: X/100
Tamanho: X/100
Latência: X/100
```

---

## Fluxo de execução

1. Rodar lote 1 (10 testes)
2. Analisar resultados — se < 9/10, ajustar prompt e retestar
3. Rodar lote 2
4. Analisar — ajustar se necessário
5. Repetir até lote 10
6. Gerar relatório final com total

## Após os testes
- Commitar resultados
- Se houve ajustes nos prompts, documentar o que mudou e por quê
- Atualizar TASKS se necessário
