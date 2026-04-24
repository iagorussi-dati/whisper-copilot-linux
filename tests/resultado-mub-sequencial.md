# Teste Snapshots SEQUENCIAIS — Reunião MUB

Simula checkpoints reais: cada snapshot recebe só o intervalo desde o último.
Testa: não repetir, cobrir todos os assuntos, separar temas.


======================================================================
CHECKPOINT 1 [0:00-3:00] — Apresentação + stack + RTO/RPO
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Kevin, o ponto focal aqui vai ser sobre backup, definir melhor o RTO e RPO de vocês. Você consegue me dar uma descrição do que vocês estão usando hoje? A gente tem o Elastic Beanstalk fazendo a orquestração do back-end. Usamos o Aurora como banco. Tem um OpenSearch pra pesquisa. E o DynamoDB em alguns casos. Os clientes estavam exigindo um RTO RPO melhor. A gente não tem formalizado isso, o chefe pediu pra documentar o RTO RPO pra apresentar pros clientes.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
PONTOS: Backup, RTO, RPO, Elastic Beanstalk, Aurora, OpenSearch, DynamoDB

📋 PONTOS EXTRAÍDOS:
Backup, RTO, RPO, Elastic Beanstalk, Aurora, OpenSearch, DynamoDB

📌 RESPOSTA:
### Resumo da Conversa  
O cliente está buscando informações sobre **backup**, **RTO/RPO**, **Elastic Beanstalk**, **Aurora**, **OpenSearch** e **DynamoDB**. Ele quer entender como esses serviços podem ser usados para melhorar a infraestrutura, garantir conformidade e otimizar custos.  

---

### 📌 **Backup**  
- **Serviço principal:** AWS Backup (gerencia políticas centralizadas).  
- **Suporte:** EC2, RDS (incluindo Aurora), EFS, DynamoDB, OpenSearch, S3.  
- **Agendamento:** Diariamente, semanal, mensal.  
- **Custo:** Backup de S3 é ~ \$0,05/GB/mês. RDS/Aurora: ~ \$0,02/GB/mês. Taxa de transferência de dados de backup é cobrada (saída de \$0,09/GB).  

💬 Como falar pro cliente:  
- “O AWS Backup centraliza tudo — vocês definem a política uma vez e ele cuida de EC2, RDS, DynamoDB, etc.”  
- “Custo de backup de banco de dados sai por cerca de 2 centavos por GB ao mês — é bem previsível.”  
- “Dá pra agendar diário pra dados críticos e semanal pro resto, tudo na mesma política.”  

---

### 📌 **RTO e RPO**  
- **Definição:**  
  - **RTO (Recovery Time Objective):** Tempo máximo tolerável de inatividade. Ex: 1 hora.  
  - **RPO (Recovery Point Objective):** Dados máximos que podem ser perdidos. Ex: 15 minutos.  
- **Estratégias:**  
  - **Backup diário + S3 Standard-IA:** RPO de até 24h, RTO de 4-6h.  
  - **Backup cont


======================================================================
CHECKPOINT 2 [3:00-6:00] — Multi-região + failover + custo
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
A gente pode pensar em ambiente duplicado em outra região, geraria RTO RPO muito melhor. Só que dobraria o custo. Duplicar a infra seria um passo ousado demais. Só de curioso, como funciona na prática? Dois load balancers em locais separados, quem faz o meio do caminho? Vocês usam Route 53? Lá tem opção de failover. Se detectar que o load balancer de uma região não tá funcionando, joga pra outra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Ambiente duplicado em outra região. Custo dobrado. Duplicação da infraestrutura. Funcionamento prático de load balancers. Uso do Route 53. Opção de failover.

📋 PONTOS EXTRAÍDOS:
Ambiente duplicado em outra região. Custo dobrado. Duplicação da infraestrutura. Funcionamento prático de load balancers. Uso do Route 53. Opção de failover.

📌 RESPOSTA:
### Resumo da Conversa  
O cliente está buscando informações sobre **ambiente duplicado em outra região**, **custo dobrado**, **duplicação da infraestrutura**, **funcionamento prático de load balancers**, **uso do Route 53** e **opção de failover**.

---

📌 **Ambiente duplicado em outra região**  
Duplicar o ambiente em outra região significa criar uma cópia idêntica da infraestrutura AWS em uma região diferente. Isso inclui EC2, RDS, buckets S3, etc. Todos os recursos são recriados na nova região.  

