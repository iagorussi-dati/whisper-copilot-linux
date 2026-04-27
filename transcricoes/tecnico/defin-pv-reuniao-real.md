# Reunião Real — PV Defin (Juliano) com Gustavo Conti
Data: 2026-04-27

## Intervalos dos snapshots (como foram apertados)

### SNAP 1 — SSM, IAM, Security Group, deploy manual
[Gustavo Conti] E aí vocês fazem uma porta SSH dela, tanto para o banco de dados, quanto para as instâncias. Ou vocês podem usar o System Manager. Ele cria uma conexão privada usando a tua autenticação da AWS. Você não precisa liberar nem Security Group da porta 22.
[Juliano] Ok. Daí só acessa via navegador?
[Gustavo Conti] Ou via navegador, ou via terminal CLI.
[Juliano] Interessante. Eu tava lendo sobre esse cara, mas vi que tinha que criar outros recursos.
[Gustavo Conti] Sim, criar IAM rules, é bem tranquilo. Na verdade tudo isso vai refletir a forma como a gente faz deploy e hoje está bem manual. Eu acredito que teria que evoluir essa parte primeiro.

### SNAP 2 — GitHub, deploy manual, git pull
[Juliano] O código de vocês está no GitHub?
[Gustavo Conti] Sim, dois repositórios, back-end e front-end, no GitHub.
[Juliano] E para deploy, vocês acessam a instância e sobem lá?
[Gustavo Conti] Deploy hoje é git pull dentro da instância, baixa alterações, aplica migrações. É só para teste.

### SNAP 3 — Next.js build estoura RAM, CodePipeline, CI/CD
[Gustavo Conti] O frontend usa Next.js, é pesado no build. Instância pequena estoura RAM. A gente faz build local e upload direto. O ideal seria Docker com multi-stage build.
[Juliano] Tem um serviço na AWS chamado CodePipeline. Conecta com GitHub, branch de produção, faz build, deploy, teste. Se causar indisponibilidade, reverte. Só paga pelo tempo da máquina de build.
[Gustavo Conti] Ah, entendi.
[Juliano] Custo normalmente fica em 1,5 dólar.

### SNAP 4 — VPN vs SSM, Bastion, segurança
[Juliano] Interessante a parte do Bastion, separar subnet pra reduzir área de ataque. Vocês indicam VPN pra acessar banco e instâncias?
[Gustavo Conti] Depende do caso. VPN gera custo alto, normalmente não recomendamos. Usamos System Manager. A arquitetura seria mais ou menos assim.

### SNAP 5 — Topologia de rede, CodePipeline, CloudWatch
[Gustavo Conti] Route joga conexões pro load balancer em subnet pública. Só LB e NAT gateway ficam na pública. ECS/EC2 e banco em subnet privada.
[Juliano] CI/CD com CodePipeline e CodeBuild. Observabilidade com CloudWatch. Vocês já usam CloudWatch?
[Gustavo Conti] Eu uso em outra empresa.

### SNAP 6 — São Paulo vs Virginia, custo, latência
[Gustavo Conti] Aqui estamos recomendando Virginia. Vocês usam São Paulo. Têm compliance específico?
[Juliano] Foi mais por questão de delay. SP é mais caro, quase o dobro.
[Gustavo Conti] SP dá 35-50ms, Virginia dá 120ms. Depende da aplicação.
[Juliano] Talvez migrar pra Virginia pra reduzir custo. RDS lá também é mais barato.

### SNAP 7 — Terraform, WAF, estimativa de custo
[Juliano] Vocês usam Terraform pra criar recursos?
[Gustavo Conti] Depende do cliente. Terraform ou CloudFormation. Adiciona horas no projeto. Eu adicionaria WAF pra cobrir ataques. SQL injection, regras gerenciadas da AWS.
[Juliano] Tendo esses recursos, vocês conseguem estimativa de preço mensal. Tem como reservar instâncias. Preciso entender volumetria. Montar projeto com migração pra Virginia. Preciso do billing atual.

### SNAP 8 — Incentivos AWS, subsídio, créditos
[Kyulin] Ver se consegue incentivo da AWS.
[Gustavo Conti] Existe possibilidade da AWS subsidiar o projeto, total ou parcialmente. Meu papel é levar o case pra AWS e buscar incentivo. Pode ser pra pagar projeto ou créditos.
[Juliano] Entendi. Acho que o caminho é esse. Estou me sentindo mais confortável.

### SNAP 9 — Crescimento, volumetria, budget
[Juliano] Budget limitado. Plataforma vai ter 600 assinaturas até início do próximo ano, 4 mil até o final. Movimentação financeira grande. Conseguimos passar volume de usuários, produtos, transações pra mensurar máquinas.
