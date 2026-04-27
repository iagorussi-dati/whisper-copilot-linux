# Teste Reunião Real — Pontos Resumidos na Chamada 2


======================================================================
SNAP 1 — SSM, IAM, Security Group, deploy manual
======================================================================

📝 TRANSCRIÇÃO (409 chars):
[Gustavo] E aí vocês fazem porta SSH. Ou podem usar System Manager, conexão privada com autenticação AWS. Não precisa liberar Security Group porta 22.
[Juliano] Ok. Acessa via navegador?
[Gustavo] Ou navegador ou CLI.
[Juliano] Interessante. Vi que tinha que criar outros recursos.
[Gustavo] Sim, IAM rules, é tranquilo. Tudo reflete na forma de deploy, hoje bem manual. Teria que evoluir essa parte primeiro.

⏱️ CHAMADA 1: 4.60s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: Cliente busca solução segura para acesso SSH sem abrir porta 22, mencionando alternativas como System Manager e necessidade de criar recursos IAM.
RESPOSTA: CURTA
✅ Contexto extraído (146 chars): Cliente busca solução segura para acesso SSH sem abrir porta 22, mencionando alternativas como System Manager e necessidade de criar recursos IAM.

⏱️ CHAMADA 2: 4.00s | Input: 146 chars
⏱️ TOTAL: 8.61s

📌 RESPOSTA (983 chars):
📌 **SSH seguro sem porta 22**  
Use **AWS Systems Manager Session Manager**. Acesso total via console AWS ou CLI, sem expor portas. Tudo em HTTPS (443).

💬 Como falar pro cliente:  
- "Vocês acessam servidores sem abrir porta 22 — só pelo console AWS."  
- "É mais seguro e não precisa de firewall extra."

---

📌 **Recursos IAM necessários**  
Crie uma **IAM Role** para instâncias EC2 e uma **IAM Policy** com permissão `ssm:StartSession`. Atribua à instância e aos usuários que farão acesso.

💬 Como falar pro cliente:  
- "Só precisa de uma Role na instância e uma Policy pra quem vai acessar."  
- "Configura uma vez e pronto — sem dor de cabeça de firewall."

---

📌 **Vantagem sobre SSH tradicional**  
Sem gerenciar chaves, sem risco de brute-force. Logs de sessão completos no CloudWatch. Atende compliance fácil.

💬 Como falar pro cliente:  
- "Acaba com gerenciamento de chaves e risco de ataques por força bruta."  
- "Tem log completo de tudo que foi feito nas sessões."


======================================================================
SNAP 2 — GitHub, deploy manual, git pull
======================================================================

📝 TRANSCRIÇÃO (210 chars):
[Juliano] Código no GitHub?
[Gustavo] Sim, dois repos, back e front.
[Juliano] Deploy, acessam instância e sobem?
[Gustavo] Hoje é git pull dentro da instância, baixa alterações, aplica migrações. Só pra teste.

⏱️ CHAMADA 1: 1.34s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: O cliente realiza atualizações manuais via git pull na instância para testes, indicando um processo simples mas suscetível a erros e não automatizado.
RESPOSTA: CURTA
✅ Contexto extraído (150 chars): O cliente realiza atualizações manuais via git pull na instância para testes, indicando um processo simples mas suscetível a erros e não automatizado.

⏱️ CHAMADA 2: 2.97s | Input: 150 chars
⏱️ TOTAL: 4.30s

📌 RESPOSTA (573 chars):
### Situação: Cliente faz atualizações manuais via git pull na instância de testes  
**Abordagem: Automatizar com CodeDeploy ou Pipeline do CodePipeline**  

📌 É possível automatizar totalmente o *deploy* de testes usando **CodePipeline + CodeDeploy**.  
Isso elimina riscos de erro manual e versão inconsistente.  
Gasta 5-10 min pra configurar a primeira vez.  

💬 Como falar pro cliente:  
- "Automatizar o *deploy* com CodePipeline elimina os riscos de erro manual que vocês têm hoje."  
- "Em 10 minutos a gente configura e depois é só apertar um botão pra atualizar."


