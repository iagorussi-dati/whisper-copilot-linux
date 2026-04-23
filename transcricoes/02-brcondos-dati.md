# [BRCondos & Dati] Discovery / Entendimento

- **Data:** Wednesday, April 22, 2026 at 4:00 PM
- **Duração:** 44:22
- **Participantes:** Rafaela Koller, Carlos Diego Russo Medeiros (iTFLEX), Rafael Heise, Danilo Noris Capeloto, Luiz Rampanelli, Dalton

---

[2:29] Rafaela Koller: Oi, Carlos. Tudo bem? Tudo ótimo. Quanto tempo, né?

[2:39] Carlos (iTFLEX): Pois é. Tudo certo por aí?

[2:51] Rafaela Koller: Deixa eu te apresentar, né? O Danilo é o nosso account manager que vai atender a BR Condos. E junto comigo e com o Danilo está o Luiz, que é o nosso arquiteto de soluções de pré-venda.

[3:14] Carlos (iTFLEX): Ela é uma franqueadora e administradora de administração de condomínio. Ela é uma administradora de econômico gigante.

[3:32] Danilo Noris Capeloto: Esse aplicativo próprio é o BR Condos, né? Pessoal utiliza muito aqui em Blumenau. Eles são de Joinville, ali no bairro América também.

[4:46] Carlos (iTFLEX): Então, por coincidência, a gente estava conversando recentemente aí na BR Condos, né? Acabamos falando aí de cloud. Você comentou que tinha recebido a indicação da Dati lá atrás da própria AWS. A Dati é um grande parceiro nosso. Além de a gente ter clientes em comum, indicar clientes, a gente também é cliente deles. A nossa estruturação da conta AWS aqui, da ITflex, tanto da PABXFLEX foi eles que orquestraram para a gente.

[5:29] Carlos (iTFLEX): E daí eu cutuquei para promover essa reunião para você conhecer a DAT e ver daqueles serviços que eles têm, desde estruturação da conta, autenticação ou até aqueles recursos de segurança mais avançados da AWS.

[5:58] Carlos (iTFLEX): Eu já falei, comentei com eles que você tem bastante autonomia, vocês estão tudo estruturados aí por conta própria, mas frente ao crescimento da empresa, eu acho importante ter um parceiro AWS.

[6:35] Carlos (iTFLEX): Beleza, então vou deixar com eles então. Obrigado, tá?

[6:42] Danilo Noris Capeloto: Obrigado, Carlos. É um prazer conhecer vocês. A gente é de Joinville também. E o Luiz aqui é o nosso pré-venda técnico, ele veio da AWS. A ideia no primeiro momento é entender um pouquinho o cenário de vocês, um pouco da empresa de vocês, né?

[8:00] Rafaela Koller: Vamos lá. Entender a BR Condes, a BR Condes nasce, na verdade, a HFPX nasce lá atrás, né? Que é um fundo de investimentos que a gente montou. Daí naquela época a gente começou com a AWS, que a gente tinha vários projetos. E daí, nesse meio tempo, nasce a BR Condes.

[8:29] Rafaela Koller: Então, desde essa época, a gente tem essa conta aí da AWS que vai ser 2014. A gente vem vindo, sempre usando a AWS. Algumas vezes a AWS fez visita com a gente, a gente conversou.

[9:13] Rafaela Koller: É porque a gente estava falando de custos, e ele falou, não, vamos então migrar essa parte de vocês serem Microsoft aí, de SQL Server, vamos botar para PostgreSQL, a gente joga a DAT junto, eles têm consultoria para isso. Mas a gente depois conversou e meio que a gente acabou fazendo dentro de casa e fomos andando.

[9:43] Rafaela Koller: A gente tem a BR Contas andando todo na AWS. A gente roda poucas coisas da AWS. Hoje a gente tem os EC2 puros lá, banco e dados em EC2, as aplicações, daí um load balance clássico, o WAF. A gente utiliza o SES, que é de e-mail, e o S3, bastante S3.

