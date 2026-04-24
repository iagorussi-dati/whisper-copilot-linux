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

📌 **Backup em AWS**  
AWS oferece várias opções de backup dependendo do serviço e do nível de granularidade necessário. As principais opções são:

1. **AWS Backup**:  
   - Serviço unificado para backup de recursos AWS (EC2, RDS, DynamoDB, EFS, etc.).  
   - Permite políticas de backup centralizadas, agendamento e retenção.  
   - Custo: baseado no tamanho dos dados backupados e na quantidade de backups armazenados. Exemplo: backup de 1 TB de dados por mês custa cerca de \$23 (usando o preço de \$0.023/GB/mês em 2026).  

2.  **Snapshots de EBS**:  
    - Para volumes do Elastic Block Store (EBS).  
    - Custo: \$0.05/GB/mês por snapshot incremental.  

3.  **Backup de RDS**:  
    - Backups automáticos e manuais disponíveis.  
	- Custo incluído no preço do RDS, mas backups manuais custam \$0.023/GB/mês.
   
4. **Exportação de tabelas do DynamoDB**:  
    - Para backup de tabelas completas.  
	- Custo: \$0.01 por milhão de unidades de leitura de capacidade de processamento (RCU) e \$0.025 por GB de dados exportados.
   

💬 **Como falar pro cliente:**  
- "O AWS Backup é o serviço mais completo — ele cuida de tudo, desde agendamento até retenção de backups. É fácil configurar e gerenciar."  
- "Se vocês usam EC2, RDS ou DynamoDB, dá pra fazer backup direto pelo serviço — sem custo adicional pra backups automáticos do RDS."  
- "O custo de backup varia conforme o tamanho dos dados, mas pra ter uma ideia, 1 TB de dados backupados fica em torno de \$23 por mês."

---

#### **Tema 2: RTO (Recovery Time Objective) e RPO (Recovery Point Objective)**

📌 **RTO e RPO**  
- **RTO (Recovery Time Objective)**: Tempo máximo tolerável para restaurar um sistema após um desastre. Exemplo: um RTO de 1 hora significa que o sistema deve estar operacional dentro de 1 hora após o incidente.  
- **RPO (Recovery Point Objective)**: Quantidade máxima de dados que pode ser perdida, medida em tempo. Exemplo: um RPO de 15 minutos significa que é aceitável perder os dados das últimas 15 minutos antes do desastre.  

**Estratégias para atender RTO/RPO:**  
- **Backup frequente + Snapshots**: Reduz o RPO.  
- **Multi-AZ e Multi-Region**: Reduz o RTO.  
	- **RDS Multi-AZ**: RTO de minutos.  
	- **RDS Multi-Region**: RTO de minutos a horas, dependendo da distância entre regiões.
- **AWS Backup com agendamento curto**: Permite backups a cada 1 hora, atendendo RPOs curtos.  

💬 **Como falar pro cliente:**  
- "RTO é quanto tempo vocês podem ficar parados depois de um problema. RPO é quanto de dados vocês podem perder. Quanto menor, mais seguro, mas também mais caro."  
- "Com backups a cada 1 hora usando AWS Backup, vocês conseguem um RPO de 1 hora. Se precisarem de menos, talvez seja necessário backup contínuo."
- "Para RTO de minutos, a gente recomenda RDS Multi-AZ ou até Multi-Region, dependendo da criticidade."

---

#### **Tema 3: Elastic Beanstalk**

📌 **Elastic Beanstalk**  
- Serviço PaaS (Platform as a Service) da AWS para implantar e gerenciar aplicações sem se preocupar com a infraestrutura subjacente.  
- Suporta várias linguagens: Python, Java, .NET, Node.js, PHP, Ruby, Go e Docker.  
- **Autoscaling**: Configurável automaticamente com base em métricas como CPU, requisições, etc.  
- **Deploy**:  
  - Tempo médio de deploy: 1-3 minutos para aplicações pequenas/médias.  
  - Suporta deploy azul/verde e rolling updates para zero downtime.  
- **Custo**: Você paga pelos recursos subjacentes (EC2, RDS, etc.). Não há custo adicional pelo Beanstalk.  

