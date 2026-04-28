# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None
base = os.path.abspath('.')

a = Analysis(
    ['launcher.py'],
    pathex=[base],
    binaries=[],
    datas=[
        ('frontend', 'frontend'),
        ('prompts', 'prompts'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.edgechromium',
        'clr_loader',
        'pythonnet',
        'sounddevice',
        'numpy',
        'httpx',
        'httpcore',
        'h11',
        'certifi',
        'idna',
        'sniffio',
        'anyio',
        'dotenv',
        'boto3',
        'botocore',
        'keyboard',
        'pyaudiowpatch',
        'ddgs',
        'primp',
        'backend',
        'backend.api',
        'backend.audio',
        'backend.audio.capture',
        'backend.audio.devices',
        'backend.audio.wav',
        'backend.transcription',
        'backend.transcription.groq',
        'backend.llm',
        'backend.llm.bedrock',
        'backend.config',
        'backend.config.settings',
        'backend.platform',
        'backend.search',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'speechbrain', 'torchaudio', 'torchvision', 'matplotlib', 'PIL', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhisperCopilot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperCopilot',
)
