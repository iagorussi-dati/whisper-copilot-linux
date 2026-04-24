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
PONTOS: Backup orquestração back-end Elastic Beanstalk Aurora banco OpenSearch pesquisa DynamoDB RTO RPO documentação clientes

📋 PONTOS EXTRAÍDOS:
Backup orquestração back-end Elastic Beanstalk Aurora banco OpenSearch pesquisa DynamoDB RTO RPO documentação clientes

📌 RESPOSTA:
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati

#### **Contexto:**
- **Cliente:** Startup em fase inicial com aplicação containerizada, atualmente em Railway.
- **Necessidade:** Migração para AWS, definição de arquitetura, estimativa de custos, e melhorias de segurança.
- **Dúvidas específicas:** Backup orquestrado, back-end em Elastic Beanstalk, banco de dados Aurora, pesquisa em OpenSearch, uso de DynamoDB, definição de RTO/RPO, e documentação para clientes.

---

### 📌 **1. Backup Orquestrado**

**Resposta Técnica:**
- **AWS Backup:** Serviço nativo para orquestrar backups de múltiplos recursos AWS (EC2, RDS, DynamoDB, EFS, etc.).
- **Funcionalidades:**
    - Agendamento de backups automáticos.
    - Definição de políticas de retenção (ex: 7, 30, 60 dias).
    - Restauração com poucos cliques.
    - Monitoramento via CloudWatch e alertas.
- **Custo:** USD 0.045 por backup de máquina virtual. Custos adicionais por tipo de recurso e armazenamento (ex: USD 0.05/GB/mês para backups de EBS). 
- **Observação:** O cliente precisa definir a frequência e a retenção de backups de acordo com a necessidade de RPO.

**💬 Como falar pro cliente:**
- "O AWS Backup orquestra todos os seus backups em um só lugar — basta definir a frequência e a retenção que ele cuida do resto."
- "Vamos configurar políticas pra cada tipo de dado — banco, aplicação, arquivos — e você tem histórico completo e pode restaurar em minutos."
- "O custo é bem acessível — a partir de USD 0.045 por backup de máquina. Te passo a estimativa final depois de definirmos a frequência."

---

### 📌 **2. Back-end em Elastic Beanstalk**

**Resposta Técnica:**
- **AWS Elastic Beanstalk:** Serviço PaaS que simplifica a implantação e gestão de aplicações sem se preocupar com infraestrutura subjacente.
- **Vantagens:**
    - Suporte a múltiplas linguagens (Python, Node.js, Java, Ruby, PHP, Go, .NET).
    - Auto Scaling e Load Balancing automáticos.
    - Fácil deploy via CLI, Console ou CI/CD (CodePipeline).
    - Integração com outros serviços AWS (RDS, S3, CloudWatch).
- **Custo:** Você paga apenas pelos recursos AWS utilizados (EC2, ELB, etc.). Não há custo adicional pelo Elastic Beanstalk.
- **Observação:** Ideal para startups que querem agilidade sem gerenciar servidores.

**💬 Como falar pro cliente:**
- "O Elastic Beanstalk é perfeito pra vocês — só subem a aplicação e a AWS cuida do resto: scaling, balanceamento, tudo automático."
- "Vocês ganham agilidade no deploy e não precisam se preocupar com a infraestrutura subjacente."
- "O custo é zero pelo Beanstalk — vocês pagam só pelos recursos que ele usa, como EC2 e Load Balancer."

---

### 📌 **3. Banco de Dados Aurora**

**Resposta Técnica:**
- **Amazon Aurora:** Banco de dados relacional compatível com MySQL e PostgreSQL, com performance 5x maior que o RDS padrão.
- **Vantagens:**
    - Compatibilidade com MySQL e PostgreSQL.
    - Auto Scaling de armazenamento (até 128 TB).
    - Replicas de leitura em até 15 milisegundos de latência.
    - Backup automático e recuperação pontual (PITR).
