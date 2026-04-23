# PV | Defin <> Dati

- **Data:** Monday, March 9, 2026 at 5:00 PM
- **Duração:** 59:17
- **Participantes:** Gustavo Conti, Cristopher David de Lima, Danilo Noris Capeloto, Juliano Nicocelli

---

[0:07] Gustavo Conti: O cara tá pedindo pra entrar, é isso? Falta o Chris, né? Ah, cadê o Chris? Sou o principal. Deixa, eu vou admitir ele e vou pedir uns 5 minutos, tá? Tá, beleza. Boa tarde, Juliano. Tudo bem?

[0:31] Juliano Nicocelli: Opa, boa tarde.

[0:35] Gustavo Conti: Pera, eu vou te pedir só dois minutos, o Christopher já tá chegando aqui, daí a gente inicia a reunião com todo mundo.

[0:41] Juliano Nicocelli: Tranquilo, tranquilo. Fala, Cris. Tudo certo, tudo certo aí.

[1:15] Cristopher David de Lima: Correria aqui como sempre, né? Padrão, cara. E aí, o que vocês me contam de bom hoje?

[1:26] Juliano Nicocelli: Então, estava hoje de manhã, na verdade, tirei um tempinho aí para fazer uma estruturação aí do que a gente tem no ambiente, Pensando um pouquinho no produto que a gente está construindo agora que é o IBES e no ecossistema do que a gente está fazendo. Posso dar uma introduzida ali para o Gustavo e para o Danilo sobre o projeto. Só

[1:56] Cristopher David de Lima: uma dúvida. Vocês já se apresentaram senão eu faço uma breve. Vou até abrir o microfone para você Gustavo. Gustavo é do nosso time de pré vendas ele cuida mais da parte técnica. Eu digo que dá para fazer e tal. Gustavo fala como. Eu acho que ele vai ter mais protagonismo aqui nessa conversa. Danilo da área comercial está entrando com a gente aqui. Tem o que um mês Danilo. Então vai estar mais como ouvinte nessa conversa.

[2:36] Gustavo Conti: Bom, a minha atuação vai ser realmente como pré-vendas técnicas. Significa basicamente que eu vou tentar entender quais são as suas necessidades. Eu já tinha passado até um briefing do que vocês trouxeram nas últimas conversas e traduzi isso em um projeto.

[3:07] Juliano Nicocelli: Legal, legal. Bom, fazendo uma introdução breve aqui, daí eu já quero mostrar aqui um material que eu construí mais cedo. A gente é uma… A Defin é uma empresa que é basicamente uma spin-off de uma boutique de investimentos de São Paulo. Então a gente já faz um ano e meio praticamente que a gente já vem construindo coisas dentro da boutique de investimentos.

[3:54] Juliano Nicocelli: A gente não tem investidores externos, a gente é bootstrap mesmo, a gente está construindo internamente. E basicamente a rotina de uma boutique de investimentos ela é dada em leitura de muitos documentos. Imagina que a WEG precisa de 20 milhões para abrir uma unidade nova. Então a WEG traz essa demanda.

[4:40] Juliano Nicocelli: A gente olha para a necessidade de capital, a quantidade de garantias, as garantias que essa empresa tem. E os documentos relacionados à saúde financeira da empresa, todas as dívidas que essa empresa tem, etc.

[5:05] Juliano Nicocelli: Então, o nosso software, ele praticamente ele tem essa capacidade de fazer essa análise documental, então a gente faz a extração, a gente tem um pipeline de extração de informações, de documentos, por exemplo, demonstrativo de resultado, balancete, esses documentos financeiros e contábeis.

[5:56] Cristopher David de Lima: Complementar porque hoje pelo que eu entendo assim do seu serviço está construindo uma esteira Vamos lá antes de chegar numa mesa de crédito uma esteira de coleta de dados automatizada.

[6:37] Cristopher David de Lima: A gente está falando de centenas e dezenas de informações transbordando ali para o seu sistema.

