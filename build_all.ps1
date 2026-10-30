$py = ".\.venv\Scripts\python.exe"
& $py schema\make_samples.py
& $py schema\validate.py
if ($LASTEXITCODE -ne 0) { Write-Host "validation failed"; exit 1 }

New-Item -ItemType Directory -Force out, web\models | Out-Null
Remove-Item out\cube.glb -ErrorAction SilentlyContinue

Get-ChildItem schema\samples\*.json | ForEach-Object {
  $n = $_.BaseName
  docker run --rm -v "${PWD}/schema/samples:/in" -v "${PWD}/out:/out" -v "${PWD}/builder:/app" zerobrick-builder blender -b -P /app/build.py -- "/in/${n}.json" "/out/${n}.glb"
}

Copy-Item out\*.glb web\models\ -Force
ConvertTo-Json -InputObject @(Get-ChildItem web\models\*.glb | ForEach-Object { $_.Name }) | Set-Content web\models\index.json
Write-Host "done. now: cd web; python -m http.server 8000"