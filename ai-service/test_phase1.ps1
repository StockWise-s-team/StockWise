# Test Phase 1 - StockWise AI Service

$baseUrl = "http://localhost:18000/api/v1"

Write-Host "`n=== Test 1: Health Check ===" -ForegroundColor Cyan
try {
    $result = Invoke-RestMethod -Uri "$baseUrl/health"
    Write-Host "PASS: $($result | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: $_" -ForegroundColor Red
}

Write-Host "`n=== Test 2: Auth Missing Header (expect 401) ===" -ForegroundColor Cyan
try {
    $body = '{"message":"test"}'
    Invoke-RestMethod -Uri "$baseUrl/advisor/chat" -Method POST -ContentType "application/json" -Body $body -ErrorAction Stop | Out-Null
    Write-Host "FAIL: Should have returned 401" -ForegroundColor Red
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -eq 401) {
        Write-Host "PASS: Got 401 as expected" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Got $status instead of 401" -ForegroundColor Red
    }
}

Write-Host "`n=== Test 3: Admin Without Role (expect 403) ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "$baseUrl/admin/sources" -Headers @{"X-User-Id"="test-user"} -ErrorAction Stop | Out-Null
    Write-Host "FAIL: Should have returned 403" -ForegroundColor Red
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -eq 403) {
        Write-Host "PASS: Got 403 as expected" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Got $status instead of 403" -ForegroundColor Red
    }
}

Write-Host "`n=== Test 4: GET Chat Stream (SSE) ===" -ForegroundColor Cyan
Write-Host "Opening SSE stream... (timeout 15s)" -ForegroundColor Yellow
try {
    $req = [System.Net.HttpWebRequest]::Create("$baseUrl/advisor/chat/stream?message=FPT+h%C3%B4m+nay?")
    $req.Method = "GET"
    $req.Headers["X-User-Id"] = "test-user-123"
    $req.Timeout = 15000
    
    $resp = $req.GetResponse()
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    
    $eventCount = 0
    $startTime = Get-Date
    
    while ($eventCount -lt 5) {
        $line = $reader.ReadLine()
        if ($null -eq $line) { break }
        
        if ($line -match "^event: (.+)") {
            $eventType = $Matches[1]
            $dataLine = $reader.ReadLine()
            if ($dataLine -match "^data: (.+)") {
                $data = $Matches[1]
                Write-Host "  [$eventType] $data" -ForegroundColor Gray
                $eventCount++
            }
        }
        
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt 15) {
            Write-Host "  Timeout after 15s" -ForegroundColor Yellow
            break
        }
    }
    
    $reader.Close()
    $resp.Close()
    
    if ($eventCount -gt 0) {
        Write-Host "PASS: Received $eventCount SSE events" -ForegroundColor Green
    } else {
        Write-Host "FAIL: No SSE events received" -ForegroundColor Red
    }
} catch {
    Write-Host "FAIL: $_" -ForegroundColor Red
}

Write-Host "`n=== Test 5: POST Chat (SSE) ===" -ForegroundColor Cyan
try {
    $req = [System.Net.HttpWebRequest]::Create("$baseUrl/advisor/chat")
    $req.Method = "POST"
    $req.ContentType = "application/json"
    $req.Headers["X-User-Id"] = "test-user-123"
    $req.Timeout = 15000
    
    $body = '{"message":"FPT hom nay?"}'
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    $req.ContentLength = $bytes.Length
    $reqStream = $req.GetRequestStream()
    $reqStream.Write($bytes, 0, $bytes.Length)
    $reqStream.Close()
    
    $resp = $req.GetResponse()
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    
    $eventCount = 0
    $hasThought = $false
    $hasFinal = $false
    $startTime = Get-Date
    
    while ($true) {
        $line = $reader.ReadLine()
        if ($null -eq $line) { break }
        
        if ($line -match "^event: (.+)") {
            $eventType = $Matches[1]
            $dataLine = $reader.ReadLine()
            if ($dataLine -match "^data: (.+)") {
                $data = $Matches[1]
                Write-Host "  [$eventType] $data" -ForegroundColor Gray
                $eventCount++
                if ($eventType -eq "thought") { $hasThought = $true }
                if ($eventType -eq "final") { $hasFinal = $true }
            }
        }
        
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt 15) { break }
    }
    
    $reader.Close()
    $resp.Close()
    
    if ($hasThought -and $hasFinal) {
        Write-Host "PASS: Got thought + final events ($eventCount total)" -ForegroundColor Green
    } elseif ($eventCount -gt 0) {
        Write-Host "PARTIAL: Got $eventCount events but missing thought or final" -ForegroundColor Yellow
    } else {
        Write-Host "FAIL: No events received" -ForegroundColor Red
    }
} catch {
    Write-Host "FAIL: $_" -ForegroundColor Red
}

Write-Host "`n=== All Tests Complete ===" -ForegroundColor Cyan