[10:31] Rafaela Koller: A gente tem a SCD, que na verdade a gente não está loucamente abrindo contas ainda, mas a gente já tem toda a infraestrutura dela. Ali é mais uma estrutura um pouquinho mais moderna, mas também a gente utiliza as partes básicas.

[11:01] Rafaela Koller: A gente está utilizando agora o KMS e o Cofre, que está mais forte. O KMS é bastante, até porque a gente precisa cumprir um regulatório do Banco Central lá, que tem que ter umas chaves que têm que ser irreversíveis, encriptar dados. Então, a nossa arquitetura hoje é muito simples. Hoje são contas tudo únicas.

[11:39] Rafaela Koller: Tem login e contas que têm menos permissão para fazer acesso no dia a dia, mas aquela arquitetura organizacional que o Carlos falou para nós, a gente não implementou. Eu acho que quando o Carlos trouxe essa parte de a gente ter uma consultoria para conversar sobre isso, a gente achou interessante porque dentro de casa a gente vai acabar não fazendo e a gente tem essa necessidade. Chegou nesse momento de maturidade que precisa.

[12:27] Danilo Noris Capeloto: Legal. Obrigado pelo briefing. Hoje vocês tem uma equipe de quantas pessoas na parte da tecnologia?

[12:36] Rafaela Koller: Nessa equipe que trabalha com a AWS, hoje é eu e o Rafa. Tudo que a gente vai fazer deploy, vai mexer em instância, vai mexer em chave, vai fazer permissões, é só eu e o Rafa que mexe. Tem uma terceira pessoa, o Clayson, que ele é o nosso backup, mas ele não é especialista.

[13:11] Rafaela Koller: Em desenvolvimento, a gente tem desenvolvedores, a gente tem pessoas que mexem com a base. Hoje, a BR-Contas, a gente acaba tendo cento e poucas franquias, em média de 800 usuários e quando tu chega nos condomínios a gente vai ter duzentos e poucos mil usuários. A gente não distribui software hoje. A gente tem o software dentro de casa para prestar o nosso serviço para essas franquias.

[14:08] Danilo Noris Capeloto: E hoje, tu falou que consome pouco AWS, mas quanto mais ou menos tem o billing de vocês?

[14:53] Rafaela Koller: Do mês passado, de março, ele ficou em 8.304 dólares.

[15:07] Rafaela Koller: Cartão. Que eu acho que deve ter dado uns 46 mil reais.

[15:36] Rafaela Koller: O S3 é uma coisa que depois que a gente começou a usar foi aumentando a conta e tá lá, né? Sabe como eles ganham dinheiro, né? Com transferência e tal.

[15:51] Danilo Noris Capeloto: Eu pergunto porque a gente tem algumas possibilidades como parceiro. Hoje vocês estão buscando alguma melhoria em tecnologia, IA, algum projeto?

[16:10] Rafaela Koller: Hoje a parte de IA a gente tá bem forte utilizando e implantando aqui com o Gemini. A gente tá utilizando muito o Google, deu muito certo pra nós.

[16:37] Rafael Heise: O Gemini e o ChatGPT, em poucos casos lá.

[16:40] Rafaela Koller: O ChatGPT eu tombei já. Usei muito no início, mas ele não tava tão corporativo pra que a gente precisava. A gente gostou da solução que é o Google. Melhoria de tecnologia, a gente tá tentando sair do Microsoft 100%. A gente tava migrando pro NetCore. E a gente quer sair do SQL Server para o Postgre.

[17:43] Danilo Noris Capeloto: Legal. Eu tô vendo três cenários que a gente pode estar trabalhando em conjunto. Hoje a gente é uma empresa de consultoria. Faz migração de on-premises pra cloud, de cloud pra cloud e até modernizações. Faz sustentação e suporte.

