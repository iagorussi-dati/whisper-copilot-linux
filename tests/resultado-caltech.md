# Teste Discovery Dati — Reunião Caltech

Prompt: discovery-dati.md (41 situações)
Reunião: Caltech mineradora, Amazon Q Business


================================================================================
SNAPSHOT 1 — Cliente é mineradora, pesquisando IA sem foco, usa DataSul e planilhas
================================================================================

💡 "Que tipo de processo vocês gostariam que a IA ajudasse? É mais na parte de análise de dados, automação de processos ou algo específico como previsão de produção?"
⚠️ "O primeiro passo é entender onde IA gera resultado de verdade — não sair fazendo sem foco."
💡 "Vocês já tentaram alguma coisa de IA antes? O que aconteceu?"
✅ "A gente tem um time de IA que faz exatamente esse mapeamento inicial — podemos marcar um workshop pra identificar onde tem mais impacto."

💡 "Vocês já têm os dados no DataSul — isso já é um bom ponto de partida pra qualquer análise de IA."
⚠️ "Planilha é limitada pra volume grande de dados. A IA na nuvem consegue processar muito mais e achar padrões que planilha não vê."
💡 "O que vocês mais sentem falta hoje? Previsão de demanda, otimização de custos, algo na cadeia de suprimentos?"
✅ "Vamos fazer uma análise rápida dos dados de vocês pra mostrar o que já é possível automatizar ou prever."


================================================================================
SNAPSHOT 2 — Contabilidade usa planilhas pra conferência, TI é pequeno
================================================================================

💡 "Planilhas pra conferencia de nota é trabalhoso — quantas horas por semana o time gasta nisso?"
⚠️ "Essa parte manual tem risco de erro e pode atrasar o processo, né?"
💡 "A gente pode automatizar essa conferencia com um workflow na AWS — reduz tempo e elimina erros."
✅ "Vou preparar uma proposta de automação focada nesse processo de conferencia de notas."


================================================================================
SNAPSHOT 3 — Cliente pergunta se IA roda local, diretoria prefere on-prem por dados sensíveis
================================================================================

💡 "A IA da AWS tem opções tanto pra rodar 100% na nuvem quanto em modo híbrido — dá pra ter parte no seu local e parte na nuvem."
💡 "Se a questão é dados sensíveis, a gente pode montar um ambiente totalmente isolado no seu servidor, sem sair da sua rede."
⚠️ "Mas é importante saber que rodar localmente pode ter custos de infra mais altos e menos escalabilidade."
✅ "Vou alinhar com o nosso especialista de IA e te mostro as opções de implantação que se encaixam na política de segurança de vocês."


================================================================================
SNAPSHOT 4 — Cliente quer entender como conectar ERP on-prem com AWS
================================================================================

💡 "O DataSul é um sistema bem comum — a gente já fez integração com ele várias vezes. A comunicação pode ser via API segura ou através de conectores específicos."
💡 "Pra ler as informações locais sem expor os dados, a gente monta uma conexão segura, tipo VPN ou PrivateLink da AWS, que fica tudo isolado."
⚠️ "Não precisa colocar o ERP na internet — a gente cria um canal privado que só a AWS acessa."
✅ "Vou te mostrar um caso que a gente fez com outro cliente que usava DataSul — assim vocês veem como funciona na prática."


================================================================================
SNAPSHOT 5 — Cliente já usa Gemini com Google Drive e está satisfeito
================================================================================

💡 "Entendi que vocês já estão usando o Gemini com o Google Drive e automatizando buscas em documentos fiscais. Vocês já têm bastante dado lá, né?"
💡 "Se vocês migrarem isso pra AWS, a gente pode fazer o mesmo com os serviços de IA da AWS — sem risco de dados ficarem públicos."
⚠️ "Construir APIs pra integrar tudo pode ser trabalhoso mesmo em 60 dias. A gente pode acelerar isso com nosso time de IA."
✅ "Vamos marcar um workshop focado pra mapear como a gente pode migrar esse fluxo já existente de vocês pro nosso time de IA em menos tempo."