[6:44] Juliano Nicocelli: Sim, exato. Então assim só só para finalizar o raciocínio ali porque a gente a gente começou a construir internamente esse software Só que a gente tem mais de 800 instituições financeiras que a gente tem relacionamento, homologadas dentro desse software. E a gente começou a tornar esse software um comercial.

[7:31] Juliano Nicocelli: Ele é um investimento em banking as a service. Então basicamente ele faz essa esteira. Então o nosso software automatiza isso. só que para um outro perfil de cliente. Então são tokenizadoras de ativos que agora está começando a crescer ativos digitais.

[8:12] Juliano Nicocelli: São empresas outras boutiques de investimentos que fazem esse processo. Pode ser até instituições financeiras. Então por exemplo Banco C6 ele já faz esse processo ele já tem o capital para emprestar para as empresas só que ele precisa analisar todos os documentos e o nosso software ele reduz a quantidade de tempo humano.

[9:08] Juliano Nicocelli: a escala do software, entende? Então a gente precisa fazer isso bastante assíncrono porque são muitos arquivos que a gente precisa processar.

[9:36] Juliano Nicocelli: Então, o nosso público ideal agora, que a gente está atacando, inclusive a gente tem uma demo para a próxima semana, são tokenizadores de ativos digitais, são instituições financeiras que já são homologadas internamente.

[10:15] Gustavo Conti: Para mim, pelo menos, está tudo ok. Preciso seguir com a arquitetura. Mas só para ter certeza, vocês ainda não receberam uma planilha com exigências, né?

[10:30] Juliano Nicocelli: Não.

[10:39] Gustavo Conti: Dos clientes de vocês. Vocês vão atender muito o banco, coisa assim. Cara, a gente recebeu… Tinha um cliente nosso que atende o Itaú. A gente recebeu uma planilha de exigência deles bem… Olha… Mais de um giga de planilha.

[10:54] Juliano Nicocelli: Por questão de compliance, porque LGBT, etc. Tem uma série de questões. Então, inclusive, a nossa infra tem hoje, atual, ela é bem MVP e tem uma série de furos. Então esse é o momento de a gente olhar para o que a gente tem, para o ambiente, para a refatoração que a gente vai precisar fazer.

[11:35] Gustavo Conti: Mas é tudo questão de momento. Não adianta vocês investirem agora 100 mil reais para construir uma paita de uma infra AWS e vocês não estão nem com os clientes que vocês esperam ter ainda.

[11:49] Juliano Nicocelli: E esse sempre foi a minha leitura assim quando eu comecei porque eu já trabalho com a AWS já faz um tempinho. Eu tenho uma noção bem interessante de ambiente AWS. E eu poderia começar no dia zero, fazendo um ambiente parrudo. Só que a minha decisão técnica é criar um monolito e ver o que a gente vai fazer. Porque trazer complexidade muito cedo traz custo, manutenção, etc.

[12:32] Gustavo Conti: Eu gosto muito de estudar, não sei se você já viu, o case da Netflix e do iFood. Os dois tiveram três momentos. O que vocês estão agora, que é o de validar produto. E aí depois um momento que eles estavam escalando muito que foi quando deu o boom ali. E aí o terceiro momento que eles estão tão grandes que ficar em ECS com Fargate é mais caro do que ir para EC2 de volta.

[13:30] Gustavo Conti: O momento que vocês estão agora, o time que vocês têm, é tudo isso que a gente pensa.

[13:34] Juliano Nicocelli: Exato, o time não dá para dar o passo maior que a perna. Enfim, cara, mas assim, eu vou mostrar aqui para vocês, para vocês terem essa noção do ambiente. Cara, basicamente assim, eu tenho duas VPS.

[14:13] Juliano Nicocelli: A real é essa, eu tenho duas VPS hoje, rodo tudo em Docker internamente, tenho banco de dados. Então a gente tem aqui duas VPS, tem a VPS1 que é a principal. Infinity, quando tiver a Infinity aqui, é o nosso produto interno que a gente construiu para resolver o problema da B8, que é a boutique de investimentos.

