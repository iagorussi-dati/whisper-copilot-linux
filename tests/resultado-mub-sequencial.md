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
### Respostas Técnicas

#### **Tema 1: Backup**

📌 **AWS oferece vários serviços para backup, cada um com casos de uso específicos:**
- **AWS Backup:** Serviço gerenciado que centraliza o backup de recursos AWS (EC2, RDS, DynamoDB, EFS, etc.). Permite políticas de backup, retenção e agendamento centralizados. Suporta backup de dados locais via AWS Backup Gateway.
- **Snaphots de EBS:** Ideais para backups de volumes de EC2. São incrementais e podem ser automatizados via Lambda ou AWS Backup.
- **RDS Snapshots:** Backups automáticos de bancos de dados RDS. Podem ser manuais ou automáticos (diários). Armazenados em S3.
- **S3 Versioning:** Para objetos armazenados no S3, mantém todas as versões de um objeto. Não é backup tradicional, mas protege contra exclusões acidentais.
- **Backup de DynamoDB:** On-demand ou programado via AWS Backup. Também pode usar exportação de tabela para S3.

**Custos (2026):**
- **AWS Backup:** Gratuito para planejar e monitorar. Taxa de armazenamento varia conforme região (ex: ~$0.05/GB/mês em us-east-1). Taxa de recuperação ~$0.01/GB.
- **Snapshots de EBS:** Armazenamento ~$0.05/GB/mês. Taxa de criação ~$0.01 por snapshot.
- **RDS Snapshots:** ~$0.023/GB/mês em us-east-1.
   

💬 **Como falar pro cliente:**
- "O **AWS Backup** é o serviço mais completo — centraliza tudo, tem política de retenção e é fácil de gerenciar. Custo é bem acessível, em média $0,05 por GB por mês."
- "Se vocês usam muito **EC2**, os


======================================================================
CHECKPOINT 2 [3:00-6:00] — Multi-região + failover + custo
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
A gente pode pensar em ambiente duplicado em outra região, geraria RTO RPO muito melhor. Só que dobraria o custo. Duplicar a infra seria um passo ousado demais. Só de curioso, como funciona na prática? Dois load balancers em locais separados, quem faz o meio do caminho? Vocês usam Route 53? Lá tem opção de failover. Se detectar que o load balancer de uma região não tá funcionando, joga pra outra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Ambiente duplicado em outra região. Custo dobrado. Duplicação da infraestrutura. Funcionamento prático de load balancers. Uso do Route 53. Failover automático.

📋 PONTOS EXTRAÍDOS:
Ambiente duplicado em outra região. Custo dobrado. Duplicação da infraestrutura. Funcionamento prático de load balancers. Uso do Route 53. Failover automático.

📌 RESPOSTA:
### Respostas Técnicas  

#### **Tema 1: Ambiente Duplicado em Outra Região**

📌 **Custo e Infraestrutura**  
- **Custo**: Manter um ambiente duplicado em outra região **dobra o custo** (ex: se hoje gasta R$ 5k/mês na região principal, com duplicação será ~R$ 10k/mês).  
- **Infraestrutura**: É uma cópia exata (EC2, RDS, S3, etc.) na região de failover. **Não compartilha recursos** — cada região tem seus próprios servidores, armazenamento e rede.  

📌 **Funcionamento Prático de Load Balancers**  
- **ALB/NLB**: Funcionam normalmente na região primária. Em failover, o tráfego é redirecionado para os LBs da região secundária.  
- **Health Checks**: Os LBs monitoram as instâncias. Se a região primária cair, os checks falham e o Route 53 aciona o failover.  

📌 **Uso do Route 53 para Failover**  
- **Configuração**: Crie um *record set* com **failover routing policy**. Defina:  
  - **Primary**: Aponta para o ALB/NLB da região principal.  
  - **Secondary**: Aponta para o ALB/NLB da região de backup.  
- **Tempo de Troca**: **< 30 segundos** (o Route 53 detecta a falha via health checks e redireciona automaticamente).  
- **Teste**: Use *Route 53 health checks* com endpoints de verificação em cada região.  

💬 **Como falar pro cliente**:  
- *"Manter um ambiente duplicado em outra região dobra o custo — é como ter duas operações iguais rodando ao mesmo tempo. Mas garante alta disponibilidade."*  
- *"O Route 53


======================================================================
CHECKPOINT 3 [6:00-9:00] — Infra exclusiva por cliente + estrutura de contas
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Teve um cliente que quer infraestrutura exclusiva. Banco deles, back-end deles. Tudo duplicado pra atender só um cliente. Acessível somente da rede deles. Não sei se é viável. Vocês teriam que ter uma conta separada só pra esse cliente. Vocês têm estrutura de contas? Não, hoje é uma só. Vocês conseguem ter uma conta de produção, uma de homologação, uma de dev. Login único entre elas. Billing unificado. Mas gera custo maior de infra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
PONTOS: Infraestrutura exclusiva para cliente único. Duplicação de sistemas. Acesso restrito à rede específica. Necessidade de contas separadas. Estrutura atual de conta única. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Cobrança unificada. Aumento de custos de infraestrutura.

📋 PONTOS EXTRAÍDOS:
Infraestrutura exclusiva para cliente único. Duplicação de sistemas. Acesso restrito à rede específica. Necessidade de contas separadas. Estrutura atual de conta única. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Cobrança unificada. Aumento de custos de infraestrutura.

📌 RESPOSTA:
### Respostas Técnicas

#### **Tema 1: Infraestrutura Exclusiva para Cliente Único**