- **Custo:** 
    - Instância db.t3.medium (2 vCPU, 4 GiB): USD 0.0336/hora ≈ USD 24/mês.
    - Armazenamento: USD 0.10/GB/mês.
    - Observação: Custo 30-40% menor que RDS equivalente.
- **Observação:** Recomendado para aplicações com necessidade de alta performance e disponibilidade.

**💬 Como falar pro cliente:**
- "O Aurora é um banco de dados relacional super performático — 5x mais rápido que o RDS padrão e compatível com MySQL/PostgreSQL."
- "Ele faz backup automático e você pode ter múltiplas réplicas de leitura com latência super baixa."
- "O custo pra uma instância média é em torno de USD 24/mês, mais armazenamento. É um excelente custo-benefício pela performance."

---

### 📌 **4. Pesquisa em OpenSearch**

**Resposta Técnica:**
- **Amazon OpenSearch Service:** Serviço de busca e análise de dados em tempo real, sucessor do Elasticsearch.
- **Vantagens:**
    - Busca full-text com relevância e autocomplete.
    - Análise de dados em tempo real (dashboards, visualizações).
    - Integração com Kibana para visualização.
    - Auto Scaling de nós de dados e de busca.
-  **Custo:**
    - Instância r6g.large.search (2 vCPU, 16 GiB): USD 0.24/hora ≈ USD 173/mês por nó.
	- Armazenamento: USD 0.10/GB/mês
    - Observação: O custo varia conforme o tamanho do cluster e o volume de dados.
- **Observação:** Ideal para funcionalidades de busca em aplicações, como catálogo de produtos ou pesquisa de documentos.

**💬 Como falar pro cliente:**
- "O OpenSearch é perfeito pra sua funcionalidade de busca — ele faz buscas rápidas e relevantes, e ainda tem análise de dados em tempo real."



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
**Contexto:** Cliente quer entender como implementar um ambiente de *failover* em outra região AWS, com duplicação de infraestrutura, uso de Route 53 e funcionamento prático de load balancers.  

---

📌 **1. Ambiente Duplicado em Outra Região**  
- **Custo:** O custo **dobra** porque você está replicando **todos** os recursos (EC2, RDS, S3, etc.) em outra região (ex: `us-east-1` → `sa-east-1`).  
- **Duplicação de Infraestrutura:**  
  - Use **AWS CloudFormation** ou **Terraform** para replicar o *stack* automaticamente.  
  - Serviços como **Amazon RDS** podem ser replicados via **Read Replicas** ou **Multi-AZ Deployments**.  
  - **S3** usa **Cross-Region Replication**.  
  - **Bancos de dados:** Para *databases* como Aurora, use **Global Database** (replicação síncrona em até 3 regiões).  

💬 Como falar pro cliente:  
- *"O custo vai dobrar porque estamos criando uma cópia idêntica da sua infra em outra região — mas isso garante alta disponibilidade."*  
- *"A duplicação é automática com ferramentas como CloudFormation — vocês não precisam configurar manualmente cada serviço."*  
- *"Para bancos de dados, usamos soluções como Aurora Global Database, que sincroniza dados entre regiões em tempo real."*  

---

📌 **2. Funcionamento Prático de Load Balancers (ALB/NLB)**  
- **ALB (Application Load Balancer):**  
  - Opera na **Camada 7** (HTTP/HTTPS).  
  - Suporta *path-based routing*, *host-based routing* e SSL termination.  
  - **Failover:** Use **Health Checks** para redirecionar tráfego para a região saudável.  
- **NLB (Network Load Balancer):**  
  - Opera na **Camada 4** (TCP/UDP).  
  - Menor latência e suporta milhões de requisições por segundo.  
  - **Failover:** Funciona com *failover* rápido (subsegundos).  

💬 Como falar pro cliente:  
- *"O ALB vai verificar se seu servidor está no ar — se não estiver, ele automaticamente manda o tráfego pra região de backup."*  
- *"O NLB é ideal se você precisa de performance extrema — ele muda o tráfego em questão de segundos."*  
- *"Ambos se integram com o Route 53 pra fazer o failover sem intervenção manual."*  

