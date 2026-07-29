# validate-common.ps1 — Static code quality checker for HarmonyOS common/ and apps/
# Checks: any type, hardcoded colors, duplicate ThemeTokens, import paths, missing JSDoc
# Usage: .\scripts\validate-common.ps1 [-Path <path>] [-Strict] [-Json]

param([string]$Path = "", [switch]$Strict, [switch]$Json)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workshop = Resolve-Path (Join-Path $scriptDir "..")

$scanPaths = @()
if (-not $Path) {
    $cp = Join-Path $workshop "common"; if (Test-Path $cp) { $scanPaths += $cp }
    $ap = Join-Path $workshop "apps";   if (Test-Path $ap) { $scanPaths += $ap }
} else { $scanPaths += $Path }

$allFiles = @()
foreach ($sp in $scanPaths) { if (Test-Path $sp) { $allFiles += Get-ChildItem $sp -Recurse -Include "*.ets", "*.ts" -File } }

$scannedCount = $allFiles.Count
$errs = New-Object System.Collections.ArrayList
$warns = New-Object System.Collections.ArrayList
$cAny = 0; $cColor = 0; $cDup = 0; $cImport = 0; $cDoc = 0

function A($f,$l,$r,$m,$s) { $script:errs.Add(@{file=$f;line=$l;rule=$r;msg=$m;snippet=$s}) | Out-Null }
function W($f,$l,$r,$m,$s) { $script:warns.Add(@{file=$f;line=$l;rule=$r;msg=$m;snippet=$s}) | Out-Null }

foreach ($file in $allFiles) {
    $rel = $file.FullName.Replace($workshop, "").TrimStart("\")
    $txt = Get-Content $file.FullName -Raw -Encoding UTF8
    if (-not $txt) { continue }
    $lines = $txt -split "\r?\n"
    $fname = $file.Name

    # Build code line index
    $code = @()
    for ($k = 0; $k -lt $lines.Count; $k++) {
        $t = $lines[$k].Trim()
        if ($t.StartsWith("*") -or $t.StartsWith("//") -or $t.Length -eq 0) { continue }
        $code += @{ n = $k + 1; t = $t }
    }

    # ---- R1: any type ----
    foreach ($c in $code) {
        if ($c.t -notmatch '\bany\b') { continue }
        if ($c.t.StartsWith("import ") -or $c.t.StartsWith("export type")) { continue }
        $sn = $c.t; if ($sn.Length -gt 80) { $sn = $sn.Substring(0, 80) }
        A $rel $c.n "no-any" "usage of 'any' type" $sn
        $cAny++
    }

    # ---- R2: Hardcoded colors ----
    if ($fname -ne "tokens.ts") {
        foreach ($c in $code) {
            if ($c.t -notmatch '#[0-9A-Fa-f]{6}') { continue }
            if ($c.t.Contains("?? '#")) { continue }
            $sn = $c.t; if ($sn.Length -gt 80) { $sn = $sn.Substring(0, 80) }
            W $rel $c.n "no-hardcoded-color" "hardcoded color value" $sn
            $cColor++
        }
    }

    # ---- R3: Duplicate ThemeTokens ----
    $hasItf = $txt.Contains("interface ThemeTokens")
    $hasImp = $txt.Contains("import") -and $txt.Contains("ThemeTokens") -and $txt.Contains("from")
    if ($fname.EndsWith(".ets") -and $fname -ne "tokens.ts" -and $hasItf -and (-not $hasImp)) {
        W $rel 1 "duplicate-theme-tokens" "ThemeTokens defined locally, should import from theme/tokens" "interface ThemeTokens {...}"
        $cDup++
    }

    # ---- R4: Import path sanity ----
    $impMatches = [regex]::Matches($txt, "from\s+'([^']+)'")
    foreach ($m in $impMatches) {
        $ip = $m.Groups[1].Value
        if ($ip.Contains("//") -or $ip.Contains("  ")) {
            A $rel 1 "bad-import" "malformed import path: $ip" $m.Value
            $cImport++
        }
    }

    # ---- R5: Missing JSDoc ----
    if ($fname -ne "index.ets" -and $fname -ne "keys.ts") {
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -notmatch '^export (function|class|const|struct|interface|enum|type)') { continue }
            $hasDoc = $false
            $cs = [Math]::Max(0, $i - 4)
            for ($j = $cs; $j -lt $i - 1; $j++) {
                if ($lines[$j].Contains("/**")) { $hasDoc = $true; break }
            }
            if (-not $hasDoc) {
                $sn = $lines[$i].Trim(); if ($sn.Length -gt 80) { $sn = $sn.Substring(0, 80) }
                W $rel ($i + 1) "missing-jsdoc" "export missing JSDoc comment" $sn
                $cDoc++
            }
        }
    }
}

