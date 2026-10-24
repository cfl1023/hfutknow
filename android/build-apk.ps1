# 构建「工大知道」APK（不依赖 Gradle）
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File build-apk.ps1
#
# 复用工作区已有的 .android-build 工具链（JDK17 + SDK34 + build-tools 34）。
# 应用只用了框架自带 API（WebView），无第三方依赖，可直接用 SDK 工具链构建。

param(
    [string]$OutDir = "",
    [switch]$Clean
)

$ErrorActionPreference = 'Continue'

$AppDir = $PSScriptRoot
$WorkspaceRoot = Split-Path (Split-Path $AppDir -Parent) -Parent
$ToolchainRoot = Join-Path $WorkspaceRoot '.android-build'

$JdkHome    = Join-Path $ToolchainRoot 'jdk'
$SdkHome    = Join-Path $ToolchainRoot 'sdk'
$BuildTools = Join-Path $SdkHome 'build-tools\34.0.0'
$PlatformJar = Join-Path $SdkHome 'platforms\android-34\android.jar'

if (-not $OutDir) { $OutDir = Join-Path $AppDir 'dist' }

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "    $msg" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------------------
Write-Step "检查工具链"
$javac     = Join-Path $JdkHome 'bin\javac.exe'
$keytool   = Join-Path $JdkHome 'bin\keytool.exe'
$aapt2     = Join-Path $BuildTools 'aapt2.exe'
$zipalign  = Join-Path $BuildTools 'zipalign.exe'
$apksigner = Join-Path $BuildTools 'apksigner.bat'
$d8        = Join-Path $BuildTools 'd8.bat'

foreach ($tool in @($javac, $keytool, $aapt2, $zipalign, $apksigner, $d8, $PlatformJar)) {
    if (-not (Test-Path $tool)) {
        Write-Fail "缺少工具：$tool`n（.android-build 工具链不完整）"
    }
}
Write-Ok "JDK / SDK 工具链完整"
$env:JAVA_HOME = $JdkHome

# ---------------------------------------------------------------------------
$BuildDir = Join-Path $AppDir 'build'
if ($Clean -and (Test-Path $BuildDir)) { Remove-Item $BuildDir -Recurse -Force }

$ResDir     = Join-Path $AppDir 'app\res'
$Manifest   = Join-Path $AppDir 'app\AndroidManifest.xml'
$SrcDir     = Join-Path $AppDir 'app\src'

$CompiledRes = Join-Path $BuildDir 'compiled-res.zip'
$GenDir      = Join-Path $BuildDir 'gen'
$ClassDir    = Join-Path $BuildDir 'classes'
$DexDir      = Join-Path $BuildDir 'dex'
$UnsignedApk = Join-Path $BuildDir 'app-unsigned.apk'
$AlignedApk  = Join-Path $BuildDir 'app-aligned.apk'