---

📌 **3. Uso do Route 53 para Failover**  
- **Health Checks:** Monitore endpoints em ambas as regiões.  
- **Routing Policies:**  
  - **Failover Routing:** Ative um *record* primário e um secundário. Se o primário falhar, o Route 53 redireciona para o secundário.  
  - **Latency Routing:** Direciona usuários para a região mais próxima (útil em *active-active*).  
- **Tempo de Transição:**  
  - **TTL (Time to Live):** Configure com **TTL baixo** (ex: 60 segundos) para failover rápido.  

💬 Como falar pro cliente:  
- *"O Route 53 faz o failover em até 1 minuto — basta configurar os *health checks* nos seus ALBs/NLBs."*  
- *"Vocês podem ter dois ambientes ativos ao mesmo tempo, e o Route 53 manda o usuário pra região mais próxima."*  
- *"Se um *health check* falhar, o Route 53 automaticamente usa o registro de backup — sem precisar de intervenção de vocês."*  

---

📌 **4. Opção de Failover (DR - Disaster Recovery)**  
- **Estratégias de DR:**  
  - **Hot Standby:** Ambiente duplicado **sempre ativo** (custo dobrado, failover em segundos).  
  - **Warm Standby:** Ambiente em *standby* (instâncias desligadas, dados replicados). Ativação em **minutos**.  
  - **Cold Standby:** Ambiente **só em backup** (ex: AMI, snapshots). Ativação em **horas**.  
- **Custo vs. RTO/RPO:**  
  - *Hot Standby* tem **RTO < 1 min** e **RPO ≈ 0** (perda de dados mínima), mas custo **100%**.  
  - *Warm Standby*: **RTO 5-15 min**, **RPO 5-30 min**, custo **~50%**.  
  - *Cold Standby*: **RTO horas**, **RPO horas/dias**, custo **~20%**.  

💬 Como falar pro cliente:  
- *"Se vocês precisam de failover instantâneo, o *hot standby* é a melhor opção — mas o custo é o dobro."*  
- *"Se vocês aceitam uns minutos de indisponibilidade, o *warm standby* reduz o custo pela metade."*  
- *"Vamos montar dois cenários pra vocês escolherem o equilíbrio entre custo e recuperação."*  

---

📌 **5. Otimização de Custos no Failover**  
- **Serviços que podem ser otimizados:**  
  - **EC2:** Use **Spot Instances** para workloads não críticos no ambiente de *standby*.  
  - **RDS:** Use **Reserved Instances** para previsibilidade de custo.  
  - **S3:**


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
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati  
**Contexto:** Cliente precisa de infraestrutura exclusiva para um cliente único, com duplicação de sistemas, acesso restrito, e estrutura de contas para produção, homologação e desenvolvimento.

---

### **Tema 1: Infraestrutura Exclusiva para Cliente Único**

📌 **Conta AWS Separada**  
A solução mais segura e recomendada é criar uma **conta AWS separada** exclusivamente para esse cliente. Isso garante:  
- **Isolamento total**: Banco de dados, aplicações e rede são completamente separados das demais contas.  
- **Controle de acesso refinado**: Você pode definir políticas de IAM e VPC específicas para esse cliente, sem impactar outros ambientes.  
- **Billing consolidado**: Apesar de ser uma conta separada, o faturamento pode ser consolidado em uma Organização AWS, facilitando o gerenciamento financeiro.  
- **SSO (Single Sign-On)**: É possível configurar um login único entre contas, para que sua equipe não precise gerenciar múltiplas credenciais.

**Duplicação de Sistemas:**  
- Para garantir alta disponibilidade e disaster recovery, recomendo usar **AWS CloudFormation** ou **Terraform** para replicar a infraestrutura em outra região (ex: São Paulo e Virginia).  
- Use **AWS Backup** para agendar backups automáticos e garantir RPO (Recovery Point Objective) de até poucos minutos.  