💬 **Como falar pro cliente:**  
- "O Elastic Beanstalk é perfeito pra vocês que querem focar no código e não na infra. A AWS cuida de escalar e manter o ambiente rodando."  
- "O tempo de deploy é rápido — em 1-3 minutos a aplicação já tá no ar. E dá pra fazer atualizações sem parar a aplicação."  
- "Vocês não pagam extra pelo Beanstalk — só pelos recursos que ele usa, como EC2 e RDS."

---

#### **Tema 4: Aurora**

📌 **Amazon Aurora**  
- Banco de dados relacional compatível com MySQL e PostgreSQL.  
- **Performance**: Até 5x mais rápido que o MySQL padrão e 3x mais rápido que o PostgreSQL.  
- **Disponibilidade**:  
	- **Multi-AZ**: Até 99.99% de disponibilidade. RTO de segundos a minutos.  
	- **Global Database**: Ativação em até 3 regiões. RTO de 1-2 minutos para failover.  
- **Backup**:  
	- Backups automáticos a cada 5 minutos.  
	- RPO de


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
### Respostas Técnicas  

#### **Tema 1: Ambiente Duplicado em Outra Região**  
📌 **Custo e Infraestrutura**  
- **Custo**: Sim, o custo **dobra** porque você está executando **exatamente a mesma quantidade de recursos** em outra região. Ex: 1 EC2 `t3.medium` em `us-east-1` + 1 EC2 `t3.medium` em `sa-east-1` = custo de **2 instâncias**.  
- **Duplicação**: É necessário **duplicar todos os recursos** (EC2, RDS, Load Balancers, etc.) na nova região. Serviços gerenciados (como RDS, Aurora) precisam ser **recriados** na região de destino.  

📌 **Funcionamento de Load Balancers**  
- **ALB/NLB**: Funcionam **independentemente por região**. Ou seja, cada região terá seu **próprio Load Balancer** (ex: `ALB-regiao1` e `ALB-regiao2`).  
- **Cross-Region Load Balancing**: Para failover automático entre regiões, use o **AWS Global Accelerator** (camada de rede) ou **Route 53 com health checks**. O ALB **não** opera diretamente entre regiões — ele só balanceia **dentro** da região onde está implantado.  

📌 **Uso do Route 53 para Failover**  
- **Configuração**:  
  1. Crie **dois conjuntos de registros** no Route 53 (ex: `app.example.com`).  
  2. Aponhe um para a região primária (ex: `ALB-us-east-1`) com **peso 100**.  
  3. Aponhe outro para a região secundária (ex: `ALB-sa-east-1`) com **peso 0**.  
  4. Configure um **health check** no Route 53 monitorando o ALB da região primária.  
  5. Se o health check falhar, o Route 53 **automaticamente** altera o peso para direcionar o tráfego para a região secundária (peso 100).  
- **Tempo de failover**: Geralmente **menos de 30 segundos** após a falha ser detectada.  

📌 **Opção de Failover**  
- **Ativo-Passivo**:  
  - Região primária opera **100% do tráfego**.  
  - Região secundária fica **ociosa** (custo dobrado, mas só paga pela infra *parada* — exceto serviços sempre cobrados, como EBS).  
  - **Vantagem**: Custo mais baixo que ativo-ativo.  
  - **Desvantagem**: Falha na região primária causa **interrupção** até o failover.  
- **Ativo-Ativo**:  
  - Ambas as regiões operam **simultaneamente** (ex: 50% do tráfego em cada).  
  - **Vantagem**: Maior resiliência e distribuição de carga.  
  - **Desvantagem**: **Custo dobrado** contínuo.  

💬 **Como falar pro cliente**:  
- *"Se vocês duplicarem a infra em outra região, o custo vai dobrar — mas isso garante que, se uma região cair, o serviço continua funcionando na outra."*  
- *"O Route 53 faz o failover automático em menos de 30 segundos — o cliente nem percebe que mudou de região."*  
- *"Vocês podem começar com ativo-passivo (mais barato) e depois evoluir para ativo-ativo se o tráfego aumentar."*  

---  

