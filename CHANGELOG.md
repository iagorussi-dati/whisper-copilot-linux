# Changelog

## 2026-04-15 - Otimização de Performance e Organização

### ✅ Implementado

#### 1. Instalação e Configuração do SpeechBrain
- Instalado `speechbrain` package (v1.1.0)
- Configurado modelo ECAPA-TDNN para embeddings de voz
- Resolvido problema de symlinks no Windows (estratégia COPY)
- Modelos baixados do HuggingFace (~90MB, cached localmente)

#### 2. Otimização de Performance
- **Pré-carregamento do modelo**: Carrega SpeechBrain em background ao iniciar reunião (~4s)
- **Paralelização**: Aumentado de 2 para 6 workers no ThreadPoolExecutor
- **Filtro de segmentos**: Processa apenas segmentos >= 1.5s (melhor acurácia)
- **Processamento seletivo**: Skip de segmentos muito curtos

#### 3. Resultados de Performance
**Antes**:
- Diarização: 15-32s por chunk ❌
- Total: 17-33s por chunk ❌

**Depois**:
- Transcrição: ~1s por chunk ✅
- Diarização: 5-8s por chunk ✅
- Total: 6-10s por chunk ✅

**Melhoria**: ~70% mais rápido!

#### 4. Correção de Bugs
- ✅ Resolvido erro de symlink no Windows (OSError WinError 1314)
- ✅ Resolvido GIL conflicts com PyAudioWPatch (subprocess isolado)
- ✅ Modelo SpeechBrain carrega corretamente com estratégia COPY

#### 5. Documentação
- Atualizado README.md com instruções completas
- Criado MELHORIAS.md com roadmap de melhorias
- Criado scripts de benchmark (`benchmark_mp3.py`, `benchmark_simple.py`)
- Adicionado troubleshooting para Windows

### 📊 Benchmarks

**Arquivo de Teste**: audio2minteste.mp3 (123s / 2 minutos)
- 35 segmentos detectados
- 33 segmentos processados (>= 1.5s)
- Transcrição: 1.12s
- Diarização estimada: 6.60s
- **Total: 7.72s** ✅

**Teste Real (App)**:
- Chunk 1: 6.69s (15 embeddings)
- Chunk 2: 10.28s (13 embeddings)
- Chunk 3: 6.83s (17 embeddings)
- **Média: ~8s** ✅

### 🔧 Configurações Atuais

```python
# Diarização
THRESHOLD = 0.20  # Cosine similarity
MIN_SEGMENT_DURATION = 1.5  # segundos
WORKERS = 6  # ThreadPoolExecutor
UPDATE_THRESHOLD = 2.0  # segundos para update de embedding

# Captura de Áudio
SAMPLE_RATE = 16000  # Hz
CHUNK_DURATION = 10  # segundos
RMS_INTERVAL = 0.1  # segundos (100ms)
```

### 📝 Arquivos Modificados

- `backend/api.py`: Otimização de diarização, pré-carregamento de modelo
- `backend/diarization/engine.py`: Estratégia COPY para Windows
- `main.py`: Configuração de variáveis de ambiente
- `README.md`: Documentação completa
- `requirements.txt`: Adicionado speechbrain

### 📝 Arquivos Criados

- `MELHORIAS.md`: Roadmap de melhorias futuras (removido - migrado para CHANGELOG)
- `CHANGELOG.md`: Este arquivo
- Scripts de benchmark e teste (removidos após uso)

### 🗑️ Limpeza de Arquivos

Removidos arquivos de teste e desenvolvimento:
- `benchmark_*.py` - Scripts de benchmark (usados para otimização)
- `test_*.py` - Scripts de teste de devices
- `diagnostico_audio.py` - Script de diagnóstico
- `list_*.py` - Scripts de listagem de devices
- `testar_loopback.py` - Teste de loopback
- `run.bat`, `setup.bat` - Substituídos por instruções no README
- `TESTE_AUDIO.md` - Documentação de testes
- `MELHORIAS.md` - Migrado para seção "Próximos Passos" neste arquivo

