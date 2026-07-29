param($ScriptsDir, $OutputFile)

$chains = @{}

Get-ChildItem $ScriptsDir -Filter "*ep0*.py" | Where-Object { $_.Name -notmatch "debug|fix|inspect" } | ForEach-Object {
    Write-Host "Processing: $($_.Name)"
    $content = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    
    # Split by "chain_id" to get individual chain blocks
    $blocks = $content -split '"chain_id":\s*"' | Select-Object -Skip 1
    
    foreach ($block in $blocks) {
        # chain_id is at the start until next quote
        if ($block -match '^([^"]+)"') {
            $chainId = $Matches[1]
        } else { continue }
        
        # chain_title
        $chainTitle = ""
        if ($block -match '"chain_title":\s*"([^"]+)"') {
            $chainTitle = $Matches[1]
        }
        
        # narrative - find """ ... """
        if ($block -match '"narrative":\s*"""\s*([\s\S]*?)""",') {
            $narrative = $Matches[1].Trim()
        } else {
            $narrative = ""
        }
        
        if ($chainId -and $narrative) {
            $chains[$chainId] = @{
                chain_id = $chainId
                chain_title = $chainTitle
                narrative = $narrative
            }
            Write-Host "  $chainId ($chainTitle): $($narrative.Length) chars"
        }
    }
}

$result = @($chains.Values)
Write-Host "`nTotal: $($result.Count) chains"

$json = ConvertTo-Json -InputObject $result -Depth 3 -Compress
[System.IO.File]::WriteAllText($OutputFile, $json, [System.Text.Encoding]::UTF8)
Write-Host "Written: $OutputFile ($([math]::Round((Get-Item $OutputFile).Length/1024,1))KB)"
