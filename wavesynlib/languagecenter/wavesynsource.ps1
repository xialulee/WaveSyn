$command = $args[0] + " --outlang=json"

for ($k=1; $k -lt $args.Count; $k++) {
    $command += " " + $args[$k]
}

Invoke-Expression $command | ConvertFrom-Json