# Setup Windows

## Pré-requisitos

- Python 3.11+ (https://python.org)
- Windows 10/11

## Instalação

```powershell
# Clonar
git clone <repo>
cd whisper-copilot-lite-linux
git checkout universal

# Instalar dependências
pip install -r requirements-windows.txt

# Configurar .env
copy .env.example .env
# Editar .env com GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

# Rodar
python main.py
```

## Áudio no Windows

### Microfone
Funciona automaticamente via `sounddevice`. Selecione no app.

### Autofalante (Monitor/Loopback)
Para capturar o som que sai do PC:

**Opção 1: Stereo Mix (nativo)**
1. Painel de Controle → Som → Gravação
2. Clique direito → "Mostrar dispositivos desabilitados"
3. Habilite "Stereo Mix" ou "Mixagem estéreo"

**Opção 2: VB-Audio Virtual Cable (gratuito)**
1. Baixe em https://vb-audio.com/Cable/
2. Instale e reinicie
3. No app, selecione "CABLE Output" como autofalante

**Opção 3: PyAudioWPatch (WASAPI Loopback)**
Já incluído nas dependências. O app detecta automaticamente dispositivos loopback.

## Hotkeys Globais

No Windows, hotkeys globais usam a tecla **Win** (Windows):
- **Win + Espaço**: Gravar/Parar
- **Win + D**: Snapshot (transcreve sem parar)

Configurável no setup do app.

Requer a lib `keyboard` (já incluída em requirements-windows.txt).
**Nota**: Pode precisar rodar como Administrador para hotkeys globais funcionarem.

## Sidebar

O chat abre como janela separada posicionada na direita da tela.
No Windows, usa a API nativa do pywebview para posicionar.

## Diferenças do Linux

| Feature | Linux (Hyprland) | Windows |
|---|---|---|
| Hotkey global | hyprctl (SUPER+key) | keyboard lib (Win+key) |
| Sidebar | hyprctl dispatch | pywebview move/resize |
| Áudio mic | sounddevice/pw-cat | sounddevice |
| Áudio monitor | parec (PulseAudio) | WASAPI loopback (PyAudioWPatch) |
| pywebview backend | GTK/WebKit | EdgeChromium/MSHTML |

## Troubleshooting

### "keyboard" não funciona
Rode como Administrador:
```powershell
# PowerShell como Admin
python main.py
```

### Áudio do autofalante não captura
1. Verifique se Stereo Mix está habilitado
2. Ou instale VB-Audio Virtual Cable
3. Teste no app: selecione o dispositivo e clique "Testar"

### pywebview não abre
```powershell
pip install pywebview[cef]
# ou
pip install pywebview
```

### Erro de SSL/certificado
```powershell
pip install certifi
set SSL_CERT_FILE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\Lib\site-packages\certifi\cacert.pem
```
