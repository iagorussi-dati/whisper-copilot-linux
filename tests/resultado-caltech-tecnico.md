# Teste Consultor Técnico — Reunião Caltech

Prompt: consultor-tecnico.md
8 testes (7 snapshots + 1 fullcontext)


================================================================================
1 — Cliente pergunta se Q Business roda local ou só nuvem (dados sensíveis)
================================================================================

   📌 O Amazon Bedrock (serviço de IA da AWS) roda **exclusivamente na nuvem AWS** — não há opção de instalação local ou on-premises. Todos os modelos (como Titan, Claude, etc.) são executados nos datacenters da AWS. Para dados sensíveis, a solução é usar a região **São Paulo (sa-east-1)** para manter os dados no Brasil, com criptografia em repouso e em trânsito. Se a diretoria insiste em rodar localmente, seria necessário usar soluções de IA de terceiros (como modelos locais), mas perdendo as vantagens de escalabilidade, atualização automática e compliance da AWS.  

💬 Como falar pro cliente:  
- "O Bedrock só roda na nuvem AWS, mas podemos garantir que tudo fique na região de São Paulo, com criptografia total — seus dados não saem do Brasil."  
- "Se a ideia é evitar nuvem, não tem como usar o Bedrock localmente. Mas a gente pode reforçar a segurança com VPC, IAM e criptografia — é o padrão pra dados sensíveis."  
- "Se realmente precisar de local, teríamos que avaliar outras soluções de IA, mas aí perde-se a integração direta com AWS e atualizações automáticas. Vamos focar na solução mais segura na nuvem primeiro?" 


================================================================================
2 — Cliente pergunta se Q Business aceita áudio
================================================================================

   📌 O Amazon Q Business **não** suporta interação por áudio ou envio de mensagens de áudio em tempo real. Ele funciona com entrada **exclusivamente por texto**. No entanto, você pode **fazer upload de arquivos de áudio (como gravações de reuniões, palestras, etc.)** como fontes de conhecimento. O serviço transcreve automaticamente esses arquivos e usa o conteúdo transcritado para responder perguntas por texto.  

💬 Como falar pro cliente:  
- "O Amazon Q Business só aceita perguntas por texto, mas vocês podem enviar arquivos de áudio pra ele processar e usar como base nas respostas."  
- "Não tem chat por voz, mas se vocês têm gravações de reuniões, por exemplo, podem subir que ele transcreve e responde perguntas sobre o conteúdo."  
- "A interação é toda textual, mas o áudio que vocês enviarem vira texto e fica disponível pra consultas futuras." 


================================================================================
3 — Cliente não entende como Q Business conecta com ERP on-prem (DataSul)
================================================================================

 📌 O Amazon Q Business pode se conectar a fontes de dados locais como o DataSul (ERP) de duas formas principais. A primeira é usando o Amazon Q Business Connector para bases de dados SQL ou via API do próprio ERP, que permite extrair dados através de endpoints seguros. A segunda é usando o AWS PrivateLink + VPC endpoint, garantindo que a comunicação aconteça dentro da rede privada da AWS, sem passar pela internet pública. Você precisa configurar uma fonte de dados no Q Business apontando pro endpoint do DataSul, com autenticação via credenciais seguras (ex: IAM role ou secrets do AWS Secrets Manager). Os dados não saem da sua rede — a conexão é feita dentro do VPC e só o índice (metadados) fica no Q Business.

💬 Como falar pro cliente:  
- "A gente configura o Q Business pra acessar o DataSul diretamente pela rede privada — não passa pela internet, então fica seguro."  
- "Você só precisa de um endpoint no ERP e das credenciais de acesso — a gente cuida da conexão via VPC, sem exposição externa."  
- "Os dados em si continuam no seu ERP — só o que pode ser consultado (texto, metadados) fica indexado no Q Business."


================================================================================
4 — Cliente já usa Gemini com Google Drive e está satisfeito
================================================================================

 📌 Se vocês já usam Gemini com Google Drive, migrar para Amazon Q Business é direto. O Amazon Q Business conecta com Google Drive (via connector) e indexa documentos — PDFs, Docs, Sheets, slides. Ele não retreina modelo com seus dados (dados ficam privados na sua conta AWS). Funciona com perguntas em NL: "quanto foi faturado em 15/03?", "quem é meu melhor cliente?". Resposta em segundos, com fonte (link direto pro doc). Custo: $0.10 por 1k de docs indexados + $0.0001 por pergunta. Para 1TB de dados, estimativa é ~\$100/mês.

