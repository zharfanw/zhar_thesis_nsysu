<#
.SYNOPSIS
Exports the LaTeX thesis source to a Word document that can be uploaded to Google Docs.

.DESCRIPTION
This script uses Pandoc to convert the thesis root file into a .docx file.
The generated .docx can be opened in Microsoft Word, LibreOffice, or uploaded
to Google Drive and opened as Google Docs.

Requirements:
- Pandoc must be installed and available in PATH.
  Download: https://pandoc.org/installing.html

Optional:
- Provide a reference .docx to control Word styles:
  .\scripts\Export-LaTeXToDocs.ps1 -ReferenceDoc .\reference.docx

.EXAMPLE
.\scripts\Export-LaTeXToDocs.ps1

.EXAMPLE
.\scripts\Export-LaTeXToDocs.ps1 -InputFile .\thesis.tex -OutputFile .\exports\thesis-google-docs.docx
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$InputFile = "thesis.tex",

    [Parameter()]
    [string]$OutputFile = "exports\thesis.docx",

    [Parameter()]
    [string]$BibliographyFile = "references.bib",

    [Parameter()]
    [string]$ReferenceDoc,

    [Parameter()]
    [switch]$OpenAfterExport,

    [Parameter()]
    [switch]$KeepIntermediate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$InputPath = Resolve-Path (Join-Path $ProjectRoot $InputFile)
$OutputPath = Join-Path $ProjectRoot $OutputFile
$OutputDir = Split-Path -Parent $OutputPath
$WorkDir = Join-Path $OutputDir "pandoc-work"
$PandocInputPath = Join-Path $WorkDir ("thesis-pandoc-{0}.tex" -f $PID)

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    throw "Pandoc is not installed or not available in PATH. Install it from https://pandoc.org/installing.html, then run this script again."
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

if (-not (Test-Path $WorkDir)) {
    New-Item -ItemType Directory -Path $WorkDir | Out-Null
}

function Resolve-TexIncludePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseDirectory,

        [Parameter(Mandatory = $true)]
        [string]$IncludeName
    )

    $Candidate = Join-Path $BaseDirectory $IncludeName
    if (Test-Path $Candidate) {
        return (Resolve-Path $Candidate).Path
    }

    if (-not [System.IO.Path]::HasExtension($Candidate)) {
        $CandidateWithExtension = "$Candidate.tex"
        if (Test-Path $CandidateWithExtension) {
            return (Resolve-Path $CandidateWithExtension).Path
        }
    }

    return $null
}

function Resolve-ImagePathForPandoc {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ImageName
    )

    if ([System.IO.Path]::IsPathRooted($ImageName) -or $ImageName -match '[/\\]') {
        return ($ImageName -replace '\\', '/')
    }

    $ImageDir = Join-Path $ProjectRoot "Images"
    $KnownExtensions = @(".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
    $ImageCandidates = @()

    if ([System.IO.Path]::HasExtension($ImageName)) {
        $ImageCandidates += Join-Path $ImageDir $ImageName
    }
    else {
        foreach ($Extension in $KnownExtensions) {
            $ImageCandidates += Join-Path $ImageDir "$ImageName$Extension"
        }
    }

    foreach ($Candidate in $ImageCandidates) {
        if (Test-Path $Candidate) {
            $RelativePath = Resolve-Path -Relative $Candidate
            return ($RelativePath -replace '^\.[/\\]', '' -replace '\\', '/')
        }
    }

    return ($ImageName -replace '\\', '/')
}

