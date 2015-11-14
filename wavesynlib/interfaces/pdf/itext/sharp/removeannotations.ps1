param($source, $target)


$selfDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$itextpath = Join-Path $selfDir "itextsharp.dll" 
Add-Type -Path $itextpath

try {
  $reader  = New-Object iTextSharp.text.pdf.PdfReader($source)
  $target  = New-Object System.IO.FileStream($target, [System.IO.FileMode]'Create', [System.IO.FileAccess]'Write')
  $stamper = New-Object iTextSharp.text.pdf.PdfStamper($reader, $target)
  $reader.RemoveAnnotations()
} finally {
  if ($stamper)  {$stamper.Close()}
  if ($reader)   {$reader.Close()}
  if ($target)   {$target.Close()}
}