💬 Como falar pro cliente:
- "O Amazon Q Business conecta direto no Google Drive de vocês, indexa tudo e responde perguntas como 'quanto faturamos em 15/03' em segundos, sem expor os dados."
- "Ele não usa seus dados pra retreinar modelo — tudo fica privado na conta de vocês na AWS."
- "Com o volume que vocês têm, o custo fica em torno de R\$100/mês — e a gente configura em 1 dia."


================================================================================
5 — Cliente acha 60 dias pouco pra construir APIs de conexão
================================================================================

 📌 O Amazon Q Business tem conexão nativa com Google Drive e OneDrive — não precisa construir API pra integrar. Só pra ERPs específicos que não têm conector pronto é que seria necessário criar API. A integração nativa já faz indexação de documentos, pastas e atualizações em tempo real. Tempo de configuração é de horas, não dias.

💬 Como falar pro cliente:  
- "O Amazon Q Business já conecta direto com Google Drive e OneDrive — não precisa de API, isso economiza o tempo todo dos 60 dias."  
- "Só pra ERPs que não têm conector pronto é que a gente teria que construir API; pra esses casos a gente pode priorizar depois."  
- "A integração nativa é rápida de configurar — em questão de horas já está funcionando e indexando os documentos de vocês." 


================================================================================
6 — Cliente quer saber quanto custa o Q Business
================================================================================

 📌 A consultoria da Dati tem preço fechado ou por hora, depende do escopo — geralmente trabalhamos com projeto fechado com valor acordado. Sobre o Amazon Q Business: os primeiros 60 dias são grátis. Depois o custo é por usuário ativo/mês e por GB de dados indexados. O preço exato varia conforme uso — vou confirmar os valores atuais.

💬 Como falar pro cliente:  
- "A consultoria a gente costuma fechar por projeto — valor único combinado no início. Se preferirem, também pode ser por hora."  
- "O Q Business depois dos 60 dias grátis cobra por usuário ativo e por volume de dados. Vou te passar o valor exato depois."  
- "O custo dele é bem baixo comparado ao que entrega — vamos incluir na proposta com números reais." 


================================================================================
7 — Cliente confuso sobre o que Q Business realmente faz
================================================================================

Com base na conversa, o Naor está com dificuldade de visualizar como aplicar os conceitos discutidos na reunião de forma prática. Ele quer um exemplo concreto de implementação para entender melhor.  

### Resposta técnica objetiva  
Os cenários mais comuns que geram essa dúvida são:  
1. **Migração de infraestrutura** (ex: de Heroku/VPS para AWS)  
2. **Implementação de escalabilidade** (auto-scaling, Fargate vs EC2)  
3. **Configuração de segurança/resiliência** (RTO/RPO, MFA, conta separada)  

Vou usar um **exemplo real de migração de aplicação containerizada** (cenário mais comum em startups), pois atende à necessidade de "vamos fazer isso" e "já fizemos isso".  

📌 **Exemplo prático: Migração de aplicação de Railway para AWS (EKS + Fargate)**  
- **O que fizemos:** Startup com 3 microservices em containers (Node.js + Python) no Railway. Estava com problemas de *cold start* e custo alto.  
- **Solução:**  
  - Migramos para **EKS com Fargate** (não precisa gerenciar nós, escala sozinho)  
  - Usamos **ALB + Path-Based Routing** para direcionar tráfego  
  - Banco de dados migrado para **RDS PostgreSQL** (com backup automático)  
  - Config


================================================================================
8 — FULLCONTEXT — conversa toda
================================================================================

### Análise das Principais Dúvidas Técnicas e Respostas

#### Dúvida 1: IA da Amazon roda somente em nuvem ou localmente? (Dados sensíveis, preferência por local)
**📌** A AWS oferece opções tanto para nuvem quanto para execução local (on-premises). Para dados sensíveis, é possível usar o **Amazon SageMaker** em modo híbrido ou mesmo soluções como **AWS Outposts** para manter dados localmente enquanto usa a capacidade de IA da AWS. Além disso, o **Amazon Bedrock** permite que você use modelos de linguagem de grande escala (LLMs) sem precisar treinar os modelos, e pode ser executado em ambientes VPC isolados para maior segurança. Para execução puramente local, a AWS oferece **SageMaker Edge Manager** e **AWS Panorama** para inferência local. Nenhum dado sensível precisa sair do ambiente local se configurado corretamente.