[18:06] Danilo Noris Capeloto: A gestão de faturamento, a cada 5 mil vocês ganham uma hora de consultoria e pode pagar por boleto. E nesse caso você consegue ter um prazo de 50 dias de fôlego. A gente tem um parceiro que é a Telecinex que faz esse billing.

[19:09] Carlos (iTFLEX): Só complementando, o faturamento é bem legal, a gente usa aqui também. Toda vez que a gente vai fazer reserva, a DAT nos apoia, define o melhor tipo de reserva, todo ano a gente tem agenda específica.

[19:55] Danilo Noris Capeloto: E o legal que com a gente trazendo o billing, a gente consegue fazer parcelamento das reservas. Vocês pagam com desconto e ainda pagam parcelado pelo boleto em seis vezes.

[20:16] Rafaela Koller: A gente tem essa oferta do Allupfront parcelada em seis vezes e a gente também consegue trazer outras soluções que são cabíveis de reserva. O CloudFront também é possível de reservar. Outros serviços de banco de dados agora saiu no Reinvent recentemente.

[21:21] Rafaela Koller: Além das reservas, a gente também traz a questão de sizing de máquina, troca de disco. A AWS atualiza todo ano as suas features, então quanto mais atualizado vocês tiverem, menor o valor vocês vão pagar, mais performance vocês vão ter.

[21:51] Rafaela Koller: Essa ideia de FinOps a gente também traz para vocês dentro da gestão de faturamento e tudo isso sem nenhum custo para vocês. O valor que vocês pagam hoje para a AWS é o mesmo que vocês pagam via gestão de faturamento.

[23:07] Rafaela Koller: Eu consigo a minha conta e eu fico com a minha liberdade? Eu posso subir instância descer instância? Não fica engessado, né?

[23:35] Rafaela Koller: Vocês tenham total autonomia. Se vocês tiverem uma organization, a gente cria ou traz essa organização para cá, continua sendo de vocês. O que vai mudar? A forma de pagamento. Em vez de pagarem para a AWS via cartão, vocês vão pagar para a Telecinex via boleto. Muda só isso. Toda a conta continua sendo de vocês.

[25:23] Luiz Eduardo Mello Rampanelli Júnior: Com essa parte de estruturação de contas eu acho que encaixa perfeitamente a questão do Well-Architected. Durante essa estruturação de contas, é validado tudo de acordo com o Well-Architected Framework da AWS. Vai ser verificado desde a excelência operacional, segurança, confiabilidade, otimização de custos, sustentabilidade. A gente tem um time específico aqui para trabalhar fazendo essas validações para vocês.

[26:09] Luiz Eduardo Mello Rampanelli Júnior: A gente vai olhar todos esses pilares que a AWS tem as melhores práticas. O pessoal da AWS costuma só te mandar documentação. Nós, DAT, a gente pega e realmente vai executar e resolver todos os findings com vocês dentro desse Well-Architected.

[27:11] Danilo Noris Capeloto: Então a gente poderia ter três frentes aqui. Billing, estruturação de conta com Well-Architected, e ser um braço de vocês nesse processo de migração da Microsoft para a AWS. São quatro frentes na realidade.

[28:02] Danilo Noris Capeloto: Como parceiro da AWS Advanced, a gente tem parceria muito forte com a AWS em questão de incentivos. Às vezes a gente pode conseguir algum incentivo que vai ajudar vocês a custear o projeto.

[29:47] Rafaela Koller: A gente tem interesse em fazer essa estruturação de conta. A gente tem hoje duas empresas bem separadas. Uma é a BR Condos. E a outra conta da SCD deve estar gerando 1.200 de AWS. São CNPJs totalmente diferentes.

[30:28] Danilo Noris Capeloto: A gente pode trazer tudo para baixo dessa organização de vocês.

[30:42] Rafael Heise: Só tem que ver, porque tem algumas questões regulatórias lá do banco, que ele não deixa misturar.

[31:15] Rafaela Koller: Pelo regulatório a gente não pode misturar negócios. BR-Condos e SCD são coisas separadas. Mas na mesma estrutura, tá tranquilo.

