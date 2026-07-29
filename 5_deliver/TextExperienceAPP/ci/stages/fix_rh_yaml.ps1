$path = 'D:\6_agent_project\omas\pdt_registry\HDT-001-RH\pdt.yaml'
$bytes = [System.IO.File]::ReadAllBytes($path)
# Byte 166 should be 0x8F (completing 式 = E5 BC 8F), currently 0x3F
$bytes[166] = 0x8F
[System.IO.File]::WriteAllBytes($path, $bytes)
Write-Host 'Fixed byte 166: 0x3F -> 0x8F'
