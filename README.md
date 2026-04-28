# Whisper Copilot Lite

Copiloto inteligente em tempo real para reuniões. Transcreve áudio, identifica speakers e gera sugestões contextuais com IA.

Desenvolvido pela **Dati** (AWS Advanced Partner, Blumenau/SC).

## Stack

| Camada | Tecnologia |
|---|---|
| **Frontend** | HTML + Tailwind CSS (single file) |
| **Backend** | Python + pywebview |
| **Transcrição** | Groq Whisper API (whisper-large-v3-turbo) |
| **IA** | Amazon Bedrock (Nova Pro) — long-term API key |
| **Web Search** | DuckDuckGo (via primp) |
| **Áudio** | sounddevice (mic) + parec/pw-cat (monitor Linux) |

## Setup (Linux)

```bash
# Dependências do sistema
sudo pacman -S python python-pip   # Arch
# sudo apt install python3 python3-pip  # Ubuntu/Debian

# Dependências Python
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar: GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

# Rodar
python main.py
```

## Configuração (.env)

```
GROQ_API_KEY=gsk_...                    # API key do Groq (https://console.groq.com/keys)
AWS_BEARER_TOKEN_BEDROCK=bedrock_...     # Long-term API key do Bedrock
AWS_REGION=us-east-1
```

---

## Modos de Operação

O copiloto tem **3 modos** (selecionados no dropdown "Comportamento"):

| Modo | Template | Uso |
|---|---|---|
| **Sugestões** | `sugestoes.md` | Frases prontas genéricas para qualquer reunião |
| **Sugestões Discovery** | `discovery-dati.md` | Discovery comercial Dati — frases prontas para o vendedor |
| **Consultor Técnico AWS** | `assistente-objetivo.md` | Pré-venda técnica — dados AWS + como falar pro cliente |

---

## Fluxo Principal — Arquitetura Incremental

O copiloto usa um fluxo de **pré-processamento incremental** que garante respostas rápidas (2-7s) em vez de processar tudo no momento do snapshot (que levava 19-32s).

### Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    GRAVAÇÃO CONTÍNUA                         │
│                                                             │
│  A cada 60s (automático):                                   │
│    1. Groq transcreve áudio (~1s)                           │
│    2. Bedrock identifica speakers (~2s)                     │
│    3. Extrai 1 ponto-chave do trecho (~1.5s, background)   │
│       → Acumula em lista de pontos incrementais             │
│                                                             │
│  Win+D (snapshot):                                          │
│    1. Flush do áudio pendente → Groq + Bedrock              │
│    2. Pega pontos desde último snapshot (checkpoint)        │
│    3. Se 1-2 pontos → resposta direta (~2-3s)              │
│       Se 3+ pontos → agrupa em categorias (~3s) + responde  │
│    4. Detecta concorrente/pergunta → web search + 📎 OBS   │
│    5. Avança checkpoint                                     │
│                                                             │
│  Win+H (fullcontext):                                       │
│    1. Agrupa TODA a transcrição por temas                   │
│    2. Gera sugestões por tema + próximos passos             │
│    3. Web search por tema técnico                           │
└─────────────────────────────────────────────────────────────┘
```

### Extração Incremental (Background)

A cada chunk de 60s, após a diarização, o sistema extrai automaticamente um ponto-chave:

```
Instrução: "Resuma o trecho em 1 frase. Responda SOMENTE a frase."
Input:     "[Juliano] Deploy hoje é git pull dentro da instância..."
Output:    "O processo de deploy atual é manual via git pull, ineficiente para produção."
```

- Tempo: ~1.5s por chunk (roda em background, não bloqueia)
- Resultado: lista de pontos acumulados (`_incremental_points`)
- Limpeza automática: remove títulos, aspas, prefixos do modelo

### Snapshot (Win+D) — Resposta por Modo

#### Consultor Técnico AWS

Formato: 📌 dados técnicos (3-5 linhas) + 💬 como falar pro cliente (2-3 frases)

```
📌 SSM Session Manager permite acesso seguro sem porta 22. Custo ~$0.30/h.
   RDS com IAM autentica via token temporário, eliminando senhas em repos.
   Requer IAM roles e políticas — sem liberação de firewall.

💬
- "Vocês podem acessar instâncias e bancos sem abrir portas — tudo via Session Manager."
- "Com IAM no RDS, login só com credenciais temporárias — muito mais seguro."
- "Elimina risco de invasão por portas abertas."
```

#### Sugestões / Discovery

Formato: frases prontas com emojis que o comercial pode falar diretamente

```
💡 "A elasticidade da AWS é perfeita pra lidar com esses picos de venda de ingressos."
⚠️ "Manter tudo na mão dá muito trabalho — a gente pode automatizar esse ciclo todo."
✅ "Vamos estruturar o ambiente pra se ajustar sozinho à volatilidade."
```

Emojis: 🔴 urgente | ⚠️ atenção | 💡 oportunidade | ✅ próximo passo

### Detecção Automática + Web Search

O sistema detecta automaticamente:

| Detecção | Keywords | Ação |
|---|---|---|
| **Concorrente** | google, gemini, azure, heroku, oracle, chatgpt, openai, gcp | Web search "X vs AWS privacy security 2026" |
| **Pergunta** | ?, como, qual, quanto, quando, por que, diferença entre | Web search "tema AWS 2026" |

Quando detecta, adiciona `📎 OBS:` no final da resposta com dados factuais da pesquisa:

```
💡 "A AWS tem políticas de privacidade rígidas — seus dados nunca treinam modelos sem permissão."
⚠️ "Com a gente, vocês têm controle total de onde os dados ficam."
✅ "Posso mostrar como estruturamos ambientes de IA na AWS pra proteger dados."

