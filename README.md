# Whisper Copilot Lite

Copiloto de reuniões em tempo real — versão leve em Python.

Captura áudio do microfone e autofalante, transcreve via Groq Whisper, identifica quem está falando por voz (SpeechBrain ECAPA-TDNN), e gera sugestões inteligentes via Claude (Bedrock proxy).

## 🚀 Performance

- **Transcrição**: ~1s por chunk de 10s (Groq Whisper API)
- **Diarização**: ~5-8s por chunk (SpeechBrain ECAPA-TDNN, 6 workers)
- **Total**: ~6-10s por chunk de áudio ✅

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Janela nativa | pywebview (WebView2 no Windows, WebKitGTK no Linux) |
| Frontend | HTML/JS/Tailwind CSS |
| Captura de áudio | sounddevice + PyAudioWPatch (WASAPI loopback) |
| Transcrição | Groq Whisper API (whisper-large-v3-turbo) |
| Diarização | SpeechBrain ECAPA-TDNN (embeddings locais) |
| Sugestões IA | Claude Sonnet 4 via API Gateway (proxy pro AWS Bedrock) |

## Instalação

### Windows

```powershell
# 1. Instalar Python 3.10+ (https://python.org)

# 2. Clonar repositório
git clone <repo-url>
cd whisper-copilot-lite

# 3. Instalar dependências
pip install -r requirements.txt

# 4. IMPORTANTE: Ativar Modo Desenvolvedor do Windows
# Para permitir symlinks sem admin:
# Configurações → Privacidade e segurança → Para desenvolvedores → Ativar "Modo de desenvolvedor"

# 5. Configurar .env
copy .env.example .env
# Editar .env com suas API keys:
# - GROQ_API_KEY (obrigatório)
# - BEDROCK_PROXY_URL (opcional, usa default)
# - BEDROCK_PROXY_KEY (opcional, usa default)

# 6. Rodar
python main.py
```

### Linux (Ubuntu/Arch)

```bash
# 1. Dependências do sistema
sudo apt install python3 python3-pip libportaudio2 gir1.2-webkit2-4.1  # Ubuntu
sudo pacman -S python python-pip portaudio webkit2gtk-4.1              # Arch

# 2. Clonar repositório
git clone <repo-url>
cd whisper-copilot-lite

# 3. Instalar dependências Python
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env com suas API keys

# 5. Rodar
python3 main.py
```

## 🎯 Uso

1. **Setup**: Selecione microfone e autofalante, valide AWS, configure participantes
2. **Reunião**: Transcrição em tempo real com identificação de speakers + sugestões IA
3. **Resumo**: Resumo automático em Markdown ao encerrar (Ctrl+Shift+S)

## 🔧 Troubleshooting

### Windows: Erro de symlink ao carregar SpeechBrain

**Erro**: `OSError: [WinError 1314] O cliente não tem o privilégio necessário`

**Solução**: Ative o Modo Desenvolvedor do Windows:
1. Abra Configurações (Win + I)
2. Vá em "Privacidade e segurança" → "Para desenvolvedores"
3. Ative "Modo de desenvolvedor"
4. Reinicie o aplicativo

**Alternativa**: Execute como administrador (não recomendado)

### Áudio do monitor não captura

**Windows**: Certifique-se de selecionar um device com "[Loopback]" no nome

**Linux**: Use device com ".monitor" no nome (PulseAudio/PipeWire)

## 📁 Estrutura

```
whisper-copilot-lite/
├── main.py                          # Entry point — abre janela pywebview
├── frontend/
│   └── index.html                   # UI completa (Setup → Meeting → Summary)
├── backend/
│   ├── api.py                       # API bridge (pywebview js_api)
│   ├── audio/
│   │   ├── capture.py               # Captura mic + monitor (sounddevice/subprocess)
│   │   ├── devices.py               # Listar e testar devices
│   │   └── wav.py                   # Encode/decode WAV
│   ├── transcription/
│   │   └── groq.py                  # Cliente Groq Whisper API
│   ├── diarization/
│   │   ├── engine.py                # SpeechBrain ECAPA-TDNN embeddings
│   │   └── voice_bank.py            # Banco de vozes + cosine similarity
│   ├── llm/
│   │   └── bedrock.py               # Cliente Bedrock proxy (Claude)
│   └── config/
│       └── settings.py              # Persistência de configuração
├── requirements.txt
└── .env.example
```

## 🔬 Melhorias Futuras

### Diarização
- [ ] Melhorar acurácia da identificação de speakers
- [ ] Comparar com projeto original (Tauri) para validar qualidade
- [ ] Ajustar threshold de similaridade (atualmente 0.20)
- [ ] Testar modelos alternativos (pyannote.audio)
- [ ] Implementar re-identificação de speakers ao longo da reunião

### Performance
- [ ] Testar GPU para SpeechBrain (CUDA)
- [ ] Otimizar número de workers baseado em CPU cores
- [ ] Cache de embeddings para speakers conhecidos

### Features
- [ ] Exportar transcrição em múltiplos formatos (JSON, TXT, SRT)
- [ ] Suporte a múltiplos idiomas
- [ ] Gravação de áudio raw para replay
- [ ] Integração com calendário (Google/Outlook)

## 📝 Notas Técnicas

### Captura de Áudio no Windows

O projeto usa uma abordagem híbrida:
- **Microfone**: `sounddevice` (estável, sem GIL issues)
- **Monitor/Loopback**: `PyAudioWPatch` em subprocess isolado

Isso evita conflitos de GIL (Global Interpreter Lock) com pywebview que causavam crashes.

### Diarização

- Usa SpeechBrain ECAPA-TDNN para extrair embeddings de voz
- Compara embeddings via cosine similarity
- Threshold padrão: 0.20 (ajustável)
- Processa apenas segmentos >= 1.5s para melhor acurácia
- 6 workers paralelos para performance

### Primeira Execução

Na primeira execução, o SpeechBrain baixa ~90MB de modelos do HuggingFace:
- `embedding_model.ckpt` (83.3MB)
- `classifier.ckpt` (5.53MB)
- Outros arquivos de configuração

Execuções subsequentes usam cache local (~4s para carregar).
