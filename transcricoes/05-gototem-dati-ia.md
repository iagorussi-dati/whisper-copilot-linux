# [GoTotem & Dati] Discovery — Projeto IA Totem

- **Data:** Wednesday, May 14, 2025 at 2:59 PM
- **Duração:** 19:15
- **Participantes:** Rafaela Koller, Reginaldo

---

[0:01] Reginaldo: Boa tarde, tudo bem?

[0:03] Rafaela Koller: Tudo certo? Vamos falar contigo novamente. O Felipe comentou comigo que é sobre a questão de IA né? Aí até queria entender pouquinho do que vocês estão pensando em usar IA, o que vocês acham que a IA consegue entregar pra vocês, até pra gente poder entender a ideia, e também entender como metrificar os resultados pra fazer a questão do ROI.

[0:38] Reginaldo: Vocês já fizeram algum projeto usando as ferramentas da AWS?

[1:00] Rafaela Koller: A gente tem a parte de cloud e de sustentação. O nosso time é dividido entre 3 times técnicos: sustentação, consulting que é o time do Felipe que entrega modernização, e o time de IA com mais de 8 pessoas que faz entrega de projetos de IA e dados.

[2:02] Reginaldo: Está bom, vamos lá. Eu vou compartilhar uma tela e vou mostrar o produto que nós temos.

[3:36] Reginaldo: Então é sobre esse produto mesmo que eu quero falar. Esse é o nosso produto de totem de autoatendimento. A gente desenvolve tanto a parte de software que é o aplicativo Android, quanto a parte de hardware. A gente oferece a solução completa.

[5:06] Reginaldo: Qual que é o principal objetivo do totem? Primeiro, agilizar o atendimento, otimizar o atendimento. E o segundo é aumentar o ticket médio, fazer com que o cliente compre mais. Porque muitas vezes quando você chega num atendente no caixa dificilmente ele vai te oferecer novos produtos. E o totem ele está ali o tempo todo oferecendo.

[5:42] Reginaldo: No nosso sistema hoje, nós temos painel de controle onde o nosso cliente, o dono do estabelecimento, ele tem que entrar lá manualmente e configurar que se comprar esse item ele ofereça uma Coca. Então é tudo manual. E às vezes o estabelecimento não faz, esquece de fazer, ou o produto acabou.

[6:23] Reginaldo: Então o que a gente está pensando com IA: 2 pontos iniciais. Primeiro, eu tenho uma IA especializada no cardápio. Tem que ser o cardápio desse cliente porque eu tenho cliente de hamburgueria, de cafeteria.

[6:51] Reginaldo: Primeiro, eu preciso de uma especialidade nesse cardápio, que consiga fazer sugestões automáticas pro cliente. Considerando o cadastro dele, a disponibilidade do produto, combinações óbvias. Também que deveria considerar o clima, então dia frio é mais fácil beber café do que refrigerante. Considerando também a região, eu tenho cliente com unidade em Florianópolis e em Recife, os gostos regionais são diferentes.

[8:03] Reginaldo: Esse é o primeiro ponto, sugestões inteligentes. E o segundo ponto, é permitir que o cliente faça o pedido sem tocar na tela, por voz. Que converse com quem está fazendo o pedido.

[8:26] Rafaela Koller: Como se fosse tipo no drive-thru que tu vai lá e faz a solicitação e a pessoa anota o teu pedido, nesse caso o totem vai trazer as sugestões na tela e tu vai dar o ok.

[8:42] Reginaldo: E você vai adicionando no caminho, quero continuar comprando. Pode fazer manualmente e fazer por voz sem ter que tocar na tela.

[9:02] Reginaldo: Esses são os 2 pontos iniciais, mas ele pode evoluir depois pra detecção facial, identificar a faixa etária da pessoa pra oferecer produto. Pessoa muito idosa determinados produtos você não vai sugerir, pessoa muito jovem determinados produtos você não vai sugerir. Mas essa questão deixa pra uma segunda etapa.

[9:44] Reginaldo: A gente pensou que vocês pudessem nos ajudar nesse ponto. A gente estaria agregando isso no nosso produto oferecendo pros nossos clientes. Uma solução nossa que a gente possa comercializar.

