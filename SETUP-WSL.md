# Setup WSL (Ubuntu)

## Pré-requisitos

### 1. WSL com GUI (WSLg)
O Windows 11 já vem com WSLg (suporte a GUI no WSL). Verifique:
```bash
echo $DISPLAY  # deve mostrar algo como :0
```

Se não tiver, atualize o WSL:
```powershell
wsl --update
```

### 2. Áudio no WSL
O WSLg já suporta áudio via PulseAudio. Verifique:
```bash
pactl info  # deve mostrar o servidor PulseAudio
pactl list sources short  # lista dispositivos de entrada
```

Se não funcionar, instale:
```bash
sudo apt install pulseaudio-utils
```

### 3. Dependências do sistema
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv libgirepository1.0-dev gir1.2-webkit2-4.1 gir1.2-gtk-3.0
```

### 4. Dependências Python
```bash
cd whisper-copilot-lite-linux
pip install -r requirements.txt
```

### 5. Configurar .env
```bash
cp .env.example .env
# Editar: GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK
```

## Rodar
```bash
python main.py
```

## Diferenças do Linux nativo

| Feature | Linux (Hyprland) | WSL |
|---|---|---|
| Hotkey global (SUPER+Espaço) | ✅ via hyprctl | ❌ não disponível |
| Foco automático no popup | ✅ via hyprctl | ⚠️ via JS (pode não funcionar 100%) |
| Áudio | ✅ PipeWire/PulseAudio | ⚠️ PulseAudio via WSLg |
| Dispositivos | ✅ pactl list sources | ⚠️ pode precisar configurar |

### Sem hotkey global
No WSL, use **Espaço** ou **T** dentro da janela do app para gravar/parar.
A opção de hotkey global no setup será desabilitada automaticamente.

## Troubleshooting

### Áudio não funciona
```bash
# Verificar se PulseAudio está rodando
pactl info

# Listar dispositivos
pactl list sources short

# Testar gravação
parecord --channels=1 --rate=16000 /tmp/test.wav
# Ctrl+C após alguns segundos
aplay /tmp/test.wav
```

### GUI não abre
```bash
# Verificar DISPLAY
echo $DISPLAY

# Testar com app simples
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; w=Gtk.Window(); w.show_all(); Gtk.main()"
```

### pywebview não funciona
```bash
pip install pywebview[gtk]
```
