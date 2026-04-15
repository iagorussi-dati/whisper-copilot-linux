# Whisper Copilot Lite

Copiloto de reuniões em tempo real. Transcreve, identifica speakers e gera sugestões inteligentes.

## Stack

- **Frontend**: HTML + Tailwind CSS (single file)
- **Backend**: Python + pywebview
- **Transcrição**: Groq Whisper API (whisper-large-v3-turbo)
- **IA**: Amazon Bedrock (Nova 2 Pro) — via long-term API key
- **Áudio**: sounddevice (mic) + parec/pw-cat (monitor Linux) / PyAudioWPatch (monitor Windows)

## Setup (Linux)

```bash
# Dependências do sistema
sudo pacman -S python python-pip   # Arch
# sudo apt install python3 python3-pip  # Ubuntu

# Dependências Python
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar: GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

# Rodar
python main.py
```

## Setup (Windows)

```powershell
# Dependências Python
pip install -r requirements-windows.txt

# Configurar .env
copy .env.example .env
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

## Como funciona

### Fluxo principal

```
Microfone (você) → Groq transcreve → [EU] "texto..."
Autofalante (outros) → Groq transcreve → Claude identifica speakers + gera sugestões
```

### Modos de transcrição

- **Automático**: transcreve a cada X segundos (configurável, mínimo 30s)
- **Manual**: pressione Espaço ou T para transcrever quando quiser

### Identificação de speakers

O Claude analisa o conteúdo das falas e identifica quem é quem:
- Se participantes foram informados no Setup → identifica pelo nome
- Se não → deduz pelo papel (organizador, cliente, apresentador)

### System Prompt customizável

Templates prontos:
- 📋 **Discovery Comercial (Dati)** — sugestões de discovery baseadas em Problem Canvas e 5W2H
- 🎭 **Piadas e Humor** — sugere piadas baseadas no contexto
- 💰 **Copiloto de Vendas** — técnicas de vendas e negociação

Também aceita upload de arquivos .md/.txt ou texto livre.

### Sugestões direcionadas

Selecione para quem as sugestões são direcionadas (EU ou qualquer participante).

## Arquitetura

```
backend/
├── api.py              # API bridge (pywebview js_api)
├── audio/
│   ├── capture.py      # Captura de áudio (sounddevice + parec/pw-cat)
│   ├── devices.py      # Listagem de dispositivos
│   └── wav.py          # Conversão PCM → WAV
├── diarization/        # (legado, não usado no fluxo atual)
│   ├── engine.py       # Embeddings SpeechBrain
│   └── voice_bank.py   # Banco de vozes
├── transcription/
│   └── groq.py         # Cliente Groq Whisper
├── llm/
│   └── bedrock.py      # Cliente Bedrock (boto3 direto, long-term API key)
└── config/
    └── settings.py     # Configuração persistente
frontend/
└── index.html          # UI completa (single file)
prompts/
├── piadas.md           # Template: piadas
└── vendas.md           # Template: vendas
Prompt_Modelo.md        # Template: Discovery Dati
main.py                 # Entry point
```

## Pipeline por chunk

1. **Groq transcreve** (~2s) — verbose_json com timestamps
2. **Claude identifica speakers** + **gera sugestões** numa chamada só (~3-6s com cache)
3. **Claude atribui falas** aos speakers (~3s)
4. **Emite** transcript + sugestões pro frontend

Total: **~8-12s por chunk** (com prompt caching ativo)

## Custos

| API | Preço | Uso típico (4 vendedores, 4 reuniões/dia, 30min) |
|---|---|---|
| Groq Whisper | $0.04/hora | ~R$24/mês |
| Bedrock (Nova 2 Pro) | ~$0.80/1M tokens | ~R$15-30/mês |
| **Total** | | **~R$40-55/mês** |

## Prompt Caching

O system prompt é cacheado no Bedrock na primeira chamada. Chamadas seguintes usam o cache (~30% mais rápido). O cache é pré-aquecido automaticamente ao iniciar a reunião.

## Troubleshooting

### Autofalante não captura (Linux)
```bash
pactl list sources short  # Verificar se PipeWire/PulseAudio está rodando
```

### Autofalante não captura (Windows)
- Ativar "Stereo Mix" nas configurações de som
- Ou instalar VB-Audio Virtual Cable (gratuito)

### Sugestões não aparecem
- Verificar se o template de System Prompt foi selecionado
- Verificar logs: `[STEP 3] NENHUMA sugestão!`
- O Claude pode achar que não tem nada relevante no trecho

### Encoding quebrado (caracteres estranhos)
- Verificar que o .env está em UTF-8
- Reiniciar o app