[15:00] Juliano Nicocelli: Depois eu entro mais pra baixo, eu falo exatamente as tecnologias de cada uma aqui. Então, eu tenho nessa VPS um Infinite rodando, tenho ferramentas… N8n, Metabase, tem DeFi, tem ferramentas de automação.

[15:48] Juliano Nicocelli: DataRoom, ele é uma extensão do Infinite aqui, só que ele é para acesso das nossas instituições financeiras. Então chega num determinado momento que a gente tem uma oportunidade. Então por exemplo a WEG precisa captar 20 milhões. Beleza isso é uma oportunidade.

[16:20] Juliano Nicocelli: Na verdade, a gente pré-seleciona essas instituições e a gente dispara. Esse usuário acessa o Data Room, que é onde ele vai visualizar os documentos dessa oportunidade. Aí tem questão de monitoramento, que a gente usa o Grafana.

[17:12] Juliano Nicocelli: Na VPS secundária aqui, tem o Brain. Isso aqui é uma aplicação Python. Ele extrai informações de documentos, ele tem workers dentro do salary ali para fazer algumas coisas em relação a essa parte do pipe de extração de documentos. Eu meio que fiz uma SQS com o Lambda ali, meio que uma gambiarra ali, pra máquina não morrer quando cair muita coisa nessa fila de processamento.

[18:32] Juliano Nicocelli: Recentemente, foi na semana passada, que eu acabei pegando o Infinite aqui, duplicando ele. Só que com uma diferença que daí eu tornei ela multitenante e ela é muito mais voltada para mercado.

[19:23] Gustavo Conti: Pode sim.

[19:23] Juliano Nicocelli: Arquitetura front-end e back-end do Brain. Aqui é o principal gargalo, o Brain. O Brain é o serviço mais crítico da Stack, responsável por processamento de documentos, extração de dados financeiros, chat com o AI, reg com o vetor.

[20:00] Juliano Nicocelli: Dentro tanto do Infinity quanto o IBES, A gente tem uma interface lá, um chat que o cara troca uma ideia e ele bate lá nesse brain, baseado nos documentos que já foram na ingestão de dados que foi feita. Utilizando como uma base de conhecimento vetorial ali, ele começa a pegar, extrair, acessar esse conhecimento para responder num chat conversacional.

[20:52] Juliano Nicocelli: Esse cara é aquele que se conecta com o brain, que aí o brain é específico para essa parte de extração de dados e voltada para a inteligência artificial, pipeline de extração de dados, classificação de documentos, etc. Então aqui a gente tem Salary Workers, LLMU Routers, PG Vector como base vetorial, OpenAI para PI por enquanto.

[21:59] Juliano Nicocelli: Eu utilizo o Languagraph, que é um framework de inteligência artificial, um framework que cria uma camada para a orquestração de agentes de ar. Então, por exemplo, o cara na interface lá deu um alô, ele bate lá no brain, aí baseado na intenção do usuário, eu faço um roteamento entre qual tipo de agente que vai responder àquela intenção do usuário.

[22:43] Gustavo Conti: Seria tipo um Strains Agents, né?

[22:45] Juliano Nicocelli: Isso, é. Exato. Então, ele roteia internamente, responde e fala quais são as fontes daquela informação que ele está trazendo.

[23:32] Juliano Nicocelli: Então, aqui até o gerador do documento aqui, ele botou alguns gargalos aqui. Salary é limitado a quatro workers. Salary consome uma memória lascada também. Enfim, ele é bastante pesado para rodar essa stack do jeito que ela está hoje.

[24:18] Juliano Nicocelli: Por exemplo, eu tenho um fluxo ali que é assim, o cara cadastrou uma oportunidade dentro da plataforma, você tem uma área de arrastar documentos. O primeiro passo, quando a gente faz esse processamento, o brain começa a classificar, ele renomeia o arquivo, baseado em alguns padrões.