======================================================================
SNAP 3 — Next.js build estoura RAM, CodePipeline
======================================================================

📝 TRANSCRIÇÃO (301 chars):
[Gustavo] Frontend Next.js, pesado no build. Instância pequena estoura RAM. Fazemos build local e upload. Ideal seria Docker multi-stage.
[Juliano] CodePipeline conecta com GitHub, branch produção, faz build deploy teste. Se causar indisponibilidade reverte. Só paga tempo da máquina. Custo 1,5 dólar.

⏱️ CHAMADA 1: 1.54s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: O cliente enfrenta problemas com o build pesado do Next.js que estoura a RAM em instâncias pequenas, necessitando de uma solução mais eficiente e econômica. Busca otimizar o processo de build e deploy.
RESPOSTA: CURTA
✅ Contexto extraído (201 chars): O cliente enfrenta problemas com o build pesado do Next.js que estoura a RAM em instâncias pequenas, necessitando de uma solução mais eficiente e econômica. Busca otimizar o processo de build e deploy.

⏱️ CHAMADA 2: 4.92s | Input: 201 chars
⏱️ TOTAL: 6.46s

📌 RESPOSTA (1275 chars):
📌 **Solução para build pesado Next.js:** Use **EC2 com instâncias maiores** (ex: c5.2xlarge ou r5.xlarge) apenas durante o build via CodeBuild, ou **Fargate com mais CPU/RAM**. Isso resolve o estouro de RAM e é mais barato que manter instâncias grandes 24h.

💬 Como falar pro cliente:  
- "A gente pode configurar o CodeBuild pra rodar em instâncias maiores só no momento do build, economizando custos."  
- "Outra opção é usar Fargate, que escala só o que precisa e você paga só pelo tempo de uso."

---

📌 **Otimização de custo:** Use **EC2 Spot** para builds não críticos (até 90% mais barato). Para deploys frequentes, **AWS Amplify Hosting** ou **CodePipeline com cache** reduzem tempo e custos.

💬 Como falar pro cliente:  
- "Com EC2 Spot, seus builds ficam até 90% mais baratos, ideal para não críticos."  
- "Amplify Hosting ou cache no CodePipeline aceleram deploys e reduzem custos de build."

---

📌 **Cache e otimização:** Ative **cache no Next.js** (`next build --incremental`) e no CodeBuild. Use **S3 para armazenar artefatos** e reduza dependências pesadas.

💬 Como falar pro cliente:  
- "Ativar cache no Next.js e no CodeBuild reduz drasticamente tempo e consumo de RAM."  
- "Armazenar artefatos no S3 e otimizar dependências também ajuda muito no custo."


======================================================================
SNAP 4 — VPN vs SSM, Bastion, segurança
======================================================================

📝 TRANSCRIÇÃO (221 chars):
[Juliano] Interessante Bastion, separar subnet pra reduzir área de ataque. Vocês indicam VPN pra acessar banco e instâncias?
[Gustavo] VPN gera custo alto, não recomendamos. Usamos System Manager. Arquitetura seria assim.

⏱️ CHAMADA 1: 1.53s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: Cliente questiona sobre segurança de rede e acesso a bancos de dados, buscando alternativas eficientes. Necessita reduzir custos e simplificar acesso às instâncias.
RESPOSTA: CURTA
✅ Contexto extraído (164 chars): Cliente questiona sobre segurança de rede e acesso a bancos de dados, buscando alternativas eficientes. Necessita reduzir custos e simplificar acesso às instâncias.

⏱️ CHAMADA 2: 5.13s | Input: 164 chars
⏱️ TOTAL: 6.66s

📌 RESPOSTA (1589 chars):
### Situação: Segurança de rede e acesso a bancos de dados  

📌 Use **Security Groups** e **Network ACLs** pra controlar tráfego de entrada/saída nas instâncias. Combine com **VPCs** pra isolar ambientes.  

