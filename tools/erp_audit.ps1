<# =====================================================================
 ERP CORE — Project Auditor (PowerShell)
 هدف السكربت: فحص هيكل مشروع Django/ERP، واستخراج تقرير شامل.
 الاستعمال (PowerShell):
   .\tools\erp_audit.ps1 -Root "D:\ERP_CORE" -Report "D:\ERP_CORE\erp_audit_report.txt"

 المزايا:
 - يعمل على أي مجلد تحدده (-Root).
 - يحصي الملفات حسب الامتداد ويكشف القوالب وملفات الإعداد.
 - يتحقق من دعم تعدد اللغات (locale، .po/.mo، أنماط i18n بالبايثون والقوالب).
 - يكتشف تطبيقات Django عبر وجود apps.py ومجلد migrations.
 - يحفظ تقرير UTF-8 شامل في المسار المحدد بـ -Report.
===================================================================== #>

[CmdletBinding()]
param(
  [Parameter(Position=0)]
  [string]$Root = (Get-Location).Path,

  [Parameter(Position=1)]
  [string]$Report = (Join-Path (Get-Location) 'erp_audit_report.txt')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ==== Helpers ====
function Resolve-Root {
  param([string]$Path)
  try {
    return (Resolve-Path -Path $Path -ErrorAction Stop).Path
  } catch {
    Write-Error "Root path not found: $Path"
    exit 1
  }
}

function Add-Line { param([string]$S) $script:__lines.Add($S) | Out-Null }
function Add-Section { param([string]$Title)
  Add-Line ''
  Add-Line ('=' * 80)
  Add-Line ("{0}" -f $Title)
  Add-Line ('=' * 80)
}

function To-Rel {
  param($Item, [string]$Base)
  try {
    return [System.IO.Path]::GetRelativePath($Base, $Item.ToString())
  } catch {
    return $Item.ToString()
  }
}

# ==== Start ====
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$rootPath = Resolve-Root -Path $Root
$reportPath = $Report
$reportDir = Split-Path -Path $reportPath -Parent
if (-not (Test-Path -LiteralPath $reportDir)) { New-Item -Path $reportDir -ItemType Directory -Force | Out-Null }

$__lines = New-Object System.Collections.Generic.List[string]

# Header
Add-Section "ERP Audit Report"
Add-Line ("Generated At   : {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Add-Line ("PowerShell     : {0}" -f $PSVersionTable.PSVersion.ToString())
Add-Line ("Root           : {0}" -f $rootPath)
Add-Line ("Report         : {0}" -f $reportPath)

# Collect files
$allFiles = Get-ChildItem -Path $rootPath -Recurse -File -Force -ErrorAction SilentlyContinue

# Top-level tree (depth 1)
$topItems = Get-ChildItem -Path $rootPath -Force -ErrorAction SilentlyContinue
Add-Section "Top-Level Structure"
foreach ($it in $topItems) {
  $type = if ($it.PSIsContainer) { 'DIR' } else { 'FILE' }
  Add-Line ("[{0}] {1}" -f $type, (To-Rel $it.FullName $rootPath))
}

# Counts by extension
Add-Section "File Type Summary"
$groups = $allFiles | Group-Object { $_.Extension.ToLowerInvariant() } | Sort-Object Count -Descending
foreach ($g in $groups) {
  $ext = if ([string]::IsNullOrWhiteSpace($g.Name)) { '<no-ext>' } else { $g.Name }
  Add-Line ("{0,-10} : {1,6}" -f $ext, $g.Count)
}

# Code file sets
$codePatterns = @('*.py','*.html','*.htm','*.js','*.jsx','*.ts','*.tsx','*.css','*.scss','*.json','*.yml','*.yaml','*.toml','*.ini','*.cfg','*.conf','*.env','*.ps1','*.sh','*.bat','*.md')
$codeFiles = $allFiles | Where-Object {
  $n = $_.Name.ToLower()
  foreach ($pat in $codePatterns) { if ($n -like $pat.Replace('*','*')) { return $true } }
  return $false
}
Add-Section "Code Files (key types)"
Add-Line ("Total code-like files: {0}" -f ($codeFiles.Count))
Add-Line "Samples:"
$codeFiles | Select-Object -First 30 | ForEach-Object { Add-Line (" - {0}" -f (To-Rel $_.FullName $rootPath)) }
if ($codeFiles.Count -gt 30) { Add-Line ("(+ {0} more ...)" -f ($codeFiles.Count - 30)) }

# Templates discovery
$tmplDirs = Get-ChildItem -Path $rootPath -Recurse -Directory -Filter 'templates' -ErrorAction SilentlyContinue
$tmplFiles = $allFiles | Where-Object { $_.FullName -match '[\\/]+templates[\\/]'}
Add-Section "Templates"
Add-Line ("Template Dirs : {0}" -f ($tmplDirs.Count))
foreach ($d in $tmplDirs) { Add-Line (" - {0}" -f (To-Rel $d.FullName $rootPath)) }
Add-Line ("Template Files: {0}" -f ($tmplFiles.Count))
$tmplFiles | Select-Object -First 30 | ForEach-Object { Add-Line (" - {0}" -f (To-Rel $_.FullName $rootPath)) }
if ($tmplFiles.Count -gt 30) { Add-Line ("(+ {0} more ...)" -f ($tmplFiles.Count - 30)) }

# Config files & Django core files
$cfgExact = @('settings.py','manage.py','pyproject.toml','requirements.txt','Pipfile','Pipfile.lock','poetry.lock',
              'docker-compose.yml','Dockerfile','celery.py','asgi.py','wsgi.py','.env')
$cfgWild  = @('*.ini','*.cfg','*.conf','*.toml','*.yaml','*.yml')

$cfgFiles = @()
$cfgFiles += $allFiles | Where-Object { $cfgExact -contains $_.Name }
foreach ($w in $cfgWild) { $cfgFiles += $allFiles | Where-Object { $_.Name -like $w } }

# Django static/locale hints
$staticDirs = Get-ChildItem -Path $rootPath -Recurse -Directory -Filter 'static' -ErrorAction SilentlyContinue
$localeDirs = Get-ChildItem -Path $rootPath -Recurse -Directory -Filter 'locale' -ErrorAction SilentlyContinue

Add-Section "Configuration & Project Files"
Add-Line ("Config/Key Files: {0}" -f ($cfgFiles.Count))
$cfgFiles | Sort-Object FullName | ForEach-Object { Add-Line (" - {0}" -f (To-Rel $_.FullName $rootPath)) }
Add-Line ("Static Dirs     : {0}" -f ($staticDirs.Count))
foreach ($d in $staticDirs) { Add-Line (" - {0}" -f (To-Rel $d.FullName $rootPath)) }
Add-Line ("Locale Dirs     : {0}" -f ($localeDirs.Count))
foreach ($d in $localeDirs) { Add-Line (" - {0}" -f (To-Rel $d.FullName $rootPath)) }

# i18n signals
$poMoResx = Get-ChildItem -Path $rootPath -Recurse -File -Include '*.po','*.mo','*.resx' -ErrorAction SilentlyContinue
$pyFiles  = $allFiles | Where-Object { $_.Extension -eq '.py' }
$htmlFiles= $allFiles | Where-Object { $_.Extension -in @('.html','.htm') }

$i18nPyPatterns = @('gettext_lazy','ugettext','pgettext','ngettext','LANGUAGES','LOCALE_PATHS','LANGUAGE_CODE')
$i18nTplPatterns = @('{% load i18n %}','{% trans','{% blocktrans')

function Count-Matches {
  param([string[]]$Files, [string]$Pattern, [switch]$Simple)
  try {
    if ($Files.Count -eq 0) { return 0 }
    if ($Simple) {
      return (Select-String -Path $Files -SimpleMatch -Pattern $Pattern -ErrorAction SilentlyContinue | Measure-Object).Count
    } else {
      return (Select-String -Path $Files -Pattern $Pattern -ErrorAction SilentlyContinue | Measure-Object).Count
    }
  } catch { return 0 }
}

Add-Section "Internationalization (i18n) Check"
Add-Line ("locale/.po/.mo/.resx files: {0}" -f ($poMoResx.Count))
foreach ($p in $poMoResx | Select-Object -First 20) { Add-Line (" - {0}" -f (To-Rel $p.FullName $rootPath)) }
if ($poMoResx.Count -gt 20) { Add-Line ("(+ {0} more ...)" -f ($poMoResx.Count - 20)) }

Add-Line "Python i18n tokens:"
foreach ($pat in $i18nPyPatterns) {
  $cnt = Count-Matches -Files $pyFiles.FullName -Pattern $pat -Simple
  Add-Line (" - {0,-14} : {1,5}" -f $pat, $cnt)
}

Add-Line "Template i18n tokens:"
foreach ($pat in $i18nTplPatterns) {
  $cnt = Count-Matches -Files $htmlFiles.FullName -Pattern $pat -Simple
  Add-Line (" - {0,-14} : {1,5}" -f $pat, $cnt)
}

# Django apps discovery (apps.py)
$appFiles = Get-ChildItem -Path $rootPath -Recurse -File -Filter 'apps.py' -ErrorAction SilentlyContinue
$appsInfo = @()
foreach ($af in $appFiles) {
  $appDir = $af.Directory
  $hasMigrations = Test-Path (Join-Path $appDir.FullName 'migrations')
  $appsInfo += [pscustomobject]@{
    AppName       = $appDir.Name
    AppPath       = (To-Rel $appDir.FullName $rootPath)
    HasMigrations = $hasMigrations
  }
}

Add-Section "Django Apps (apps.py)"
Add-Line ("Discovered apps: {0}" -f ($appsInfo.Count))
foreach ($a in ($appsInfo | Sort-Object AppName)) {
  Add-Line (" - {0,-28} | {1,-6} | {2}" -f $a.AppName, (if($a.HasMigrations){'migr'}else{'no-mg'}), $a.AppPath)
}

# Finish
$sw.Stop()
Add-Section "Summary"
Add-Line ("Elapsed: {0} ms" -f $sw.ElapsedMilliseconds)

# Write report
$__lines | Set-Content -LiteralPath $reportPath -Encoding UTF8
Write-Host ("[OK] Audit report written to: {0}" -f $reportPath)
