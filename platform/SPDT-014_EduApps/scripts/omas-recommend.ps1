# SPDT-001 omas-recommend.ps1 鈥?OMAS resource matching checkpoint
# Usage: .\scripts\omas-recommend.ps1 -AppName "xxx" [-Brief]

param([string]$AppName="", [switch]$All, [switch]$Brief)

$root = "D:\92_products\SPDT-001_Harmony"

# Load resource catalog from JSON
$catalog = @"
{
  "SDC": {
    "desc": "Code Generation & Review Pipeline",
    "action": "GoalTree decomposition + CodeReview template",
    "triggers": ["AI","agent","coach","tutor","code","snippet","programming"]
  },
  "CMC": {
    "desc": "Content Production Pipeline",
    "action": "Store listing + brand manual + help docs",
    "triggers": ["reader","note","diary","rss","article","report","doc","content"]
  },
  "Design_SOP": {
    "desc": "Multi-Agent Cluster Designer",
    "action": "Generate AI agent cluster architecture",
    "triggers": ["AI","agent","coach","tutor","杈呭","闂瓟","programming"]
  },
  "UIUX": {
    "desc": "UI/UX Design Recipes & Golden Tests",
    "action": "Layout recipe matching + brand consistency check",
    "triggers": ["UI","visual","card","list","tool","new_app"]
  },
  "OGC": {
    "desc": "Quality Audit Gate",
    "action": "ArkTS code audit + brand compliance",
    "triggers": ["new_app","release","audit","check"]
  },
  "MODLIB": {
    "desc": "Module Asset Library (152 modules)",
    "action": "Search reusable Python modules",
    "triggers": ["python","pipeline","data","backend"]
  },
  "MAC": {
    "desc": "Market Analysis Cell",
    "action": "Market gap scan + competitor analysis",
    "triggers": ["new_brand","market","planning"]
  }
}
"@ | ConvertFrom-Json

# Get apps to analyze
if ($AppName) {
  $apps = Get-ChildItem "$root\apps\$AppName" -Directory -ErrorAction SilentlyContinue
  if (-not $apps) { Write-Host "APP '$AppName' not found"; return }
} else {
  $apps = Get-ChildItem "$root\apps" -Directory | Sort-Object Name
}

# Analyze each app
foreach ($app in $apps) {
  $appDir = $app.FullName
  $configFile = "$appDir\entry\src\main\ets\app.config.ts"
  $appName = $app.Name.ToLower()
  
  # Extract features from config
  $keywords = @()
  if (Test-Path $configFile) {
    $config = (Get-Content $configFile -Raw).ToLower()
    foreach ($kw in @("AI","agent","tutor","coach","quiz","exam","test","question")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("code","snippet","api","http","json","regex","formatter","editor")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("note","diary","reader","rss","article","read")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("habit","meditation","nutrition","pomodoro","focus","health")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("scan","translate","clipboard","image","tool")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("flashcard","word","vocab","language","learn","study","gaokao","education")) { if ($config -match $kw) { $keywords += $kw } }
    foreach ($kw in @("mindmap","chart","graph","visualize")) { if ($config -match $kw) { $keywords += $kw } }
  }
  if (-not $keywords) { $keywords += "new_app" }
  
  # Match resources
  $matched = @{}
  foreach ($res in $catalog.PSObject.Properties) {
    $triggers = $res.Value.triggers
    foreach ($kw in $keywords) {
      if ($triggers -contains $kw -and -not $matched.ContainsKey($res.Name)) {
        $matched[$res.Name] = $res.Value
        break
      }
    }
  }
  # Always recommend CMC + OGC for new apps
  if (-not $matched.ContainsKey("CMC")) { $matched["CMC"] = $catalog.CMC }
  if (-not $matched.ContainsKey("OGC")) { $matched["OGC"] = $catalog.OGC }
  
  # Output
  Write-Host ""
  Write-Host "=== $($app.Name) ===" -ForegroundColor Cyan
  Write-Host "  Keywords: $($keywords -join ', ')" -ForegroundColor DarkGray
  Write-Host "  Resources: $($matched.Count)" -ForegroundColor White
  
  foreach ($key in ($matched.Keys | Sort-Object)) {
    $m = $matched[$key]
    $star = if ($key -eq "Design_SOP" -or $key -eq "SDC") { "P0" } else { "  " }
    Write-Host "  [$star] $key : $($m.desc)" -ForegroundColor Yellow
    if (-not $Brief) {
      Write-Host "         -> $($m.action)" -ForegroundColor DarkGray
    }
  }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Analyzed: $($apps.Count) apps"
Write-Host "Embed into init-app.ps1: add '. .\omas-recommend.ps1 -AppName `$Name' at script end"
