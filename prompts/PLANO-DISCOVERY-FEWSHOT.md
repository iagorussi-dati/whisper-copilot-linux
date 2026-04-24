# Plano — Few-shot Discovery Dati

## Objetivo
Montar o prompt `discovery-dati.md` com few-shot examples extraídos de 5 reuniões reais de discovery.

## Estrutura do prompt final

1. **IDENTIDADE** — Quem é o copiloto, o que é a Dati, serviços, diferenciais
2. **COMPORTAMENTO** — Modo sugestões, frases prontas pro comercial, regras
3. **FORMATAÇÃO** — Emojis, estrutura das sugestões
4. **OBSERVAÇÃO** — O que NÃO fazer (narrar, ser técnico demais, etc.)
5. **EXEMPLOS (few-shot)** — ~40 situações organizadas por categoria

## Formato de cada exemplo

```
### [Categoria] — Situação N

**SITUAÇÃO:**
Cliente: "transcrição real"

**Abordagem 1 — Foco: [ângulo]**
💡/⚠️/🔴/✅ "frase pronta 1"
💡/⚠️/🔴/✅ "frase pronta 2"
💡/⚠️/🔴/✅ "frase pronta 3"
✅ "frase pronta 4"
> Obs: por que essa abordagem faz sentido nesse contexto

**Abordagem 2 — Foco: [outro ângulo]**
(mesma estrutura)

**Abordagem 3 — Foco: [outro ângulo]**
(mesma estrutura)

**Abordagem 4 — Foco: [outro ângulo]**
(mesma estrutura)
```

## Categorias e quantidade de situações

| # | Categoria | Situações | Fonte principal |
|---|---|---|---|
| 1 | Entendimento do negócio | 6 | 01,02,03,04,05 |
| 2 | Stack técnica / infra | 6 | 01,02,03,04 |
| 3 | Billing / forma de pagamento | 5 | 02,03 |
| 4 | Dores e problemas | 7 | 01,02,03,04,05 |
| 5 | Orçamento / timeline | 5 | 04,05 |
| 6 | Ofertas / oportunidades Dati | 6 | 02,03,04,05 |
| 7 | Próximos passos / fechamento | 5 | 01,02,04,05 |
| **Total** | | **~40** | |

## Processo

1. ✅ Ler e analisar 5 transcrições
2. ✅ Mapear 42 situações em 7 categorias
3. ✅ Definir formato (situação + 4 abordagens + obs)
4. ✅ Validar formato com usuário
5. ⬜ Montar identidade + comportamento + formatação + observação
6. ⬜ Montar few-shot categoria 1 — Entendimento do negócio (6)
7. ⬜ Montar few-shot categoria 2 — Stack técnica (6)
8. ⬜ Montar few-shot categoria 3 — Billing (5)
9. ⬜ Montar few-shot categoria 4 — Dores (7)
10. ⬜ Montar few-shot categoria 5 — Orçamento/timeline (5)
11. ⬜ Montar few-shot categoria 6 — Ofertas Dati (6)
12. ⬜ Montar few-shot categoria 7 — Próximos passos (5)
13. ⬜ Revisar e ajustar com usuário
