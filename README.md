# Whisper Copilot

Copiloto inteligente em tempo real. Transcreve áudio, identifica speakers e gera sugestões contextuais.

## Stack

- **Frontend**: HTML + Tailwind CSS (single file)
- **Backend**: Python + pywebview
- **Transcrição**: Groq Whisper API (whisper-large-v3-turbo)
- **IA**: Amazon Bedrock (Nova 2 Pro) — via long-term API key
- **Áudio**: sounddevice (mic) + PyAudioWPatch WASAPI loopback (monitor Windows) / parec/pw-cat (monitor Linux)

## Setup (Windows)

```powershell
# Dependências Python
pip install -r requirements-windows.txt

# Nota: se pythonnet falhar no Python 3.14+, instale antes:
pip install pythonnet==3.1.0rc0

# Configurar .env
copy .env.example .env
# Editar: GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

# Rodar
python main.py
```

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

## Configuração (.env)

```
GROQ_API_KEY=gsk_...                    # API key do Groq (https://console.groq.com/keys)
AWS_BEARER_TOKEN_BEDROCK=bedrock_...     # Long-term API key do Bedrock
AWS_REGION=us-east-1
```

As API keys ficam fixas no `.env` — o app carrega automaticamente ao iniciar.

## Como funciona

### Fluxo principal

```
Microfone (você) → Groq transcreve → [EU] "texto..."
Autofalante (outros) → Groq transcreve → IA identifica speakers + gera sugestões
```

### Instruções (3 camadas com hierarquia)

O system prompt é montado com 3 partes, em ordem de prioridade:

1. **Contexto Adicional** (prioridade máxima) — texto livre, sempre priorizado
2. **Atuação** — define a especialidade do copiloto
3. **Comportamento** — define como o copiloto responde

#### Comportamento (como responde)
- 💬 **Conversa Natural** — responde como um amigo inteligente
- 📋 **Sugestões** — gera ações com emojis
- ⚡ **Assistente Objetivo** — máximo 3 frases
- 🔍 **Pesquisa** — análise profunda com web search

#### Atuação (em que área atua)
- 📋 **Discovery Comercial** — discovery baseada em Problem Canvas e 5W2H
- 🔧 **Consultor Técnico AWS** — arquitetura e boas práticas
- 💰 **Copiloto de Vendas** — técnicas de vendas e negociação
- 🎭 **Piadas e Humor** — sugere piadas baseadas no contexto
- 📄 **Arquivo custom** — upload de .md/.txt

### Dispositivos de áudio

- **Microfone**: captura via sounddevice (dispositivo padrão marcado com ⭐)
- **Autofalante (loopback)**: captura via WASAPI loopback no Windows (dispositivo padrão detectado automaticamente)
- VU meter funcional para ambos durante teste e gravação

### Modos de transcrição

- **Automático**: transcreve a cada X segundos (configurável, mínimo 60s)
- **Snapshot**: SUPER+D para transcrever sem parar a gravação

### Identificação de speakers

A IA analisa o conteúdo das falas e identifica quem é quem:
- Se participantes foram informados no Setup → identifica pelo nome
- Modo "Muitas pessoas" → deduz automaticamente
- Modo "Automático" → identifica pelo papel (organizador, cliente, etc.)

### Sugestões direcionadas

Selecione para quem as sugestões são direcionadas (EU ou qualquer participante).

### Resumo

Ao encerrar a sessão:
1. Botão mostra "⏳ Finalizando..." (feedback visual)
2. Vai para tela de Resumo
3. Usuário escreve o que deseja (resumo executivo, action items, ata, etc.)
4. Bedrock gera o relatório em Markdown
5. Opções de copiar ou salvar como .md

## Arquitetura

```
backend/
├── api.py              # API bridge (pywebview js_api)
├── audio/
│   ├── capture.py      # Captura de áudio (sounddevice + WASAPI loopback)
│   ├── devices.py      # Listagem de dispositivos + detecção de padrão
│   └── wav.py          # Conversão PCM → WAV
├── transcription/
│   └── groq.py         # Cliente Groq Whisper
├── llm/
│   └── bedrock.py      # Cliente Bedrock (boto3, long-term API key)
└── config/
    └── settings.py     # Configuração persistente
frontend/
└── index.html          # UI completa (single file)
prompts/
├── conversa-natural.md # Template: conversa
├── sugestoes.md        # Template: sugestões
├── assistente-objetivo.md # Template: assistente
├── pesquisa.md         # Template: pesquisa
├── consultor-tecnico.md # Template: técnico
├── piadas.md           # Template: piadas
└── vendas.md           # Template: vendas
main.py                 # Entry point
```

## Pipeline por chunk

1. **Groq transcreve** (~0.7s) — verbose_json com timestamps
2. **Bedrock analisa** + **gera sugestões** (~1-3s)
3. **Emite** transcript + sugestões pro frontend

Total: **~2-4s por chunk**

## Custos estimados

| API | Preço | Uso típico (4 sessões/dia, 30min) |
|---|---|---|
| Groq Whisper | $0.04/hora | ~R$24/mês |
| Bedrock (Nova 2 Pro) | ~$0.80/1M tokens | ~R$15-30/mês |
| **Total** | | **~R$40-55/mês** |

## Troubleshooting

### Autofalante não captura (Windows)
- O app detecta automaticamente o dispositivo WASAPI loopback padrão (marcado com ⭐)
- Se não aparecer, verifique se PyAudioWPatch está instalado
- O dispositivo loopback correto deve corresponder à saída de áudio ativa (headset/alto-falante)

### Autofalante não captura (Linux)
```bash
pactl list sources short  # Verificar se PipeWire/PulseAudio está rodando
```

### Sugestões não aparecem
- Verificar se um Comportamento foi selecionado nas Instruções
- A IA pode achar que não tem nada relevante no trecho

### Erro de API
- Verificar que o `.env` tem as keys corretas
- Verificar que o `.env` está em UTF-8
