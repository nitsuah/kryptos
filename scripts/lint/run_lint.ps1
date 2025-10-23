<#
Run the repository linters. This script attempts to run ruff, pylint, and a small
markdown checker. It is tolerant if a tool isn't installed and prints install
instructions.

Usage:
  pwsh ./scripts/lint/run_lint.ps1
#>

Write-Host "Starting lint run..."

# Helper: run command if available
function Invoke-IfExists($cmd, $cmdArgs) {
    $exe = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($null -ne $exe) {
        Write-Host "Running: $cmd $cmdArgs"
        # split args into array so subcommands and params are passed separately
        $argArray = @()
        if ($null -ne $cmdArgs -and $cmdArgs -ne '') {
            $argArray = $cmdArgs -split '\s+'
        }
        & $cmd @argArray
        return $LASTEXITCODE
    }
    else {
        Write-Host "Tool not found: $cmd (skipping)"
        return 0
    }
}

$errs = 0

# 1) ruff
 Invoke-IfExists ruff "check ."
 $r = $LASTEXITCODE
 if ($r -ne 0) { $errs += $r }

# 2) pylint (examples & scripts)
 Invoke-IfExists pylint "examples scripts --rcfile .pylintrc"
 $p = $LASTEXITCODE
 if ($p -ne 0) { $errs += $p }

# 3) markdown checker (python)
$py = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $py) {
    Write-Host "Running markdown checks"
    python .\scripts\lint\check_md.py
    if ($LASTEXITCODE -ne 0) { $errs += $LASTEXITCODE }
} else {
    Write-Host "Python not found; skipping markdown checks"
}

if ($errs -ne 0) {
    Write-Host "Linting completed with errors: $errs" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "Linting completed OK" -ForegroundColor Green
    exit 0
}
pwsh -NoLogo -Command "python -m flake8 src tests"
