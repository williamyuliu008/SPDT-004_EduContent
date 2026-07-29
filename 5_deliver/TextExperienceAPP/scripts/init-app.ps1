# SPDT-001 init-app.ps1 v2 — 一键创建鸿蒙APP（增强版）
# 新增: 自动注入 signingConfigs + 品牌化参数 + 小龙虾端点预配置
# Usage: .\scripts\init-app.ps1 -Name "xxx" -Brand "ThinkKit" -Color "5B8C5A" [-AgentMode] [-Agent]

param(
    [Parameter(Mandatory=$true)] [string]$Name,
    [Parameter(Mandatory=$true)] [string]$Brand,
    [Parameter(Mandatory=$true)] [string]$Color,
    [string]$Desc = "鸿蒙精品应用",
    [string]$LobsterEndpoint = "",        # 小龙虾API地址 (e.g. http://localhost:8848)
    [switch]$AgentMode,                    # 注入智能体维度模块 (legacy: agent-init/observer/network)
    [switch]$Agent,                        # 集成 common/agent-core 公共模块 (Phase 2+ 推荐)
    [switch]$InjectSigning,                # 从已有签名材料自动注入
    [string]$SignSource = "",             # 签名材料来源APP名 (默认从gaokao-agent复用)
    [switch]$Compile,
    [switch]$Deploy,
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"
$APP_ROOT = "D:\92_products\SPDT-001_Harmony"
$TEMPLATE = "$APP_ROOT\templates\base"
$TARGET = "$APP_ROOT\apps\$Name"

# ── Brand registry ──
$BRAND_REGISTRY = @{
    "ThinkKit"      = @{ prefix="thinkkit-"; color="#5B8C5A"; short="TK"; iconClass="thinkkit-icon" }
    "Craftsman"     = @{ prefix="craftsman-"; color="#E87A2A"; short="CM"; iconClass="craftsman-icon" }
    "HarmonyCoder"  = @{ prefix="harmonycoder"; color="#7B2D8E"; short="HC"; iconClass="hc-icon" }
    "RhythmHabit"   = @{ prefix="rhythm-"; color="#3B82B0"; short="RH"; iconClass="rhythm-icon" }
    "GaokaoAgent"   = @{ prefix="gaokao-"; color="#C44536"; short="GK"; iconClass="gaokao-icon" }
}

# Generate bundleName
$bundleName = "com.harmonyworkshop.$($Name.ToLower() -replace '-','.')"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SPDT-001 Init App v2" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Name      : $Name" 
Write-Host "  Brand     : $Brand (#$Color)"
Write-Host "  Bundle    : $bundleName"
if ($Agent) { Write-Host "  Agent     : ENABLED (common/agent-core)" -ForegroundColor Magenta }
if ($AgentMode) { Write-Host "  AgentMode : ENABLED (legacy)" -ForegroundColor DarkGray }
if ($InjectSigning) { Write-Host "  Signing   : Auto-inject from $SignSource" -ForegroundColor Yellow }
if ($LobsterEndpoint) { Write-Host "  Lobster   : $LobsterEndpoint" -ForegroundColor Cyan }
Write-Host "========================================"

# ── Step 1: Copy template ──
if (Test-Path $TARGET) {
    Write-Host "[ERROR] $TARGET already exists" -ForegroundColor Red
    exit 1
}
Copy-Item -Recurse $TEMPLATE $TARGET
Write-Host "[1/8] Template copied" -ForegroundColor Green

# ── Step 2: Replace placeholders ──
function Replace-In-File($path, $replacements) {
    if (-not (Test-Path $path)) { return }
    $content = Get-Content $path -Raw -Encoding UTF8
    foreach ($k in $replacements.Keys) {
        $content = $content -replace [regex]::Escape($k), $replacements[$k]
    }
    [System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
}

$displayName = $Name -replace '-', ' '
$r = @{
    '{{BUNDLE_NAME}}'        = $bundleName
    '{{VENDOR}}'             = $Brand
    '{{APP_DISPLAY_NAME}}'   = $displayName
    '{{BRAND_NAME}}'         = $Brand
    '{{BRAND_COLOR}}'        = $Color
    '{{APP_SHORT_DESC}}'     = $Desc
    '{{LOBSTER_ENDPOINT}}'   = if ($LobsterEndpoint) { $LobsterEndpoint } else { "http://localhost:8848" }
    '{{BRAND_SHORT}}'        = if ($BRAND_REGISTRY[$Brand]) { $BRAND_REGISTRY[$Brand].short } else { "" }
}

$replaceTargets = @(
    "$TARGET\AppScope\app.json5",
    "$TARGET\entry\src\main\resources\base\element\string.json",
    "$TARGET\entry\src\main\ets\app.config.ts",
    "$TARGET\entry\src\main\ets\pages\Index.ets"
)
foreach ($t in $replaceTargets) {
    Replace-In-File $t $r
}
Write-Host "[2/8] Placeholders replaced" -ForegroundColor Green

# ── Step 3: string.json fix ──
$strFile = "$TARGET\entry\src\main\resources\base\element\string.json"
$moduleDesc = if ($AgentMode) { "$Brand $displayName (Agent)" } else { "$Brand $displayName" }
$strContent = @"
{
  "string": [
    { "name": "app_name", "value": "$displayName" },
    { "name": "module_desc", "value": "$moduleDesc" },
    { "name": "EntryAbility_desc", "value": "$moduleDesc" },
    { "name": "EntryAbility_label", "value": "$displayName" }
  ]
}
"@
[System.IO.File]::WriteAllText($strFile, $strContent, [System.Text.Encoding]::ASCII)
Write-Host "[3/8] string.json fixed" -ForegroundColor Green

# ── Step 4: Auto-inject signingConfigs ──
if ($InjectSigning) {
    if (-not $SignSource) { $SignSource = "gaokao-agent" }
    $sourceBP = "$APP_ROOT\apps\$SignSource\build-profile.json5"
    if (-not (Test-Path $sourceBP)) {
        Write-Host "[WARN] Sign source '$SignSource' not found, skipping signing injection" -ForegroundColor Yellow
    } else {
        Write-Host "[4/8] Injecting signingConfigs from $SignSource..." -ForegroundColor Cyan
        
        $sourceJson = Get-Content $sourceBP -Raw -Encoding UTF8
        # Extract signingConfigs block
        $signMatch = [regex]::Match($sourceJson, '("signingConfigs"\s*:\s*\[[^\]]*?(?:\{[^}]*\}[^\]]*)*\])')
        if ($signMatch.Success) {
            $signingBlock = $signMatch.Groups[1].Value
        } else {
            # Try multiline approach: find from "signingConfigs" to matching closing bracket
            $lines = $sourceJson -split "`n"
            $inSigning = $false; $depth = 0; $signLines = @()
            foreach ($line in $lines) {
                if ($line -match '"signingConfigs"') { $inSigning = $true }
                if ($inSigning) {
                    $signLines += $line
                    $open = ($line.ToCharArray() | Where-Object { $_ -eq '[' }).Count
                    $close = ($line.ToCharArray() | Where-Object { $_ -eq ']' }).Count
                    $depth += ($open - $close)
                    if ($depth -le 0 -and $signLines.Count -gt 1) { break }
                }
            }
            $signingBlock = $signLines -join "`n"
        }
        
        $targetJson = Get-Content "$TARGET\build-profile.json5" -Raw -Encoding UTF8
        # Insert signingConfigs after the first { of "app" block
        if ($targetJson -match '"signingConfigs"\s*:\s*\[\s*\]') {
            $targetJson = $targetJson -replace '"signingConfigs"\s*:\s*\[\s*\]', $signingBlock
            [System.IO.File]::WriteAllText("$TARGET\build-profile.json5", $targetJson, [System.Text.Encoding]::UTF8)
            Write-Host "  signingConfigs injected from $SignSource" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Could not find empty signingConfigs in target" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[4/8] signingConfigs: skipped (use -InjectSigning to auto-inject)" -ForegroundColor DarkGray
}

# ── Step 5: Brand params injection ──
Write-Host "[5/8] Brand params..." -ForegroundColor Cyan
$brandInfo = $BRAND_REGISTRY[$Brand]
$lobEp = if ($LobsterEndpoint) { $LobsterEndpoint } else { "http://localhost:8848" }
$agEnabled = if ($AgentMode -or $Agent) { 'true' } else { 'false' }
$appConfigContent = @"
// SPDT-001 Brand Configuration
// Auto-generated by init-app.ps1 v2
export const APP_CONFIG = {
  name: '$displayName',
  bundleName: '$bundleName',
  brand: {
    name: '$Brand',
    short: '$($brandInfo.short)',
    color: '$($brandInfo.color)',
    iconClass: '$($brandInfo.iconClass)',
    prefix: '$($brandInfo.prefix)'
  },
  build: {
    platform: 'HarmonyOS',
    sdkVersion: '6.1.1(24)',
    initDate: '$(Get-Date -Format 'yyyy-MM-dd')'
  },
  lobster: {
    endpoint: '$lobEp',
    enabled: $agEnabled
  }
};
"@
[System.IO.File]::WriteAllText("$TARGET\entry\src\main\ets\app.config.ts", $appConfigContent, [System.Text.Encoding]::UTF8)
Write-Host "  app.config.ts generated with brand params" -ForegroundColor Green

# ── Step 5b: Agent-core integration (Phase 2+) ──
if ($Agent) {
    Write-Host "[5b] Agent-core integration..." -ForegroundColor Magenta
    
    # 1. Copy common/agent-core/*.ets into APP
    $agentCoreSource = "$APP_ROOT\common\agent-core\*.ets"
    $agentTarget = "$TARGET\entry\src\main\ets\common\agent"
    if (Test-Path $agentCoreSource) {
        New-Item -ItemType Directory -Force $agentTarget | Out-Null
        Copy-Item $agentCoreSource $agentTarget -Force
        $agentFileCount = (Get-ChildItem $agentTarget\*.ets).Count
        Write-Host "  Copied $agentFileCount agent-core .ets files to common/agent/" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] common/agent-core/ not found, skipping agent copy" -ForegroundColor Yellow
    }

    # 2. Ensure storage files exist and inject agent keys
    $storageDir = "$TARGET\entry\src\main\ets\common\storage"
    New-Item -ItemType Directory -Force $storageDir | Out-Null

    $keysPath = "$storageDir\keys.ts"
    if (Test-Path $keysPath) {
        $keysContent = Get-Content $keysPath -Raw -Encoding UTF8
        if ($keysContent -notmatch 'AGENT_PROFILE') {
            # Inject agent keys before the closing }
            $keysContent = $keysContent -replace '\}(\s*as const;?)', @"

  // ---- Agent · 智能体维度 ----
  /** 用户画像 (A维度) */
  AGENT_PROFILE: 'AGENT_PROFILE',
  /** 知识点掌握度 (A维度) */
  AGENT_MASTERY: 'AGENT_MASTERY',
  /** 内容清单 (E维度) */
  CONTENT_MANIFEST: 'CONTENT_MANIFEST',
}\$1
"@
            [System.IO.File]::WriteAllText($keysPath, $keysContent, [System.Text.Encoding]::UTF8)
            Write-Host "  Injected AGENT_PROFILE/AGENT_MASTERY/CONTENT_MANIFEST into keys.ts" -ForegroundColor Green
        } else {
            Write-Host "  keys.ts already has agent keys, skipping" -ForegroundColor DarkGray
        }
    } else {
        # Create keys.ts from scratch
        @"
/**
 * storage/keys.ts — 存储 Key 常量枚举 (auto-generated by init-app.ps1 -Agent)
 */

export const STORAGE_KEYS = {
  // ---- 通用 ----
  APP_SETTINGS: 'APP_SETTINGS',

  // ---- Agent · 智能体维度 ----
  AGENT_PROFILE: 'AGENT_PROFILE',
  AGENT_MASTERY: 'AGENT_MASTERY',
  CONTENT_MANIFEST: 'CONTENT_MANIFEST',
} as const;

export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];
"@ | Out-File $keysPath -Encoding utf8
        Write-Host "  Created keys.ts with agent keys" -ForegroundColor Green
    }

    # 3. Ensure storageService.ts has proper context type import
    $ssPath = "$storageDir\storageService.ts"
    if (Test-Path $ssPath) {
        $ssContent = Get-Content $ssPath -Raw -Encoding UTF8
        $needsUpdate = $false
        if ($ssContent -notmatch "from '@kit.AbilityKit'") {
            $ssContent = $ssContent -replace "(import preferences from '@ohos.data.preferences';)", "`$1`nimport { common } from '@kit.AbilityKit';"
            $needsUpdate = $true
        }
        if ($ssContent -match 'static async init\(context: object\)') {
            $ssContent = $ssContent -replace 'static async init\(context: object\)', 'static async init(context: common.Context)'
            $needsUpdate = $true
        }
        if ($needsUpdate) {
            [System.IO.File]::WriteAllText($ssPath, $ssContent, [System.Text.Encoding]::UTF8)
            Write-Host "  Updated storageService.ts with proper context type" -ForegroundColor Green
        } else {
            Write-Host "  storageService.ts already correct" -ForegroundColor DarkGray
        }
    } else {
        # Create storageService.ts from scratch
        @"
/**
 * storage/storageService.ts — based on Preferences CRUD (auto-generated by init-app.ps1 -Agent)
 */

import preferences from '@ohos.data.preferences';
import { common } from '@kit.AbilityKit';
import { StorageKey } from './keys';

let _preferences: preferences.Preferences | null = null;
const PREFERENCES_NAME = 'HarmonyStudioDB';

async function getPreferences(): Promise<preferences.Preferences> {
  if (_preferences !== null) { return _preferences; }
  throw new Error('[StorageService] not initialized');
}

export class StorageService<T> {
  private readonly key: string;

  constructor(storeKey: StorageKey | string) { this.key = storeKey; }

  static async init(context: common.Context): Promise<void> {
    _preferences = await preferences.getPreferences(context, PREFERENCES_NAME);
  }

  async getAll(): Promise<T[]> {
    try {
      const pref = await getPreferences();
      const raw = await pref.get(this.key, '[]');
      return JSON.parse((raw as object).toString()) as T[];
    } catch { return []; }
  }

  async saveAll(items: T[]): Promise<void> {
    const pref = await getPreferences();
    await pref.put(this.key, JSON.stringify(items));
    await pref.flush();
  }

  async clear(): Promise<void> {
    const pref = await getPreferences();
    await pref.delete(this.key);
    await pref.flush();
  }
}
"@ | Out-File $ssPath -Encoding utf8
        Write-Host "  Created storageService.ts with @kit.AbilityKit import" -ForegroundColor Green
    }
} else {
    Write-Host "[5b] Agent-core: skipped (use -Agent to integrate common/agent-core)" -ForegroundColor DarkGray
}

# ── Step 6: Agent modules (optional) ──
if ($AgentMode) {
    Write-Host "[6/8] Agent modules..." -ForegroundColor Magenta
    
    $agentDir = "$TARGET\entry\src\main\ets\agent"
    New-Item -ItemType Directory -Force $agentDir | Out-Null
    
    # agent-init.ets — agent bootstrap
    @"
// Agent bootstrap — auto-generated by init-app.ps1 v2 (AgentMode)
import { APP_CONFIG } from '../app.config';

export class AgentInit {
  private lobsterEndpoint: string;

  constructor() {
    this.lobsterEndpoint = APP_CONFIG.lobster.endpoint;
    console.info('[Agent] Initialized for', APP_CONFIG.brand.name);
  }

  async healthCheck(): Promise<boolean> {
    try {
      const resp = await fetch(`\${this.lobsterEndpoint}/health`);
      return resp.ok;
    } catch (e) {
      console.warn('[Agent] Lobster unreachable:', e);
      return false;
    }
  }

  async postTask(taskType: string, payload: object): Promise<object> {
    const resp = await fetch(`\${this.lobsterEndpoint}/task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_id: APP_CONFIG.name,
        task_type: taskType,
        payload: payload
      })
    });
    return resp.json();
  }
}

export const agent = new AgentInit();
"@ | Out-File "$agentDir\agent-init.ets" -Encoding utf8

    # agent-observer.ets — monitors battery/preferences/system
    @"
// Agent system observers — auto-generated
import { batteryInfo } from '@kit.BasicServicesKit';
import { preferences } from '@kit.ArkData';

export class AgentObserver {
  private prefs: preferences.Preferences | null = null;

  async initPreferences(context: Context): Promise<void> {
    this.prefs = preferences.getPreferencesSync(context, { name: 'agent_state' });
    console.info('[Observer] Preferences ready');
  }

  getBatteryInfo(): { level: number; charging: boolean } {
    return {
      level: batteryInfo.batterySOC,
      charging: batteryInfo.isBatteryCharging
    };
  }

  async getState(key: string): Promise<string> {
    if (!this.prefs) return '';
    return (await this.prefs.get(key, '')) as string;
  }

  async setState(key: string, value: string): Promise<void> {
    if (!this.prefs) return;
    await this.prefs.put(key, value);
    await this.prefs.flush();
  }
}

export const observer = new AgentObserver();
"@ | Out-File "$agentDir\agent-observer.ets" -Encoding utf8

    # agent-network.ets — HTTP capability probe
    @"
// Agent network capability — auto-generated
export class AgentNetwork {
  async probeHttp(): Promise<{ ok: boolean; latencyMs: number }> {
    const t0 = Date.now();
    try {
      const resp = await fetch('https://www.example.com', { method: 'HEAD' });
      return { ok: resp.ok, latencyMs: Date.now() - t0 };
    } catch {
      return { ok: false, latencyMs: -1 };
    }
  }
}

export const networkProbe = new AgentNetwork();
"@ | Out-File "$agentDir\agent-network.ets" -Encoding utf8

    Write-Host "  agent-init.ets / agent-observer.ets / agent-network.ets created" -ForegroundColor Green
} else {
    Write-Host "[6/8] Agent modules: skipped (use -AgentMode to generate)" -ForegroundColor DarkGray
}

# ── Step 7: PREFLIGHT ──
if (-not $SkipPreflight) {
    Write-Host "[7/8] PREFLIGHT..." -ForegroundColor Cyan
    $preflight = "$APP_ROOT\ci\stages\preflight.ps1"
    $pfResult = & powershell -ExecutionPolicy Bypass -File $preflight -BrandPrefix "$Name" 2>&1
    $pfText = $pfResult -join "`n"
    if ($pfText -match "PREFLIGHT RESULT:.*?(\d+) pass.*?(\d+) fail") {
        Write-Host "  $($Matches[1]) pass, $($Matches[2]) fail" -ForegroundColor $(if($Matches[2] -eq "0"){'Green'}else{'Red'})
    }
} else {
    Write-Host "[7/8] PREFLIGHT: skipped" -ForegroundColor DarkGray
}

# ── Step 8: Compile + Deploy (optional) ──
if ($Compile) {
    Write-Host "[8/8] Compile $Name..." -ForegroundColor Cyan
    $env:DEVECO_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
    $env:OHOS_BASE_SDK_HOME = "D:\9_infra\DevEco\6.1\sdk"
    Push-Location $TARGET
    $result = & "D:\9_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat" `
        --mode module -p product=default assembleHap --analyze=normal --parallel --incremental 2>&1
    Pop-Location
    $text = $result -join "`n"
    if ($text -match "BUILD SUCCESSFUL") {
        Write-Host "  BUILD SUCCESS" -ForegroundColor Green
        if ($Deploy) {
            Write-Host "  Deploying to device..." -ForegroundColor Cyan
            $hap = Get-ChildItem "$TARGET\entry\build\default\outputs\default\*-signed.hap" -EA SilentlyContinue | Select-Object -First 1
            if ($hap) {
                $hdc = "C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe"
                & $hdc install $hap.FullName
                & $hdc shell aa start -a EntryAbility -b $bundleName
                Write-Host "  Deployed + Launched" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  BUILD FAILED" -ForegroundColor Red
        ($text -split "`n") | Where-Object { $_ -match "ERROR" } | Select-Object -Last 3 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
    }
} else {
    Write-Host "[8/8] Compile: skipped (use -Compile to build)" -ForegroundColor DarkGray
}

# ── Summary ──
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DONE: $TARGET" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bundle   : $bundleName"
Write-Host "Brand    : $Brand ($Color)"
Write-Host "Agent    : $(if($Agent){'AGENT-CORE'}elseif($AgentMode){'LEGACY'}else{'DISABLED'})"
Write-Host "Signed   : $(if($InjectSigning){'INJECTED'}else{'MANUAL SYNC NEEDED'})"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  Build:  python apps\build-all.py --app $Name"
Write-Host "  Deploy: python apps\build-all.py --app $Name --deploy"
Write-Host "  Smoke:  .\scripts\smoke-test.ps1 -All -AgentMode"
