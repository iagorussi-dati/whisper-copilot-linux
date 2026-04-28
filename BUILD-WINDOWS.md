# Build Windows — Whisper Copilot

## Pré-requisitos

- Windows 10/11
- Python 3.11+ ([python.org](https://www.python.org/downloads/) — marcar "Add to PATH")
- Git ([git-scm.com](https://git-scm.com/download/win))

## 1. Clonar e instalar

```powershell
git clone https://github.com/iagorussi-dati/whisper-copilot-linux.git
cd whisper-copilot-linux
git checkout windows

pip install -r requirements.txt
pip install pyinstaller
```

## 2. Configurar .env

```powershell
copy .env.example .env
notepad .env
```

Preencher:
```
GROQ_API_KEY=gsk_...
AWS_BEARER_TOKEN_BEDROCK=bedrock_...
AWS_REGION=us-east-1
```

## 3. Testar antes do build

```powershell
# Rodar como Administrador (necessário pra hotkeys)
python main.py
```

Se funcionar, seguir pro build.

## 4. Gerar executável

```powershell
pyinstaller whisper-copilot.spec
```

O executável fica em `dist/WhisperCopilot/WhisperCopilot.exe`.

## 5. Preparar pra distribuição

```powershell
# Copiar .env pra dentro da pasta do executável
copy .env dist\WhisperCopilot\

# Testar o executável (como Administrador)
dist\WhisperCopilot\WhisperCopilot.exe
```

## 6. Distribuir

### Opção A: Zipar a pasta

Zipar `dist/WhisperCopilot/` inteira e enviar. O destinatário:
1. Descompacta
2. Edita o `.env` com as keys dele
3. Roda `WhisperCopilot.exe` como Administrador

### Opção B: Gerar instalador (Inno Setup)

1. Baixar [Inno Setup](https://jrsoftware.org/isdl.php) e instalar
2. Abrir `installer.iss` no Inno Setup Compiler
3. Compilar (Ctrl+F9)
4. O instalador fica em `installer/WhisperCopilot-Setup.exe`

O instalador:
- Cria atalho na área de trabalho
- Cria entrada no menu Iniciar
- Tem desinstalador

**Obs:** O destinatário ainda precisa editar o `.env` dentro da pasta de instalação com as keys dele.

## Observações

- **Rodar como Administrador** — a lib `keyboard` precisa de permissão pra capturar hotkeys globais (Win+Space, Win+D, Win+H)
- **Áudio do sistema** usa WASAPI loopback — o dispositivo de saída precisa estar ativo
- **Antivírus** pode bloquear o executável na primeira vez — adicionar exceção se necessário
- O build precisa ser feito **no Windows** — não funciona cross-compile do Linux