[31:34] Luiz Eduardo Mello Rampanelli Júnior: Isso tudo é levado em conta durante a estruturação. Essa questão de não ter ambiente fintech no meio, o pessoal aqui já tem expertise para lidar.

[32:43] Danilo Noris Capeloto: A estrutura de contas e o Billing juntos.

[32:59] Luiz Eduardo Mello Rampanelli Júnior: A gente tem um CloudFormation, basicamente um read, para pegar o que vocês têm de estrutura ali dentro. Ele não vai em workload, ele vai me dizer como que está configurado, se tem WAF, se não tem, se tem MFA, se está usando EC2, S3. Ele só me lista o que vocês estão usando para a gente poder fazer a análise inicial.

[34:57] Carlos (iTFLEX): A gente fez aqui, a gente integrou a autenticação da AWS com o Google Workspace. Fica mais fácil. Eu consigo criar acesso para os analistas com acesso restrito a alguma conta. Normalmente tem uma conta de organização que já segue um e-mail padrão.

[36:06] Carlos (iTFLEX): O ideal é ir para outra conta, não ficar na mesma conta. Conta de segurança. O KMS é crítico para falar com o Banco Central. Às vezes faz sentido ter uma conta específica só para ele. E essa criação de contas a AWS não cobra.

[37:16] Carlos (iTFLEX): Vocês estão em boas mãos, Dati. Eu conheci o CEO deles, depois conheci a equipe. Contratem a equipe que eu gosto do trabalho.

[38:06] Carlos (iTFLEX): Vou pedir licença para vocês que vou ter que sair. Mas estão conectados, precisando, contem conosco. Um abraço, gente.

[39:02] Rafaela Koller: Esse mês o Bradesco pegou e pau foi 47 mil no cartão. Então, sim, é legal ter faturamento via boleto. Acho que a gente consegue passar tranquilo aqui com o nosso CFO. E essa parte do Well-Architected é bem importante para nós. A gente acho que chegou nesse momento de maturidade. E a gente quer fazer isso.

[40:08] Rafael Heise: É uma conta de entrada interessante, porque aí depois vocês entendendo essa estrutura de contas, vão poder entender melhor o serviço que a gente usa.

[40:38] Danilo Noris Capeloto: E hoje o suporte vocês tem deles lá? Ou vocês mesmos fazem o suporte e monitoramento?

[40:43] Rafaela Koller: Não, não tem suporte. Não tem plano de suporte. Nunca usei suporte.

[40:48] Rafael Heise: A gente foi meio na raça. Se não der ruim, a gente continua. Se der ruim, a gente dá o rollback.

[41:41] Rafael Heise: A gente é velho, né? A gente vem lá da época que a gente mesmo fazia as coisas, montava os servidores. A AWS hoje oferece bastante serviço de infraestrutura, que é plug and play. Como a gente já vem dos velhos tempos, a gente acaba se virando muito sozinho. Claro que isso às vezes traz um pouco de sofrimento. Algumas coisas podiam ser resolvidas mais rápido. Mas trazer esse conhecimento acho que vai ser bem inteligente.

[42:27] Danilo Noris Capeloto: A gente tem alguns eventos que a gente faz aqui. Tem a October Cloud, que tem várias informações. E tem workshops junto com a AWS.

[42:52] Danilo Noris Capeloto: Vamos combinar o seguinte. Eu vou levantar todas as informações que eu preciso. Preparo uma apresentação, trago pra vocês. Provavelmente semana que vem seria melhor.

[43:45] Danilo Noris Capeloto: Beleza, gente. Obrigado pela oportunidade, pelo bate-papo. E fica aí o convite, quando vier pra Blumenau, vem conhecer a Dati, tomar um café.

[44:16] Rafaela Koller: Beleza então, gente. Tchau, obrigado, até logo. Boa semana, tchau, tchau.