💬 Como falar pro cliente:  
- "Security Groups agem como firewall de instância, bloqueando o que não precisa."  
- "VPC isola seu ambiente, reduzindo riscos de acesso externo não autorizado."  

### Situação: Reduzir custos de infraestrutura  

📌 **EC2 Spot Instances** podem reduzir custos em até 90% para workloads flexíveis. Use **Reserved Instances** para workloads estáveis. Otimize com **Auto Scaling**.  

💬 Como falar pro cliente:  
- "Spot Instances cortam custos drasticamente se seu sistema aguenta interrupções ocasionais."  
- "Reserved Instances trazem economia para servidores que ficam sempre ligados."  

### Situação: Simplificar acesso às instâncias  

📌 **AWS Systems Manager Session Manager** elimina necessidade de SSH/RDP. Acesso via navegador ou CLI, com logs e auditoria integrados.  

💬 Como falar pro cliente:  
- "Session Manager acessa suas instâncias sem abrir portas na firewall."  
- "Tudo é registrado, facilitando auditoria e aumentando a segurança."  

### Situação: Acesso seguro a bancos de dados  

📌 **RDS IAM Authentication** usa credenciais temporárias via IAM, eliminando senhas. Combine com **VPC Endpoints** pra evitar exposição na internet.  

💬 Como falar pro cliente:  
- "Autenticação IAM no RDS remove senhas, usando tokens temporários e seguros."  
- "VPC Endpoints mantém seu banco de dados sem IP público, aumentando a proteção."


======================================================================
SNAP 5 — Topologia rede, CodePipeline, CloudWatch
======================================================================

📝 TRANSCRIÇÃO (241 chars):
[Gustavo] Route joga pro load balancer em subnet pública. Só LB e NAT na pública. ECS/EC2 e banco em subnet privada.
[Juliano] CI/CD com CodePipeline e CodeBuild. Observabilidade com CloudWatch. Vocês usam?
[Gustavo] Eu uso em outra empresa.

⏱️ CHAMADA 1: 1.33s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: Cliente descreve infraestrutura de rede com load balancer em subnet pública e serviços em privada. Pergunta sobre uso de ferramentas AWS de CI/CD e observabilidade.
RESPOSTA: CURTA
✅ Contexto extraído (164 chars): Cliente descreve infraestrutura de rede com load balancer em subnet pública e serviços em privada. Pergunta sobre uso de ferramentas AWS de CI/CD e observabilidade.

⏱️ CHAMADA 2: 4.00s | Input: 164 chars
⏱️ TOTAL: 5.32s

📌 RESPOSTA (873 chars):
### Situação: Perguntas sobre CI/CD e observabilidade na infra descrita

📌 **CI/CD**: Use **CodePipeline** com **CodeBuild** e **CodeDeploy**. Integra com GitHub, ACL no deploy em subnets privadas. Suporta rollback automático via CloudWatch Alarms.

💬 Como falar pro cliente:  
- "O CodePipeline orquestra todo o fluxo, desde o repositório até o deploy nos serviços em subnet privada."  
- "Com CodeDeploy, vocês fazem deploy seguro em instâncias privadas, com rollback se algo der errado."

📌 **Observabilidade**: **CloudWatch** para métricas e logs (até em subnets privadas). **X-Ray** para tracing de requisições entre ALB e serviços. Alerta via SNS em falhas.

💬 Como falar pro cliente:  
- "CloudWatch coleta tudo, mesmo nos serviços em privado, e já vem integrado ao ALB."  
- "X-Ray mostra o caminho exato de cada requisição, ajudando a identificar gargalos rápido."


======================================================================
SNAP 6 — São Paulo vs Virginia, custo, latência
======================================================================

📝 TRANSCRIÇÃO (230 chars):
[Gustavo] Recomendando Virginia. Vocês usam SP. Compliance específico?
[Juliano] Mais por delay. SP mais caro, quase dobro.
[Gustavo] SP 35-50ms, Virginia 120ms.
[Juliano] Migrar pra Virginia pra reduzir custo. RDS lá mais barato.

