# Build main.pdf.
#
# Figure PDFs are gitignored (*.pdf), so on a fresh clone they must be
# regenerated from the committed SVGs before LaTeX runs.
#
# Usage:  .\build.ps1          build
#         .\build.ps1 -Clean   remove aux files first

param([switch]$Clean)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$miktex = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
if (Test-Path $miktex) { $env:Path = "$miktex;$env:Path" }

$inkscape = "$env:ProgramFiles\Inkscape\bin\inkscape.exe"

# Regenerate any figure PDF that is missing or older than its SVG source.
if (Test-Path $inkscape) {
    foreach ($svg in Get-ChildItem -Recurse -Filter *.svg images) {
        $pdf = [IO.Path]::ChangeExtension($svg.FullName, 'pdf')
        if (-not (Test-Path $pdf) -or (Get-Item $pdf).LastWriteTime -lt $svg.LastWriteTime) {
            Write-Host "svg -> pdf: $($svg.Name)"
            & $inkscape --export-type=pdf --export-filename=$pdf $svg.FullName | Out-Null
        }
    }
} else {
    Write-Warning "Inkscape not found at $inkscape - skipping SVG conversion."
}

# These have no source in the repo (no SVG, and make_component_figure.py cannot
# rebuild them without the gitignored CSV data). They are currently red
# PLACEHOLDER pages - copy the real files in before circulating the PDF.
$placeholders = 'images/3arm.pdf', 'images/LISAarm-analysis.pdf', 'images/FDM.png'
$missing = $placeholders | Where-Object { -not (Test-Path $_) }
if ($missing) { Write-Warning "Figure(s) absent, LaTeX will fail: $($missing -join ', ')" }
else { Write-Warning "Using placeholder figures: $($placeholders -join ', ')" }

if ($Clean) { latexmk -C main.tex | Out-Null }

# latexmk runs pdflatex/bibtex as many times as needed.
latexmk -pdf -interaction=nonstopmode -file-line-error main.tex

if (Test-Path main.pdf) { Write-Host "`nBuilt: $(Resolve-Path main.pdf)" }
