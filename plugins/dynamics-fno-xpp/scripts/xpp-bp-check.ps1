<#
.SYNOPSIS
Best-practice check of chosen objects with Microsoft's xppbp.exe. Reads only.

.DESCRIPTION
Runs xppbp.exe once per target, with the module and model names read from the package's
Descriptor. The d365fo MCP's run_bp_check (1.21.0) passes one name for both, so it can't check
a model whose name differs from its module (e.g. "The Asset Guardian" in TheAssetGuardian), and
it compiles labels into the package's Resources folder first. This script does neither.

xppbp reads the last COMPILED metadata (XppMetadata) together with the current XML, so objects
edited since the last build give mixed results. A clean BP check is not a build.

Exit codes: 0 every target checked, no BP errors (warnings may be listed)
            1 at least one BP error
            2 a target was NOT checked (xppbp processed nothing, or the module/model wasn't found)

.PARAMETER Package
The package folder, the one that holds Descriptor\ (e.g. <PLD>\TheAssetGuardian). Default: current directory.

.PARAMETER Targets
xppbp element selectors, e.g. Table:TAGAssetCriticalityClass, Form:TAGAssetCriticalityClasses,
Class:TAGEnumTest, TableExtension:EntAssetObjectTable.TheAssetGuardian. Comma-separated values
are split. Omit to check the whole model (-all), which takes much longer.

.PARAMETER PackagesRoot
PackagesLocalDirectory. Default: the parent of -Package when it holds Bin\xppbp.exe, otherwise
the first <drive>:\AosService\PackagesLocalDirectory that does.

.EXAMPLE
powershell -NoProfile -File xpp-bp-check.ps1 -Package J:\AosService\PackagesLocalDirectory\TheAssetGuardian -Targets Table:TAGAssetCriticalityClass,Class:TAGEnumTest
#>
param(
    [string]$Package = (Get-Location).Path,
    [string[]]$Targets = @(),
    [string]$PackagesRoot
)

$ErrorActionPreference = 'Stop'

$descriptor = Get-ChildItem -Path (Join-Path $Package 'Descriptor') -Filter '*.xml' -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $descriptor) { Write-Error "No Descriptor\*.xml under $Package. Pass -Package <the package folder>."; exit 2 }
[xml]$info = Get-Content -LiteralPath $descriptor.FullName -Raw
$module = [string]$info.AxModelInfo.ModelModule
$model = [string]$info.AxModelInfo.Name
if (-not $module) { $module = Split-Path $Package -Leaf }

if (-not $PackagesRoot) {
    $parent = Split-Path (Resolve-Path $Package).Path -Parent
    if (Test-Path (Join-Path $parent 'Bin\xppbp.exe')) {
        $PackagesRoot = $parent
    } else {
        foreach ($drive in 'J', 'K', 'C', 'D', 'E', 'F', 'G', 'I') {
            $candidate = "${drive}:\AosService\PackagesLocalDirectory"
            if (Test-Path (Join-Path $candidate 'Bin\xppbp.exe')) { $PackagesRoot = $candidate; break }
        }
    }
}
$xppbp = Join-Path $PackagesRoot 'Bin\xppbp.exe'
if (-not (Test-Path $xppbp)) { Write-Error "xppbp.exe not found under '$PackagesRoot'. Pass -PackagesRoot."; exit 2 }

$selectors = @($Targets | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($selectors.Count -eq 0) { $selectors = @('-all') }

$common = @("-metadata:$PackagesRoot", "-module:$module", "-model:$model",
            "-compilerMetadata:$PackagesRoot", "-packagesRoot:$PackagesRoot")

"xppbp: $xppbp"
"module: $module   model: $model   targets: $($selectors -join ', ')"
$totalWarnings = 0; $totalErrors = 0; $notChecked = @()

foreach ($target in $selectors) {
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $lines = @(& $xppbp @common $target 2>&1 | ForEach-Object { "$_" })
    $code = $LASTEXITCODE
    ""
    "===== $target  (exit $code, $([math]::Round($timer.Elapsed.TotalSeconds, 1)) s)"
    $lines | Where-Object { $_ -notmatch '^\s*$' -and $_ -notmatch '^Memory usage' }

    $text = $lines -join "`n"
    $processed = if ($text -match '(\d+) elements processed') { [int]$Matches[1] } else { 0 }
    if ($text -match 'Warnings: (\d+)') { $totalWarnings += [int]$Matches[1] }
    if ($text -match 'Errors: (\d+)') { $totalErrors += [int]$Matches[1] }
    if ($processed -eq 0 -or $text -match 'ModuleNotFound|ItemNotFound|does not exist|could not be found') {
        "NOT CHECKED: xppbp evaluated no element for $target. This is not a clean result."
        $notChecked += $target
    }
}

""
"TOTAL: $totalWarnings warning(s), $totalErrors error(s), $($selectors.Count - $notChecked.Count) of $($selectors.Count) target(s) checked"
if ($notChecked.Count -gt 0) { exit 2 }
if ($totalErrors -gt 0) { exit 1 }
exit 0