⏱️ CHAMADA 1: 1.53s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: Juliano busca migrar de SP para Virginia para reduzir custos, pois SP é quase o dobro mais caro e oferece maior delay.
RESPOSTA: CURTA
✅ Contexto extraído (118 chars): Juliano busca migrar de SP para Virginia para reduzir custos, pois SP é quase o dobro mais caro e oferece maior delay.

⏱️ CHAMADA 2: 2.87s | Input: 118 chars
⏱️ TOTAL: 4.40s

📌 RESPOSTA (579 chars):
### Migração SP (sa-east-1) para Virginia (us-east-1)

📌 **Custo:** Virginia tem preços ~40% mais baixos que SP em EC2, RDS e S3. Impacto direto na conta mensal.
**Performance:** Latência maior para usuários BR, mas aceitável para backend e dados não críticos em tempo real.
**Suporte:** Todos serviços principais disponíveis em Virginia sem perda de funcionalidade.

💬 Como falar pro cliente:  
- "Virginia reduz custos em até 40% mantendo todos os serviços que vocês usam hoje."  
- "A latência maior só afeta se sua aplicação precisa de resposta super rápida pra usuários BR."


======================================================================
SNAP 7 — Terraform, WAF, estimativa custo
======================================================================

📝 TRANSCRIÇÃO (317 chars):
[Juliano] Usam Terraform?
[Gustavo] Depende do cliente. Terraform ou CloudFormation. Adiciona horas. Adicionaria WAF pra ataques, SQL injection, regras gerenciadas AWS.
[Juliano] Com esses recursos, estimativa de preço mensal. Reservar instâncias. Preciso volumetria. Projeto migração Virginia. Preciso billing atual.

⏱️ CHAMADA 1: 1.44s
🔍 Classificação:
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
CONTEXTO: O cliente precisa de estimativa de custos mensais para migração para Virginia, incluindo recursos como WAF e reservação de instâncias, e requer dados de volumetria e billing atual.  
RESPOSTA: MÉDIA
✅ Contexto extraído (180 chars): O cliente precisa de estimativa de custos mensais para migração para Virginia, incluindo recursos como WAF e reservação de instâncias, e requer dados de volumetria e billing atual.

⏱️ CHAMADA 2: 5.83s | Input: 180 chars
⏱️ TOTAL: 7.26s

📌 RESPOSTA (998 chars):
### Situação: Estimativa de custos para migração para Virginia (us-east-1)

📌 **Custo dos recursos:**
- WAF: USD 3.00 por regra de firewall gerenciada + USD 1.00 por regra personalizada por mês. Mínimo de USD 20/mês.
- Instância reservada: até 72% de desconto vs on-demand. Preços variam por tipo (ex: t3.large: ~USD 220/mês reservado 1 ano).

📌 **Dados necessários para estimativa:**
- Quantidade de regras WAF planejadas (gerenciadas e personalizadas).
- Número e tipos de instâncias que serão reservadas (ex: 2 x t3.large, 1 x m5.xlarge).

📌 **Billing atual:**
- Solicite o gasto mensal atual com cloud (provedor atual) e consumo de dados de tráfego.
- Peça volume de armazenamento, requisições de API e pico de CPU para calcular preciso.

💬 Como falar pro cliente:  
- "O WAF custa USD 3 por regra gerenciada e USD 1 por regra personalizada — vamos definir quantas vocês precisam."  
- "Instâncias reservadas reduzem o custo em até 72%, vou precisar saber os tipos e quantidades para calcular."


======================================================================
SNAP 8 — Incentivos AWS, subsídio, créditos
======================================================================

📝 TRANSCRIÇÃO (241 chars):
[Kyulin] Ver se consegue incentivo AWS.
[Gustavo] AWS pode subsidiar projeto, total ou parcial. Meu papel levar case pra AWS buscar incentivo. Pode ser pra pagar projeto ou créditos.
[Juliano] Entendi. Caminho é esse. Estou mais confortável.

