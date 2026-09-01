<#
.SYNOPSIS
	Copy generated locator files from the EU5 user dir into the mod.

.DESCRIPTION
	After running in-game console command 'MapObjects.GenerateGameLocators <type>',
	the game writes generated_locators_<type>.txt (or generated_map_object_locators_<type>.txt)
	into the user dir (default F:\Paradox Interactive\Europa Universalis V).
	This script finds the newest such file per locator type, validates it
	(rejects empty / all-zero-position files), backs up the current mod file,
	and copies the new file into in_game/gfx/map/map_objects/ as
	generated_map_object_locators_<type>.txt.

	NOTE: dock generation in-game is currently broken (produces all-zero positions).
	Use tools/generate_dock_locators.py instead for the dock type.

.PARAMETER UserDir
	EU5 user directory. Default: F:\Paradox Interactive\Europa Universalis V

.PARAMETER ModDir
	Mod root. Default: parent of this script's folder (tools/..)

.EXAMPLE
	powershell -NoProfile -ExecutionPolicy Bypass -File tools\update_locators.ps1
#>
param(
	[string]$UserDir = "F:\Paradox Interactive\Europa Universalis V",
	[string]$ModDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$targetDir = Join-Path $ModDir "in_game\gfx\map\map_objects"
if (-not (Test-Path $targetDir)) { throw "Target dir not found: $targetDir" }
if (-not (Test-Path $UserDir)) { throw "User dir not found: $UserDir" }

$expectedDockMin = 4000
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $targetDir "backup_$timestamp"
$report = @()

foreach ($type in @("city", "combat", "unit_stack", "vfx", "dock")) {
	$name = "generated_map_object_locators_$type.txt"
	$altName = "generated_locators_$type.txt"

	# 1) newest matching file in user dir (exclude the mod folder itself)
	$candidates = @()
	foreach ($n in @($name, $altName)) {
		$candidates += Get-ChildItem -Path $UserDir -Recurse -Filter $n -File -ErrorAction SilentlyContinue |
			Where-Object { $_.FullName -notlike "$ModDir*" }
	}
	$candidates = $candidates | Sort-Object LastWriteTime -Descending
	if (-not $candidates) {
		$report += "[SKIP] $type : no generated file found in user dir"
		Write-Host "[SKIP] $type : no generated file found in user dir" -ForegroundColor Yellow
		continue
	}
	$src = $candidates[0]

	# 2) validation
	$content = [System.IO.File]::ReadAllText($src.FullName)
	if ([string]::IsNullOrWhiteSpace($content) -or -not $content.Contains("id=")) {
		$report += "[FAIL] $type : generated file invalid: $($src.FullName)"
		Write-Host "[FAIL] $type : generated file invalid: $($src.FullName)" -ForegroundColor Red
		continue
	}
	# reject all-zero positions (known engine failure for dock)
	$nonZero = ([regex]::Matches($content, 'position=\{\s*-?[1-9]')).Count
	$posCount = ([regex]::Matches($content, 'position=\{')).Count
	if ($posCount -gt 0 -and $nonZero -eq 0) {
		$report += "[FAIL] $type : all positions are 0,0,0 (failed generation - use tools/generate_dock_locators.py for dock): $($src.FullName)"
		Write-Host "[FAIL] $type : all positions 0,0,0 - rejected" -ForegroundColor Red
		continue
	}
	if ($type -eq "dock") {
		$count = ([regex]::Matches($content, 'id=')).Count
		if ($count -lt $expectedDockMin) {
			$report += "[WARN] dock : only $count entries (expected ~4891)"
			Write-Host "[WARN] dock : only $count entries (expected ~4891)" -ForegroundColor Yellow
		}
	}

	# 3) backup current mod file
	$dst = Join-Path $targetDir $name
	if (Test-Path $dst) {
		New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
		Copy-Item -Path $dst -Destination (Join-Path $backupDir $name) -Force
	}

	# 4) copy
	Copy-Item -Path $src.FullName -Destination $dst -Force
	$report += "[DONE] $type : $($src.FullName) -> $dst"
	Write-Host "[DONE] $type : $($src.FullName)" -ForegroundColor Green
}

Write-Host ""
Write-Host "===== SUMMARY =====" -ForegroundColor Cyan
$report | ForEach-Object { Write-Host $_ }
if (Test-Path $backupDir) { Write-Host "Backup dir: $backupDir" -ForegroundColor Cyan }
Write-Host ""
Write-Host "Next: restart the game and check logs\game.log for 'incomplete' / dock messages." -ForegroundColor Cyan
