# Branch `universal` — Teste WSL/Ubuntu

**Status: EM TESTE — não usar em produção**

Esta branch adapta o Whisper Copilot para funcionar fora do Hyprland/Wayland, especificamente no WSL (Ubuntu). Precisa ser validada antes de merge na `dev`.

## O que mudou em relação à `dev`

| Componente | `dev` (Hyprland) | `universal` (WSL) |
|---|---|---|
| Hotkey global (SUPER+Espaço) | hyprctl | Desabilitada — usar Espaço/T dentro do app |
| Foco no popup | hyprctl dispatch focuswindow | xdotool (X11) ou JS fallback |
| Detecção de plataforma | Não tinha | `backend/platform.py` detecta SO, WSL, Wayland, X11 |
| Áudio | PipeWire (pw-cat/parec) | PulseAudio via WSLg ou sounddevice fallback |

## Checklist de testes no WSL

### 1. Setup básico
- [ ] `python main.py` abre sem erros
- [ ] Janela principal renderiza corretamente
- [ ] Janela flutuante (popup) abre ao iniciar

### 2. Dispositivos de áudio
- [ ] `pactl list sources short` lista dispositivos
- [ ] Microfone aparece no dropdown do app
- [ ] Botão "Testar" funciona e mostra VU meter
- [ ] Autofalante (monitor) aparece se disponível

### 3. Gravação e transcrição
- [ ] Espaço/T inicia gravação (bolinha vermelha no popup)
- [ ] Espaço/T para gravação
- [ ] Groq transcreve o áudio (transcrição aparece no popup)
- [ ] Bedrock identifica speakers

### 4. Chat / Copiloto
- [ ] Após transcrição, input do popup recebe foco
- [ ] Enter vazio gera resposta do copiloto
- [ ] Instrução digitada gera resposta baseada na instrução
- [ ] Chat puro (perguntar sem gravar) funciona
- [ ] Respostas respeitam o response_mode (curta/completa/pesquisa)

### 5. Hotkey global
- [ ] Opção de hotkey global aparece no setup
- [ ] No WSL, deve mostrar aviso de que não está disponível (ou simplesmente não funcionar)
- [ ] Espaço/T dentro do app continua funcionando normalmente

### 6. Foco do popup
- [ ] Na 1ª transcrição, popup recebe foco e input fica selecionável
- [ ] Na 2ª transcrição em diante, popup recebe foco
- [ ] Se fechar o popup e gravar de novo, popup reabre

### 7. Finalização
- [ ] Botão "Encerrar" funciona
- [ ] Tela de finalização permite gerar relatório
- [ ] "Nova Reunião" volta ao setup

## Problemas conhecidos / esperados no WSL

1. **Hotkey global não funciona** — WSL não tem compositor de janelas. Usar Espaço/T.
2. **Foco do popup pode falhar** — depende do WSLg e do gerenciador de janelas do Windows. Se não focar, clicar manualmente no popup.
3. **Áudio pode não ser detectado** — WSLg precisa estar atualizado. Verificar com `pactl info`.
4. **Latência de áudio** — WSLg adiciona latência no áudio. A transcrição pode ter qualidade menor.
5. **pywebview GTK** — pode precisar de `pip install pywebview[gtk]` e dependências GTK.

## Como testar

```bash
# 1. Clonar e entrar na branch
git clone <repo>
cd whisper-copilot-lite-linux
git checkout universal

# 2. Setup (ver SETUP-WSL.md para detalhes)
pip install -r requirements.txt
cp .env.example .env
# Editar .env com GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

# 3. Verificar áudio
pactl list sources short

# 4. Rodar
python main.py

# 5. Testar o fluxo
# - Selecionar mic, testar
# - Validar AWS
# - Configurar system prompt
# - Iniciar
# - Espaço para gravar, Espaço para parar
# - Digitar instrução ou Enter vazio
# - Verificar resposta
```

## Reportar problemas

Ao encontrar um problema, anotar:
1. O que fez (passo a passo)
2. O que esperava acontecer
3. O que aconteceu
4. Log do terminal (copiar as últimas 20 linhas)
