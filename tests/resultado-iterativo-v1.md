# Teste Iterativo v1 — Consultor Técnico (prompt atualizado)

Prompt: assistente-objetivo.md (11281 chars)
Web search: query gerada pelo modelo

## SNAP 1 — Cliente fala experiência AWS (EC2, Lambda, CloudFront, S3)

🔍 Query: aws services ec2 s3 cloudfront lambda usage AWS 2026

📌 Com 4-5 anos de experiência em EC2, Elastic Beanstalk, Lambda, CloudFront e S3, você já tem uma base sólida na AWS. Em 2026, alguns pontos úteis para aprofundar ou atualizar são:

1. **Fargate**: Se você já usa EC2 e Elastic Beanstalk, vale a pena avaliar o Fargate para containers. Ele elimina a necessidade de gerenciar servidores, escalando automaticamente apenas os containers necessários. O tempo de deploy costuma ser até 50% mais rápido que o Elastic Beanstalk.

2. **Serverless com Lambda**: Com sua experiência em Lambda, em 2026, o Lambda agora suporta até **10 GB de memória** e **timeout de 15 minutos**, permitindo tarefas mais pesadas. Além disso, a integração com S3 triggers está mais eficiente, permitindo processamento de arquivos em tempo real com latência reduzida.

3. **CloudFront Functions**: Lançado em 2025, o CloudFront Functions permite executar JavaScript leve na edge em **milissegundos**, ideal para manipulações de headers, redirecionamentos ou validações simples, sem precisar de Lambda@Edge. Isso pode simplificar seu fluxo de CDN.

4. **S3 Avançado**: O S3 agora tem **S3 Object Lambda** totalmente integrado, permitindo que você execute código Lambda para processar dados **no momento do acesso**, sem copiar ou mover objetos. Útil para cenários de transformação de dados em tempo real (ex.: redimensionar imagens, mascarar dados sensíveis).

5. **Terraform e IaC**: Com sua experiência em EC2, S...

⚠️ ANÁLISE: Resposta LONGA DEMAIS. Listou 5 features sem pergunta específica. Deveria ter identificado que não tinha pergunta e sugerido próxima pergunta.

---

## SNAP 2 — Migração Google→AWS, Cloud Functions vs Lambda, tempo de execução

🔍 Query: terraform aws vs google cloud functions comparison AWS 2026

📌 AWS Lambda tem limite de 15 minutos por execução em 2026. Se precisa de tarefas mais longas, o melhor é usar Fargate ou EC2.
Para comparar com Google:
- Cloud Functions (2ª geração) = baseado em Cloud Run = não tem limite de tempo, mas recomenda-se até 60 minutos.
- Cloud Run = mesmo modelo, ideal para workloads de média duração.
- AWS Lambda = 15 minutos rígido.

Se o tempo médio das functions for acima de 15 minutos, recomendo migrar essas para Fargate (containers) ou ECS/EKS com auto-scaling.

💬 Como falar pro cliente:
- "Na AWS, Lambda tem limite de 15 minutos — se suas functions passam disso, vamos usar Fargate que não tem esse limite."
- "Na Google, Cloud Functions 2ª geração não tem esse limite, mas na AWS a solução equivalente pra tarefas longas é o Fargate."
- "Vamos verificar o tempo médio das suas functions — se passar de 15 minutos, a gente já planeja migrar pra Fargate que é mais adequado."

✅ ANÁLISE: BOM. Resumido, direto, respondeu a pergunta, deu alternativa, 💬 separado.

---

## SNAP 3 — Redis local sem uso claro

🔍 Query: redis local cache service inactive status AWS 2026

📌 Se o Redis está parado e não tem uso claro, melhor desligar pra economizar recursos e evitar riscos de segurança. Se for migrar pra AWS, o ElastiCache for Redis é a opção nativa — 100% compatível com Redis, gerenciado pela AWS. Custo a partir de ~USD 13/mês por nó (micro).