📎 OBS: Dados usados em IA na AWS seguem o framework de responsabilidade compartilhada,
onde o cliente mantém controle sobre os dados e a AWS garante a infraestrutura segura.
```

### Agrupamento (3+ pontos)

Quando o snapshot tem 3 ou mais pontos acumulados, o sistema agrupa em 2-3 categorias antes de responder:

```
9 pontos → Chamada intermediária (2-3s):
  1. Segurança e Acesso (SSM, IAM, VPN, Bastion)
  2. Deploy e Automação (git pull, CodePipeline, CI/CD)
  3. Infraestrutura (Next.js, Virginia, CloudWatch)

→ Resposta por categoria (4-7s)
```

### Fullcontext (Win+H)

Gera resposta completa agrupada por temas da reunião inteira:

- Agrupa toda a transcrição por temas
- Cada tema: título + contexto + sugestões + 💬
- Último bloco: "Próximos passos"
- Web search por tema técnico (múltiplas queries)

### Tempos Medidos

| Cenário | Tempo | Antes |
|---|---|---|
| Snapshot 1 ponto | **2-3s** | 6-10s |
| Snapshot 2 pontos | **3-5s** | 7-32s |
| Snapshot 4+ pontos (agrupado) | **7-9s** | 19-20s |
| Snapshot 0 pontos (edge case) | **0s** | — |
| Extração incremental (background) | **1.5s/chunk** | — |

### Cache (Bedrock)

- `cachePoint` no system prompt (bloco separado)
- TTL: 5 minutos, reseta a cada hit
- Pre-warm na inicialização da sessão
- Economia: ~60% nas chamadas subsequentes

---

## Arquitetura

```
backend/
├── api.py              # API bridge (pywebview js_api) — fluxo principal
├── audio/
│   ├── capture.py      # Captura de áudio (sounddevice + parec/pw-cat)
│   ├── devices.py      # Listagem de dispositivos + detecção de padrão
│   └── wav.py          # Conversão PCM → WAV
├── transcription/
│   └── groq.py         # Cliente Groq Whisper
├── llm/
│   └── bedrock.py      # Cliente Bedrock (boto3, long-term API key, cachePoint)
├── search.py           # Web search (DuckDuckGo via primp)
├── config/
│   └── settings.py     # Configuração persistente
└── platform.py         # Detecção de plataforma + hotkeys (Hyprland/X11)
frontend/
└── index.html          # UI completa (single file, Tailwind CSS)
prompts/
├── sugestoes.md        # Template: sugestões genéricas
├── discovery-dati.md   # Template: discovery comercial Dati (41 situações few-shot)
├── discovery-dati-selecao.md  # Versão completa com 160 abordagens
├── assistente-objetivo.md     # Template: consultor técnico AWS (10 situações few-shot)
├── consultor-tecnico.md       # Cópia do assistente-objetivo
└── consultor-tecnico-selecao.md  # Versão completa com 36 abordagens
tests/
├── test_fluxo.py       # 25 testes de integração (100%)
└── TESTES-INTEGRACAO.md # Documentação dos testes
transcricoes/           # 8 reuniões discovery + 6 técnicas (dados de treino)
tools/                  # Ferramentas de seleção de abordagens (HTML standalone)
main.py                 # Entry point
```

## Hotkeys

| Tecla | Ação |
|---|---|
| `Super+Space` | Iniciar/parar gravação |
| `Super+D` | Snapshot (transcreve + gera sugestão do intervalo) |
| `Super+H` | Fullcontext (sugestões da reunião inteira por temas) |

## Custos Estimados

| API | Preço | Uso típico (4 sessões/dia, 30min) |
|---|---|---|
| Groq Whisper | $0.04/hora | ~R$24/mês |
| Bedrock (Nova Pro) | ~$0.80/1M tokens | ~R$15-30/mês |
| **Total** | | **~R$40-55/mês** |

## Testes

```bash
# Rodar suite de integração (requer API keys configuradas)
python tests/test_fluxo.py

# Resultado esperado: 25/25 passed (100%)
```

Cobertura dos testes:
1. Carregamento de templates (3 modos)
2. Classificação (pergunta, concorrente, contexto)
3. Snapshot Discovery (com/sem pergunta, formato)
4. Snapshot Consultor Técnico (com/sem pergunta, formato)
5. Intervalo de checkpoint (não repete entre snapshots)
6. Fullcontext (temas, próximos passos)
7. Web search (query limpa, resultados)
8. Cache Bedrock (warm, hit, latência)
