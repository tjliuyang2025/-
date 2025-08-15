Set WshShell = CreateObject("WScript.Shell")
strWorkingDir = WshShell.CurrentDirectory
Set shortcut = WshShell.CreateShortcut("视频预览工具.lnk")
shortcut.TargetPath = strWorkingDir & "\start_app.bat"
shortcut.WorkingDirectory = strWorkingDir
shortcut.IconLocation = strWorkingDir & "\images\icon.png"
shortcut.Description = "视频预览工具"
shortcut.Save 