💬 Como falar pro cliente:
- "A AWS permite que vocês usem IA tanto na nuvem quanto localmente. Para dados sensíveis, podemos configurar tudo para ficar só no seu ambiente, sem sair da sua rede."
-  "Se a preocupação é com dados sensíveis, a gente pode usar o AWS Outposts, que é como se a nuvem estivesse dentro do seu data center, com total controle local."
- "Vocês podem fazer inferência de modelos localmente com o SageMaker Edge, mantendo todos os dados dentro da sua infraestrutura."

#### Dúvida 2: É possível enviar áudio ou é somente texto para o modelo de IA?
**📌** Sim, o **Amazon Q Business** e o **Amazon Transcribe** suportam o upload de arquivos de áudio e vídeo. O áudio é transcrevido para texto e, em seguida, pode ser usado como fonte de conhecimento para o modelo de IA. O Amazon Q Business permite que você faça perguntas baseadas nessas transcrições. No entanto, a interação (perguntas e respostas) é feita por texto.

💬 Como falar pro cliente:
- "Sim, vocês podem enviar áudios e vídeos. O sistema transcreve tudo e usa como base pra responder perguntas."
- "A interação é por texto, mas qualquer áudio ou vídeo que vocês subirem será processado e poderá ser consultado depois."
- "Por exemplo, se vocês têm gravações de reuniões, podem subir todas e o time pode consultar informações só fazendo perguntas por texto."

#### Dúvida 3: Como funciona a comunicação para ler informações locais no ERP DataSul?
**📌** Para integrar o ERP DataSul com soluções de IA na AWS, existem algumas abordagens. A mais direta é usar **AWS Lambda** com **Amazon API Gateway** para criar APIs que se comunicam com o DataSul. Outra opção é usar **AWS AppFlow** para conectar diretamente com o DataSul, se ele tiver conectores disponíveis, e fazer a extração dos dados para **Amazon S3** ou **Amazon RDS**. Para cenários mais complexos, **AWS Glue** pode ser usado para ETL e extração de dados do ERP para a nuvem, mantendo a segurança dos dados sensíveis.

💬 Como falar pro cliente:
- "A gente pode criar APIs simples usando AWS Lambda e API Gateway pra se comunicar com o DataSul. Isso permite que o sistema de IA acesse as informações de forma segura."
- "Se o DataSul tiver conectores, podemos usar o AWS AppFlow pra puxar os dados direto pra S3 ou RDS, sem precisar montar APIs do zero."
- "Outra opção é usar o AWS Glue pra fazer o ETL dos dados do ERP pra nuvem, tudo de forma segura e controlada."

#### Dúvida 4: Já estamos usando Gemini com Google Drive. Qual a vantagem de migrar para AWS?
**📌** Ao usar o Gemini com Google Drive, há riscos de que os dados enviados possam ser usados para retreinar os modelos do Gemini, o que pode tornar as informações públicas ou acessíveis a terceiros. Além disso, a AWS oferece **Amazon Q Business** com conexão nativa com o Google Drive, sem necessidade de construir APIs. O Amazon Q Business garante que os dados não são usados para treinar modelos, mantendo a privacidade. A AWS também oferece maior controle de segurança, compliance e governança, especialmente importante para dados sensíveis de uma mineradora.

💬 Como falar pro cliente:
- "Com o Gemini, os dados que vocês enviam podem ser usados pra retreinar os modelos, o que pode expor informações sensíveis. Na AWS, isso não acontece."
- "O Amazon Q Business tem conexão nativa com o Google Drive, então não precisa construir API alguma. É mais rápido e seguro."
- "Na AWS, vocês têm controle total sobre os dados — nada sai do seu ambiente sem permissão, e atendemos todos os requisitos de compliance."

#### Dúvida 5: Construir APIs pode ser trabalhoso em 60 dias. Existe uma solução mais rápida?
**📌** Sim, o **Amazon Q Business** tem conexão nativa com o **Google Drive**, eliminando a necessidade de construir APIs. Além disso, **AWS AppFlow** oferece conectores pré-prontos para diversos sistemas, incluindo ERPs. Para o DataSul, se não houver conector pronto, **AWS Lambda** com **API Gateway** pode ser configurado rapidamente para criar endpoints de integração. A Dati pode entregar essa integração em menos de 60 dias, dependendo da complexidade.

💬 Como falar pro cliente:
- "Não precisa construir API nenhuma. O Amazon Q Business já se conecta direto com o Google Drive."
- "Se for preciso integrar com o DataSul, o AWS AppFlow pode
