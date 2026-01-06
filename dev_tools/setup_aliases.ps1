# Titanium Alias Setup Script
# Run this to configure PowerShell aliases for the current session and print instructions for permanent setup.

function Set-TitaniumAliases {
    $root = Get-Location
    
    # Define aliases
    Set-Alias -Name push -Value "$root\dev_tools\secure_push.sh" -Scope Global -ErrorAction SilentlyContinue
    Set-Alias -Name watcher -Value "$root\maintenance\titanium_watcher.sh" -Scope Global -ErrorAction SilentlyContinue
    Set-Alias -Name sync -Value "$root\dev_tools\sync.sh" -Scope Global -ErrorAction SilentlyContinue

    Write-Host "✅ Aliases set for this session:" -ForegroundColor Green
    Write-Host "  push    -> ./dev_tools/secure_push.sh"
    Write-Host "  watcher -> ./maintenance/titanium_watcher.sh"
    Write-Host "  sync    -> ./dev_tools/sync.sh"
    Write-Host ""
    Write-Host "👉 To make this permanent, add the following to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host "   (type 'notepad `$PROFILE' to open)"
    Write-Host ""
    Write-Host "   Set-Alias push `"$root\dev_tools\secure_push.sh`""
    Write-Host "   Set-Alias watcher `"$root\maintenance\titanium_watcher.sh`""
    Write-Host "   Set-Alias sync `"$root\dev_tools\sync.sh`""
}

Set-TitaniumAliases
