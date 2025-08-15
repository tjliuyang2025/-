$WorkingDir = "C:\Users\Liuyang\Desktop\coding\视频预览软件"
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$WorkingDir\视频预览工具.lnk")
$Shortcut.TargetPath = "python.exe"
$Shortcut.Arguments = "$WorkingDir\main.py"
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.IconLocation = "$WorkingDir\images\icon.png"
$Shortcut.Description = "视频预览工具"
$Shortcut.Save() 