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
PONTOS: Backup necessário. Definição de RTO e RPO. Documentação de requisitos para clientes.

📋 PONTOS EXTRAÍDOS:
Backup necessário. Definição de RTO e RPO. Documentação de requisitos para clientes.

📌 RESPOSTA:
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati

---

📌 **1. Backup Necessário**

**📌** Para definir uma estratégia de backup eficaz é fundamental alinharmos o **RTO (Recovery Time Objective)** e o **RPO (Recovery Point Objective)** com os requisitos de negócio do cliente. 

- **RTO** define o tempo máximo aceitável para restaurar os sistemas após um desastre.
- **RPO** define o ponto no tempo até o qual os dados podem ser restaurados (por exemplo, perda de até 1 hora de dados).

**Serviços AWS recomendados:**
- **AWS Backup:** Serviço gerenciado que centraliza o backup de recursos AWS (EC2, RDS, EFS, DynamoDB, etc.). Permite políticas de backup, agendamento e retenção centralizados.
- **Amazon S3 Versioning:** Para dados em S3, o versionamento permite recuperar versões anteriores de objetos.
- **Amazon RDS Snapshots:** Snapshots automáticos ou manuais para bases de dados RDS.
- **EBS Snapshots:** Para volumes do Elastic Block Store.

**💬 Como falar pro cliente:**
- *"Para garantir que seus dados estejam sempre seguros, precisamos definir seu RTO e RPO. Com isso, podemos configurar o AWS Backup para atender exatamente às suas necessidades de recuperação."*
- *"O AWS Backup é um serviço que centraliza todos os seus backups, seja de máquinas, bancos de dados ou arquivos. Ele automatiza tudo e reduz a complexidade."*
- *"Vamos configurar políticas de backup de acordo com sua criticidade. Por exemplo, dados financeiros podem ter RPO de 5 minutos, enquanto logs podem ter RPO de 1 hora."*

---

📌 **2. Definição de RTO e RPO**

**📌** A definição de **RTO** e **RPO** é crucial para qualquer estratégia de resiliência e disaster recovery. 

- **RTO (Recovery Time Objective):** Tempo máximo tolerável de inatividade. Exemplos:
  - **RTO de 1 hora:** Sistemas críticos que precisam estar no ar rapidamente.
  - **RTO de 24 horas:** Sistemas menos críticos.
  
- **RPO (Recovery Point Objective):** Quantidade máxima de dados que pode ser perdida, medida em tempo. Exemplos:
  - **RPO de 5 minutos:** Dados financeiros, transações.
  - **RPO de 4 horas:** Logs e dados menos críticos.

**Como definir:**
1. **Entrevista com as partes interessadas:** Entender o impacto no negócio de diferentes cenários de perda de dados e tempo de inatividade.
2. **Análise de impacto:** Avaliar quais sistemas são mais críticos.
3. **Definir níveis de serviço:** Com base na análise, estabelecer RTO e RPO para cada sistema.

**💬 Como falar pro cliente:**
- *"RTO é o tempo que vocês podem ficar fora do ar sem causar danos graves ao negócio. RPO é quanto de dados vocês podem perder. Precisamos desses números para projetar sua solução de DR."*
- *"Vamos fazer uma análise de impacto com sua equipe para definir esses valores. Assim, garantimos que o custo seja proporcional ao risco."*
- *"Com base no RTO e RPO, podemos recomendar desde soluções simples com backups em uma única região até soluções mais complexas com multi-região."*

---

📌 **3. Documentação de Requisitos para Clientes**

**📌** Uma documentação de requisitos clara é essencial para o sucesso de qualquer projeto. Ela evita retrabalho e alinha expectativas.

**Elementos-chave da documentação:**
1.  **Objetivos do Projeto:** O que se pretende alcançar?
2.  **Escopo:** O que está incluído e o que não está?
3.  **Requisitos Funcionais:** Descreve as funcionalidades que o sistema deve ter.
4.  **Requisitos Não Funcionais:** Descreve desempenho, segurança, usabilidade, etc.
5.  **RTO/RPO:** Como discutido acima.
6.  **Volumetria:** Quantidade de dados, número de usuários, frequência de acesso.
7.  **Integrações:** Sistemas externos com os quais precisará se integrar (ex: Google Drive, outros APIs).
8.  **Conformidade:** Requisitos legais e regulatórios (ex: LGPD, HIPAA).

**Modelo de coleta de requisitos:**
- **Questionário:** Enviar ao cliente para preencher com informações básicas.
-  **Workshop:** Reunião de alinhamento para detalhar requisitos e esclarecer dúvidas.
- **Documentação de Referência:** Se o cliente já usa outro sistema, pedir documentação existente para entender o contexto.