# ============================================================================
# Output
# ============================================================================

if ($Json) {
    @{ scannedFiles=$scannedCount; errors=@($errs); warnings=@($warns);
       summary=@{ anyTypeUsage=$cAny; hardcodedColors=$cColor; duplicateThemeTokens=$cDup;
                  badImports=$cImport; missingJSDoc=$cDoc } } | ConvertTo-Json -Depth 4
    exit 0
}

Write-Host ("`n{0}`n{1}`n{2}" -f ("="*50), "  Code Quality Report", "="*50) -ForegroundColor Cyan
Write-Host "Scanned: $scannedCount files" -ForegroundColor Gray

# Errors
if ($errs.Count -gt 0) {
    Write-Host "`n>>> ERRORS: $($errs.Count) <<<" -ForegroundColor Red
    $errs | Group-Object { $_.rule } | ForEach-Object {
        Write-Host "  [$($_.Name)] x$($_.Count)" -ForegroundColor Red
        $n = 0
        foreach ($e in $_.Group) {
            if ($n++ -ge 5) { Write-Host "    ... and more" -ForegroundColor Gray; break }
            Write-Host "    $($e.file):$($e.line)  $($e.snippet)" -ForegroundColor Red
        }
    }
} else { Write-Host "`n>>> ERRORS: 0 <<<" -ForegroundColor Green }

# Warnings
if ($warns.Count -gt 0) {
    Write-Host "`n>>> WARNINGS: $($warns.Count) <<<" -ForegroundColor Yellow
    $warns | Group-Object { $_.rule } | ForEach-Object {
        Write-Host "  [$($_.Name)] x$($_.Count)" -ForegroundColor Yellow
        $n = 0
        foreach ($w in $_.Group) {
            if ($n++ -ge 3) { Write-Host "    ... and more" -ForegroundColor Gray; break }
            Write-Host "    $($w.file):$($w.line)  $($w.snippet)" -ForegroundColor Yellow
        }
    }
} else { Write-Host "`n>>> WARNINGS: 0 <<<" -ForegroundColor Green }

# Summary table
Write-Host ""
Write-Host ("{0,-20} {1}" -f "Check", "Count") -ForegroundColor Cyan
Write-Host ("{0,-20} {1}" -f "----", "-----") -ForegroundColor Cyan
$cols = @(
    @{l="any type usage"; v=$cAny; c=if($cAny-gt0){"Red"}else{"Green"}},
    @{l="hardcoded colors"; v=$cColor; c=if($cColor-gt0){"Yellow"}else{"Green"}},
    @{l="dup ThemeTokens"; v=$cDup; c=if($cDup-gt0){"Red"}else{"Green"}},
    @{l="bad imports"; v=$cImport; c=if($cImport-gt0){"Red"}else{"Green"}},
    @{l="missing JSDoc"; v=$cDoc; c=if($cDoc-gt0){"Yellow"}else{"Green"}}
)
foreach ($col in $cols) {
    Write-Host ("{0,-20} {1}" -f $col.l, $col.v) -ForegroundColor $col.c
}

$total = $errs.Count + $warns.Count
if ($total -eq 0) {
    Write-Host "`n*** ALL CLEAN - No issues found! ***" -ForegroundColor Green
} else {
    Write-Host "`nTip: re-run with -Json for machine-readable output" -ForegroundColor Gray
}

if ($Strict -and $errs.Count -gt 0) { exit 1 }
exit 0
