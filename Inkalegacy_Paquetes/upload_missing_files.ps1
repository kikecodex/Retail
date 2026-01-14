
$ftpHost = "ftp.inkalegacy.com"
$user = "inkalegacy"
$pass = "eCanEipRWaQHz54U"

$filesToUpload = @(
    @{ Local = "scripts\agent_integration.js"; Remote = "/public_html/scripts/agent_integration.js" },
    @{ Local = "Imagenes\llamita.png"; Remote = "/public_html/Imagenes/llamita.png" }
)

$webclient = New-Object System.Net.WebClient
$webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)

foreach ($file in $filesToUpload) {
    $localPath = Join-Path (Get-Location) $file.Local
    $remoteUrl = "ftp://$ftpHost$($file.Remote)"
    
    Write-Host "Subiendo $($file.Local) a $remoteUrl..."
    
    try {
        $webclient.UploadFile($remoteUrl, "STOR", $localPath)
        Write-Host "Subida exitosa: $($file.Local)"
    } catch {
        Write-Error "Error subiendo $($file.Local): $_"
    }
}