**💬 Como falar pro cliente:**
- *"Para garantir que o projeto atenda perfeitamente às suas necessidades, precisamos de uma documentação de requisitos completa. Isso inclui objetivos, escopo funcional e não funcional, e suas necessidades de RTO/RPO."*
- *"Vamos enviar um questionário e agendar um workshop para detalharmos tudo juntos. Assim, evitamos surpresas e retrabalho."*
- *"Com base nessa documentação, vamos desenhar a arquitetura e estimar custos e prazos com muita precisão."*

---

### 📌 **Dicas Adicionais Baseadas nos Dados Web (2026)**

#### **Certificações AWS**
- **Estratégias e Hacks:** Focar em palavras-chave e cenários práticos que são frequentemente testados. Por exemplo, entender profundamente os pilares do **Well-Architected Framework** (Operacional, Seguro, Eficiente, de Performance e


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
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati

---

#### **1. Ambiente Duplicado em Outra Região**

📌 **Custo e Infraestrutura**  
- **Custo**: Sim, o custo **dobra** quando você duplica o ambiente em outra região. Isso ocorre porque você está provisionando recursos idênticos (EC2, RDS, S3, etc.) em outra região AWS.  
- **Infraestrutura**: A duplicação da infraestrutura pode ser feita de duas formas:  
  1. **Manualmente**: Via CloudFormation ou Terraform, criando stacks idênticos na nova região.  
  2. **Automaticamente**: Usando AWS CloudFormation StackSets ou AWS Organizations para replicar recursos entre regiões.  

📌 **Funcionamento Prático de Load Balancers**  
- **ALB/NLB**: Você precisa criar **Load Balancers (ALB ou NLB)** na nova região também. Eles funcionarão da mesma forma que na região principal.  
- **Configuração**: Os Listeners e Target Groups precisam ser reconfigurados na nova região, apontando para as novas instâncias/ECS/Fargate.  
- **Saída de Dados**: Lembre-se de que há custo de **saída de dados entre regiões** (aprox. **$0.01/GB** para regiões brasileiras).  

📌 **Uso do Route 53 para Failover**  
- **Health Checks**: Configure **Route 53 Health Checks** para monitorar o endpoint principal.  
- **Failover Routing**: Use **Route 53 Failover Routing** para redirecionar o tráfego para a região secundária caso a principal caia.  
  - Exemplo: Crie um registro com *Set Identifier* e *Failover* (Primary/Secondary).  
- **Tempo de Mudança**: A mudança geralmente ocorre em **30-60 segundos** após a falha ser detectada.  

📌 **Opção de Failover**  
- **Ativo-Passivo**: A região secundária fica **inativa** e só é acionada em falha. Custo mantém-se **dobrado**, mas só a região principal é usada.  
- **Ativo-Ativo**: Ambas as regiões estão **ativas**, e o Route 53 distribui tráfego (pesado ou não). Custo **dobrado**, mas com **alta disponibilidade** e **redundância**.  
- **RTO/RPO**:  
  - **Ativo-Passivo**: RTO em **minutos** (tempo de ativação). RPO depende do último backup replicado.  
  - **Ativo-Ativo**: RTO em **segundos**, RPO próximo de **zero** se usar banco de dados multi-região (ex: Aurora Global Database).  

💬 **Como falar pro cliente**:  
- *"Duplicar o ambiente em outra região dobra o custo, mas garante alta disponibilidade. A gente recomenda usar o Route 53 pra fazer o failover automático em caso de falha."*  
- *"O failover com Route 53 é rápido — em menos de 1 minuto o tráfego é redirecionado. Você pode escolher entre ativo-passivo (mais econômico) ou ativo-ativo (mais robusto)."*  
- *"Vamos configurar health checks pro Route 53 monitorar a região principal. Se cair, ele automaticamente manda o tráfego pro backup sem você precisar fazer nada."*  

---

#### **2. Backup de Dados Web (2026)**

📌 **Solução AWS para Backup de Sites/WebApps**  
- **Serviço Recomendado**: **AWS Backup** é o serviço gerenciado para centralizar backups de recursos AWS (EC2, RDS, EFS, S3, etc.).  
- **Funcionalidades**:  
  - Agendamento de backups diários/semanais/mensais.  
  - Retenção configurável (ex: manter últimos 7 dias, 4 semanas, 12 meses).  
  - Restauração com poucos cliques.  
- **Custo**:  
  - **Backup de EBS**: **$0.05/GB/mês** de dados armazenados.  
  - **Backup de RDS**: **$0.023/GB/mês** de dados armazenados.  
  - **S3 Versioning**: **$0.0036/1,000 regras de versão/mês** (se usar S3 como storage).  

📌 **Backup de Dados em Tempo Real (ex: Tradução em Linha)**  
- **Desafio**: Se o site/app tem dados dinâmicos (ex: tradução em tempo real), o backup precisa ser **contínuo** ou **em tempo quase real**.  
- **Solução**:  
  - **RDS (Aurora)**: Use **Aurora Global Database** com replicação multi-região (RPO < 1 minuto).  
  - **S3**: Ative **S3 Versioning** e **Object Lock** para dados imutáveis.  
  - **EFS**: Use **EFS One Zone** ou **Multi-AZ** com replicação para outra região.  

📌 **Exemplo de Custo para um Site Médio**  
- **Site com 100 GB de dados (EC2 + RDS + S3)**:  
  - **Backup Diário**: **100 GB * $0.05 = $5/mês** (EBS) + **100 GB * $0.023 = $2.30/mês** (RDS) = **$7.30/mês**.  
  - **Armazenamento de Backup (30 dias)**: **100 GB * 30 dias * $0.05


======================================================================
CHECKPOINT 3 [6:00-9:00] — Infra exclusiva por cliente + estrutura de contas
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
Teve um cliente que quer infraestrutura exclusiva. Banco deles, back-end deles. Tudo duplicado pra atender só um cliente. Acessível somente da rede deles. Não sei se é viável. Vocês teriam que ter uma conta separada só pra esse cliente. Vocês têm estrutura de contas? Não, hoje é uma só. Vocês conseguem ter uma conta de produção, uma de homologação, uma de dev. Login único entre elas. Billing unificado. Mas gera custo maior de infra.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
PONTOS: Infraestrutura exclusiva para cliente. Duplicação de sistemas. Acesso restrito à rede específica. Contas separadas necessárias. Estrutura de contas atuais. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Cobrança unificada. Custo maior de infraestrutura.

📋 PONTOS EXTRAÍDOS:
Infraestrutura exclusiva para cliente. Duplicação de sistemas. Acesso restrito à rede específica. Contas separadas necessárias. Estrutura de contas atuais. Ambientes de produção homologação e desenvolvimento. Login único entre ambientes. Cobrança unificada. Custo maior de infraestrutura.

📌 RESPOSTA:
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati  

---

#### **1. Infraestrutura Exclusiva para Cliente**  
📌 **Conta AWS Separada**  
- **Sim, é necessário criar uma conta AWS separada** para cada cliente que exige isolamento total (banco de dados, aplicação, rede).  
- **Vantagens**:  
  - Isolamento completo: nenhum compartilhamento de recursos com outros clientes.  
  - Acesso restrito à rede específica do cliente (ex.: VPC dedicada, security groups, NACLs).  
  - Conformidade simplificada (LGPD, ISO, etc.), pois os dados ficam totalmente segregados.  
- **Gerenciamento**:  
  - **AWS Organizations** permite consolidar o *billing* de todas as contas em uma única visão, mas cada conta opera de forma independente.  
  - **SSO (Single Sign-On)**: login único entre contas para facilitar o acesso dos times (ex.: equipe de DevOps acessa todas as contas com um único usuário).  

💬 Como falar pro cliente:  
- *"A gente recomenda criar uma conta AWS só pra vocês — assim, tudo fica isolado: banco, aplicação, rede. Ninguém mais usa esse ambiente."*  
- *"O billing pode ser consolidado, mas cada conta é independente. Vocês veem o custo total, mas sabem exatamente o que cada cliente gasta."*  
- *"Com SSO, os seus times acessam todas as contas com um único login — prático e seguro."*  

---

#### **2. Duplicação de Sistemas**  
📌 **Estratégia de Duplicação**  
- **Cenários comuns**:  
  - **Homologação (Stage)**: Réplica idêntica da produção para testes finais antes de ir ao ar.  
  - **Desenvolvimento (Dev)**: Ambiente com dados fictícios ou anonimizados (custo menor).  
- **Como duplicar**:  
  - **Infra as Code (IaC)**: Usar *CloudFormation* ou *Terraform* para replicar a arquitetura em uma conta diferente.  
  - **Backup e Restore**:  
    - **RDS**: Snapshots automáticos para duplicar bancos.  
    - **S3**: Versionamento e replicação entre *buckets*.  
    - **EC2**: *AMIs* (Amazon Machine Images) para clonar máquinas.  
- **Custos**:  
  - **Produção**: Custo integral (100% dos recursos ativos).  
  - **Homologação**: 30-50% do custo de produção (recursos em *scale-down* ou *spot instances*).  
  - **Desenvolvimento**: 10-20% do custo de produção (recursos mínimos + dados sintéticos).  

💬 Como falar pro cliente:  
- *"A gente pode duplicar o sistema em contas separadas: produção, homologação e desenvolvimento. Cada uma com o nível de recursos que vocês precisarem."*  
- *"Usando Infra as Code, a gente replica tudo em minutos — sem trabalho manual."*  
- *"O custo de homologação costuma ser 30-50% do de produção. Desenvolvimento fica ainda mais barato, com dados fictícios."*  

---

#### **3. Acesso Restrito à Rede Específica**  
📌 **Como Implementar**  
- **VPC Dedicada**:  
  - Cada conta tem sua própria VPC com subnets, route tables e gateways.  
  - **Isolamento de rede**: Sem sobreposição de IPs entre contas.  
- **Controle de Acesso**:  
  - **Security Groups e NACLs**: Filtrar tráfego por IP, porta e protocolo.  
  - **AWS PrivateLink**: Conectar serviços entre contas sem expor na internet (ex.: banco de dados de um cliente não fica acessível para outros).  
  - **VPC Peering ou Transit Gateway**: Se houver necessidade de comunicação *controlada* entre contas (ex.: sistema de um cliente precisa acessar API do outro).  
- **Acesso Externo**:  
  - **VPN ou Direct Connect**: Para conectar a rede do cliente à VPC dele.  
  - **Restrição de IPs**: Permitir só IPs específicos do cliente.  

💬 Como falar pro cliente:  
- *"Cada cliente tem sua própria rede na AWS — ninguém consegue ver ou acessar os recursos dos outros."*  
- *"A gente configura regras de firewall pra liberar só os IPs da sua empresa. Se precisar de conexão direta, usamos VPN ou Direct Connect."*  
- *"Se precisar de comunicação entre sistemas de clientes diferentes, a gente faz com PrivateLink — seguro e sem internet."*  

---

#### **4. Estrutura de Contas Atuais**  
📌 **Modelo Recomendado (Multi-Account Strategy)**  
- **Padrão AWS Well-Architected**:  
  - **Conta de Produção**: Sistema principal em operação.  
  - **Conta de Homologação**: Réplica para testes finais.  
  - **Conta de Desenvolvimento**: Ambiente para desenvolvimento contínuo.  
  - **Conta de Networking/Segurança**: Centraliza firewalls (AWS Network Firewall), DNS (Route 53) e logging (CloudTrail, VPC Flow Logs).  
  - **Conta de Billing/Organizações**: Gerencia cobrança consolidada e políticas de segurança.  
- **Vantagens**:  
  - **Segurança**: Isolamento de ambientes.  
  - **Custo**: Otimização por conta (ex.: desligar recursos de dev à noite).  
  - **Escalabilidade**: Fácil adicionar novas contas para novos projetos ou clientes.  

💬 Como falar pro


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
```
📌 **Contexto identificado:**  
O cliente usa MSP com a Dati, billing via boleto, deploy com **CodePipeline** (branch *master*), infraestruturas diferentes e **Terraform**. Não houve pergunta direta, mas o contexto mostra necessidades técnicas relacionadas a fluxo de CI/CD, gestão de billing e multi-conta.

💬 **3 perguntas para o consultor explorar com o cliente:**  
- "**Como vocês gerenciam as diferenças de infra entre ambientes (ex: dev, prod) usando Terraform? Querem padronizar ou isolar cada conta?**"  
- "**O deploy via CodePipeline no branch *master* é intencional? Vocês precisam de estágios de aprovação (ex: antes de ir pra produção) ou querem adicionar testes automáticos?**"  
- "**O billing consolidado via boleto atende sua necessidade de controle de custos por projeto/cliente? Precisam de alertas de gasto por infra específica?**"  
``` 

> **Próximo passo:** Use essas perguntas para mapear riscos (ex: deploy direto de *master* sem review) ou oportunidades (ex: otimizar custo com tags no Terraform). Se o cliente responder, eu ajudo com a técnica! 


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
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati  
*(Baseado nas dúvidas identificadas)*

---

#### **1. Demora no Auto Scaling do Elastic Beanstalk**  
📌 **Causa principal:** O Elastic Beanstalk usa auto scaling padrão do EC2, que tem *latência* por causa da inicialização da instância (bootstrapping). Em 2026, o tempo médio pra escalar uma instância EC2 no EB ainda é **1-3 minutos** (depende da AMI e do tamanho da instância).  
**Solução rápida:**  
- Ativar *Warm Pool* no EB: mantém instâncias pré-inicializadas em standby. Reduz o tempo de scaling pra **20-30 segundos**.  
- Usar *Multi-AZ* com balanceamento de carga: evita gargalos durante a escala.  
**Custo:** +~15% no billing (pela instância em standby).  

💬 Como falar pro cliente:  
- *"O delay no scaling do Elastic Beanstalk é normal — acontece porque a instância precisa inicializar do zero. A gente corrige isso com um ‘pool’ de máquinas prontas, que reduz o tempo pra menos de 30 segundos."*  
- *"Isso adiciona só 15% no custo mensal, mas elimina o problema de lentidão quando o tráfego sobe de repente."*  
- *"Vamos configurar isso na proposta — é a primeira coisa que fazemos quando o cliente reclama de demora no scaling."*  

---

#### **2. Custo-Benefício do Fargate para Monolito**  
📌 **Situação em 2026:**  
- **Fargate** é **20-30% mais caro** que EC2 para cargas *contínuas* (monolito 24/7).  
- **Benefício chave:** Tempo de deploy **reduzido pela metade** (ex: de 10 min pra 5 min) e *zero manutenção* de OS/pacotes.  
- **Quando compensa?**  
  - Se o time não tem DevOps ou não quer gerenciar patches.  
  - Se o tráfego é *intermitente* (ex: picos de 2h/dia) — o Fargate escala só o container, não a máquina inteira.  
  - Monolitos com **menos de 2 vCPUs** (Fargate tem preço fixo por vCPU/hora; EC2 pequeno já é subutilizado).  

**Exemplo concreto de custo (2026):**  
- Monolito médio: 1 vCPU + 2GB RAM.  
  - EC2 (t3.small): **R$ 120/mês** (us-east-1).  
  - Fargate: **R$ 160/mês** (+33%).  
*Mas:* Se o deploy manual leva 10h/mês (2 pessoas), o Fargate gera economia de **R$ 1.800/mês** em mão de obra.  

💬 Como falar pro cliente:  
- *"O Fargate sai mais caro na conta da AWS, mas se o seu time perde tempo com atualizações de sistema ou deploys demorados, ele compensa na produtividade — até 5x mais rápido no ciclo de lançamento."*  
- *"Para monolitos que rodam 24h, o EC2 ainda é mais barato. Mas se vocês têm picos curtos ou não têm quem cuide da infra, o Fargate é a escolha certa."*  
- *"Vamos fazer uma simulação com os números reais de vocês — se a economia de mão de obra cobrir a diferença de custo, é vantajoso."*  

---

#### **3. Acesso à Máquina para Troubleshooting Urgente**  
📌 **Solução em 2026 (100% compatível com Well-Architected):**  
- **EC2:** Acesso SSH/RDP direto (via *Session Manager* do SSM — **sem abrir porta 22/3389** na internet).  
  - *Session Manager* é **gratuito** (pago só pelo EC2).  
  - Funciona mesmo se a instância perde rede (via AWS PrivateLink).  
- **Fargate:**  
  - **Não tem acesso direto à máquina** (por design — é *serverless*).  
  - Soluções:  
    1. **Mode de Debug:** Iniciar um *sidecar container* com bash (via AWS CLI: `aws ecs execute-command`).  
    2. **Dump de memória:** Usar *AWS Distro for OpenTelemetry* + logs do CloudWatch.  
    3. **Réplica local:** Fazer *snapshot* do volume e rodar em EC2 temporário (tempo médio: 5 min).  

**Regra de segurança (obrigatória):**  
- Nunca abrir SSH público sem MFA. Usar *Session Manager* é o padrão ouro em 2026.  

💬 Como falar pro cliente:  
- *"Para EC2, usamos o Session Manager — vocês acessam a máquina em 10 segundos, sem expor portas na internet e com log completo de comandos. É o método mais seguro que existe."*  
- *"No Fargate não tem SSH, mas a gente resolve rápido: ou entramos via comando remoto no container, ou criamos uma cópia local do ambiente em 5 minutos pra debug."*  
- *"Se vocês precisam de acesso urgente hoje, já temos um playbook pronto — não vamos perder tempo com firewall ou configuração."*  

---

### 📌 Observações Gerais para o Consultor  
1. **Auto Scaling lento no EB:** Sempre sugerir
