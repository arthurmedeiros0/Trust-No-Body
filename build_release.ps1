$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$buildRoot = Join-Path $env:TEMP ("tnb_release_" + $PID)
$stage = Join-Path $buildRoot 'assets'
$dist = Join-Path $buildRoot 'dist'
$work = Join-Path $buildRoot 'work'
$spec = Join-Path $buildRoot 'spec'
$release = Join-Path $projectRoot 'release'

New-Item -ItemType Directory -Force -Path $stage, $dist, $work, $spec, $release | Out-Null
foreach ($folder in 'cenarios', 'colisoes', 'dados', 'logo') {
    Copy-Item -LiteralPath (Join-Path $projectRoot $folder) -Destination $stage -Recurse
}
# Essas cópias permanecem no repositório como originais históricos.
foreach ($relative in @('cozinha/cozinha_dia.png', 'cozinha/cozinha_noite.png',
                        'entrada/entrada_dia.png', 'entrada/entrada_noite.png',
                        'olho_magico/Rua Deserta ao Entardecer.png',
                        'olho_magico/Rua Suburbana Sob o Luar.png')) {
    Remove-Item -LiteralPath (Join-Path (Join-Path $stage 'cenarios') $relative)
}
New-Item -ItemType Directory -Force -Path (Join-Path $stage 'personagens') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stage 'personagens/protagonista') | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot 'personagens/protagonista/classicos') -Destination (Join-Path $stage 'personagens/protagonista') -Recurse
Copy-Item -LiteralPath (Join-Path $projectRoot 'personagens/visitantes') -Destination (Join-Path $stage 'personagens') -Recurse

# V2–V4 são saídas antigas. O carregador atual usa PROCESSING_VERSION='v7'.
$ricardo = Join-Path $stage 'personagens/visitantes/ricardo'
Get-ChildItem -LiteralPath $ricardo -File -Recurse -Filter '*.png' |
    Where-Object { $_.Name -match '_v[234]_' } |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName }

$data = @(
    "$(Join-Path $stage 'cenarios');cenarios",
    "$(Join-Path $stage 'colisoes');colisoes",
    "$(Join-Path $stage 'dados');dados",
    "$(Join-Path $stage 'logo');logo",
    "$(Join-Path $stage 'personagens');personagens"
)
$arguments = @('-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--windowed',
               '--name', 'TrustNoBody', '--hidden-import', 'logica_infeccao',
               '--distpath', $dist, '--workpath', $work, '--specpath', $spec, '--log-level', 'WARN')
foreach ($item in $data) { $arguments += @('--add-data', $item) }
$arguments += (Join-Path $projectRoot 'main.py')
& python @arguments
if ($LASTEXITCODE -ne 0) { throw 'A geração da build falhou.' }

$executable = Join-Path $dist 'TrustNoBody/TrustNoBody.exe'
$verification = Start-Process -FilePath $executable -ArgumentList '--verify-release' -WorkingDirectory $dist -WindowStyle Hidden -PassThru -Wait
if ($verification.ExitCode -ne 0) { throw 'A verificação dos recursos da build falhou.' }

$archive = Join-Path $release 'TrustNoBody-Windows.zip'
Compress-Archive -LiteralPath (Join-Path $dist 'TrustNoBody') -DestinationPath $archive -Force
Write-Output "Build validada: $archive"