💬 Como falar pro cliente:  
- "Vamos duplicar toda a sua infraestrutura em outra região — isso garante que você tenha uma cópia exata pronta pra usar se precisar."  
- "Cada serviço, desde máquinas até bancos de dados, será recriado igual na nova região."  
- "Isso demanda planejamento pra garantir que tudo funcione como no ambiente principal."

---

📌 **Custo dobrado**  
Manter um ambiente duplicado em outra região **dobra o custo** porque você está pagando por todos os recursos duas vezes (EC2, armazenamento, dados transferidos, etc.). Não há descontos por duplicação — é o mesmo preço por cada recurso em cada região.

💬 Como falar pro cliente:  
- "Manter a infraestrutura duplicada em outra região vai dobrar o custo — você paga por cada recurso duas vezes."  
- "Não tem desconto por ter dois ambientes — é o custo cheio de cada um."  
- "Mas isso garante alta disponibilidade — você evita perda total se uma região cair."

---

📌 **Duplicação da infraestrutura**  
A duplicação pode ser feita de duas formas:  
1. **Automática** usando AWS CloudFormation ou Terraform — você cria um template e aplica na outra região.  
2. **Manual** — cria cada


======================================================================
CHECKPOINT 3 [6:00-9:00] — Infra exclusiva por cliente + estrutura de contas
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Teve um cliente que quer infraestrutura exclusiva. Banco deles, back-end deles. Tudo duplicado pra atender só um cliente. Acessível somente da rede deles. Não sei se é viável. Vocês teriam que ter uma conta separada só pra esse cliente. Vocês têm estrutura de contas? Não, hoje é uma só. Vocês conseguem ter uma conta de produção, uma de homologação, uma de dev. Login único entre elas. Billing unificado. Mas gera custo maior de infra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
PONTOS: Infraestrutura exclusiva para cliente único. Duplicação de sistemas e acesso restrito. Estrutura de contas e ambientes de produção homologação e desenvolvimento.

📋 PONTOS EXTRAÍDOS:
Infraestrutura exclusiva para cliente único. Duplicação de sistemas e acesso restrito. Estrutura de contas e ambientes de produção homologação e desenvolvimento.

📌 RESPOSTA:
### Resumo da Conversa  
O cliente está buscando informações sobre **infraestrutura exclusiva para cliente único**, **duplicação de sistemas**, **acesso restrito**, e **estrutura de contas e ambientes** (produção, homologação e desenvolvimento). 

---

### Tema 1: Infraestrutura Exclusiva para Cliente Único

📌 Criar uma conta AWS separada para cada cliente grande é o padrão. Garante isolamento total de recursos — aplicação, banco de dados, rede e segurança. O faturamento pode ser consolidado via AWS Organizations, mas cada conta mantém seus recursos independentes. Acesso entre contas é feito via Resource Access Manager, IAM roles ou VPC peering — sem sobreposição de recursos.

💬 Como falar pro cliente:
- "A conta separada garante que esse cliente tem tudo isolado — nada se mistura com outros, nem banco nem aplicação."
- "O billing pode ser único pra facilitar seu controle, mas cada conta opera de forma independente."
- "O acesso entre contas é controlado por políticas finas — só o que precisa passa, o resto fica bloqueado."

---

### Tema 2: Duplicação de Sistemas

📌 Para duplicar sistemas (ex: homologação e produção), use **AWS CloudFormation** ou **Terraform** para replicar a infraestrutura de forma automatizada. Ambientes de **dev**, **hom** e **prod** devem estar em contas ou VPCs separadas. Use **tags** para identificar o ambiente de cada recurso. Isso facilita o gerenciamento de custos e permissões por ambiente.

💬 Como falar pro cliente:
- "Usamos CloudFormation ou Terraform pra duplicar tudo automaticamente — você não precisa configurar manualmente cada ambiente."
- "Cada ambiente (dev, hom, prod) fica isolado em VPCs ou contas separadas — zero risco de misturar dados."
- "Com tags, você controla custos por ambiente e restringe acessos com precis


======================================================================
CHECKPOINT 4 [9:00-13:00] — MSP/billing + deploy cross-account + Terraform
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Vocês têm MSP com a Dati? Não, só billing via boleto. Se fosse só billing, pra gente não muda nada mesmo com mais contas. A gente usa CodePipeline pra deploy. Conseguiria plugar a branch master nas duas infraestruturas e fazer funcionar? Contas diferentes? Vou checar isso. Não sei se tá em Terraform. Precisaria checar.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Uso de MSP e Dati. Billing via boleto. Deploy com CodePipeline. Infraestruturas e branch master. Terraform.