💬 Como falar pro cliente:
- "Se não está em uso, o melhor é desligar — evita custo de infra e risco de segurança."
- "Se um dia precisar de cache, o ElastiCache da AWS é Redis compatível e totalmente gerenciado — a gente não precisa se preocupar com manutenção."
- "O custo começa em USD 13 por mês pra um nó pequeno — se for usar, a gente coloca na proposta."

✅ ANÁLISE: BOM. Curto, objetivo, com preço e alternativa.

---

## SNAP 4 — Sidecar e jobs

🔍 Query: background jobs sidecar service integration AWS 2026

📌 Jobs em background e sidecars são suportes comuns em microservices.

Para jobs em background a AWS recomenda:
- EventBridge Scheduler (suporta tasks até 1h, com precisão de 1 minuto)
- ECS Fargate com schedule via CloudWatch Events (para tasks recorrentes)
- Step Functions para orquestração de múltiplas tasks

Para sidecars:
- ECS Fargate suporta múltiplos containers por task (sidecar padrão)
- EKS tem implementação de sidecar via Kubernetes patterns
- Service Connect no ECS injeta automaticamente um sidecar proxy para service mesh

O custo de tasks em background depende do tempo de execução — EventBridge Scheduler é gratuito até 1 milhão execuções/mês.

💬 Como falar pro cliente:
- "Para jobs em background, usamos o EventBridge Scheduler — é simples e gratuito até 1 milhão de execuções por mês."
- "Se precisar de sidecar, no ECS Fargate dá pra colocar quantos containers precisarem na mesma task — cada um roda independente."
- "No EKS também temos sidecar padrão com Kubernetes — se vocês já usam, é a mesma coisa."

✅ ANÁLISE: BOM. Organizado, com opções claras e custo.

---

## SNAP 1 v2 (após ajuste de prompt) — Cliente fala experiência AWS

📌 Com 4-5 anos de experiência em EC2, Elastic Beanstalk e Lambda, vale a pena focar em duas tendências de 2026 que vão elevar sua eficiência:

1. Graviton5 nos novos M9g instances: 192 núcleos ARM, 25% mais performance geral que gerações anteriores — ideal pra workloads em EC2 que já estão otimizados pra ARM.
2. Elastic Beanstalk agora tem integração direta com Lambda para event-driven — você pode definir funções Lambda como handlers de requisições HTTP sem configurar API Gateway manualmente.

Além disso, CloudFront tem novo recurso de edge functions em todas as regiões, permitindo executar JavaScript no edge com latência <10ms para casos como personalização de headers ou redirects dinâmicos.

💬 Como falar pro cliente:
- "Com os novos processadores Graviton5, EC2 ganha até 25% mais performance — se vocês têm workloads em ARM, compensa migrar pra M9g."
- "O Elastic Beanstalk agora conecta direto com Lambda sem precisar de API Gateway — simplifica o deploy de microserviços event-driven."
- "CloudFront agora executa funções no edge em todas as regiões, ideal pra ajustes rápidos em requisições com latência mínima."

⚠️ ANÁLISE: MELHOR que v1 (3 pontos vs 5), mas ainda lista features sem pergunta. Aceitável pra contexto onde o cliente está se apresentando.

---

## SNAP 2 v2 (após ajuste) — Cloud Functions vs Lambda

📌 AWS Lambda tem timeout máximo de 15 minutos por execução em 2026. Não tem como ultrapassar isso — se precisar de processos mais longos, a alternativa é usar Fargate ou EC2. O tempo médio de execução na maioria dos casos é de segundos a poucos minutos. Pra jobs longos, o padrão é dividir em etapas ou usar Step Functions pra orquestrar.

💬 Como falar pro cliente:
- "O Lambda na AWS tem limite de 15 minutos por execução — se precisar de mais tempo, a gente migra esse processo pro Fargate ou EC2."
- "O tempo médio de execução costuma ser bem menor — a maioria das functions roda em segundos ou alguns minutos."
- "Se vocês têm jobs que passam dos 15 minutos, a gente pode usar Step Functions pra dividir em etapas ou Fargate pra ficar mais robusto."

✅ ANÁLISE: PERFEITO. Curto, direto, respondeu a pergunta, deu alternativa.