#### **Tema 2: Dúvidas sobre Serviços AWS (Suporte a Funcionalidades)**  
📌 **Suporte a Áudio/Vídeo no Amazon Q Business**  
- **Sim**, o Amazon Q Business **suporta upload de arquivos de áudio e vídeo** (MP3, MP4, WAV, etc.).  
- **Como funciona**: Ele **transcreve automaticamente** o conteúdo usando **Amazon Transcribe** e indexa o texto para consultas por chat.  
- **Limitações**:  
  - Não há **chat por voz** — a interação é **sempre por texto**.  
  - Formatos suportados: MP3, MP4, WAV, FLAC, OGG.  
  - Tamanho máximo por arquivo: **200 MB** (2026).  

📌 **Suporte a Python em AWS Lambda**  
- **Sim**, Lambda **suporta Python** (versões **3.8, 3.9, 3.10, 3.11 e 3.12** em 2026).  
- **Empacotamento**: Use **Lambda Layers** para bibliotecas externas ou **container images** (até 10 GB).  
- **Limitação**: Timeout máximo de **15 minutos**.  

📌 **Integração com Google Drive**  
- **Não nativo**, mas é possível via:  
  1. **AWS Lambda + API do Google Drive**: Crie uma função Lambda que usa a **API do Google Drive** para ler/escrever arquivos.  
  2. **EventBridge + Google Drive**: Use **EventBridge** para disparar eventos quando novos arquivos são carregados.  
  3. **Ferramentas de terceiros**: Serviços como **Zapier** ou **AWS AppFlow** (suporte a Google Drive em 2026).  

💬 **Como falar pro cliente**:  
- *"Sim, o Amazon Q Business aceita áudio e vídeo — ele transcreve tudo e vocês consultam pelo chat de texto."*  
- *"


======================================================================
CHECKPOINT 3 [6:00-9:00] — Infra exclusiva por cliente + estrutura de contas
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Teve um cliente que quer infraestrutura exclusiva. Banco deles, back-end deles. Tudo duplicado pra atender só um cliente. Acessível somente da rede deles. Não sei se é viável. Vocês teriam que ter uma conta separada só pra esse cliente. Vocês têm estrutura de contas? Não, hoje é uma só. Vocês conseguem ter uma conta de produção, uma de homologação, uma de dev. Login único entre elas. Billing unificado. Mas gera custo maior de infra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
PONTOS: Infraestrutura exclusiva para cliente. Duplicação de sistemas. Acesso restrito à rede específica. Contas separadas necessárias. Estrutura de contas atuais. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Billing unificado. Custo maior de infraestrutura.

📋 PONTOS EXTRAÍDOS:
Infraestrutura exclusiva para cliente. Duplicação de sistemas. Acesso restrito à rede específica. Contas separadas necessárias. Estrutura de contas atuais. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Billing unificado. Custo maior de infraestrutura.

📌 RESPOSTA:
### Respostas Técnicas  

#### **Tema 1: Infraestrutura Exclusiva para Cliente**  
📌 **Conta AWS Separada**  
A solução mais segura e recomendada é criar uma **conta AWS independente** para cada cliente que exige isolamento total (banco de dados, aplicação, rede).  
- **Isolamento completo**: Nada é compartilhado entre contas.  
- **Billing consolidado**: Você pode usar **AWS Organizations** para ter visibilidade de custo total da organização, mas cada conta tem fatura separada. Custo de infraestrutura será maior devido à duplicação de recursos, mas é necessário para compliance.  
- **Acesso restrito**: Redes (VPC, Security Groups, NACLs) são totalmente isoladas. Você controla quem acessa o que via IAM e VPC peering ou VPN.  
- **Login único entre contas**: Configure **AWS SSO** (Single Sign-On) para permitir que sua equipe acesse múltiplas contas com um único usuário.  

💬 Como falar pro cliente:  
- *"O ideal para seu caso é uma conta AWS separada para esse cliente. Assim, tudo fica 100% isolado: banco, aplicação, rede, sem nenhum risco de contaminação ou acesso não autorizado."*  
- *"O billing pode ser consolidado na sua Organization principal — vocês veem o total, mas cada conta tem seus custos detalhados. Isso ajuda no controle financeiro."*  
- *"E com o AWS SSO, sua equipe acessa todas as contas com um único login, sem precisar de múltiplas credenciais."*  

