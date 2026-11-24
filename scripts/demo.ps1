param(
    [string]$Repository = ".benchmark/click-full",
    [string]$Database = ".repoguard/demo.sqlite",
    [string]$Base = "HEAD~1",
    [string]$Target = "HEAD"
)
$ErrorActionPreference = "Stop"
$Tool = Join-Path $PSScriptRoot "..\.venv\Scripts\repoguard.exe"
& $Tool --repo $Repository --db $Database index --base $Base --target $Target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Tool --repo $Repository --db $Database definition click.formatting.iter_rows --target $Target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Tool --repo $Repository --db $Database plan click.formatting.iter_rows aligned_rows --target $Target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Tool --repo $Repository --db $Database impact $Base $Target --format markdown
exit $LASTEXITCODE
