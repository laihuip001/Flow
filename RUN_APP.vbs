Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the script's directory
strScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to project root directory
WshShell.CurrentDirectory = strScriptDir

' Python path
strPython = "C:\Users\laihuip001\AppData\Local\Programs\Python\Python314\pythonw.exe"

' Start Flet App directly (no backend needed for direct API mode)
WshShell.Run """" & strPython & """ flet_app/main.py", 1, False
