param($source, $executable, $refAsm="")

# usage: .\cscompiler.ps1 cscode.cs cscode.exe System.Windows.Forms.dll

Add-Type -AssemblyName Microsoft*CSharp

if ($refAsm -ne "") {$refList = $refAsm.Split(";")} 

$params = New-Object System.CodeDom.Compiler.CompilerParameters
$params.GenerateExecutable = $true
$params.OutputAssembly = $executable
if ($refAsm) {
  $refList | foreach {$params.ReferencedAssemblies.Add($_)}
}

$code = cat $source

$provider = New-Object Microsoft.CSharp.CSharpCodeProvider
$provider.CompileAssemblyFromSource($params, $code)