[10:07] Rafaela Koller: Isso vocês iriam precificar como uma solução extra, algo a mais que vocês entregariam pro teu cliente final?

[10:19] Reginaldo: Eu ainda não sei mas provavelmente sim, vai ter custo a mais. Aí começamos a conversar com algumas empresas. Eu já conversei com uma parceira do Google, o Google fez link com o parceiro deles, e ele já me mandou escopo inicial usando as ferramentas do Google, Gemini e outras ferramentas.

[10:58] Reginaldo: E como a AWS também tem, e como vocês agora são nosso parceiro com a AWS, perguntei na última reunião se vocês tinham essa especialidade, falaram que sim.

[11:16] Rafaela Koller: Sim faz, conseguimos te atender. Eu tenho 2 perguntas. Sobre a questão especializada no cardápio do cliente, a GoTotem tem acesso a esse cardápio? Como que a gente pode fazer esse acesso?

[12:07] Reginaldo: Eu tenho o banco de dados centralizado onde estão todos os cardápios e todos os pedidos. Então você também tem a informação de histórico de pedidos, o que cada pessoa comprou com que, quais foram os adicionais.

[12:22] Rafaela Koller: Já tem uma base ali de conhecimento que a gente pode utilizar, as informações dos produtos, os combos e tudo mais pra que a IA já possa sugerir com base nesse conhecimento que você já tem registrado.

[12:44] Rafaela Koller: E uma outra questão. Essa questão da voz, já é primordial, já tem que sair na fase 1? Ou poderia ser projetos faseados? Eu entro com uma fase fazendo sugestões, vocês fazem os testes, a gente vai aprimorando, aí depois entra com uma fase 2 com a voz.

[13:08] Reginaldo: Dá pra dividir em 2 projetos também. A voz ela só vai converter voz em texto e texto em voz e consumir esse primeiro serviço de sugestões. Essa API de voz além de outras coisas, você pode adicionar no carrinho.

[13:51] Rafaela Koller: Então começar com a utilização da IA, treinamento, questão dos pedidos, combos, sugestões. E depois a gente vem com uma segunda fase com a voz. Uma outra pergunta, sobre orçamento. Vocês têm orçamento pré-estabelecido pra esse projeto?

[14:27] Reginaldo: Está muito embrionário. A gente começou a conversar com empresas agora, 1 semana, 2 semanas. A gente não tem noção nenhuma ainda de quanto custa. A gente está agora em prospecções, conhecendo as empresas, como que dá pra fazer, quem que pode fazer, e também analisar os orçamentos.

[15:08] Rafaela Koller: Eu preciso saber do meu lado o que o meu técnico precisa entregar, além da arquitetura, o escopo do projeto e também a estimativa de custo de AWS.

[15:10] Reginaldo: Vou te mandar documento. Ali tem alguns requisitos, os entregáveis. E eu vou usar também algumas partes da proposta que o pessoal do Google me mandou, que ela também completa. Vocês também podem seguir essa linha.

[15:35] Rafaela Koller: Me passa, eu vou compartilhar com o meu arquiteto especialista de IA, e provavelmente eu vou puxar uma agenda contigo mais técnica.

[16:40] Reginaldo: Não é projeto urgente. A gente não está com aquela urgência que nós tínhamos por questão da infra. É projeto que a gente está pesquisando, mas é projeto inevitável pra gente. É uma modernização do nosso produto que a gente enxerga como inevitável.

[17:00] Rafaela Koller: Vamos ver o que a gente consegue fazer pra acelerar. Usando os incentivos que a Dati tem, usando a nossa mão de obra, e fazendo que isso aconteça o mais rápido possível. Como tu falou não é urgente mas é inevitável então vamos tentar trazer isso o quanto antes.

[17:53] Reginaldo: Pode chamar de IA Totem Autoatendimento.

[18:33] Rafaela Koller: Bom, a princípio era isso, obrigada por compartilhar as tuas ideias aí com a gente.

[18:45] Reginaldo: Hoje ainda eu te mando, tá?

[19:09] Rafaela Koller: Eu que agradeço Reginaldo. Até uma volta, tchau tchau.

[19:12] Reginaldo: Valeu. Tchau.
