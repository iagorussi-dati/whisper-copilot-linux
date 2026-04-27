# Teste Abordagens de Latência

Cenário: 9 chunks de 1min + snapshot no final
16 temas pra cobrir

- ATUAL: C1=10.4s C2=8.6s Total=19.0s Cobertura=16/16 Ctx=1151chars
- ROLLING: Snap=5.2s ChunksTotal=40.6s (4.5s/chunk) Cobertura=8/16 Resumo=2301chars
- LOCAL: C1=8.8s C2=17.3s Total=26.1s Cobertura=9/16 Ctx=296chars
- HÍBRIDA: Snap=3.4s (resumo pronto) Cobertura=8/16

Rolling summary final (2301 chars):
### Resumo Atualizado

O cliente enfrenta múltiplos desafios em sua infraestrutura e processos de desenvolvimento e operações na AWS. Primeiramente, há a preocupação com segurança, pois o cliente necessita estabelecer conexões seguras e gerenciadas com seus recursos na AWS, sem expor portas públicas como a 22 (SSH) para potenciais ameaças. Isso é crucial para evitar acessos não autorizados e simplificar a gestão de permissões. Adicionalmente, o cliente possui um processo de deploy manual e simplório, que consiste em dois repositórios no GitHub e onde o deploy é realizado através de um simples `git pull` dentro da instância EC2. Esse método manual é suscetível a erros, não escalável e difícil de automatizar, representando uma dor significativa no fluxo de desenvolvimento e operações.

Além disso, o cliente enfrenta um desafio relacionado ao **build de uma aplicação Frontend em Next.js**. Atualmente, o processo de build é realizado em uma instância EC2 de tamanho pequeno, que frequentemente estoura a capacidade de RAM devido à pesadez do build. Para contornar esse problema, a equipe tem feito o build localmente e depois realizado o upload dos arquivos para a instância, o que não é uma solução sustentável ou eficiente. Esse processo manual é trabalhoso, propenso a erros e dificulta a integração contínua e a entrega contínua (CI/CD).

O cliente também menciona a utilização de uma arquitetura de **Bastion Host** para melhorar a segurança. No entanto, essa abordagem requer a separação de sub-redes (subnets) para reduzir a superfície de ataque, o que adiciona complexidade à arquitetura de rede. Além disso, embora o Bastion Host aprimore a segurança ao limitar o acesso direto às instâncias, ele ainda requer a exposição de uma porta pública (geralmente a porta 22) para o host bastion, o que representa um risco de segurança residual.

Quanto à utilização de **VPN**, o cliente menciona que, embora seja uma opção para estabelecer conexões seguras, ela não é recomendada devido aos altos custos associados. VPNs podem ser uma solução eficaz para conectar redes de forma segura, mas os custos operacionais e de manutenção são significativos, o que a torna menos viável para o cliente.

#### Desafios Adicionais:

Recentemente, foram discutidos novos desafios que incluem:

1. **Esc
