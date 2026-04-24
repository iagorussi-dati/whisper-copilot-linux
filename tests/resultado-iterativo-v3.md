# Teste Iterativo v3 — Classificação SIM/NAO


============================================================
SEM PERGUNTA — experiência AWS [Classificação: **NAO**]
============================================================

### Conversa

**Contexto:**  
Você tem 4-5 anos de experiência com AWS, trabalhando com EC2, Elastic Beanstalk, Lambda, CloudFront e S3. Isso indica que já está familiarizado com serviços computação, armazenamento e distribuição de conteúdo. Para avançar na conversa e entender suas necessidades ou objetivos específicos, preciso de mais detalhes sobre seus desafios atuais ou projetos futuros.

📌 Você tem experiência intermediária com AWS, cobrindo serviços essenciais de compute, storage e CDN. Para direcionar a conversa, vamos precisar entender seus objetivos ou desafios atuais.

💬 Perguntas pra fazer:
- "Qual é o principal desafio ou objetivo que vocês estão tentando alcançar com a infraestrutura atual? (ex: reduzir custos, melhorar performance, escalar para mais usuários)"
- "Vocês têm métricas de desempenho ou de custo que queiram melhorar? (ex: tempo de resposta, custo por usuário, disponibilidade)"
- "Existe alguma necessidade específica de compliance ou requisitos regulatórios que precisamos considerar na arquitetura?"   

> Obs: Com essas perguntas, conseguimos entender a dor do cliente e direcionar a solução de forma mais precisa.   


============================================================
SEM PERGUNTA — stack atual [Classificação: **NAO**]
============================================================

 📌 Entendi que vocês usam Elastic Beanstalk, Aurora, OpenSearch e DynamoDB. Isso já é uma boa base pra entender a arquitetura atual.

💬 Perguntas pra fazer:
- "Qual o principal desafio atual: escalabilidade, custo ou tempo de deploy?"
- "Vocês têm métricas de pico de requisição ou consumo de recursos?"
- "Quais são os planos de crescimento nos próximos 6 meses?"


============================================================
COM PERGUNTA — Lambda vs Cloud Functions [Classificação: **SIM**]
============================================================

 📌 AWS Lambda tem timeout padrão de 15 minutos por execução. Se precisar de tempos mais longos, o serviço máximo suportado é de 60 minutos — mas isso exige configuração específica no momento da criação da função e não é recomendado para tarefas muito longas. Para jobs que demoram mais de 1 hora, o melhor é usar Fargate ou EC2. Google Cloud Functions ainda tem timeout máximo de 9 minutos — não mudou de 2024 pra cá.

💬 Como falar pro cliente:  
- "Na AWS, função Lambda roda até 15 minutos por padrão, mas dá pra aumentar pra 60 minutos se configurar certo."  
- "Se a tarefa demorar mais que isso, o ideal é usar outro serviço — Fargate ou EC2 — porque não tem como passar de 60 minutos no Lambda."  
- "Na Google, o limite ainda é 9 minutos — se vocês precisam de mais tempo, AWS é mais flexível." 


============================================================
COM PERGUNTA — Redis sem uso [Classificação: **NAO**]
============================================================

 📌 Você tem um Redis local instalado mas inativo, e não sabe se era pra usar como cache. Precisa entender se vale a pena ativar ou migrar pra algo na nuvem.

💬 Perguntas pra fazer:  
- "Qual era a intenção original de usar Redis aqui? Cache de banco, sessão de usuários, ou outra coisa?"  
- "Quanto de tráfego ou quantas requisições vocês têm hoje que precisaria de cache?"  
- "Vocês têm algum requisito de alta disponibilidade ou compliance que mudaria a escolha do cache?"   
