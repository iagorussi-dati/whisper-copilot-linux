[Setup]
AppId={{B5E2F8A1-3C4D-4E5F-9A6B-7C8D9E0F1A2B}
AppName=Whisper Copilot
AppVersion=1.1
AppPublisher=Dati
DefaultDirName={autopf}\WhisperCopilot
DefaultGroupName=Whisper Copilot
OutputDir=installer
OutputBaseFilename=WhisperCopilot-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\WhisperCopilot.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\WhisperCopilot\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\Whisper Copilot"; Filename: "{app}\WhisperCopilot.exe"; IconFilename: "{app}\WhisperCopilot.exe"
Name: "{group}\Whisper Copilot"; Filename: "{app}\WhisperCopilot.exe"
Name: "{group}\Desinstalar Whisper Copilot"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\WhisperCopilot.exe"; Description: "Abrir Whisper Copilot"; Flags: nowait postinstall skipifsilent
