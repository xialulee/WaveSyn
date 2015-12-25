param($srcContent, $srcBookmark, $target)


$selfDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$itextpath = Join-Path $selfDir "itextsharp.dll" 
Add-Type -Path $itextpath

try {
  $readerC  = New-Object iTextSharp.text.pdf.PdfReader($srcContent)
  $readerB  = New-Object iTextSharp.text.pdf.PdfReader($srcBookmark)
  $bookmark = [iTextSharp.text.pdf.SimpleBookmark]::GetBookmark($readerB)
  $target   = New-Object System.IO.FileStream($target, [System.IO.FileMode]'Create', [System.IO.FileAccess]'Write')
  $stamper  = New-Object iTextSharp.text.pdf.PdfStamper($readerC, $target)
  $stamper.Outlines = $bookmark
} finally {
  if ($stamper)  {$stamper.Close()}
  if ($readerB)  {$readerB.Close()}
  if ($readerC)  {$readerC.Close()}
  if ($target)   {$target.Close()}
}