⏱️ CHAMADA 1: 1.44s
🔍 Classificação:
CLASSIFICAÇÃO: SIM
CONCORRENTE: NAO
CONTEXTO: Cliente busca incentivo ou subsídio da AWS para custear projeto, precisa de apoio para reduzir gastos.
RESPOSTA: CURTA
✅ Contexto extraído (102 chars): Cliente busca incentivo ou subsídio da AWS para custear projeto, precisa de apoio para reduzir gastos.

⏱️ CHAMADA 2: 4.39s | Input: 102 chars
⏱️ TOTAL: 5.83s

📌 RESPOSTA (938 chars):
### Situação: Cliente busca incentivo ou subsídio da AWS para custear projeto

📌 AWS tem programas de crédito: AWS Activate (até USD 100k em créditos), AWS Marketplace Credits, e Support Plans com descontos. É necessário validar elegibilidade e ter conta corporativa.

💬 Como falar pro cliente:  
- "A AWS tem créditos de até USD 100k pelo Activate — vamos verificar se vocês se encaixam."  
- "Com o Support Plan Enterprise, vocês ganham descontos e créditos extras, depende do tamanho do contrato."

### Situação: Cliente precisa de apoio para reduzir gastos

📌 Começar pelo Rightsizing (EC2, RDS) e Reserved Instances (até 70% de desconto). Use Cost Explorer para identificar picos e o AWS Budgets para alertas de gasto.

💬 Como falar pro cliente:  
- "Com Rightsizing e Reserved Instances, vocês reduzem até 70% do custo de infraestrutura."  
- "Vamos configurar Budgets para alertar antes do gasto estourar — assim evitam surpresas."


======================================================================
SNAP 9 — Crescimento, volumetria, budget
======================================================================

📝 TRANSCRIÇÃO (206 chars):
[Juliano] Budget limitado. Plataforma vai ter 600 assinaturas início próximo ano, 4 mil final. Movimentação financeira grande. Conseguimos passar volume usuários, produtos, transações pra mensurar máquinas.

⏱️ CHAMADA 1: 1.54s
🔍 Classificação:
CLASSIFICAÇÃO: SIM  
CONCORRENTE: NAO  
CONTEXTO: Cliente tem orçamento restrito mas prevê aumento significativo de assinaturas. Necessita medir infraestrutura para lidar com crescimento e transações financeiras.  
RESPOSTA: CURTA
✅ Contexto extraído (162 chars): Cliente tem orçamento restrito mas prevê aumento significativo de assinaturas. Necessita medir infraestrutura para lidar com crescimento e transações financeiras.

⏱️ CHAMADA 2: 4.92s | Input: 162 chars
⏱️ TOTAL: 6.45s

📌 RESPOSTA (1193 chars):
### Situação: Cliente com orçamento restrito e crescimento previsto

📌 Comece com métricas no CloudWatch — é gratuito e essencial. Identifique gargalos antes de escalar. Use alarmes de CPU, memória e disco.
💬 Como falar pro cliente:
- "Vamos configurar alarmes básicos no CloudWatch pra identificar onde está o gargalo antes de qualquer investimento."
- "Isso não custa nada e garante que qualquer otimização ou escala será direcionada exatamente onde precisa."

📌 Use EC2 T3/T4g para começar — são baratos e escaláveis verticalmente. Quando atingir 80% de CPU constante, migre para instâncias maiores ou use Auto Scaling.
💬 Como falar pro cliente:
- "Começamos com instâncias T3 baratas, que cabem no orçamento, e escalamos só quando realmente necessário."
- "Assim vocês economizam agora e só pagam mais quando o crescimento exigir."

📌 RDS Serverless (Aurora) para transações financeiras — paga só pelo que usa. Garante escalabilidade sem custo fixo alto. Atende LGPD na região SP.
💬 Como falar pro cliente:
- "O Aurora Serverless é perfeito pra transações: vocês pagam só quando há pico, sem custo fixo alto."
- "É seguro e atende LGPD, mantendo seus dados no Brasil com custo controlado."