function Convert-LatexForPandoc {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.HashSet[string]]$VisitedFiles
    )

    $ResolvedPath = (Resolve-Path $Path).Path
    if ($VisitedFiles.Contains($ResolvedPath)) {
        return ""
    }
    [void]$VisitedFiles.Add($ResolvedPath)

    $Source = Get-Content -Raw -Encoding UTF8 -LiteralPath $ResolvedPath
    $BaseDirectory = Split-Path -Parent $ResolvedPath

    $Source = [regex]::Replace(
        $Source,
        '\\(?:input|include)\s*\{([^}]+)\}',
        {
            param($Match)

            $IncludePath = Resolve-TexIncludePath -BaseDirectory $BaseDirectory -IncludeName $Match.Groups[1].Value
            if ($IncludePath) {
                return Convert-LatexForPandoc -Path $IncludePath -VisitedFiles $VisitedFiles
            }

            return $Match.Value
        }
    )

    # Pandoc misses images wrapped only by \centerline, even though LaTeX accepts it.
    $Source = [regex]::Replace(
        $Source,
        '\\centerline\s*\{\s*(\\includegraphics(?:\[[^\]]*\])?\{[^}]+\})\s*\}',
        "\begin{center}`n`$1`n\end{center}"
    )

    # Background watermarks are page decoration in PDF output and usually hide/vanish in DOCX.
    $Source = [regex]::Replace($Source, '\\BackImage(?:\[[^\]]*\])?\{[^}]+\}', '')

    $Source = [regex]::Replace(
        $Source,
        '\\includegraphics(\[[^\]]*\])?\{([^}]+)\}',
        {
            param($Match)

            $Options = $Match.Groups[1].Value
            $ImagePath = Resolve-ImagePathForPandoc -ImageName $Match.Groups[2].Value
            return "\includegraphics$Options{$ImagePath}"
        }
    )

    # The template uses display math to align cover-page identity text. DOCX/Google Docs
    # handles that more reliably as regular text, while real equations remain math.
    $Source = [regex]::Replace(
        $Source,
        '(?s)\\\[\s*\\begin\{aligned\}\s*(.*?)\s*\\end\{aligned\}\s*\\\]',
        {
            param($Match)

            $Lines = $Match.Groups[1].Value -split '\\\\'
            $ConvertedLines = foreach ($Line in $Lines) {
                $CleanLine = $Line.Trim()
                if (-not $CleanLine) {
                    continue
                }

                $CleanLine = $CleanLine -replace '&', ''
                $CleanLine = $CleanLine -replace '\\quad', ' '
                do {
                    $BeforeCleanLine = $CleanLine
                    $CleanLine = $CleanLine -replace '\\zh\s*\{([^{}]*)\}', '$1'
                    $CleanLine = $CleanLine -replace '\\text\s*\{([^{}]*)\}', '$1'
                } while ($CleanLine -ne $BeforeCleanLine)
                $CleanLine.Trim()
            }

            return (($ConvertedLines -join "`n`n") + "`n")
        }
    )

    do {
        $Before = $Source
        $Source = [regex]::Replace($Source, '\\zh\s*\{([^{}]*)\}', '$1')
    } while ($Source -ne $Before)

    return $Source
}

$VisitedFiles = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$PandocSource = Convert-LatexForPandoc -Path $InputPath -VisitedFiles $VisitedFiles
Set-Content -LiteralPath $PandocInputPath -Value $PandocSource -Encoding UTF8

$PathSeparator = [System.IO.Path]::PathSeparator
$ResourcePath = @(
    $ProjectRoot.Path,
    (Join-Path $ProjectRoot "Images"),
    (Join-Path $ProjectRoot "Chapters")
) -join $PathSeparator

$PandocArgs = @(
    $PandocInputPath,
    "--from=latex",
    "--to=docx",
    "--standalone",
    "--output=$OutputPath",
    "--resource-path=$ResourcePath",
    "--metadata=link-citations=true"
)

$BibliographyPath = Join-Path $ProjectRoot $BibliographyFile
if (Test-Path $BibliographyPath) {
    $PandocArgs += @(
        "--citeproc",
        "--bibliography=$BibliographyPath"
    )
}

if ($ReferenceDoc) {
    $ReferenceDocPath = Resolve-Path (Join-Path $ProjectRoot $ReferenceDoc)
    $PandocArgs += "--reference-doc=$ReferenceDocPath"
}

Write-Host "Exporting LaTeX to DOCX..."
Write-Host "Input : $InputPath"
Write-Host "Pandoc input: $PandocInputPath"
Write-Host "Output: $OutputPath"

Push-Location $ProjectRoot
try {
    & pandoc @PandocArgs
}
finally {
    Pop-Location
}

$PandocExitCodeVariable = Get-Variable -Name LASTEXITCODE -ErrorAction SilentlyContinue
$PandocExitCode = if ($PandocExitCodeVariable) { $PandocExitCodeVariable.Value } else { 0 }
if ($PandocExitCode -ne 0) {
    throw "Pandoc export failed with exit code $PandocExitCode."
}

Write-Host "Done. Upload this DOCX to Google Drive and open it with Google Docs:"
Write-Host $OutputPath

if (-not $KeepIntermediate) {
    Remove-Item -LiteralPath $PandocInputPath -Force -ErrorAction SilentlyContinue
}

if ($OpenAfterExport) {
    Start-Process -FilePath $OutputPath
}
