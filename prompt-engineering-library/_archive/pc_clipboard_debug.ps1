# UTF-8 Encoding Fix
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Debug Script - AI Clipboard Pro
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AI Clipboard Pro - Debug Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Clipboard
Write-Host "[1/4] Checking clipboard..." -ForegroundColor Yellow
$Text = Get-Clipboard
if (-not $Text) {
    Write-Host "  -> ERROR: Clipboard is empty!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}
Write-Host "  -> OK! Got text (length: $($Text.Length))" -ForegroundColor Green
Write-Host ""

# Step 2: Check Server
Write-Host "[2/4] Checking server connection..." -ForegroundColor Yellow
try {
    $Health = Invoke-RestMethod -Uri 'http://localhost:8000/' -Method Get -TimeoutSec 5
    Write-Host "  -> OK! Server: status=$($Health.status), version=$($Health.version)" -ForegroundColor Green
}
catch {
    Write-Host "  -> ERROR: Cannot connect to server!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}
Write-Host ""

# Step 3: Call API with UTF-8 encoding
Write-Host "[3/4] Running AI conversion..." -ForegroundColor Yellow

# Create JSON body with proper UTF-8 encoding
$BodyObject = @{
    text  = $Text
    style = "business"
}
$Body = $BodyObject | ConvertTo-Json -Compress
$BodyBytes = [System.Text.Encoding]::UTF8.GetBytes($Body)

$Headers = @{
    Authorization = "Bearer your_secret_token_here"
}

try {
    # Use WebRequest for better encoding control
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
    $ResponseStream = $Response.GetResponseStream()
    $Reader = New-Object System.IO.StreamReader($ResponseStream, [System.Text.Encoding]::UTF8)
    $ResponseText = $Reader.ReadToEnd()
    $Reader.Close()
    $Response.Close()
    
    $ResponseJson = $ResponseText | ConvertFrom-Json
    
    if ($ResponseJson.result) {
        Write-Host "  -> OK! Conversion successful!" -ForegroundColor Green
        Write-Host ""
        
        # Step 4: Save to clipboard
        Write-Host "[4/4] Saving to clipboard..." -ForegroundColor Yellow
        Set-Clipboard -Value $ResponseJson.result
        Write-Host "  -> OK! Clipboard updated!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host " Result (Ctrl+V to paste):" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host $ResponseJson.result
    }
    elseif ($ResponseJson.error) {
        Write-Host "  -> Error: $($ResponseJson.message)" -ForegroundColor Red
    }
}
catch {
    Write-Host "  -> API call error!" -ForegroundColor Red
    Write-Host "  -> Detail: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
