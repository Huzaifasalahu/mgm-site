; AutoClaw NSIS Installer Script
; Windows installer for AutoClaw AI Agent Platform

!include "MUI2.nsh"
!include "FileFunc.nsh"

; General settings
Name "AutoClaw"
OutFile "AutoClaw_Setup.exe"
InstallDir "$PROGRAMFILES\AutoClaw"
InstallDirRegKey HKLM "Software\AutoClaw" ""
RequestExecutionLevel admin

; Icons
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "GPL-3.0.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Installation sections
Section "AutoClaw Core" SecCore
    SetOutPath "$INSTDIR"
    
    ; Copy main application files
    File "main.py"
    File "agent.py"
    File "tools.py"
    
    ; Copy skills directory
    SetOutPath "$INSTDIR\skills"
    File /r "skills\*.*"
    
    ; Copy UI directory
    SetOutPath "$INSTDIR\ui"
    File /r "ui\*.*"
    
    ; Copy Python runtime (bundled)
    SetOutPath "$INSTDIR\python"
    File /r "python_embed\*.*"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\AutoClaw"
    CreateShortcut "$SMPROGRAMS\AutoClaw\AutoClaw.lnk" "$INSTDIR\python\python.exe" "$INSTDIR\main.py"
    CreateShortcut "$DESKTOP\AutoClaw.lnk" "$INSTDIR\python\python.exe" "$INSTDIR\main.py"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Register in registry
    WriteRegStr HKLM "Software\AutoClaw" "" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoClaw" "DisplayName" "AutoClaw"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoClaw" "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\AutoClaw.lnk" "$INSTDIR\python\python.exe" "$INSTDIR\main.py"
SectionEnd

; Uninstall section
Section "Uninstall"
    ; Remove registry entries
    DeleteRegKey HKLM "Software\AutoClaw"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoClaw"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\AutoClaw\AutoClaw.lnk"
    RMDir "$SMPROGRAMS\AutoClaw"
    Delete "$DESKTOP\AutoClaw.lnk"
    
    ; Remove files
    RMDir /r "$INSTDIR"
SectionEnd

; Post-install actions
Function .onInstSuccess
    MessageBox MB_YESNO "Installation complete! Would you like to launch AutoClaw now?" IDNO noLaunch
    Exec '"$INSTDIR\python\python.exe" "$INSTDIR\main.py"'
    noLaunch:
FunctionEnd
