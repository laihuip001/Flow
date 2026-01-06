# UTF-8 Encoding Fix
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Get style from argument, default to "business"
param([string]$Style = "business")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AI Clipboard Pro - Style: $Style" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$Text = Get-Clipboard
if (-not $Text) {
    Write-Host "ERROR: Clipboard is empty!" -ForegroundColor Red
    Read-Host "Press Enter"
    exit
}

Write-Host "Processing..." -ForegroundColor Yellow

$BodyObject = @{ text = $Text; style = $Style }
$Body = $BodyObject | ConvertTo-Json -Compress
$BodyBytes = [System.Text.Encoding]::UTF8.GetBytes($Body)

try {
    $Request = [System.Net.WebRequest]::Create('http://localhost:8000/process')
    $Request.Method = 'POST'
    $Request.ContentType = 'application/json; charset=utf-8'
    $Request.Headers.Add('Authorization', 'Bearer your_secret_token_here')
    $Request.ContentLength = $BodyBytes.Length
    $Request.Timeout = 60000
    
    $RequestStream = $Request.GetRequestStream()
    $RequestStream.Write($BodyBytes, 0, $BodyBytes.Length)
    $RequestStream.Close()
    
    $Response = $Request.GetResponse()
    $Reader = New-Object System.IO.StreamReader($Response.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $ResponseJson = $Reader.ReadToEnd() | ConvertFrom-Json
    $Reader.Close()
    $Response.Close()
    
    if ($ResponseJson.result) {
        Set-Clipboard -Value $ResponseJson.result
        Write-Host "Done! Clipboard updated." -ForegroundColor Green
        Write-Host "----------------------------------------"
        Write-Host $ResponseJson.result
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "----------------------------------------"
Read-Host "Press Enter"