[25:17] Juliano Nicocelli: Eu começo a fatiar o problema, eu não posso fazer com que um usuário de um tenant joga 50 arquivos e o outro clica lá no botão salvar e a plataforma trava porque o cara tá classificando arquivo.

[26:05] Juliano Nicocelli: Olhando mais para a VPS1, que é o servidor principal, Eu rodo dois ambientes, então rodo sandbox e produção. Então, aqui eu tenho front-end React, tenho sandbox, tenho produção. O back-end Next.js tem sandbox de produção.

[26:48] Juliano Nicocelli: E daí, olhando para dados, eu tenho o PostgreSandbox, E o Postgres de produção, Redis. E pra storage a gente utiliza o Minio e fazendo hoje backup pra AWS S3.

[27:30] Juliano Nicocelli: Aqui olhando mais para tools e integrações, nessa VPS1 ali eu tenho algumas ferramentas externas, DeFi, N8n, Evolution API.

[28:23] Cristopher David de Lima: Já caiu hoje. Brincadeira.

[29:04] Gustavo Conti: pelo preço que eles cobram pra fazer a integração?

[29:08] Juliano Nicocelli: É! Isso aí é que nem construir casa no terreno da sogra, né? Mas, enfim, isso aqui não é nem o foco da migração para a AWS. O negócio é o nosso core, a nossa plataforma, o iBez.

[30:04] Juliano Nicocelli: Monitoramento, a gente tem ali o Grafana com Prometheus, lock para logs e os connectors aqui para coleta de logs.

[30:57] Juliano Nicocelli: E olhando para o VPS2, o servidor secundário, aqui a gente tem o Brain isolado. Eu tenho o ambiente do Infinity, eu tenho um Brain que é específico e esse aqui do IBS, ele é multitenant.

[31:32] Cristopher David de Lima: Desculpa, mas você falou de Postgres. Tua ideia é trazer esse banco também pra dentro da AWS?

[31:45] Juliano Nicocelli: É cara, isso aí acho que é o principal. Cada uma dessas aplicações, ela tem um banco, mas por uma questão de custo, eu não precisaria ter uma instância para todos, por serviço. Talvez uma instância com bases específicas, alguma coisa mais centralizada inicialmente, num RDS.

[32:39] Juliano Nicocelli: Cara, assim, é isso. Em relação ao ambiente, é mais ou menos isso que a gente tem. Eu acho que fica nítido que ter tudo isso dentro de duas VPS é loucura, né? Em termos de escala, você não tem como escalar isso.

[33:31] Juliano Nicocelli: Hoje, eu fiz a aplicação do Activate lá, tá, Cris? Eu peguei, como eu já tinha a conta, eu já fiz a aplicação.

[33:48] Gustavo Conti: Pegasse as mil doletas ainda?

[33:50] Juliano Nicocelli: Ainda não. Então apliquei lá para ver o que rola. E é isso. Aí assim, eu já tenho baseado nesse desafio aqui, uma arquitetura mínima de AWS. Mas não sei se a gente precisa entrar aqui, ou se vocês querem ver.

[34:18] Gustavo Conti: Se quiser mostrar ela aí. Vou até usar ela para montar o projeto.

[34:28] Juliano Nicocelli: Arquitetura de AWS proposta. Eu peguei ali uma skill de IA de AWS e apresentei o problema e falei, cara, me dá uma arquitetura que resolva esses problemas, mas que também deixe o meu custo controlado.

[34:55] Gustavo Conti: Ela fez o que toda IA costuma fazer, que é um over-engineer, né? Colocar ECS com Fargate, Elastic Cache com Redis, Postgres com RDS, SQS…

[35:41] Gustavo Conti: Não, eu concordo bastante com ela, assim, acho que a parte do front ali, principalmente, né, da entrega principal, CloudFront, o WAF e o Route 53 para o DNS.

[36:03] Juliano Nicocelli: Eu nem usaria, porque a gente usa já o Cloudflare para o DNS, então em tese a gente já está servindo com isso.

[36:17] Gustavo Conti: O Cloudflare e o WAF são essenciais para entrega de conteúdo. O front de vocês está separado?

