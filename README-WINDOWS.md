# Branch `windows` — Whisper Copilot para Windows

Versão do Whisper Copilot adaptada para rodar nativamente no Windows 10/11.

## Setup rápido

```powershell
git clone <repo>
cd whisper-copilot-lite-linux
git checkout windows

pip install -r requirements-windows.txt

copy .env.example .env
# Editar .env com GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK

python main.py
```

## O que muda em relação ao Linux

| Componente | Linux (Hyprland) | Windows |
|---|---|---|
| Áudio mic | sounddevice / pw-cat | sounddevice |
| Áudio monitor | parec (PulseAudio) | WASAPI loopback (PyAudioWPatch) |
| Hotkey global | hyprctl (SUPER+key) | keyboard lib (Win+key) |
| Sidebar | hyprctl dispatch | Windows API (ctypes) |
| pywebview | GTK/WebKit | EdgeChromium |

## Áudio

### Microfone
Funciona automaticamente. Selecione no app.

### Autofalante (capturar som do PC)
3 opções:
1. **Stereo Mix**: Painel de Controle → Som → Gravação → Habilitar "Stereo Mix"
2. **VB-Audio Virtual Cable** (gratuito): https://vb-audio.com/Cable/
3. **WASAPI Loopback**: Automático via PyAudioWPatch (já incluído)

## Hotkeys

- **Win + Espaço**: Gravar / Parar
- **Win + D**: Snapshot (transcreve sem parar gravação)

Configurável no setup. Pode precisar rodar como **Administrador**.

## Dependências

```
pywebview>=5.0
sounddevice>=0.5
numpy>=1.26
httpx>=0.27
python-dotenv>=1.0
boto3>=1.35
keyboard>=0.13
PyAudioWPatch>=0.2
ddgs>=9.0
```

## Troubleshooting

| Problema | Solução |
|---|---|
| Hotkey não funciona | Rodar como Administrador |
| Autofalante não captura | Habilitar Stereo Mix ou instalar VB-Audio |
| pywebview não abre | `pip install pywebview[cef]` |
| Erro SSL | `pip install certifi` |

Ver detalhes completos em [SETUP-WINDOWS.md](SETUP-WINDOWS.md).