**Acesso Restrito:**  
- **VPCs isoladas**: Crie uma VPC dedicada para esse cliente, com sub-redes privadas e públicas conforme necessidade.  
- **Security Groups e NACLs**: Restrinja o tráfego apenas às portas e IPs necessários.  
- **IAM Roles e Policies**: Crie papéis (roles) com permissões mínimas necessárias para cada serviço ou usuário.  
- **AWS PrivateLink**: Se houver necessidade de conectar essa conta a outras contas ou serviços externos, use PrivateLink para manter o tráfego dentro da AWS.

💬 **Como falar pro cliente:**  
- "Vamos criar uma conta AWS só pra esse cliente. Assim, tudo fica isolado: banco, aplicação, rede. O faturamento pode ser consolidado, mas cada conta opera de forma independente."  
- "Para garantir que vocês não percam dados, vamos configurar backups automáticos e replicar a infraestrutura em outra região. Isso assegura que, mesmo em um desastre, vocês voltem ao ar rápido."  
- "O acesso vai ser super restrito. Só as pessoas autorizadas vão poder entrar, e cada uma com permissões específicas. Tudo isso sem atrapalhar o resto da operação de vocês."

---

### **Tema 2: Estrutura de Contas para Produção, Homologação e Desenvolvimento**

📌 **Organização AWS (AWS Organizations)**  
A melhor prática para gerenciar múltiplos ambientes (produção, homologação e desenvolvimento) é utilizar **AWS Organizations**. Isso permite:  
- **Contas separadas para cada ambiente**: Cada ambiente (prod, hom, dev) fica em uma conta diferente, garantindo isolamento e segurança.  
- **Billing detalhado**: Você pode ver o custo de cada ambiente separadamente, facilitando o controle orçamentário.  
- **Centralized Logging**: Use **AWS CloudTrail** e **Amazon CloudWatch** para centralizar logs de todas as contas em uma conta dedicada para monitoramento.  
- **Políticas Organizacionais (Service Control Policies - SCPs)**: Restrinja o uso de serviços específicos em contas de desenvolvimento para evitar custos acidentais. Por exemplo, bloquear o uso de instâncias de banco de dados de alto custo na conta de dev.  

**Exemplo de Estrutura:**  
- **Conta Produção**: Envio de notas fiscais, processamento de pagamentos, etc.  
- **Conta Homologação**: Testes de carga, validação de novas features antes de ir pra produção.  
- **Conta Desenvolvimento**: Ambientes de desenvolvimento, testes unitários, POCs.  

**Automação:**  
- Use **AWS CloudFormation StackSets** ou **Terraform Workspaces** para implantar a mesma arquitetura em todas as contas, garantindo consistência.  
- **AWS CodePipeline**: Crie pipelines de CI/CD separados para cada ambiente, com estágios de aprovação para promoção de hom para prod.  

💬 **Como falar pro cliente:**  
- "Vamos estruturar três contas separadas na AWS: uma para produção, outra para homologação e outra para desenvolvimento. Isso garante que os ambientes não se misturem e você tenha controle total de custos e segurança."  
- "Com a AWS Organizations, vocês conseguem ver o custo de cada ambiente separadamente e aplicar políticas para evitar gastos acidentais nos ambientes de desenvolvimento."  
- "Automatizamos tudo com CloudFormation. Assim, qualquer mudança que vocês fizerem em desenvolvimento pode ser replicada facilmente para homologação e produção, sem erro e com rastreabilidade."

---

### **Tema 3: Duplicação de Sistemas e Disaster Recovery**

📌 **Duplicação de Sistemas**  
Para duplicar sistemas entre ambientes (ex: prod e hom), utilize:  
- **AWS CloudFormation**: Crie templates que podem ser implantados em qualquer conta/região.  
- **AWS Backup**: Configure planos de backup para bancos de dados (RDS, DynamoDB), EFS, S3, etc. O RPO pode ser definido em minutos.  
- **Amazon S3 Cross-Region Replication**: Replique dados do S3 entre regiões para disaster recovery.  