[36:27] Juliano Nicocelli: Separado. A gente poderia botar ele estático, inclusive, no próprio S3. Olhando aqui pra parte mais de back-end, ela sugeriu um Fargate aqui pro back-end, pras APIs do back-end, mais os serviços do brain aqui. E conectado isso com um SQS aqui. S3 para arquivos. RDS Postgres OK, Elastic Cache.

[37:46] Gustavo Conti: Uma imagem separada de Redis. É tipo o RDS do Redis, no caso.

[37:53] Juliano Nicocelli: Entendi. Observabilidade aqui, CloudWatch, eu já utilizei, acho que faz sentido. X-Ray, não sei.

[38:14] Gustavo Conti: X-Ray é um serviço de telemetria. Você vai conseguir medir, por exemplo, desde que a solicitação chegou no CloudFront até que ela chegou no banco de dados, em quantos milissegundos demorou cada salto entre um componente e outro.

[38:34] Juliano Nicocelli: Ah, tá. Entendi. É tipo um trace de ponta a ponta, né?

[38:40] Gustavo Conti: É. Ele já usou o Datadog, não?

[38:50] Gustavo Conti: Datadog e Rally, que são serviços que são semelhantes. O Xray é uma versão mais enxugada desses serviços.

[39:39] Gustavo Conti: Ele é bem legal. E é bem baratinho de colocar também.

[39:41] Juliano Nicocelli: Legal. Bom, aqui, então, principais princípios dessa arquitetura. Separar API de workers. O brain não deve competir por recursos. Ambiente isolado, sandbox e production em VPC separadas.

[40:24] Gustavo Conti: Então, deixa eu só, antes de você continuar ali pra baixo, deixa eu voltar um pouquinho pra cima. O que você achou da ideia do ECS com Fargate?

[40:44] Juliano Nicocelli: Eu vou te explicar o porquê que a gente precisa decidir agora entre EC2 e Fargate.

[41:20] Gustavo Conti: O Fargate você vai pagar barato em AWS. mas vai pagar mais caro em ter alguém para construir isso para você e em ter alguém para manter isso para você. Dá mais um pouco mais de engenharia operacional.

[42:09] Juliano Nicocelli: Entendi. Quando você fala EC2, você tá falando de EC2 pura?

[42:28] Gustavo Conti: EC2 pura mesmo.

[42:37] Gustavo Conti: Eu não recomendo Beanstalk pra ninguém não, é chato.

[43:07] Juliano Nicocelli: Sim, é verdade. Mas cara, olhando pra EC2, eu acho que a gente precisa começar da maneira menos complexa possível. Porque se eu criar aqui uma arquitetura de canhão, eu vou ter que refatorar muita coisa.

[44:05] Gustavo Conti: A ideia é essa, a gente migra para EC2 mesmo que não seja o melhor custo benefício e a gente ir modernizando aos poucos.

[44:37] Juliano Nicocelli: O ponto principal é o seguinte, a gente não tem o cliente ainda para esse IBES. Então não faz sentido a gente polir muito essa arquitetura se ela não tem ninguém para quebrar ela.

[45:29] Juliano Nicocelli: Mas é que ela utiliza bibliotecas muito pesadas para extração de informações, de documentos, etc. Talvez, nesse caso em específico do Python, a gente precisa ter alguma sofisticação em relação a como a gente vai estruturar ela.

[46:20] Juliano Nicocelli: Para fins de front-end, back-end isso aí é bem tranquilo a EC2 na veia conectada lá no RDS já é o suficiente.

[46:35] Gustavo Conti: Deixa eu só anotar isso aqui. E aí o segundo ponto que eu queria te trazer sobre essa mudança de ambientes isolados. Você pode ter duas opções. Uma delas é ter duas VPCs dentro de uma mesma conta. E o outro, que é o mais recomendado, é você ter contas separadas.

[47:12] Gustavo Conti: Porque daí, cara, tem certeza que nenhum vai impactar o outro. Só que assim, você ter contas ou VPC separadas vai te trazer um custo a mais, que é de VPC. Dois NAT Gateways, dois Load Balancers, você vai ter dois de tudo.

