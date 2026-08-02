# novel-pro one-click skill pack + GitHub Release publisher
# Usage: .\release.ps1   or double-click release.bat

$ErrorActionPreference = "Stop"

$ProjectName = "novel-pro"
$Repo = "ouzx6696-cmyk/novel-pro"
$SkillDir = $PSScriptRoot
$DistDir = Join-Path $SkillDir "dist"

Write-Host ""
Write-Host "============================================"
Write-Host "  novel-pro skill pack release tool"
Write-Host "============================================"
Write-Host ""

# 1. Check gh
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] GitHub CLI (gh) not found. Install: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] gh not logged in. Run: gh auth login" -ForegroundColor Red
    exit 1
}

# 2. Read version from skill.json
$skillJsonPath = Join-Path $SkillDir "skill.json"
$Version = "0.2.3-pro"
if (Test-Path $skillJsonPath) {
    try {
        $meta = Get-Content $skillJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($meta.version) { $Version = [string]$meta.version }
    } catch {
        Write-Host "[WARN] Failed to parse skill.json, using default version $Version" -ForegroundColor Yellow
    }
}

$Tag = "v$Version"
$ZipName = "$ProjectName-$Version.zip"
$ZipPath = Join-Path $DistDir $ZipName
$ReleaseTitle = "novel-pro $Version"

Write-Host "[INFO] Version : $Version"
Write-Host "[INFO] Tag     : $Tag"
Write-Host "[INFO] Local zip: $ZipPath"
Write-Host "[INFO] Repo    : $Repo"
Write-Host ""

# 3. Stage files into temp dir
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

$TempDir = Join-Path $env:TEMP ("novel-pro-pack-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempDir | Out-Null

$excludeDirs = @(".git", "__pycache__", ".idea", ".vscode", "dist", ".workbuddy", ".zcode")
$excludeFiles = @(".gitignore", "release.bat", "release.ps1")

Write-Host "[1/4] Copying release files..."

Get-ChildItem -Path $SkillDir -Force | ForEach-Object {
    $name = $_.Name
    if ($excludeDirs -contains $name) { return }
    if ($excludeFiles -contains $name) { return }
    if ($name -like "*.pyc" -or $name -like "*.pyo" -or $name -like "*.pyd") { return }

    $dest = Join-Path $TempDir $name
    if ($_.PSIsContainer) {
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    } else {
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }
}

# Strip nested __pycache__
Get-ChildItem -Path $TempDir -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }

# 4. Build zip
Write-Host "[2/4] Building $ZipName ..."
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

$items = Get-ChildItem -Path $TempDir -Force
if (-not $items) {
    Write-Host "[ERROR] Temp pack directory is empty" -ForegroundColor Red
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

Compress-Archive -Path (Join-Path $TempDir "*") -DestinationPath $ZipPath -Force

if (-not (Test-Path $ZipPath)) {
    Write-Host "[ERROR] Failed to create zip" -ForegroundColor Red
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

$zipSize = (Get-Item $ZipPath).Length
Write-Host "[OK] Local skill pack ready" -ForegroundColor Green
Write-Host "     Path: $ZipPath"
Write-Host "     Size: $zipSize bytes"
Write-Host ""

# 5. Create or reuse release
Write-Host "[3/4] Checking GitHub Release $Tag ..."
gh release view $Tag --repo $Repo 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Creating release $Tag ..."
    $notes = @"
## novel-pro $Version

Chinese long-form novel writing Skill package.

### Includes
- 14 skill modules + 12 agents
- 17 operation dispatch cards (single source of truth)
- Context Pack knowledge compression (通用写作底座 + 类型风格知识两层)
- 写作模式（write.draft 草稿）+ 编辑模式（Reader 冷读 + Anti-AI 扫描 + 整体返修裁决 + 提交）
- Version gate + migration support
- 25 题材（含年代重生 era-rebirth）

### Install
1. Download ``$ZipName`` and extract
2. Run:
   ``python tools/init.py <project-path> --genre <题材编号>``
3. See README.md for details
"@
    $notesFile = Join-Path $env:TEMP ("novel-pro-notes-" + [guid]::NewGuid().ToString("N") + ".md")
    Set-Content -Path $notesFile -Value $notes -Encoding UTF8
    try {
        gh release create $Tag --repo $Repo --title $ReleaseTitle --notes-file $notesFile
        if ($LASTEXITCODE -ne 0) { throw "gh release create failed" }
    } finally {
        Remove-Item $notesFile -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "[INFO] Release exists; will re-upload asset"
}

# 6. Upload zip
Write-Host "[4/4] Uploading $ZipName to Releases ..."
gh release upload $Tag $ZipPath --repo $Repo --clobber
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Upload failed (local zip kept)" -ForegroundColor Red
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "[OK] Uploaded to Releases" -ForegroundColor Green
Write-Host "     https://github.com/$Repo/releases/tag/$Tag"
Write-Host ""

# 7. Cleanup temp only
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "============================================"
Write-Host "  DONE"
Write-Host "  Local : $ZipPath"
Write-Host "  Online: https://github.com/$Repo/releases/tag/$Tag"
Write-Host "============================================"
Write-Host ""
