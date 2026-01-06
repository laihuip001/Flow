# クリップボードの内容をAIで変換するスクリプト

# 設定
$Url = "http://localhost:8000/process"
$Style = "business" # business, casual, summary, english, proofread

# クリップボードからテキスト取得
$Text = Get-Clipboard

if (-not $Text) {
    Write-Host "⚠️ クリップボードが空です" -ForegroundColor Yellow
    exit
}

Write-Host "📩 受信: $Text" -ForegroundColor Cyan
Write-Host "🔄 変換中 ($Style)..." -ForegroundColor Yellow

# JSON作成
$Body = @{
    text = $Text
    style = $Style
} | ConvertTo-Json -Compress

# API呼び出し (.envのAPI_TOKENがある場合はヘッダーに追加が必要)
try {
    # トークンが必要な場合は以下を有効化
    # $Headers = @{ Authorization = "Bearer your_token" }
    
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType "application/json" # -Headers $Headers
    
    if ($Response.result) {
        # 結果をクリップボードにコピー
        $Response.result | Set-Clipboard
        
        Write-Host "✅ 完了: クリップボードを更新しました" -ForegroundColor Green
        Write-Host "--------------------------------------------------"
        Write-Host $Response.result
        Write-Host "--------------------------------------------------"
    }
}
catch {
    Write-Host "❌ エラー: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $Stream = $_.Exception.Response.GetResponseStream()
        $Reader = [System.IO.StreamReader]::new($Stream)
        Write-Host $Reader.ReadToEnd()
    }
}

Pause
