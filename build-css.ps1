# Build Tailwind CSS (no Node.js required)
# Uses standalone tailwindcss.exe from project root
$exe = Join-Path $PSScriptRoot "tailwindcss.exe"
$input = Join-Path $PSScriptRoot "static\css\input.css"
$output = Join-Path $PSScriptRoot "static\css\tailwind.css"

if (-not (Test-Path $exe)) {
    Write-Host "tailwindcss.exe not found. Download from:"
    Write-Host "https://github.com/tailwindlabs/tailwindcss/releases/latest"
    Write-Host "Save as tailwindcss.exe in project root."
    exit 1
}

& $exe -i $input -o $output --minify
Write-Host "Built: $output"
