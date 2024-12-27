<#
.SYNOPSIS
    Automatyzuje budowę, publikację, wdrożenie, uruchomienie i utylizację narzędzia diagnostycznego KubeDiag Toolkit w Kubernetes.

.DESCRIPTION
    Ten skrypt PowerShell umożliwia:
    1. Budowę obrazu Docker z narzędziami diagnostycznymi.
    2. Tagowanie i publikację obrazu na lokalny rejestr Docker.
    3. Wdrożenie obrazu na klaster Kubernetes.
    4. Uruchomienie interaktywnej sesji w pod diagnostycznym.
    5. Utylizację zasobów Kubernetes oraz lokalnych obrazów Docker.

.NOTES
    Autor: d2i4
    Data: 2024-04-27
#>

# ================================
# Konfiguracja Skryptu
# ================================

# Ustawienia Docker
$dockerImageName = "kubediag-toolkit"
$dockerImageTag = "latest"
$localRegistry = "localhost:5000"
$fullImageName = "{0}/{1}:{2}" -f $localRegistry, $dockerImageName, $dockerImageTag

# Pliki YAML Kubernetes
$deploymentFileTemplate = "diagnostic-deployment-template.yaml"
$deploymentFile = "diagnostic-deployment.yaml"
$serviceFileTemplate = "diagnostic-service-template.yaml"
$serviceFile = "diagnostic-service.yaml"

# Ustawienia Podów
$kubeLabelSelector = "app=kubediag"

# Ścieżki do plików
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition
$deploymentFileTemplatePath = Join-Path $scriptDirectory $deploymentFileTemplate
$serviceFileTemplatePath = Join-Path $scriptDirectory $serviceFileTemplate
$deploymentFilePath = Join-Path $scriptDirectory $deploymentFile
$serviceFilePath = Join-Path $scriptDirectory $serviceFile

# ================================
# Funkcje Skryptu
# ================================

function Build-DockerImage {
    Write-Host "Budowanie obrazu Docker: $dockerImageName ..." -ForegroundColor Cyan
    try {
        docker build -t $dockerImageName .
        if ($LASTEXITCODE -ne 0) {
            Throw "Błąd podczas budowania obrazu Docker."
        }
        Write-Host "Obraz Docker '$dockerImageName' zbudowany pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error $_
        exit 1
    }
}

function Push-DockerImage {
    Write-Host "Tagowanie obrazu Docker..." -ForegroundColor Cyan
    try {
        docker tag $dockerImageName $fullImageName
        Write-Host "Obraz oznaczony jako '$fullImageName'." -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas tagowania obrazu Docker: $_"
        exit 1
    }

    Write-Host "Pushowanie obrazu Docker do lokalnego rejestru..." -ForegroundColor Cyan
    try {
        docker push $fullImageName
        if ($LASTEXITCODE -ne 0) {
            Throw "Błąd podczas pushowania obrazu Docker."
        }
        Write-Host "Obraz Docker '$fullImageName' wypchnięty pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error $_
        exit 1
    }
}

function Deploy-Kubernetes {
    Write-Host "Aktualizacja plików YAML z pełną nazwą obrazu..." -ForegroundColor Cyan
    try {
        # Aktualizacja Deployment YAML
        (Get-Content $deploymentFileTemplatePath) -replace "<IMAGE_NAME>", $fullImageName | Set-Content $deploymentFilePath
        Write-Host "Plik Deployment zaktualizowany: $deploymentFilePath" -ForegroundColor Green

        # Aktualizacja Service YAML (jeśli potrzebne)
        (Get-Content $serviceFileTemplatePath) -replace "<SERVICE_NAME>", "kubediag-service" | Set-Content $serviceFilePath
        Write-Host "Plik Service zaktualizowany: $serviceFilePath" -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas aktualizacji plików YAML: $_"
        exit 1
    }

    Write-Host "Wdrażanie Deployment na Kubernetes..." -ForegroundColor Cyan
    try {
        kubectl apply -f $deploymentFilePath
        Write-Host "Deployment wdrożony pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas wdrażania Deployment: $_"
        exit 1
    }

    Write-Host "Wdrażanie Service na Kubernetes..." -ForegroundColor Cyan
    try {
        kubectl apply -f $serviceFilePath
        Write-Host "Service wdrożony pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas wdrażania Service: $_"
        exit 1
    }
}

function Run-DiagnosticPod {
    Write-Host "Uruchamianie poda diagnostycznego..." -ForegroundColor Cyan
    try {
        $podName = kubectl get pods -l $kubeLabelSelector -o jsonpath="{.items[0].metadata.name}"
        if (-not $podName) {
            Throw "Nie znaleziono poda diagnostycznego. Upewnij się, że Deployment jest wdrożony."
        }
        Write-Host "Pod znaleziony: $podName" -ForegroundColor Green
        kubectl exec -it $podName -- /bin/bash
    }
    catch {
        Write-Error "Błąd podczas uruchamiania poda diagnostycznego: $_"
        exit 1
    }
}

function Cleanup-Kubernetes {
    Write-Host "Usuwanie Deployment i Service z Kubernetes..." -ForegroundColor Cyan
    try {
        kubectl delete -f $deploymentFilePath -f $serviceFilePath
        Write-Host "Deployment i Service usunięte pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas usuwania zasobów Kubernetes: $_"
    }
}

function Cleanup-DockerImage {
    Write-Host "Usuwanie lokalnych obrazów Docker..." -ForegroundColor Cyan
    try {
        docker rmi $dockerImageName -f
        docker rmi $fullImageName -f
        Write-Host "Obrazy Docker usunięte pomyślnie." -ForegroundColor Green
    }
    catch {
        Write-Error "Błąd podczas usuwania obrazów Docker: $_"
    }
}

function Show-Menu {
    Clear-Host
    Write-Host "=============================" -ForegroundColor Yellow
    Write-Host "     KubeDiag Toolkit Menu    " -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Yellow
    Write-Host "1. Buduj i wypchnij obraz Docker"
    Write-Host "2. Wdróż na Kubernetes"
    Write-Host "3. Uruchom pod diagnostyczny"
    Write-Host "4. Utylizuj zasoby"
    Write-Host "5. Wyjście"
}

# ================================
# Menu Główne Skryptu
# ================================

while ($true) {
    Show-Menu
    $choice = Read-Host "Wybierz opcję (1-5)"

    switch ($choice) {
        "1" {
            Build-DockerImage
            Push-DockerImage
            Pause
        }
        "2" {
            Deploy-Kubernetes
            Pause
        }
        "3" {
            Run-DiagnosticPod
            Pause
        }
        "4" {
            Cleanup-Kubernetes
            Cleanup-DockerImage
            Pause
        }
        "5" {
            Write-Host "Zamykanie skryptu." -ForegroundColor Green
            break
        }
        default {
            Write-Host "Nieprawidłowy wybór. Spróbuj ponownie." -ForegroundColor Red
            Pause
        }
    }
}
