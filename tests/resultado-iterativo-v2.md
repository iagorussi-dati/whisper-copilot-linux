# Teste Iterativo v2 — Com/Sem pergunta


============================================================
SEM PERGUNTA — Cliente fala experiência
============================================================

📌 Com 4-5 anos de experiência em EC2, Elastic Beanstalk, Lambda, CloudFront e S3 você já domina os pilares essenciais da AWS. Em 2026, dois pontos importantes: todos esses serviços têm novas versões com otimizações de custo e performance — EC2 G6 (GPU para IA generativa) e Lambda com snapStart em mais linguagens (agora suporta Python e Java). Além disso, o CloudFront tem suporte nativo a edge computing com functions em JavaScript no edge.

💬 Como falar pro cliente:
- "Seu conhecimento atual já cobre a base da AWS — EC2, Lambda, S3 e CloudFront são o core de qualquer arquitetura."
- "Agora em 2026 o Lambda tem snapStart pra Python também — reduz o cold start em até 70% se vocês usarem."
- "Se quiserem otimizar custo e performance, podemos migrar pro EC2 G6 ou usar edge functions no CloudFront."


============================================================
SEM PERGUNTA — Cliente descreve stack atual
============================================================

📌 O Elastic Beanstalk é bom pra orquestração simples mas tem limites de customização. Se vocês grows em escala, vale a pena migrar pra ECS Fargate ou EKS — deploy mais rápido e auto-scaling mais fino. O Aurora já está bom — é compatível com MySQL e PostgreSQL, então não tem surpresa. O OpenSearch integrado com DynamoDB via zero-ETL (lançado em 2026) é um ganho de performance: dados do Dynamo vão direto pro OpenSearch sem ETL manual, economia de 15-20% de custo de infra por não precisar de Lambda de sync. O DynamoDB é ótimo pra casos de baixa latência e alta taxa de escrita — mas se vocês usam pra leitura pesada, talvez valha migrar pra Aurora ou revisar os acessos.

💬 Como falar pro cliente:
- "O Elastic Beanstalk é bom pra começar, mas se vocês quiserem mais controle e escalabilidade, migrar pro ECS Fargate é o próximo passo."
- "A integração zero-ETL entre DynamoDB e OpenSearch já tá disponível — dados passam direto sem você precisar configurar nada, e o custo cai uns 15%."
- "Se o Dynamo está sendo usado pra leitura pesada, talvez valha a pena repensar — Aurora pode ser mais eficiente nesse caso."


============================================================
COM PERGUNTA — Cloud Functions vs Lambda
============================================================

📌 AWS Lambda tem timeout máximo de 15 minutos por execução. Se precisar de tarefas mais longas, o padrão é usar Fargate ou EC2. Google Cloud Functions 2ª geração (baseada em Cloud Run) permite até 60 minutos de execução — isso mudou muito em 2025/2026.

💬 Como falar pro cliente:  
- "Na AWS, funções Lambda não passam de 15 minutos — se a tarefa for mais longa, a solução é usar Fargate ou EC2."  
- "Na Google, a segunda geração das functions permite até 60 minutos — mas isso já é bem diferente do modelo da AWS."  
- "Se vocês têm tarefas que demoram mais de 15 minutos, na AWS a gente recomenda outro serviço — não é possível estender o Lambda."


============================================================
COM PERGUNTA — Redis sem uso
============================================================

📌 Redis é um banco de dados em memória rápido, ideal pra cache, sessões, filas. Se hoje não está ativo, avaliar se realmente precisa antes de migrar. Se for usar, AWS oferece ElastiCache for Redis (gerenciado) — elimina trabalho de infra e tem alta disponibilidade. Custo em 2026: instância cache.t4g.micro (menor) sai por ~ US$0,025/hora na região SP — barato pra maioria dos casos.

💬 Como falar pro cliente:
- "Se vocês não usam hoje, o primeiro passo é ver se realmente precisam — às vezes cache não traz ganho se o banco já é rápido."
- "Se for usar, o ElastiCache da AWS é gerenciado — vocês não precisam configurar nada de infra, só usar."
- "O custo é baixo — a menor instância sai menos de R$200 por mês na região SP. Vale a pena se realmente houver necessidade."