================================================================================
SNAPSHOT 6 — Cliente acha 60 dias pouco pra construir APIs e precisa falar com gerente
================================================================================

💡 "Entendi que vocês precisam de um tempo pra alinhar internamente com a gerente — sem problemas, a gente respeita esse processo."
⚠️ "Pra quando vocês tiverem o retorno, já posso preparar o nosso time técnico pra gente avançar mais rápido."
✅ "Vou te mandar um resumo por email com os pontos que a gente discutiu hoje — assim facilita a conversa com a gerente."
💡 "Se a gente já tiver algum material inicial, pode te mandar agora pra ajudar na decisão dela."


================================================================================
SNAPSHOT 7 — Cliente pede case real, quer ver exemplo concreto
================================================================================

💡 "Claro, Naor. A gente já implementou um sistema de recomendação de produtos pra uma loja virtual que aumentou 15% as vendas em 3 meses."
💡 "Também fizemos um chatbot pra um banco que reduziu 40% das ligações pro SAC."
✅ "Posso te passar casos reais que a gente já entregou pra vocês verem o impacto."


================================================================================
FULLCONTEXT Win+H — CONVERSA TODA
================================================================================

### **💡 Uso de IA e Preferência por Soluções Locais**
*Contexto: Naor menciona que a mineradora está começando na parte de IA e tem preferência em rodar soluções localmente devido à sensibilidade dos dados. Eles já usam Gemini com Google Drive para automatizar processos, como lançamento de notas fiscais.*

💡 "Entendi que a questão de dados sensíveis é crítica pra vocês, e a diretoria prefere rodar localmente."
💡 "Na AWS, temos opções de IA que podem rodar localmente, no seu ambiente on-premise, sem precisar ir pra nuvem."
⚠️ "Migrar o que vocês já têm com Gemini pra AWS pode ser feito de forma segura, sem expor seus dados."
✅ "Vou preparar um caso de uso real que a gente já fez com outro cliente do setor mineral, pra vocês verem como funciona na prática."

---

### **🔗 Integração com ERP e Automação de Processos**
*Contexto: As informações principais estão no ERP DataSul. Eles estão desenvolvendo uma automatização para lançamento de notas fiscais usando Gemini e Google Drive e questionam como a comunicação com o ERP local funcionaria.*

💡 "Vocês já têm uma automatização com Gemini e Google Drive — isso é um ótimo ponto de partida."
💡 "A gente pode criar APIs seguras pra conectar o ERP de vocês com serviços de IA na AWS, sem precisar mudar o que já funciona."
⚠️ "Construir essas APIs pode parecer trabalhoso, mas nosso time de IA já fez isso várias vezes e pode acelerar o processo."
✅ "Vamos marcar um workshop focado pra mapear como a gente integra isso de forma tranquila no seu ERP."

---

### **💰 Forma de Pagamento AWS (Cartão vs. Boleto)**
*Contexto: Danilo perguntou se o cliente faz pagamento da AWS por cartão ou boleto, indicando uma possível oportunidade de otimização de custos e fluxo de caixa.*

💡 "Se vocês migrarem pro pagamento por boleto, ganham IOF e câmbio na mão — melhora o fluxo de caixa."
⚠️ "No cartão, tem aquele IOF extra e o câmbio que varia — no boleto é tudo fixo em real."
💡 "E a cada 5 mil dólares de consumo, vocês ganham 1 hora de consultoria grátis com a gente."
✅ "Vou te mandar os detalhes por email, pra vocês analisarem com calma com a contabilidade."

---

### **📊 Processos Manuais e Oportunidades de Automação**
*Contexto: Carlos mencita que usam planilhas para conferência e lançamento de notas, o que indica um processo manual e propenso a erros.*

💡 "Uso de planilhas pra conferência e lançamento de notas deve consumir bastante tempo do time de vocês."