foreach ($d in @($BuildDir, $GenDir, $ClassDir, $DexDir, $OutDir)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# ---------------------------------------------------------------------------
Write-Step "1/5 编译资源（aapt2）"
& $aapt2 compile --dir $ResDir -o $CompiledRes
if ($LASTEXITCODE -ne 0) { Write-Fail "资源编译失败" }
Write-Ok "compiled-res.zip"

Write-Step "2/5 链接资源并生成 R.java"
$linkArgs = @(
    'link',
    '-o', $UnsignedApk,
    '-I', $PlatformJar,
    '--manifest', $Manifest,
    '--java', $GenDir,
    '--min-sdk-version', '21',
    '--target-sdk-version', '34',
    '--version-code', '3',
    '--version-name', '1.0.0',
    '--auto-add-overlay'
)
$linkArgs += $CompiledRes
& $aapt2 @linkArgs
if ($LASTEXITCODE -ne 0) { Write-Fail "资源链接失败" }
Write-Ok "R.java 已生成"

# ---------------------------------------------------------------------------
Write-Step "3/5 编译 Java（javac）"
$javaFiles = @()
$javaFiles += Get-ChildItem $SrcDir -Recurse -Filter '*.java' | Select-Object -ExpandProperty FullName
$javaFiles += Get-ChildItem $GenDir -Recurse -Filter '*.java' | Select-Object -ExpandProperty FullName
if ($javaFiles.Count -eq 0) { Write-Fail "没有找到 Java 源文件" }

$argFile = Join-Path $BuildDir 'javac-args.txt'
function To-SlashPath([string]$path) { return $path.Replace('\', '/') }

$lines = @('-encoding','UTF-8','-source','8','-target','8',
           '-bootclasspath',(To-SlashPath $PlatformJar),
           '-classpath',(To-SlashPath $PlatformJar),
           '-d',(To-SlashPath $ClassDir),'-nowarn')
foreach ($f in $javaFiles) { $lines += (To-SlashPath $f) }

$joined = ($lines -join "`n")
$sb = New-Object System.Text.StringBuilder
foreach ($ch in $joined.ToCharArray()) {
    if ([int]$ch -lt 128) { [void]$sb.Append($ch) }
    else { [void]$sb.AppendFormat('\u{0:x4}', [int]$ch) }
}
[System.IO.File]::WriteAllText($argFile, $sb.ToString(), (New-Object System.Text.ASCIIEncoding))

& $javac "@$argFile"
if ($LASTEXITCODE -ne 0) { Write-Fail "Java 编译失败" }
$classCount = (Get-ChildItem $ClassDir -Recurse -Filter '*.class').Count
Write-Ok "编译出 $classCount 个 class"

# ---------------------------------------------------------------------------
Write-Step "4/5 转 DEX（d8）"
$classFiles = @(Get-ChildItem $ClassDir -Recurse -Filter '*.class' | Select-Object -ExpandProperty FullName)
$d8ArgsFile = Join-Path $BuildDir 'd8-args.txt'
$d8Lines = @('--min-api','21','--lib',$PlatformJar.Replace('\','/'),
             '--output',$DexDir.Replace('\','/'))
foreach ($f in $classFiles) { $d8Lines += $f.Replace('\','/') }

$d8Joined = ($d8Lines -join "`n")
$sbD8 = New-Object System.Text.StringBuilder
foreach ($ch in $d8Joined.ToCharArray()) {
    if ([int]$ch -lt 128) { [void]$sbD8.Append($ch) }
    else { [void]$sbD8.AppendFormat('\u{0:x4}', [int]$ch) }
}
[System.IO.File]::WriteAllText($d8ArgsFile, $sbD8.ToString(), (New-Object System.Text.ASCIIEncoding))

& $d8 "@$d8ArgsFile"
if ($LASTEXITCODE -ne 0) { Write-Fail "d8 转换失败" }
Write-Ok "classes.dex 已生成"

# 把 DEX 追加进 APK
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($UnsignedApk, 'Update')
try {
    $entryName = 'classes.dex'
    $existing = $zip.GetEntry($entryName)
    if ($existing) { $existing.Delete() }
    $dexPath = Join-Path $DexDir 'classes.dex'
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $dexPath, $entryName) | Out-Null
    Write-Ok "classes.dex 已打入"
} finally {
    $zip.Dispose()
}

# ---------------------------------------------------------------------------
Write-Step "5/5 对齐并签名"
& $zipalign -f 4 $UnsignedApk $AlignedApk
if ($LASTEXITCODE -ne 0) { Write-Fail "zipalign 失败" }
Write-Ok "已对齐"

$Keystore  = Join-Path $AppDir 'keystore.jks'
$StorePass = 'hfutknow'
$KeyAlias  = 'hfutknow'

if (-not (Test-Path $Keystore)) {
    Write-Host "    首次构建，生成签名密钥…"
    & $keytool -genkeypair -v `
        -keystore $Keystore -alias $KeyAlias `
        -keyalg RSA -keysize 2048 -validity 10000 `
        -storepass $StorePass -keypass $StorePass `
        -dname "CN=HFUT Know, OU=Student, O=HFUTKnow, L=Hefei, ST=Anhui, C=CN" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Fail "生成密钥失败" }
    Write-Ok "密钥已生成：$Keystore"
}

$FinalApk = Join-Path $OutDir '工大知道-v1.0.0.apk'
& $apksigner sign `
    --ks $Keystore --ks-key-alias $KeyAlias `
    --ks-pass "pass:$StorePass" --key-pass "pass:$StorePass" `
    --out $FinalApk $AlignedApk
if ($LASTEXITCODE -ne 0) { Write-Fail "签名失败" }

& $apksigner verify --print-certs $FinalApk 2>&1 | Select-Object -First 3
Write-Ok "签名验证通过"

$size = [math]::Round((Get-Item $FinalApk).Length / 1KB, 0)
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  构建成功！" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ("  APK：{0}" -f $FinalApk)
Write-Host ("  大小：{0:N0} KB" -f $size)
Write-Host ""
Write-Host " 安装到手机：微信文件传输助手发过去 → 手机上点开 → 允许未知来源即可"
Write-Host ""