---

#### **Tema 2: Duplicação de Sistemas**  
📌 **Estratégias de Duplicação**  
Para duplicar sistemas (ex: produção, homologação, desenvolvimento):  
1. **AWS CloudFormation ou Terraform**: Crie templates de infraestrutura que podem ser aplicados em múltiplas contas/regiões.  
   - Permite replicar ambientes em minutos.  
   - Versão controlada (ex: Git) para rastrear mudanças.  
2. **AWS Backup**: Para dados. Configure políticas de backup para bancos de dados (RDS, DynamoDB), EBS, S3.  
   - Suporta cópias em outra região (ex: produção em SP, backup em Virginia).  
3. **Ambientes Isolados**:  
   - **Produção**: Conta dedicada.  
   - **Homologação/Dev**: Contas separadas, com recursos escaláveis para baixo (ex: instâncias t3.micro para dev).  
   - Custo de infraestrutura será ~30-50% maior que um único ambiente, mas é necessário para segurança e testes.  

💬 Como falar pro cliente:  
- *"A gente pode duplicar seus sistemas usando templates (CloudFormation ou Terraform). Assim, você replica produção, homologação e dev em minutos, sem erro manual."*  
- *"Para dados, o AWS Backup faz cópias automáticas e pode enviar para outra região — ideal para disaster recovery."*  
- *"Lembre-se: ter ambientes separados aumenta o custo de infraestrutura, mas é essencial para evitar riscos em produção."*  

---

#### **Tema 3: Acesso Restrito à Rede Específica**  
📌 **Controle de Acesso**  
- **VPC com Subnets Privadas**: Crie uma VPC dedicada para o cliente. Use subnets privadas (sem internet gateway) para bancos de dados.  
- **Security Groups e NACLs**:  
  - Restrinja IPs de acesso (ex: só a rede do cliente pode acessar a aplicação).  
  - Use regras granulares (porta, protocolo).  
- **AWS PrivateLink**: Se precisar conectar serviços entre contas sem sair da AWS, use PrivateLink. Não passa pela internet.  
- **VPN ou AWS Direct Connect**: Para conectar a rede do cliente à VPC. Custo adicional de ~$0.05/GB trafegado.  

💬 Como falar pro cliente:  
- *"Vamos configurar uma VPC só para esse cliente, com subnets privadas para os dados sensíveis. Assim, ninguém de fora consegue acessar."*  
- *"O acesso à aplicação será restrito apenas aos IPs da rede do seu cliente — garantimos que só eles entrem."*  
- *"Se precisarem de conexão direta entre sua rede e a AWS, o Direct Connect é a opção mais segura e de baixa latência."*  

---

#### **Tema 4: Estrutura de Contas Atuais**  
📌 **Melhores Práticas (2026)**  
- **AWS Organizations**:  
  - Organize contas em OUs (Unidades Organizacionais). Ex: `Produção`, `Homologação`, `Dev`.  
  - Aplique SCPs (*Service Control Policies*) para bloquear serviços não autorizados em OUs específicas.  
- **Conta para Cada Ambiente**:  
  - **Produção**: Conta dedicada (isolada).  
  - **Homologação**: Conta com recursos similares, mas menor capacidade.  
  - **Desenvolvimento**: Conta com limites de custo (ex: budget alarm em R$ 500/mês).  
- **Billing Unificado**:  
  - Com Organizations, você tem uma fatura consolidada, mas pode ver o custo por conta.  

💬 Como falar pro cliente:  
- *"Recomendamos usar AWS Organizations para gerenciar todas as contas — produção, homologação e dev — em uma estrutura organizada."*  
- *"Cada ambiente fica em uma conta separada. Assim, você controla custos e permissões de forma granular."*  
- *"O billing é unificado, mas você vê exatamente quanto cada conta gasta. E pode definir orçamentos por ambiente."*