📌 **Conta AWS Separada**  
A melhor prática é criar uma conta AWS **totalmente separada** para cada cliente que exige isolamento completo (banco de dados, aplicações, rede). Isso garante:  
- **Isolamento total**: Nada é compartilhado entre clientes.  
- **Controle de acesso**: Rede e permissões podem ser restritas apenas àquele cliente.  
- **Compliance**: Atende a requisitos de segregação de dados (ex: LGPD, HIPAA).  

**Billing Consolidado**:  
- As contas podem ser agrupadas em uma **AWS Organization** para ter cobrança unificada.  
- O cliente visualiza um único extrato consolidado, mas cada conta tem seus custos detalhados.  

**SSO (Single Sign-On)**:  
- É possível configurar **AWS SSO** para login único entre todas as contas da Organization.  
- Permite que a equipe acesse todas as contas com um único usuário, sem precisar de credenciais separadas.  

**Custo**:  
- **Aumento de custos**: Esperar um aumento de **15-30%** devido à duplicação de recursos (ex: dois RDS em vez de um).  
- **Exemplo concreto**:  
  - 1 EC2 `t3.medium` (R$ 450/mês) em conta única.  
  - Em contas separadas: 2 EC2 `t3.medium` = **R$ 900/mês**.  
  - Custo adicional de gerenciamento: ~**R$ 200/mês** (monitoramento, backups).  
  - **Total estimado**: **R$ 1.100/mês** (contra R$ 450/mês antes).  

💬 **Como falar pro cliente**:  
- "O ideal é criar uma conta AWS só


======================================================================
CHECKPOINT 4 [9:00-13:00] — MSP/billing + deploy cross-account + Terraform
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Vocês têm MSP com a Dati? Não, só billing via boleto. Se fosse só billing, pra gente não muda nada mesmo com mais contas. A gente usa CodePipeline pra deploy. Conseguiria plugar a branch master nas duas infraestruturas e fazer funcionar? Contas diferentes? Vou checar isso. Não sei se tá em Terraform. Precisaria checar.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: NAO
CONCORRENTE: NAO
PONTOS: Uso de MSP e Dati. Billing via boleto. Deploy com CodePipeline. Infraestruturas em branch master. Uso de Terraform.

📋 PONTOS EXTRAÍDOS:
Uso de MSP e Dati. Billing via boleto. Deploy com CodePipeline. Infraestruturas em branch master. Uso de Terraform.

📌 RESPOSTA:
### Contexto e Sugestões de Perguntas

Como não houve uma pergunta técnica específica do cliente, vou reconhecer o contexto fornecido e sugerir **3 perguntas** que o consultor técnico (Gustavo Conti) pode fazer ao cliente para aprofundar a discussão e entender melhor as necessidades técnicas. 

#### Contexto Reconhecido
- **MSP e Dati:** Entendido que a Dati é um AWS Advanced Partner e atuará como MSP (Managed Service Provider) para o cliente.
- **Billing via Boleto:** O cliente prefere pagamentos via boleto bancário em vez de cartão de crédito ou débito automático.
    - **Observação:** A AWS aceita boletos para pagamentos de faturas, mas é importante verificar se o cliente está ciente de que pode haver taxas adicionais dependendo do método de pagamento escolhido. 
- **Deploy com CodePipeline:** O cliente já utiliza ou deseja utilizar o AWS CodePipeline para automação de *deploy*.
    - **Observação:** O CodePipeline integra-se bem com GitHub, AWS CodeCommit, e outros repositórios. É crucial saber onde o código está hospedado.
- **Infraestruturas em Branch Master:** O cliente mantém sua infraestrutura em código no branch *master* (ou *main*).
    - **Observação:** É uma prática comum, mas é importante verificar se há políticas de *code review* e *CI/CD* configuradas para evitar mudanças não testadas.
- **Uso de Terraform:** O cliente utiliza Terraform para gerenciamento de infraestrutura como código (IaC).
	- **Observação:** A Dati tem expertise em Terraform e pode otimizar e versionar os *scripts*. É importante saber se o estado do Terraform está remoto (ex: S3 + DynamoDB) para evitar conflitos.

---

### Sugestões de Perguntas para o Consultor

💬 **Pergunta 1: Sobre o Billing


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
### Respostas Técnicas  

#### **Tema 1: Demora no Auto Scaling do Elastic Beanstalk**

📌 **Auto Scaling no Elastic Beanstalk**  
O Elastic Beanstalk usa o **Auto Scaling Group (ASG)** por trás dos panos. O tempo de escala depende de:  
- **Tempo de inicialização da instância**: EC2 leva ~1-3 minutos pra iniciar (varia conforme tamanho da instância e imagem).  
- **Health checks**: O EB verifica a saúde da aplicação antes de adicionar/remover instâncias (pode levar +1 minuto).  
- **Políticas de escala**:  
  - **Scale-out** (aumentar): Geralmente leva **2-5 minutos** (iniciar nova instância + deploy da app).  
  - **Scale-in** (diminuir): Mais rápido (~1-2 minutos), pois só desliga instâncias.  

**Como reduzir a demora**:  
1. **Pré-esquentar instâncias**: Use *Instance Warmup* no ASG (configurável no `.ebextensions`).  
2. **Políticas agressivas**: Defina thresholds mais baixos (ex: CPU > 60% por 2 minutos em vez de 5).  
3. **Imagens otimizadas**: Use AMI minimalista ou *EC2 Image Builder* pra reduzir tempo de boot.  

💬 **Como falar pro cliente**:  
- *"O Elastic Beanstalk demora um pouco pra escalar porque precisa iniciar a máquina inteira e verificar se a aplicação tá saudável. Em média, são 2-5 minutos pra aumentar capacity."*  
- *" Dá pra reduzir esse tempo otimizando as imagens das máquinas ou ajustando as regras de escala. A gente pode fazer isso sem mudar a estrutura atual de vocês."*  
- *"Se a demora for crítica pro seu negócio, podemos migrar pro
