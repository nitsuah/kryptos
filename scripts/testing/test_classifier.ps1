# FINAL SCRIPT - Process tests one by one, track progress
Set-Location "C:\Users\ajhar\code\kryptos"

# Get all test files
$allTests = Get-ChildItem tests\test_*.py | Select-Object -ExpandProperty Name | Sort-Object

# Initialize or load progress
$progressFile = "test_progress.json"
if (Test-Path $progressFile) {
    $progress = Get-Content $progressFile | ConvertFrom-Json
    $tested = @($progress.tested)
    $fast = @($progress.fast)
    $slow = @($progress.slow)
    Write-Host "Resuming from previous run..." -ForegroundColor Yellow
    Write-Host "Already tested: $($tested.Count)" -ForegroundColor Cyan
} else {
    $tested = @()
    $fast = @()
    $slow = @()
    Write-Host "Starting fresh..." -ForegroundColor Cyan
}

$remaining = $allTests | Where-Object { $tested -notcontains $_ }

Write-Host "Total tests: $($allTests.Count)"
Write-Host "Remaining: $($remaining.Count)`n"

foreach ($testFile in $remaining) {
    $idx = $tested.Count + 1
    Write-Host "[$idx/$($allTests.Count)] $testFile... " -NoNewline

    $job = Start-Job -ScriptBlock {
        param($tf)
        Set-Location "C:\Users\ajhar\code\kryptos"
        $out = & "C:/Users/ajhar/code/kryptos/.venv/Scripts/python.exe" -m pytest "tests\$tf" -m "not slow" -q --tb=no 2>&1 | Out-String
        return $out
    } -ArgumentList $testFile

    $start = Get-Date
    $completed = Wait-Job $job -Timeout 90
    $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)

    if ($null -eq $completed) {
        Write-Host "TIMEOUT (>90s) [SLOW]" -ForegroundColor Magenta
        Stop-Job $job
        $slow += $testFile
    } else {
        $output = Receive-Job $job
        if ($output -match "\d+ passed") {
            if ($duration -gt 60) {
                Write-Host "${duration}s [SLOW]" -ForegroundColor Red
                $slow += $testFile
            } else {
                Write-Host "${duration}s [FAST]" -ForegroundColor Green
                $fast += $testFile
            }
        } else {
            Write-Host "NO TESTS" -ForegroundColor Yellow
            $fast += $testFile  # Count as fast if no tests to run
        }
    }

    Remove-Job $job -Force
    $tested += $testFile

    # Save progress after each test
    @{
        tested = $tested
        fast = $fast
        slow = $slow
    } | ConvertTo-Json | Out-File $progressFile
}

Write-Host "`n========================================"  -ForegroundColor Cyan
Write-Host "RESULTS" -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "FAST: $($fast.Count)" -ForegroundColor Green
Write-Host "SLOW: $($slow.Count)" -ForegroundColor Red

Write-Host "`nSLOW TESTS:" -ForegroundColor Red
$slow | ForEach-Object { Write-Host "  $_" }

Write-Host "`nFAST TESTS saved to FAST_TESTS.txt"
$fast | Out-File "FAST_TESTS.txt"

Write-Host "SLOW TESTS saved to SLOW_TESTS.txt"
$slow | Out-File "SLOW_TESTS.txt"