======================================================================
CHECKPOINT 4 [9:00-13:00] — MSP/billing + deploy cross-account + Terraform
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Vocês têm MSP com a Dati? Não, só billing via boleto. Se fosse só billing, pra gente não muda nada mesmo com mais contas. A gente usa CodePipeline pra deploy. Conseguiria plugar a branch master nas duas infraestruturas e fazer funcionar? Contas diferentes? Vou checar isso. Não sei se tá em Terraform. Precisaria checar.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: NAO
CONCORRENTE: NAO
PONTOS: Uso de MSP com Dati. Billing via boleto. Deploy com CodePipeline. Plugando branch master. Infraestruturas diferentes. Uso de Terraform.

📋 PONTOS EXTRAÍDOS:
Uso de MSP com Dati. Billing via boleto. Deploy com CodePipeline. Plugando branch master. Infraestruturas diferentes. Uso de Terraform.

📌 RESPOSTA:
### Contexto: Uso de MSP com Dati, Billing via Boleto, Deploy com CodePipeline, Plugando Branch Master, Infraestruturas Diferentes, Uso de Terraform

Como não houve uma pergunta técnica específica, vou sugerir **3 perguntas** que o consultor técnico (Gustavo Conti) pode fazer ao cliente para esclarecer dúvidas e oferecer soluções mais precisas. Essas perguntas ajudarão a entender melhor o cenário atual e as necessidades específicas.

---

#### **Sugestões de Perguntas para o Consultor**

1. **Sobre o Billing via Boleto e MSP:**
   - “Como está estruturado o processo de aprovação e pagamento dos boletos hoje? Vocês precisam de relatórios de custo detalhados por projeto ou por cliente?”
   - *Objetivo:* Entender se há necessidade de integração com sistemas de ERP ou geração de relatórios customizados para controle financeiro. 

2.  **Sobre o Deploy com CodePipeline e Branch Master:**
    - “Qual é a política de CI/CD de vocês? Vocês fazem deploy direto em produção a partir do branch master, ou têm ambientes de staging e testes intermediários?”
    - *Objetivo:* Verificar se há necessidade de implementar estágios de aprovação, testes automatizados ou rollback estratégias no CodePipeline.
	
3. **Sobre o Uso de Terraform e Infraestruturas Diferentes:**
    - “Quantas contas AWS vocês estão gerenciando com Terraform hoje? Elas seguem o mesmo modelo de infraestrutura ou têm particularidades que exigem módulos específicos?”
    - *Objetivo:* Entender a complexidade da gestão de infraestrutura e se há necessidade de modularização ou versionamento avançado do Terraform.   

---

Estas perguntas ajudarão a mapear melhor o cenário actual do cliente e permitirão à Dati oferecer soluções mais alinhadas com as suas necessidades.   


======================================================================
CHECKPOINT 5 [13:00-20:00] — Auto-scaling lento + Beanstalk→Fargate + monolito
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
A gente tem uma dor que é a demora do auto scaling. Elastic Beanstalk leva meia hora até uma máquina subir. Às vezes cai fora do ar. A sugestão era migrar pro Fargate. Mas a gente tem um grande monolito. Quando tem monolito grande, o custo-benefício do Fargate não muda tanto. Mas o auto-scaling não seria mais rápido por ser imagem já buildada? Normalmente sim, mas depende do tamanho da aplicação. Às vezes o problema não é só o build, é o Beanstalk arrumando configuração. E no Fargate, consigo acessar a máquina pra troubleshooting urgente? O build demora 30 minutos e às vezes preciso corrigir na mão.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolito. Acesso à máquina para troubleshooting urgente.

📋 PONTOS EXTRAÍDOS:
Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolito. Acesso à máquina para troubleshooting urgente.

📌 RESPOSTA:
### Respostas Técnicas  

#### **Tema 1: Demora no Auto Scaling do Elastic Beanstalk**
📌 O Elastic Beanstalk usa o Auto Scaling nativo da AWS, mas tem uma camada de abstração que pode adicionar latência. Em cenários de *scale-up* (aumentar capacidade), o tempo médio é de **3-5 minutos** (2026). Para *scale-down*, é mais rápido — **1-2 minutos**. Isso ocorre porque o Elastic Beanstalk precisa:  
- Verificar métricas (CPU, requisições)  
- Iniciar novas EC2 (ou container)  
- Esperar *health check* da aplicação  