[47:57] Juliano Nicocelli: Entendi. É, então, eu não sei. Sinceramente, eu não sei. O isolamento é importante. Eu acho que o principal ponto é ter o isolamento.

[49:04] Gustavo Conti: Então eu vou montar um projeto para ti com isolamento por conta. Se você falar assim não, estava com muito caro, quero uma conta só para tudo, a gente segue com uma conta só.

[49:23] Juliano Nicocelli: Boa. Beleza, então. Show. Posso avançar aqui?

[49:34] Juliano Nicocelli: Aqui ele falou só um pouco da arquitetura de rede, das VPCs. Aqui ele sugeriu ter as duas VPCs, VPC de sandbox e de produção.

[50:09] Juliano Nicocelli: Como a gente tem as ações mais longas dentro do Celery ali, talvez seria o ideal o Fargate comparando com o Lambdas por causa dos limites de 15 minutos.

[50:48] Gustavo Conti: ALB é o Load Balancer. Application Load Balancer.

[51:43] Juliano Nicocelli: Esses caras aqui não são nem problema, sabe? Em termos de arquitetura. Hoje na VPS ele funciona. O único desafio maior é em termos de segurança, por causa de firewall, fechamento de portas, etc.

[52:32] Juliano Nicocelli: Basicamente hoje tem um problema que é justamente esse, porque como o API do Brain, lá tem o API, tem o salary, que é o worker. Se eu jogo 50 documentos lá e o worker começa a trabalhar e alguém joga mais 50 documentos, ele vai bater na API capaz de falhar por causa de falta de recurso, porque quem gerencia a fila é o Python.

[53:30] Cristopher David de Lima: Só vou interromper rapidinho. Eu vou precisar sair aqui para um compromisso. Conte, será que a gente já deixa marcado para de repente quinta, sexta-feira a gente voltar com arquitetura?

[54:05] Gustavo Conti: Ainda não, deixa eu dar uma analisada melhor nesses documentos, daí eu monto o projeto certinho e eu te mando a gente marcar.

[54:14] Cristopher David de Lima: Fechou então. Bom restinho de reunião, pessoal. Um abraço, tchau, tchau.

[55:02] Juliano Nicocelli: Filas e processamento. Ficou bem legal esse documento, né?

[55:08] Gustavo Conti: Bem complexo.

[55:11] Juliano Nicocelli: É, cara. Então, eu utilizei uma skill ali da AWS com o Cloud Code. Depois eu vou te passar.

[56:07] Juliano Nicocelli: Mas enfim, aqui, cara, só ele deu aqui as filas. Então, por exemplo, classificação de documentos, então uma fila de classificação, uma fila de extração. Basicamente, o front-end, o cara jogou 50 arquivos lá, ele joga na fila de classificação.

[57:26] Juliano Nicocelli: Enfim, isso aqui são os detalhes técnicos. Aí olhando um pouco para a segurança aqui, ele botou AFRI, rede privada, enfim. Mas cara, é isso. Se tu quiser, eu te mando até esses documentos aí.

[57:50] Gustavo Conti: É, me manda esses dois documentos. Se achar também aquela skill ali, eu realmente quero, tá?

[58:22] Gustavo Conti: Mas beleza, cara. Eu já finalizei aqui, dei o projeto, mas cara, bem legal mesmo. Parabéns, inclusive, pelas apresentações. Ter um entendimento sobre tudo que foi construído é fenomenal. Se todo cliente viesse com essas informações que você me trouxe, eu estaria no paraíso.

[58:40] Juliano Nicocelli: Legal, cara. Show de bola. Cara, prazer falar contigo. Eu vou te mandar esse conteúdo aí. E até a próxima.

[59:14] Gustavo Conti: Isso aí é tudo meu. Valeu, Juliano.

[59:16] Juliano Nicocelli: Falou. Até mais, querido. Tchau, tchau.
