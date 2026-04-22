# Changelog — Branch `windows`

## 2026-04-22

### Merge da branch `dev` — todas as features novas

#### Snapshot incremental (Win+D) e Full Context (Win+H)
- **Win+D (Snapshot)**: checkpoint da gravação. Cada snapshot pega só o áudio desde o último. Não repete sugestões anteriores.
- **Win+H (Full Context)**: analisa toda a transcrição acumulada. Visão geral, pode repetir pontos-chave.
- `whisper-fullcontext.sh` criado para Linux/Hyprland
- `platform.py` atualizado: suporta 3 hotkeys (toggle, snapshot, fullcontext)
- No Windows: `keyboard` lib registra Win+H automaticamente

#### Prompts reescritos
- **Copiloto Pessoal** (antes "Conversa Natural"): prompt minimalista, tom natural, sem modo analista. Testado em 50+ cenários.
- **Sugestões**: frases prontas que a pessoa pode falar diretamente. Não mais "Pergunte X" → agora "Com que frequência vocês usam...?"
- **Consultor Técnico AWS** (antes "Assistente Objetivo"): web search automático, preços e specs atualizados.

#### Tokens ajustados
- Short: 80 tokens (~250 chars, 2-3 frases)
- Full: 200 tokens (~600 chars)
- Research: 600 tokens (detalhado)

#### UI
- "Tipo de Resposta" só aparece em Copiloto Pessoal e Sugestões
- "Conversa Natural" renomeado → "Copiloto Pessoal"
- "Assistente Objetivo" renomeado → "Consultor Técnico AWS"
- "Nova Sessão" vai direto pro setup (não abre resumo de novo)
- Evento `fullcontext_started` no chat popup

#### Web search
- Só ativa no modo `research` + templates `assistente` ou `pesquisa`
- Search direto (sem step de check) — latência ~5s vs ~10s anterior

#### Testes
- Protocolo de testes: 11 categorias, 110 testes mínimos
- 107/109 testes passaram (98.2%)
- Fixtures de áudio em `tests/fixtures/`
- Scripts de teste reutilizáveis em `tests/protocolo_*.py`

---

## O que falta para build Windows

### Pré-requisitos
```powershell
pip install -r requirements-windows.txt
```

### Build com PyInstaller
O arquivo `whisper-copilot.spec` já existe. Para gerar o executável:
```powershell
pip install pyinstaller
pyinstaller whisper-copilot.spec
```

O executável fica em `dist/whisper-copilot/whisper-copilot.exe`.

### Checklist antes do build
- [ ] `.env` com GROQ_API_KEY e AWS_BEARER_TOKEN_BEDROCK
- [ ] Testar áudio: mic via sounddevice, monitor via WASAPI loopback (PyAudioWPatch)
- [ ] Testar hotkeys: Win+Espaço (toggle), Win+D (snapshot), Win+H (fullcontext)
- [ ] Testar sidebar: posicionamento via ctypes (GetSystemMetrics)
- [ ] Testar pywebview: EdgeChromium backend
- [ ] Verificar que `prompts/` e `frontend/` estão incluídos no spec

### Problemas conhecidos
- `keyboard` lib pode precisar de Administrador no Windows
- WASAPI loopback precisa de Stereo Mix habilitado ou VB-Audio Virtual Cable
- pywebview no Windows pode precisar de `pip install pywebview[cef]` se EdgeChromium não funcionar

### Arquivos Windows-específicos
- `requirements-windows.txt` — dependências
- `whisper-copilot.spec` — config PyInstaller
- `icon.ico` — ícone do executável
- `launcher.py` — launcher alternativo
- `SETUP-WINDOWS.md` — guia de instalação
- `README-WINDOWS.md` — documentação da branch