**Disaster Recovery (DR):**  
- **Piloto Automático (Pilot Light)**: Mantenha uma có


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
📌 **Contexto identificado:** O cliente usa MSP com a Dati, billing via boleto, deploy com CodePipeline no branch master, múltiplas infraestruturas e Terraform. Não houve pergunta direta — isso indica que o cliente já tem parte da infraestrutura em produção e pode estar buscando otimização, clareza ou novas implementações.

💬 **3 perguntas para o consultor fazer ao cliente:**  
- **"Qual é a principal dor hoje? Vocês precisam de mais controle sobre os custos, velocidade de deploy ou segurança na infraestrutura?"**  
  *(Foco: entender a real necessidade em vez de supor)*  

- **"Vocês têm métricas de uso atuais? Quantas pipelines estão rodando, qual o pico de deploy e quanto custa a infra hoje?"**  
  *(Foco: sem dados, qualquer estimativa de otimização ou custo é chute)*  

- **"Quais são os próximos passos de crescimento? Vocês pretendem aumentar o número de ambientes, incluir novos serviços (ex: IA, dados) ou precisam de conformidade específica?"**  
  *(Foco: planejar escalabilidade e evitar retrabalho)*
``` 

> 🔍 **Próximo passo:** Use essas perguntas para direcionar a conversa e identificar onde a Dati pode agregar valor (ex: otimização de custo com Reserved Instances, padronização de Terraform, ou melhoria no pipeline de deploy). Se o cliente mencionar algum ponto específico, eu ajudo com a resposta técnica. 


======================================================================
CHECKPOINT 5 [13:00-20:00] — Auto-scaling lento + Beanstalk→Fargate + monolito
======================================================================

📝 TRANSCRIÇÃO DO INTERVALO:
A gente tem uma dor que é a demora do auto scaling. Elastic Beanstalk leva meia hora até uma máquina subir. Às vezes cai fora do ar. A sugestão era migrar pro Fargate. Mas a gente tem um grande monolito. Quando tem monolito grande, o custo-benefício do Fargate não muda tanto. Mas o auto-scaling não seria mais rápido por ser imagem já buildada? Normalmente sim, mas depende do tamanho da aplicação. Às vezes o problema não é só o build, é o Beanstalk arrumando configuração. E no Fargate, consigo acessar a máquina pra troubleshooting urgente? O build demora 30 minutos e às vezes preciso corrigir na mão.

🔍 CHAMADA 1 (classificação + pontos):
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
PONTOS: Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolitos grandes. Dificuldade de troubleshooting no Fargate.

📋 PONTOS EXTRAÍDOS:
Demora no auto scaling do Elastic Beanstalk. Custo-benefício do Fargate para monolitos grandes. Dificuldade de troubleshooting no Fargate.

📌 RESPOSTA:
### Resumo da Reunião Técnica - Copiloto de Pré-vendas Dati  
**Contexto:** Cliente usa MSP com a Dati, billing via boletos, e está avaliando modernização de infraestrutura.  

---

### **Tema 1: Demora no Auto Scaling do Elastic Beanstalk**

📌 **Auto Scaling no Elastic Beanstalk**  
O Elastic Beanstalk usa o **EC2 Auto Scaling** por trás. O tempo de escala pode ser **lento** em comparação com Fargate porque:  
- **Tempo de inicialização da instância EC2:** Leva ~1-3 minutos pra subir uma nova instância (depende da AMI e tamanho da instância).  
- **Health checks:** O EB verifica a saúde da aplicação antes de liberar o tráfego — pode adicionar +30-60 segundos.  
- **Configuração do Scaling Policy:** Se estiver usando métricas como CPU (ex: >70% por 5 minutos), o *trigger* demora pra disparar.  

**Soluções:**  
- **Configurar *Scaling Policies* mais agressivas:** Usar métricas como “Network In/Out” ou “Request Count” pra disparar mais rápido.  
- **Usar *Warm Pool* de instâncias:** Manter algumas instâncias pré-criadas em *standby* reduz o tempo de escala.  
- **Trocar pra Fargate:** Se o problema for latência, Fargate escala em ~30-50 segundos (veja Thema 2).  

💬 **Como falar pro cliente:**  
- *"O Elastic Beanstalk demora pra escalar porque precisa subir instâncias inteiras de EC2 — cada uma leva cerca de 1-3 minutos no pior caso. Mas dá pra otimizar isso com políticas mais agressivas ou um pool de instâncias prontas."*  
- *"Se a demora for crítica, o Fargate escala em menos da metade do tempo — vale a pena testar se encaixa no orçamento de vocês."*  
- *"O primeiro passo é a gente verificar as políticas de escala atuais de vocês — às vezes é só ajustar o *threshold* que já melhora bastante."*  

---

### **Tema 2: Custo-Benefício do Fargate para Monolitos Grandes**  

📌 **Fargate vs EC2 para Monolitos Grandes (2026)**  
**Fargate:**  
- **Vantagens:**  
  - **Sem gerenciamento de infra:** Não precisa cuidar de ASG, AMI, patch de SO.  
  - **Escala mais rápido:** 30-50 segundos pra subir um novo *container*.  
  - **Ideal para *spikes* imprevisíveis:** Paga só pelo que usa (ex:  `1 vCPU + 2GB = ~R$ 50/mês` por container *24/7*).  
- **Desvantagens (custo):**  
  - **Custo fixo por vCPU/GB:** Em **2026**, o preço médio em São Paulo (`sa-east-1`) é **R$ 0,04/vCPU-h** e **R$ 0,008/GB-h**.  
  - **Monolito grande = 1 container só:** Se o monolito usar 4 vCPU e 8GB, o custo mensal é **~R$ 460** (fixo, 24/7).  
  - **Sem *overcommit*:** Ao contrário do EC2, não dá pra otimizar com *CPU Burst* ou *Reserved Instances*.  

**EC2 (ex: c6i.2xlarge):**  
- **Custo mensal:** ~R$ 250/mês (On-Demand na SP).  
- **Benefício:** Pode colocar *múltiplas instâncias* atrás de ASG e balanceador.  
- **Otimização:** Com *Reserved Instances* (1 ano, total upfront), o custo cai **~40%** → **R$ 150/mês**.  

**Conclusão:**  
- **Fargate compensa se:**  
  - O time não tem expertise pra gerenciar EC2/ASG.  
  - A aplicação tem *spikes* sazonais (ex: Black Friday) — paga só no pico.  
  - O custo do monolito for **< R$ 300/mês** em Fargate.  
- **EC2 compensa se:**  
  - O monolito for grande (**> 4 vCPU**) e rodar 24/7.  
  - Houver possibilidade de *Reserved Instances* ou *Spot* (se tolerar intermitência).  

💬 **Como falar pro cliente:**  
- *"Pra monolitos grandes, o Fargate é mais simples e escala rápido, mas pode sair até 2x mais caro que EC2 se a aplicação roda o tempo todo."*  
- *"Se vocês têm um time de infra ou querem reduzir custo, EC2 com Reserved Instances é mais econômico — mas exige mais manutenção."*  
- *"Vamos fazer uma simulação concreta com os dados de tráfego de vocês? Assim a gente compara os dois cenários em números reais."*  

---

### **Tema 3: Dificuldade de Troubleshooting no Fargate**  

📌 **Troubleshooting no Fargate (2026)**  
**Problemas comuns:**  
- **Logs dispersos:** Logs de container vão pro **CloudWatch Logs** (por padrão). Se não estiver configurado, *não tem acesso ao syslog do host*.  
- **Sem SSH/Console:** Não dá pra entrar no *host* ou no container sem ferramentas específicas.  
- **Métricas limitadas
