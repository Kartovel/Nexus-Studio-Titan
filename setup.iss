[Setup]
; Базовая информация
AppName=Nexus Studio Titan
AppVersion=6.3
AppPublisher=Nexus Studio
; {autopf} автоматически выбирает C:\Program Files
DefaultDirName={autopf}\NexusStudio
DefaultGroupName=Nexus Studio Titan
OutputDir=.\Installer
OutputBaseFilename=NexusStudio_v6.3

; Сжатие
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

; =========================================================
; НАСТРОЙКИ ВНЕШНЕГО ВИДА
; =========================================================
WizardStyle=modern dark
WizardBackColor=#1E1E24
WizardImageBackColor=#1E1E24
WizardSmallImageBackColor=#1E1E24

; Иконка самого файла-установщика (.exe)
SetupIconFile=assets\icon.ico

; Твой арт слева (164x314 .bmp)
WizardImageFile=assets\installer_left.bmp

; Логотип в правом верхнем углу (55x58 .bmp)
WizardSmallImageFile=assets\installer_logo.bmp

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать значок на рабочем столе"; GroupDescription: "Дополнительные значки:"; Flags: unchecked

[InstallDelete]
; ВАЖНО: Полностью очищаем папку программы от старой версии перед установкой обновления.
; Это предотвращает накопление мусорных .dll файлов от предыдущих сборок.
Type: filesandordirs; Name: "{app}\*"

[Files]
; Копируем всё содержимое папки сборки в папку установки {app}
Source: "dist\NexusStudio_Titan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Ярлык в меню Пуск
Name: "{group}\Nexus Studio Titan"; Filename: "{app}\NexusStudio_Titan.exe"; IconFilename: "{app}\NexusStudio_Titan.exe"
; Ярлык на рабочем столе
Name: "{commondesktop}\Nexus Studio Titan"; Filename: "{app}\NexusStudio_Titan.exe"; Tasks: desktopicon; IconFilename: "{app}\NexusStudio_Titan.exe"

[Run]
; Автозапуск после установки
Filename: "{app}\NexusStudio_Titan.exe"; Description: "Запустить Nexus Studio Titan"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  WizardForm.DirBrowseButton.Left := WizardForm.DirEdit.Left + WizardForm.DirEdit.Width + 10;
end;