📋 PONTOS EXTRAÍDOS:
Uso de MSP e Dati. Billing via boleto. Deploy com CodePipeline. Infraestruturas e branch master. Terraform.

📌 RESPOSTA:
### Resumo da Conversa  
O cliente está buscando informações sobre **MSP, Dati, billing via boleto, deploy com CodePipeline, infraestrutura e branch master, Terraform.** 

---

### Tema 1: Uso de MSP e Dati

📌 A Dati é uma consultoria AWS Advanced Partner e pode atuar como MSP (Managed Service Provider) para o cliente. Isso inclui sustentação proativa, monitoramento 24/7, e aplicação de patches de segurança. Como MSP, a Dati assume a responsabilidade operacional da infraestrutura, oferecendo relatórios mensais de performance e custos. 

💬 Como falar pro cliente:
- "A gente pode atuar como MSP de vocês — assumimos o dia a dia da infra, monitoramento 24/7 e aplicação de patches."
- "Vocês recebem relatórios mensais de performance e custos — assim sempre sabem o que tá rolando."
- "Isso libera a equipe de vocês pra focar no core business em vez de ficar apagando incêndio."

---

### Tema 2: Billing via Boleto

📌 A AWS aceita pagamentos via boleto bancário para contas no Brasil. É possível configurar no console da AWS ou via AWS Organizations para contas filhas. O boleto é gerado mensalmente e tem vencimento em até 5 dias úteis. Taxa adicional de 3-5% por uso de boleto. 

💬 Como falar pro cliente:
- "Pagamento via boleto é suportado pra contas no Brasil — a gente configura no console ou via Organizations."
- "O boleto vem com vencimento em até 5 dias úteis e tem taxa de 3-5%."
- "Se vocês preferirem, podemos automatizar a geração do boleto todo mês."

---

### Tema 3: Deploy com CodePipeline

📌 O AWS CodePipeline automatiza o deploy contínuo. Integra com GitHub, CodeCommit


======================================================================
CHECKPOINT 5 [13:00-20:00] — Auto-scaling lento + Beanstalk→Fargate + monolito
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
A gente tem uma dor que é a demora do auto scaling. Elastic Beanstalk leva meia hora até uma máquina subir. Às vezes cai fora do ar. A sugestão era migrar pro Fargate. Mas a gente tem um grande monolito. Quando tem monolito grande, o custo-benefício do Fargate não muda tanto. Mas o auto-scaling não seria mais rápido por ser imagem já buildada? Normalmente sim, mas depende do tamanho da aplicação. Às vezes o problema não é só o build, é o Beanstalk arrumando configuração. E no Fargate, consigo acessar a máquina pra troubleshooting urgente? O build demora 30 minutos e às vezes preciso corrigir na mão.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolito grande. Dificuldade de troubleshooting no Fargate.

📋 PONTOS EXTRAÍDOS:
Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolito grande. Dificuldade de troubleshooting no Fargate.

📌 RESPOSTA:
```
📌 **Demora no auto scaling do Elastic Beanstalk:**  
O Elastic Beanstalk usa auto scaling padrão do EC2 — pode demorar 3-5 minutos pra escalar por causa da inicialização da instância. Se precisar de resposta mais rápida, recomendo Fargate ou usar *asg* customizado com *warm pool*.  

**Custo-benefício do Fargate para monolito grande:**  
Fargate é mais caro que EC2 puro (cerca de 15-20% a mais). Mas pra monolito grande, se o time não tem expertise de infra, o ganho em produtividade e velocidade de deploy compensa. Se já tem equipe forte, EC2 com *autoscaling* bem configurado sai mais barato.  

**Dificuldade de troubleshooting no Fargate:**  
É mais abstrato — não tem acesso à máquina host. Logs e métricas ficam no CloudWatch. Pra debug mais profundo, usar *AWS X-Ray* ou *CloudTrail*. Se precisar de acesso ao container, *exec* no Fargate funciona, mas é mais lento que no EC2.

💬 Como falar pro cliente:  
- "O Elastic Beanstalk demora um pouco pra escalar porque inicializa a máquina inteira. Se vocês precisam de resposta mais rápida, podemos usar Fargate ou configurar um *warm pool*."  
- "Fargate é mais caro, mas pra monolito grande, se o time não quer perder tempo gerenciando servidores, o ganho em velocidade de deploy e segurança compensa."  
- "Troubleshooting no Fargate é diferente — a gente usa CloudWatch, X-Ray e *exec* nos containers. É seguro, mas requer um pouco de adaptação."
``` 
