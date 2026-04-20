# Resultado dos Testes — 2026-04-20

## Teste 1: 4min-teste (Migração AWS — apresentação de proposta)

### Contexto
Reunião entre Rafa (cliente) e Cris (consultor) sobre migração de infraestrutura para AWS.
2 snapshots de 2min cada.

### Snapshot 1 (0-2min)
> ⚠️ "Cris, você mencionou que alguns serviços funcionarão de forma diferente na AWS — quais são os principais impactos disso para a gente no dia a dia?"

✅ **Pergunta pronta, natural, relevante ao trecho.** Cris estava explicando a arquitetura e a sugestão aprofunda.

### Snapshot 2 (2-4min)
> ⚠️ "Você mencionou que o Step Functions faz retry de 2 a 3 vezes em falhas — isso pode impactar a latência percebida pelo usuário final em casos de erro?"

✅ **Não repetiu o snapshot 1.** Focou no tema novo (Step Functions, retry, filas FIFO). Pergunta técnica pertinente.

### Full Context (Win+H)
> ⚠️ "Você falou que dados serão gravados no S3 para depois serem consultados pelo ATI — qual é o tempo esperado entre gravação e disponibilidade desses dados?"

✅ **Analisou a conversa inteira e trouxe ponto que não foi coberto nos snapshots.**

### Avaliação
- Fluxo incremental: ✅ Cada snapshot trouxe sugestão nova
- Não repetiu: ✅
- Tom de pergunta pronta: ✅
- Relevância: ✅

---

## Teste 2: Discovery (Reunião comercial — EKS/containers)

### Contexto
Discovery com Reginaldo (cliente, venda de ingressos) e consultores. 4 snapshots de 2min.

### Snapshot 1 (0-2min)
> ⚠️ "Entendi, a volatilidade do tráfego do site de vendas de ingressos exige escalabilidade automática, certo?"
> 💡 "Vocês já avaliaram os custos atuais..."

✅ **Captou o tema central (escalabilidade) e fez pergunta direta.**

### Snapshot 2 (2-4min)
> ⚠️ "Trabalhar com containers vai exigir adaptação do seu atual workflow de desenvolvimento — vocês já têm algum conhecimento em Kubernetes ou precisam..."

✅ **Tema novo (containers/Kubernetes). Não repetiu escalabilidade.**

### Snapshot 3 (4-6min)
> ⚠️ "O site de vendas de ingressos já teve picos que causaram queda ou lentidão?"
> 💡 "Vocês precisam que a migração para containers inclua também a infra..."

✅ **Aprofundou dor do cliente (picos de tráfego). Pergunta direta.**

### Snapshot 4 (6-8min)
> ⚠️ "Usar Norte da Virgínia pode reduzir custos, mas precisamos validar se a latência para usuários brasileiros é aceitável — vocês já mediram isso?"

✅ **Tema novo (região AWS, latência). Combinou informação + pergunta.**

### Full Context (Win+H)
> ⚠️ "A latência da região Norte da Virgínia para usuários brasileiros realmente preocupa vocês no pico de vendas?"
> 💡 "Vocês precisam que a migração para containers..."

✅ **Panorama geral, priorizou o ponto mais crítico (latência + picos).**

### Avaliação
- Fluxo incremental: ✅ 4 snapshots, 4 temas diferentes
- Não repetiu: ✅ Cada snapshot focou no trecho novo
- Tom de pergunta pronta: ✅ Todas são frases que a pessoa pode falar
- Relevância: ✅ Captou dores reais (escalabilidade, containers, latência)
- Full context vs snapshot: ✅ Full context mais analítico

---

## Teste 3: Migração AWS (arquivo curto, 1 snapshot)

### Snapshot 1 (inteiro)
> ⚠️ "Você quer que eu destaque quais serviços terão mudança significativa na operação?"
> 💡 "Quais funcionalidades são críticas pra vocês nesse momento..."

✅ **Pergunta pronta e relevante.**

### Full Context
> "O que ficou sem resposta: Entendimento do nível de conhecimento do Rafa..."

✅ **Modo analítico, identificou gaps na conversa.**

---

## Comparação: Antes vs Depois

### Antes (teste 01)
> 🔴 "Renata, exija imediatamente de Pessoa 1 o nome e cargo exato do decisor de custos"

❌ Tom de instrução, não de pergunta pronta.

### Depois (teste atual)
> ⚠️ "Com que frequência vocês usam esse armazenamento hoje?"
> 💡 "Vocês já avaliaram os custos atuais da infraestrutura?"

✅ Pergunta pronta, natural, que a pessoa pode falar diretamente.

---

## Métricas

| Métrica | Valor |
|---|---|
| Testes executados | 3 |
| Snapshots totais | 7 |
| Sugestões com tom correto (pergunta pronta) | 7/7 (100%) |
| Snapshots sem repetição | 7/7 (100%) |
| Full context mais analítico que snapshot | 3/3 (100%) |
| Tempo médio snapshot (transcrição + resposta) | ~10s |
| Tempo médio full context (sem transcrição) | ~5s |

## Conclusão
- Prompt de sugestões reescrito funciona: frases prontas, tom natural
- Snapshot incremental segue o fluxo sem repetir
- Full context dá panorama completo e pode repetir pontos-chave
- Speaker ID funcionou bem (identificou Rafa, Cris, Reginaldo por nome)