**Estrutura Final**:
```
whisper-copilot-lite/
├── backend/           # Código Python
├── frontend/          # UI (HTML/JS)
├── .env.example       # Template de configuração
├── .gitignore
├── main.py            # Entry point
├── requirements.txt
├── README.md          # Documentação principal
└── CHANGELOG.md       # Este arquivo
```

### 🐛 Issues Conhecidos

1. **Acurácia da Diarização**: Precisa validar contra projeto original (Tauri)
2. **Identificação de Speakers**: Claude nem sempre identifica nomes corretamente
3. **Performance pode melhorar**: GPU (CUDA) pode reduzir para < 5s

### 🎯 Próximos Passos

#### Prioridade 1: Compatibilidade Universal de Devices
**Objetivo**: Garantir que o app funcione em qualquer PC sem problemas de detecção de áudio

**Tarefas**:
- [ ] Testar em múltiplos PCs Windows (diferentes versões, hardware)
- [ ] Testar em múltiplos PCs Linux (Ubuntu, Arch, Fedora)
- [ ] Validar detecção de devices em diferentes cenários:
  - Headset USB
  - Microfone/Speaker integrados
  - Bluetooth
  - Múltiplos devices conectados
- [ ] Implementar fallback automático se device selecionado falhar
- [ ] Adicionar diagnóstico de devices no setup
- [ ] Melhorar mensagens de erro quando device não funciona

#### Prioridade 2: Melhorar Acurácia da Diarização
**Objetivo**: Igualar ou superar qualidade do projeto original (Tauri)

**Tarefas**:
- [ ] Comparar side-by-side com projeto original usando mesmo áudio
- [ ] Testar diferentes thresholds (atual: 0.20)
- [ ] Testar modelos alternativos:
  - `speechbrain/spkrec-xvect-voxceleb`
  - `pyannote/speaker-diarization`
- [ ] Ajustar filtros de segmento (atual: >= 1.5s)
- [ ] Implementar normalização de embeddings
- [ ] Adicionar logging detalhado de similaridade

#### Prioridade 3: System Prompt Customizável
**Objetivo**: Permitir usuário customizar comportamento do Claude

**Tarefas**:
- [ ] Adicionar aba "System Prompt" no setup
- [ ] Textarea para usuário editar prompt
- [ ] Salvar prompt customizado no config
- [ ] Enviar prompt junto com chamadas do Bedrock/Lambda
- [ ] Incluir exemplos de prompts úteis:
  - Foco em action items
  - Foco em decisões técnicas
  - Foco em perguntas não respondidas
  - Tom formal vs casual

**Implementação**:
```python
# backend/config/settings.py
@dataclass
class AppConfig:
    # ... campos existentes ...
    system_prompt: str = ""  # Novo campo

# backend/llm/bedrock.py
def suggest(self, context: str, system_prompt: str = ""):
    # Incluir system_prompt na chamada
    prompt = f"{system_prompt}\n\n{context}" if system_prompt else context
    # ...
```

#### Outras Melhorias

**Performance**:
- [ ] Testar GPU (CUDA) para SpeechBrain
- [ ] Ajustar workers baseado em CPU cores
- [ ] Implementar cache de embeddings

**Features**:
- [ ] Exportar transcrição em múltiplos formatos (JSON, TXT, SRT)
- [ ] Suporte a múltiplos idiomas
- [ ] Gravação de áudio raw para replay
- [ ] Integração com calendário (Google/Outlook)
- [ ] Correção manual de identificação de speakers durante reunião

**UX**:
- [ ] Indicador visual de qualidade de áudio
- [ ] Notificação quando speaker novo é detectado
- [ ] Atalhos de teclado para funções comuns
- [ ] Dark mode / Light mode

---

## Versões Anteriores

### 2026-04-14 - Setup Inicial
- Implementação base do projeto
- Captura de áudio (sounddevice + PyAudioWPatch)
- Transcrição via Groq Whisper
- Interface pywebview
- Sugestões via Claude (Bedrock proxy)
