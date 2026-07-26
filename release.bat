@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
:: novel-pro 一键产出本地技能包并发布到 Releases
:: 用法：双击运行，或在项目根目录执行 release.bat
:: 产物：dist\novel-pro-<version>.zip（本地保留）
::       同时上传到 GitHub Releases
:: ============================================

set "PROJECT_NAME=novel-pro"
set "SKILL_DIR=%~dp0"
if "%SKILL_DIR:~-1%"=="\" set "SKILL_DIR=%SKILL_DIR:~0,-1%"
set "DIST_DIR=%SKILL_DIR%\dist"
set "VERSION="

echo.
echo ============================================
echo   novel-pro 技能包一键发布工具
echo ============================================
echo.

:: 1. 检查 gh CLI
where gh >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 GitHub CLI ^(gh^)
    echo 请先安装：https://cli.github.com/
    pause
    exit /b 1
)

:: 2. 检查 gh 登录
gh auth status >nul 2>&1
if errorlevel 1 (
    echo [错误] GitHub CLI 未登录
    echo 请执行：gh auth login
    pause
    exit /b 1
)

:: 3. 从 skill.json 读取版本号
if exist "%SKILL_DIR%\skill.json" (
    for /f "usebackq tokens=2 delims=:, " %%a in (`findstr /r "\"version\"" "%SKILL_DIR%\skill.json"`) do (
        set "VERSION=%%a"
        set "VERSION=!VERSION:"=!"
        set "VERSION=!VERSION:,=!"
        set "VERSION=!VERSION: =!"
    )
)

if "%VERSION%"=="" (
    echo [警告] 无法从 skill.json 读取版本，使用默认值 0.2.2-pro
    set "VERSION=0.2.2-pro"
)

set "TAG=v%VERSION%"
set "ZIP_NAME=%PROJECT_NAME%-%VERSION%.zip"
set "ZIP_PATH=%DIST_DIR%\%ZIP_NAME%"
set "RELEASE_TITLE=novel-pro %VERSION%"
set "REPO=ouzx6696-cmyk/novel-pro"

echo [信息] 版本号：%VERSION%
echo [信息] Release Tag：%TAG%
echo [信息] 本地产物：%ZIP_PATH%
echo [信息] 目标仓库：%REPO%
echo.

:: 4. 准备 dist 与临时目录
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
set "TEMP_DIR=%TEMP%\novel-pro-pack-%RANDOM%"
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo [步骤 1/4] 复制发行文件（排除 .git / __pycache__ / dist / 脚本自身）...

robocopy "%SKILL_DIR%" "%TEMP_DIR%" /E ^
    /XD .git __pycache__ .idea .vscode dist ^
    /XF .gitignore *.pyc *.pyo *.pyd release.bat ^
    /NFL /NDL /NJH /NJS /nc /ns /np >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo [错误] 文件复制失败，robocopy 退出码 %RC%
    rd /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

for /d /r "%TEMP_DIR%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

:: 5. 生成 zip（PowerShell Compress-Archive）
echo [步骤 2/4] 生成压缩包 %ZIP_NAME% ...
if exist "%ZIP_PATH%" del /f /q "%ZIP_PATH%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path (Join-Path '%TEMP_DIR%' '*') -DestinationPath '%ZIP_PATH%' -Force"

if not exist "%ZIP_PATH%" (
    echo [错误] 压缩包生成失败
    rd /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

for %%A in ("%ZIP_PATH%") do set "ZIP_SIZE=%%~zA"
echo [成功] 本地技能包已生成
echo         路径：%ZIP_PATH%
echo         大小：%ZIP_SIZE% 字节
echo.

:: 6. 创建或复用 Release
echo [步骤 3/4] 检查 / 创建 GitHub Release %TAG% ...

gh release view "%TAG%" --repo "%REPO%" >nul 2>&1
if errorlevel 1 (
    echo [信息] Release 不存在，正在创建...
    gh release create "%TAG%" ^
        --repo "%REPO%" ^
        --title "%RELEASE_TITLE%" ^
        --notes "## novel-pro %VERSION%

中文长篇小说创作 Skill 发行包。

### 包含内容
- 14 个 skills 模块 + 11 个 agents
- 15 张操作派发卡（唯一权威）
- Context Pack 知识预制
- 完整创作闭环：规划 → Prompt → 写作 → 冷读 → 提交
- 版本门禁 + 迁移支持

### 安装
1. 下载 `%ZIP_NAME%` 并解压
2. 在目标项目执行：
   ```
   python tools/init.py <project-path> --genre <题材编号>
   ```
3. 详见仓库 README.md
"
    if errorlevel 1 (
        echo [错误] 创建 Release 失败
        rd /s /q "%TEMP_DIR%" 2>nul
        pause
        exit /b 1
    )
) else (
    echo [信息] Release 已存在，将覆盖上传资产
)

:: 7. 上传 zip
echo [步骤 4/4] 上传 %ZIP_NAME% 到 Releases ...
gh release upload "%TAG%" "%ZIP_PATH%" --repo "%REPO%" --clobber
if errorlevel 1 (
    echo [错误] 上传失败（本地 zip 已保留）
    rd /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

echo [成功] 已上传到 Releases
echo         https://github.com/%REPO%/releases/tag/%TAG%
echo.

:: 8. 清理临时目录（保留 dist 下的 zip）
rd /s /q "%TEMP_DIR%" 2>nul

echo ============================================
echo   完成
echo   本地包：%ZIP_PATH%
echo   在线：  https://github.com/%REPO%/releases/tag/%TAG%
echo ============================================
echo.
pause
endlocal