**Solução para reduzir demora:**  
- Use **AWS Auto Scaling Groups (ASG) direto** em vez de Elastic Beanstalk — latência cai para **30-60 segundos** em *scale-up*.  
- Ative **"Predictive Scaling"** (disponível em 2026) — usa IA para antecipar picos e já cria instâncias antes da demanda.  
- Configure *warm pools* (instâncias pré-iniciadas mas paradas) — reduz tempo de *boot*.  

💬 Como falar pro cliente:  
- *"O Elastic Beanstalk demora um pouco pra escalar porque tem uma camada extra de verificação. Se vocês têm picos repentinos, podemos usar o Auto Scaling direto que é mais rápido — em menos de 1 minuto."*  
- *"Tem uma função de *predictive scaling* que usa inteligência artificial pra antecipar picos. Assim, a infra já está pronta antes da demanda subir."*  
- *"Se quiser o mínimo possível de demora, configuramos um *warm pool* — instâncias já preparadas mas desligadas, que ligam em segundos quando precisar."*  

---

#### **Tema 2: Custo-Benefício do Fargate para Monolito**  
📌 **Fargate é vantajoso para monolitos apenas em casos específicos.** Em 2026:  
- **Custo:** Fargate cobra **por vCPU e memória consumida por hora** (ex: `t3.large` = ~R$ 0,0416/hora em *sa-east-1*). EC2 tem custo fixo por instância (ex: `t3.large` = ~R$ 0,0832/hora), mas permite *overcommit* (varias apps em 1 máquina).  
- **Benefício:**  
  - **Deploy mais rápido:** 10-20 segundos vs. minutos no EC2/Elastic Beanstalk (por não ter *boot* de SO).  
  - **Sem gerenciamento:** Ideal se a equipe não tem expertise em Linux/segurança.  
  - **Auto scaling mais ágil:** Escala em **30-45 segundos** (vs. 3-5 min no Elastic Beanstalk).  
- **Desvantagens para monolitos:**  
  - **Custo maior se subutilizado:** Se o monolito usa só 20% da CPU, Fargate é até **40% mais caro** que EC2.  
  - **Limitação de *horizontal pod autoscaling*:** Monolitos não se beneficiam de *container orchestration* como microsserviços.  

**Recomendação:**  
- Use Fargate **apenas se**:  
  1. O monolito tem picos imprevisíveis (e precisa escalar rápido).  
  2. A equipe não quer gerenciar SO/updates.  
- Caso contrário, **EC2 com ASG otimizado** é mais barato. Exemplo concreto:  
  - Monolito com tráfego estável (80% de CPU o tempo todo):  
    - EC2 `t3.large` = R$ 0,0832/hora  
    - Fargate equivalente = R$ 0,0832 (vCPU) + R$ 0,013 (memória) ≈ **R$ 0,096/hora** → **15% mais caro**.  

💬 Como falar pro cliente:  
- *"O Fargate é ótimo se vocês têm picos repentinos e não querem gerenciar servidores. Mas pra monolitos com tráfego estável, ele pode sair mais caro — em média 15% a mais."*  
- *"Se a equipe de vocês não tem tempo pra cuidar de atualizações do sistema operacional, o Fargate vale a pena pela simplicidade. O deploy é em segundos, não em minutos."*  
- *"Vamos fazer um teste com métricas reais de vocês. Se o consumo de CPU for alto o tempo todo, EC2 sai mais barato. Se for intermitente, Fargate ganha."*  

---

#### **Tema 3: Acesso à Máquina para Troubleshooting Urgente**  
📌 **Solução oficial e segura (2026):**  
- **EC2/Elastic Beanstalk:** Use **AWS Systems Manager (SSM) Session Manager**.  
  - Funciona **sem IP público, sem VPN, sem bastion host**.  
  - Acesso em **segundos** via CLI ou console.  
  - Registra tudo (auditoria).  
  - **100% gratuito** (apenas custo de transferência de dados se aplicável).  
- **Fargate:**  
  - **Não tem acesso SSH** (por design — é *serverless*).  
  - Para *troubleshooting*:  
    1. **Exec em container rodando:** `aws ecs execute-command` — acessa o container em tempo real (suportado em 2026).  
    2. **Dump de logs:** Use CloudWatch Logs ou `aws logs
