$json_args = ConvertTo-Json $args
$byte_str = [System.Text.Encoding]::Unicode.GetBytes($json_args) -Join ' '
$input | wscallusingjsonargs.py $byte_str


