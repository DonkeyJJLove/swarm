# KubeDiag Toolkit

**KubeDiag Toolkit** to zaawansowane narzędzie diagnostyczne zaprojektowane do pracy w środowisku Kubernetes. Umożliwia administratorom i inżynierom DevOps monitorowanie, diagnozowanie oraz rozwiązywanie problemów sieciowych i aplikacyjnych w klastrze Kubernetes przy użyciu zestawu narzędzi pentesterskich i diagnostycznych.

Ten samouczek przeprowadzi Cię przez cały proces konfiguracji lokalnego rejestru Docker, budowania obrazu diagnostycznego, wdrażania go na Kubernetes oraz zaawansowanego użytkowania narzędzia diagnostycznego. Skoncentrujemy się na środowisku Windows z użyciem PowerShell.

---

## Spis Treści

1. [Wymagania Wstępne](#1-wymagania-wstępne)
2. [Konfiguracja Lokalnego Rejestru Docker](#2-konfiguracja-lokalnego-rejestru-docker)
3. [Struktura Projektu KubeDiag Toolkit](#3-struktura-projektu-kubediag-toolkit)
4. [Budowanie i Publikacja Obrazu Docker](#4-budowanie-i-publikacja-obrazu-docker)
5. [Konfiguracja Kubernetes do Korzystania z Lokalnego Rejestru](#5-konfiguracja-kubernetes-do-korzystania-z-lokalnego-rejestru)
6. [Wdrożenie KubeDiag Toolkit na Kubernetes](#6-wdro%C5%BCenie-kubediag-toolkit-na-kubernetes)
7. [Uruchamianie i Korzystanie z Poda Diagnostycznego](#7-uruchamianie-i-korzystanie-z-poda-diagnostycznego)
8. [Zaawansowane Użycie KubeDiag Toolkit](#8-zaawansowane-u%C5%BCycie-kubediag-toolkit)
9. [Diagnostyka Samego KubeDiag Toolkit](#9-diagnostyka-samego-kubediag-toolkit)
10. [Utylizacja Zasobów](#10-utylizacja-zasob%C3%B3w)
11. [Najlepsze Praktyki i Rekomendacje](#11-najlepsze-praktyki-i-rekomendacje)
12. [Podsumowanie](#12-podsumowanie)
13. [Załączniki](#13-za%C5%82%C4%85czniki)
14. [Instrukcja Użycia KubeDiag Toolkit](#14-instrukcja-u%C5%BCycia-kubediag-toolkit)
15. [Przykładowe Polecenia Diagnostyczne](#15-przyk%C5%82adowe-polecenia-diagnostyczne)
16. [Rozszerzenia i Przyszła Rozbudowa](#16-rozszerzenia-i-przysz%C5%82a-rozbudowa)
17. [Dodatkowe Zasoby](#17-dodatkowe-zasoby)

---

## 1. Wymagania Wstępne

Przed rozpoczęciem upewnij się, że posiadasz następujące narzędzia i uprawnienia:

- **Docker Desktop dla Windows:** [Pobierz i zainstaluj](https://www.docker.com/products/docker-desktop)
- **Kubernetes CLI (kubectl):** Zainstalowany i skonfigurowany do komunikacji z Twoim klastrem Kubernetes. [Instrukcje instalacji](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **PowerShell:** Zainstalowany na Twoim systemie (najlepiej wersja 5.1 lub nowsza).
- **Konto Docker Hub:** Potrzebne do publikacji obrazu Docker (możesz zarejestrować się [tutaj](https://hub.docker.com/signup)).
- **Uprawnienia Administratora:** Potrzebne do wykonywania operacji na klastrze Kubernetes.

---

## 2. Konfiguracja Lokalnego Rejestru Docker

### a. Uruchomienie Lokalnego Rejestru Docker na Porcie `5000`

Lokalny rejestr Docker umożliwia przechowywanie i zarządzanie obrazami Docker w Twojej sieci lokalnej. Poniżej znajdziesz kroki do jego skonfigurowania.

1. **Otwórz PowerShell jako Administrator:**

   Kliknij prawym przyciskiem myszy na ikonie PowerShell i wybierz "Uruchom jako administrator".

2. **Uruchom Lokalny Rejestr Docker:**

   Wprowadź poniższe polecenie, aby uruchomić kontener rejestru Docker na porcie `5000`:

   ```powershell
   docker run -d -p 5000:5000 --restart always --name local-registry registry:2
   ```

   **Wyjaśnienie:**
   - `-d`: Uruchamia kontener w tle.
   - `-p 5000:5000`: Mapuje port 5000 hosta na port 5000 kontenera.
   - `--restart always`: Automatycznie restartuje kontener po restarcie systemu.
   - `--name local-registry`: Nadaje kontenerowi nazwę `local-registry`.
   - `registry:2`: Używa oficjalnego obrazu rejestru Docker w wersji 2.

3. **Sprawdzenie Statusu Kontenera Rejestru:**

   Aby upewnić się, że rejestr działa poprawnie, wykonaj:

   ```powershell
   docker ps
   ```

   **Oczekiwany wynik:**

   ```
   CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                    NAMES
   abc123def456   registry:2     "/entrypoint.sh /etc…"   2 minutes ago    Up 2 minutes    0.0.0.0:5000->5000/tcp   local-registry
   ```

4. **Testowanie Dostępności Rejestru:**

   Użyj narzędzia `curl` do sprawdzenia, czy rejestr jest dostępny:

   ```powershell
   curl http://localhost:5000/v2/_catalog
   ```

   **Oczekiwany wynik:**

   ```json
   {
     "repositories": []
   }
   ```

   Jeśli otrzymujesz ten wynik, oznacza to, że rejestr działa poprawnie.

### b. Diagnostyka Problemów z Lokalnym Rejestrem Docker

Jeśli napotkasz na problemy z dostępnością rejestru, wykonaj poniższe kroki diagnostyczne.

#### i. Sprawdzenie Logów Kontenera Rejestru Docker

```powershell
docker logs local-registry
```

**Co sprawdzić:**
- Czy pojawiają się błędy lub ostrzeżenia?
- Czy rejestr wskazuje, że nasłuchuje na porcie `5000`?

**Przykładowe logi:**

```
time="2024-04-27T10:00:00Z" level=info msg="starting registry ..."
time="2024-04-27T10:00:01Z" level=info msg="listening on [::]:5000"
```

#### ii. Sprawdzenie Użycia Portu 5000

Upewnij się, że port `5000` jest otwarty i nasłuchuje.

**Użycie PowerShell:**

```powershell
Get-NetTCPConnection -LocalPort 5000
```

**Użycie netstat:**

```powershell
netstat -ano | findstr :5000
```

**Co sprawdzić:**
- Czy port `5000` jest w stanie `LISTENING`?
- Który proces (PID) używa tego portu? Powinien to być proces związany z Docker.

#### iii. Sprawdzenie Firewall Windows

Upewnij się, że zapora systemu Windows nie blokuje portu `5000`.

1. **Otwórz Panel Sterowania**.
2. Przejdź do **System i zabezpieczenia** > **Zapora systemu Windows Defender**.
3. Kliknij **Zaawansowane ustawienia**.
4. W **Regułach przychodzących** dodaj nową regułę:
   - **Typ reguły:** Port
   - **Protokół i porty:** TCP, port 5000
   - **Działanie:** Zezwól na połączenie
   - **Profil:** Wszystkie (Domena, Prywatny, Publiczny)
   - **Nazwa reguły:** Docker Registry Port 5000

---

## 3. Struktura Projektu KubeDiag Toolkit

Upewnij się, że Twoja struktura katalogów wygląda następująco:

```
C:.
├── Dockerfile
├── diagnostic-deployment-template.yaml
├── diagnostic-deployment.yaml
├── diagnostic-service-template.yaml
├── diagnostic-service.yaml
├── diagnostic_logic.py
├── requirements.txt
└── deploy_diagnostic.ps1
```

**Opis plików:**

- `Dockerfile`: Definicja obrazu Docker z narzędziami diagnostycznymi.
- `diagnostic-deployment-template.yaml`: Szablon YAML dla Deployment w Kubernetes z placeholderami.
- `diagnostic-deployment.yaml`: Wygenerowany plik YAML Deployment.
- `diagnostic-service-template.yaml`: Szablon YAML dla Service w Kubernetes z placeholderami.
- `diagnostic-service.yaml`: Wygenerowany plik YAML Service.
- `diagnostic_logic.py`: Skrypt Python oferujący interfejs do uruchamiania narzędzi diagnostycznych.
- `requirements.txt`: Lista zależności Pythona.
- `deploy_diagnostic.ps1`: Skrypt PowerShell automatyzujący proces budowy, publikacji, wdrożenia i utylizacji.

---

## 4. Budowanie i Publikacja Obrazu Docker

### a. Budowanie Obrazu Docker

Korzystając z lokalnego rejestru Docker, zbudujmy obraz diagnostyczny i wypchnijmy go do rejestru.

1. **Otwórz PowerShell** w katalogu zawierającym `Dockerfile` i inne pliki projektu.

2. **Uruchom skrypt PowerShell:**

   ```powershell
   ./deploy_diagnostic.ps1
   ```

3. **Wybierz opcję budowania i pushowania obrazu Docker:**

   - W menu wpisz `1` i naciśnij `Enter`.
   - Skrypt wykona następujące kroki:
     - Zbuduje obraz Docker nazwany `kubediag-toolkit`.
     - Oznaczy obraz pełną nazwą z lokalnego rejestru (`localhost:5000/kubediag-toolkit:latest`).
     - Wypchnie obraz do lokalnego rejestru Docker.

**Przykładowy wynik:**

```
Budowanie obrazu Docker: kubediag-toolkit ... 
Sending build context to Docker daemon  4.096kB
Step 1/14 : FROM debian:bullseye-slim
 ---> a1b2c3d4e5f6
...
Successfully built f6e5d4c3b2a1
Successfully tagged kubediag-toolkit:latest
Tagowanie obrazu Docker...
Obraz oznaczony jako 'localhost:5000/kubediag-toolkit:latest'.
Pushowanie obrazu Docker do lokalnego rejestru...
The push refers to repository [localhost:5000/kubediag-toolkit]
f6e5d4c3b2a1: Pushed
...
latest: digest: sha256:abcdef1234567890 size: 1234
Obraz Docker 'localhost:5000/kubediag-toolkit:latest' wypchnięty pomyślnie.
```

### b. Ręczne Budowanie i Pushowanie Obrazu (Opcjonalnie)

Jeśli chcesz wykonać te kroki ręcznie, wykonaj poniższe polecenia.

1. **Budowanie obrazu:**

   ```powershell
   docker build -t kubediag-toolkit .
   ```

2. **Tagowanie obrazu:**

   ```powershell
   docker tag kubediag-toolkit localhost:5000/kubediag-toolkit:latest
   ```

3. **Pushowanie obrazu do lokalnego rejestru:**

   ```powershell
   docker push localhost:5000/kubediag-toolkit:latest
   ```

**Oczekiwany wynik:**

Powinieneś zobaczyć komunikaty potwierdzające przesyłanie warstw obrazu.

### c. Weryfikacja Wypchniętego Obrazu

Sprawdź, czy obraz został poprawnie przesłany do rejestru:

```powershell
curl http://localhost:5000/v2/_catalog
```

**Oczekiwany wynik:**

```json
{
  "repositories": [
    "kubediag-toolkit"
  ]
}
```

Możesz również sprawdzić tagi obrazu:

```powershell
curl http://localhost:5000/v2/kubediag-toolkit/tags/list
```

---

## 5. Konfiguracja Kubernetes do Korzystania z Lokalnego Rejestru

Aby Kubernetes mógł pobierać obrazy z lokalnego rejestru, musisz skonfigurować go odpowiednio.

### a. Konfiguracja Docker Desktop do Używania Lokalnego Rejestru

Jeśli używasz Docker Desktop z wbudowanym Kubernetes, wykonaj poniższe kroki:

1. **Otwórz Docker Desktop.**

2. **Przejdź do Ustawień Docker:**

   Kliknij ikonę Docker w pasku zadań, wybierz "Settings" (Ustawienia).

3. **Dodaj Lokalny Rejestr jako Niezabezpieczony:**

   - Przejdź do sekcji **Docker Engine**.
   - Dodaj konfigurację `insecure-registries`, aby dodać lokalny rejestr jako zaufany.
   - Przykład konfiguracji:

     ```json
     {
       "insecure-registries": ["localhost:5000"],
       "debug": true,
       "experimental": false
     }
     ```

4. **Zastosuj Zmiany i Zrestartuj Docker Desktop:**

   Kliknij "Apply & Restart" (Zastosuj i Uruchom ponownie), aby zastosować zmiany.

### b. Tworzenie Secret dla Lokalnego Rejestru (Opcjonalnie)

Jeśli lokalny rejestr wymaga uwierzytelniania, musisz utworzyć `Secret` w Kubernetes. Jednak w przypadku lokalnego rejestru na porcie `5000`, który jest skonfigurowany jako niezabezpieczony, nie jest to konieczne.

---

## 6. Wdrożenie KubeDiag Toolkit na Kubernetes

### a. Przygotowanie Szablonów YAML

Skrypt PowerShell używa szablonów YAML do generowania plików Deployment i Service z odpowiednimi wartościami. Upewnij się, że pliki `diagnostic-deployment-template.yaml` i `diagnostic-service-template.yaml` znajdują się w katalogu projektu i zawierają odpowiednie placeholdery.

#### i. `diagnostic-deployment-template.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubediag-deployment
  labels:
    app: kubediag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kubediag
  template:
    metadata:
      labels:
        app: kubediag
    spec:
      containers:
      - name: kubediag-container
        image: <IMAGE_NAME>
        imagePullPolicy: Always
        stdin: true
        tty: true
        securityContext:
          runAsUser: 0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
        volumeMounts:
        - name: capture-data
          mountPath: /captures
      volumes:
      - name: capture-data
        emptyDir: {}
      restartPolicy: Always
```

#### ii. `diagnostic-service-template.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kubediag-service
  labels:
    app: kubediag
spec:
  selector:
    app: kubediag
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

### b. Wdrożenie za Pomocą Skryptu PowerShell

1. **Uruchom skrypt PowerShell:**

   ```powershell
   ./deploy_diagnostic.ps1
   ```

2. **Wybierz opcję wdrożenia na Kubernetes:**

   - W menu wpisz `2` i naciśnij `Enter`.
   - Skrypt zaktualizuje szablony YAML z pełną nazwą obrazu (`localhost:5000/kubediag-toolkit:latest`).
   - Wdroży Deployment i Service na klaster Kubernetes.

### c. Ręczne Wdrożenie (Opcjonalnie)

Jeśli chcesz wykonać te kroki ręcznie, wykonaj poniższe polecenia.

1. **Zastąp placeholder `<IMAGE_NAME>` pełną nazwą obrazu w `diagnostic-deployment-template.yaml`:**

   ```powershell
   (Get-Content diagnostic-deployment-template.yaml) -replace "<IMAGE_NAME>", "localhost:5000/kubediag-toolkit:latest" | Set-Content diagnostic-deployment.yaml
   ```

2. **Zastąp placeholder `<SERVICE_NAME>` w `diagnostic-service-template.yaml` (jeśli potrzebne):**

   W naszym przypadku `kubediag-service` jest już zdefiniowany, więc nie musimy go zmieniać. Jeśli jednak chcesz dynamicznie zastępować nazwy, możesz dostosować szablon według własnych potrzeb.

3. **Wdróż Deployment i Service:**

   ```powershell
   kubectl apply -f diagnostic-deployment.yaml
   kubectl apply -f diagnostic-service.yaml
   ```

---

## 7. Uruchamianie i Korzystanie z Poda Diagnostycznego

### a. Uruchomienie Poda Diagnostycznego

1. **Uruchom skrypt PowerShell:**

   ```powershell
   ./deploy_diagnostic.ps1
   ```

2. **Wybierz opcję uruchomienia poda diagnostycznego:**

   - W menu wpisz `3` i naciśnij `Enter`.
   - Skrypt zidentyfikuje pod diagnostyczny i otworzy interaktywną sesję Bash.

**Przykładowy wynik:**

```
Uruchamianie poda diagnostycznego...
Pod znaleziony: kubediag-deployment-abcde
root@kubediag-deployment-abcde:/app#
```

### b. Korzystanie z Narzędzi Diagnostycznych

Po zalogowaniu się do poda diagnostycznego możesz korzystać z dostępnych narzędzi. Poniżej znajdują się przykłady użycia niektórych z nich.

#### 1. Sprawdzanie Usługi HTTP za Pomocą `curl`

```bash
curl -I http://<SERVICE-IP>:<PORT>
```

**Przykład:**

```bash
curl -I http://10.0.0.1:80
```

#### 2. Skanowanie Portów za Pomocą `nmap`

```bash
nmap -Pn <TARGET-IP>
```

**Przykład:**

```bash
nmap -Pn 10.0.0.2
```

#### 3. Testowanie Przepustowości Sieci za Pomocą `iperf3`

- **Na serwerze:**

  ```bash
  iperf3 -s
  ```

- **Na kliencie:**

  ```bash
  iperf3 -c <SERVER-IP>
  ```

**Przykład:**

```bash
iperf3 -c 10.0.0.3
```

#### 4. Przechwytywanie Ruchu Sieciowego za Pomocą `tcpdump`

```bash
tcpdump -i eth0 -w /captures/capture.pcap
```

**Przykład:**

```bash
tcpdump -i eth0 -w /captures/capture.pcap
```

#### 5. Skanowanie Podatności HTTP za Pomocą `nikto`

```bash
nikto -h http://<TARGET-URL>
```

**Przykład:**

```bash
nikto -h http://10.0.0.4
```

#### 6. Monitorowanie Procesów za Pomocą `htop`

```bash
htop
```

#### 7. Interakcja z Kubernetes za Pomocą `kubectl`

```bash
kubectl get pods
kubectl describe svc <SERVICE-NAME>
```

**Przykład:**

```bash
kubectl get pods
kubectl describe svc kubediag-service
```

### c. Przykładowe Zestawy Poleceń Diagnostycznych

Możesz stworzyć skrypty lub aliasy do często używanych poleceń, aby przyspieszyć proces diagnostyczny.

**Przykład Skryptu Diagnostycznego:**

```bash
#!/bin/bash

# Sprawdzenie usługi HTTP
echo "Sprawdzanie usługi HTTP..."
curl -I http://10.0.0.1:80

# Skanowanie portów
echo "Skanowanie portów..."
nmap -Pn 10.0.0.2

# Testowanie przepustowości sieci
echo "Testowanie przepustowości sieci..."
iperf3 -c 10.0.0.3

# Przechwytywanie ruchu sieciowego
echo "Przechwytywanie ruchu sieciowego..."
tcpdump -i eth0 -w /captures/capture_$(date +%Y%m%d).pcap &
TCPDUMP_PID=$!

# Czekanie przez 60 sekund
sleep 60

# Zatrzymywanie tcpdump
kill $TCPDUMP_PID

echo "Diagnostyka zakończona."
```

---

## 8. Zaawansowane Użycie KubeDiag Toolkit

### a. Automatyzacja Diagnostyki

Możesz tworzyć skrypty automatyzujące wykonywanie określonych zadań diagnostycznych, co pozwala na regularne monitorowanie i szybkie reagowanie na problemy.

**Przykład Skryptu Automatyzującego Diagnostykę:**

```bash
#!/bin/bash

# Sprawdzenie usługi HTTP
echo "Sprawdzanie usługi HTTP..."
curl -I http://10.0.0.1:80

# Skanowanie portów
echo "Skanowanie portów..."
nmap -Pn 10.0.0.2

# Testowanie przepustowości sieci
echo "Testowanie przepustowości sieci..."
iperf3 -c 10.0.0.3

# Przechwytywanie ruchu sieciowego
echo "Przechwytywanie ruchu sieciowego..."
tcpdump -i eth0 -w /captures/capture_$(date +%Y%m%d).pcap &
TCPDUMP_PID=$!

# Czekanie przez 60 sekund
sleep 60

# Zatrzymywanie tcpdump
kill $TCPDUMP_PID

echo "Diagnostyka zakończona."
```

### b. Używanie `hostname -I` w Środowisku Kontenerów

W kontenerach, aby uzyskać adres IP, użyj `hostname -I` zamiast `ip`.

**Przykład:**

```bash
ip_address=$(hostname -I | awk '{print $1}')
echo "Adres IP poda diagnostycznego: $ip_address"
```

### c. Integracja z Innymi Narzędziami

Możesz integrować KubeDiag Toolkit z innymi narzędziami monitorującymi, takimi jak **Prometheus** czy **Grafana**, aby uzyskać bardziej zaawansowane możliwości monitorowania i wizualizacji danych.

### d. Ręczne Aktualizacje i Rozbudowa

Jeśli chcesz dodać więcej narzędzi diagnostycznych do obrazu Docker, edytuj `Dockerfile` i dodaj odpowiednie polecenia instalacyjne. Następnie przebuduj obraz Docker i wypchnij go do lokalnego rejestru.

**Przykład: Dodanie `trivy` do Skanowania Bezpieczeństwa**

1. **Edytuj `Dockerfile`:**

   ```dockerfile
   RUN apt-get update && apt-get install -y trivy && rm -rf /var/lib/apt/lists/*
   ```

2. **Budowanie i Pushowanie Obrazu:**

   Uruchom ponownie skrypt PowerShell i wybierz opcję budowania i pushowania obrazu.

   ```powershell
   ./deploy_diagnostic.ps1
   ```

3. **Wdrożenie Nowej Wersji Obrazu na Kubernetes:**

   - Wybierz opcję `1` i `2` w menu skryptu, aby zbudować nowy obraz i wdrożyć go na Kubernetes.

---

## 9. Diagnostyka Samego KubeDiag Toolkit

### a. Sprawdzanie Statusu Poda Diagnostycznego

Możesz sprawdzić status poda diagnostycznego za pomocą poniższego polecenia:

```powershell
kubectl get pods -l app=kubediag
```

**Przykład Wyniku:**

```
NAME                         READY   STATUS    RESTARTS   AGE
kubediag-deployment-abcde     1/1     Running   0          5m
```

### b. Sprawdzanie Logów Poda

Aby zobaczyć logi poda diagnostycznego:

```powershell
kubectl logs <POD-NAME>
```

**Przykład:**

```powershell
kubectl logs kubediag-deployment-abcde
```

### c. Testowanie Narzędzi Diagnostycznych

Po zalogowaniu się do poda diagnostycznego, uruchom kilka narzędzi diagnostycznych, aby upewnić się, że są zainstalowane i działają poprawnie.

**Przykład:**

```bash
curl --version
nmap --version
iperf3 --version
```

**Przykładowy wynik:**

```
curl 7.68.0 (x86_64-pc-linux-gnu) libcurl/7.68.0 OpenSSL/1.1.1f zlib/1.2.11 libidn2/2.2.0 librtmp/2.3
...
Nmap version 7.80 ( https://nmap.org )
...
iperf 3.1.3
...
```

---

## 10. Utylizacja Zasobów

### a. Utylizacja za Pomocą Skryptu PowerShell

1. **Uruchom skrypt PowerShell:**

   ```powershell
   ./deploy_diagnostic.ps1
   ```

2. **Wybierz opcję utylizacji zasobów:**

   - W menu wpisz `4` i naciśnij `Enter`.
   - Skrypt usunie Deployment i Service z Kubernetes oraz lokalne obrazy Docker.

**Przykładowy wynik:**

```
Usuwanie Deployment i Service z Kubernetes...
deployment.apps/kubediag-deployment deleted
service/kubediag-service deleted
Deployment i Service usunięte pomyślnie.
Usuwanie lokalnych obrazów Docker...
Obrazy Docker usunięte pomyślnie.
```

### b. Ręczna Utylizacja (Opcjonalnie)

Jeśli chcesz usunąć zasoby ręcznie, wykonaj poniższe polecenia.

1. **Usuwanie Deployment i Service:**

   ```powershell
   kubectl delete -f diagnostic-deployment.yaml
   kubectl delete -f diagnostic-service.yaml
   ```

2. **Usuwanie Lokalnych Obrazów Docker:**

   ```powershell
   docker rmi kubediag-toolkit -f
   docker rmi localhost:5000/kubediag-toolkit:latest -f
   ```

---

## 11. Najlepsze Praktyki i Rekomendacje

### a. Bezpieczeństwo

- **Kontrola Dostępu:** Implementuj Role-Based Access Control (RBAC) w Kubernetes, aby ograniczyć dostęp do poda diagnostycznego tylko do uprawnionych użytkowników.
- **Skanowanie Obrazów:** Regularnie skanuj obrazy Docker pod kątem luk bezpieczeństwa za pomocą narzędzi takich jak **Trivy**.
- **Aktualizacje:** Regularnie aktualizuj obrazy Docker oraz narzędzia diagnostyczne, aby zapewnić zgodność z najnowszymi standardami bezpieczeństwa.

### b. Monitorowanie i Logowanie

- **Monitorowanie Zasobów:** Używaj narzędzi takich jak **Prometheus** i **Grafana** do monitorowania zasobów poda diagnostycznego.
- **Logowanie Operacji:** Upewnij się, że logujesz wszystkie operacje wykonywane przez skrypt PowerShell oraz aktywności wewnątrz poda diagnostycznego.

### c. Automatyzacja

- **Integracja z CI/CD:** Zintegruj skrypt PowerShell z systemami CI/CD (np. GitHub Actions, Jenkins) aby automatyzować proces budowy, testowania i wdrażania obrazu Docker.
- **Harmonogram Zadań:** Użyj narzędzi takich jak **CronJobs** w Kubernetes do automatycznego wykonywania zadań diagnostycznych w określonych odstępach czasu.

### d. Dokumentacja

- **Aktualna Dokumentacja:** Utrzymuj aktualną dokumentację dotyczącą używanych narzędzi diagnostycznych, wersji oraz procedur bezpieczeństwa.
- **Instrukcje dla Zespołu:** Zapewnij, że cały zespół posiada dostęp do samouczków i instrukcji dotyczących korzystania z KubeDiag Toolkit.

### e. Optymalizacja Zasobów

- **Limity Zasobów:** Ustaw odpowiednie limity zasobów (CPU, pamięć) dla poda diagnostycznego, aby zapobiec nadmiernemu zużyciu zasobów klastra.
- **Minimalizacja Obrazu:** Używaj lekkich bazowych obrazów Docker i instaluj tylko niezbędne narzędzia, aby zmniejszyć rozmiar obrazu i czas jego pobierania.

---

## 12. Podsumowanie

**KubeDiag Toolkit** to potężne narzędzie diagnostyczne dla środowisk Kubernetes, które integruje szereg narzędzi diagnostycznych w jednym obrazie Docker. Dzięki automatyzacji procesu budowy, wdrożenia oraz utylizacji za pomocą skryptu PowerShell, zarządzanie narzędziem staje się bardziej efektywne i bezpieczne.

### Korzyści:

- **Wszechstronność:** Możliwość diagnozowania problemów na różnych warstwach sieciowych i aplikacyjnych.
- **Automatyzacja:** Skrypt PowerShell automatyzuje kluczowe procesy, oszczędzając czas i minimalizując błędy.
- **Elastyczność:** Możliwość rozbudowy i dostosowania narzędzia do specyficznych potrzeb środowiska Kubernetes.

### Rekomendacje:

- **Regularne Aktualizacje:** Upewnij się, że obraz Docker oraz narzędzia diagnostyczne są regularnie aktualizowane.
- **Bezpieczeństwo:** Implementuj odpowiednie środki bezpieczeństwa, takie jak RBAC i skanowanie obrazów.
- **Monitorowanie:** Korzystaj z narzędzi monitorujących, aby śledzić wydajność i stan poda diagnostycznego.

Dzięki temu kompleksowemu samouczkowi jesteś teraz gotowy, aby efektywnie korzystać z **KubeDiag Toolkit** w swoim środowisku Kubernetes, umożliwiając szybkie i precyzyjne diagnozowanie oraz rozwiązywanie problemów sieciowych i aplikacyjnych.

---

## 13. Załączniki

### a. `deploy_diagnostic.ps1`

```powershell
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
# Usunięto zmienną $dockerHubUsername, ponieważ nie jest używana
$dockerImageTag = "latest"
$localRegistry = "localhost:5000"
# Poprawione przypisanie zmiennej $fullImageName za pomocą operatora formatowania
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
```

### b. `Dockerfile`

```dockerfile
# Bazowy obraz
FROM debian:bullseye-slim

# Metadane
LABEL maintainer="twoj.email@domena.com"
LABEL description="KubeDiag Toolkit - Obraz diagnostyczny z narzędziami pentesterskimi dla Kubernetes"

# Instalacja niezbędnych narzędzi
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nmap \
    dnsutils \
    net-tools \
    tcpdump \
    telnet \
    iproute2 \
    vim \
    less \
    iperf3 \
    nikto \
    traceroute \
    htop \
    metasploit-framework \
    && rm -rf /var/lib/apt/lists/*

# Instalacja kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Instalacja Python i zależności
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Kopiowanie skryptów
COPY diagnostic_logic.py /app/diagnostic_logic.py

# Ustawienie katalogu roboczego
WORKDIR /app

# Ustawienie domyślnego użytkownika
USER root

# Ustawienie domyślnego terminala
CMD ["/bin/bash"]
```

### c. `requirements.txt`

```plaintext
# Zależności Pythona dla diagnostic_logic.py
flask
requests
```

### d. `diagnostic_logic.py`

```python
#!/usr/bin/env python3
import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas wykonywania polecenia: {e}", file=sys.stderr)

def main():
    print("KubeDiag Toolkit - Prosty interfejs do uruchamiania narzędzi diagnostycznych")
    while True:
        print("\nDostępne opcje:")
        print("1. Sprawdzenie usługi HTTP za pomocą curl")
        print("2. Skanowanie portów za pomocą nmap")
        print("3. Testowanie przepustowości sieci za pomocą iperf3")
        print("4. Przechwytywanie ruchu sieciowego za pomocą tcpdump")
        print("5. Skanowanie podatności HTTP za pomocą nikto")
        print("6. Wyjście")
        choice = input("Wybierz opcję (1-6): ")

        if choice == '1':
            url = input("Podaj URL do sprawdzenia: ")
            run_command(f"curl -I {url}")
        elif choice == '2':
            target = input("Podaj adres IP lub domenę do zeskanowania: ")
            run_command(f"nmap -Pn {target}")
        elif choice == '3':
            server = input("Podaj adres serwera iperf3: ")
            run_command(f"iperf3 -c {server}")
        elif choice == '4':
            interface = input("Podaj interfejs sieciowy (np. eth0): ")
            filename = input("Podaj nazwę pliku do zapisania przechwyconych pakietów: ")
            run_command(f"tcpdump -i {interface} -w /captures/{filename}")
        elif choice == '5':
            target = input("Podaj URL do zeskanowania za pomocą nikto: ")
            run_command(f"nikto -h {target}")
        elif choice == '6':
            print("Zamykanie KubeDiag Toolkit.")
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
```

### e. `diagnostic-deployment-template.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubediag-deployment
  labels:
    app: kubediag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kubediag
  template:
    metadata:
      labels:
        app: kubediag
    spec:
      containers:
      - name: kubediag-container
        image: <IMAGE_NAME>
        imagePullPolicy: Always
        stdin: true
        tty: true
        securityContext:
          runAsUser: 0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
        volumeMounts:
        - name: capture-data
          mountPath: /captures
      volumes:
      - name: capture-data
        emptyDir: {}
      restartPolicy: Always
```

### f. `diagnostic-service-template.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kubediag-service
  labels:
    app: kubediag
spec:
  selector:
    app: kubediag
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

---

## 14. Instrukcja Użycia KubeDiag Toolkit

### a. Przygotowanie Środowiska

1. **Instalacja Docker Desktop:**

   - Pobierz Docker Desktop z [oficjalnej strony](https://www.docker.com/products/docker-desktop).
   - Zainstaluj Docker Desktop zgodnie z instrukcjami instalatora.
   - Uruchom Docker Desktop i zaloguj się na swoje konto Docker Hub.

2. **Instalacja Kubernetes CLI (kubectl):**

   - Pobierz najnowszą wersję `kubectl` dla Windows z [oficjalnej strony](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/).
   - Dodaj `kubectl` do zmiennej środowiskowej PATH.

3. **Instalacja PowerShell:**

   - Upewnij się, że używasz PowerShell w wersji 5.1 lub nowszej. Możesz sprawdzić wersję za pomocą:

     ```powershell
     $PSVersionTable.PSVersion
     ```

4. **Logowanie do Lokalnego Rejestru Docker:**

   - Jeśli Twój lokalny rejestr wymaga uwierzytelnienia (w naszym przypadku nie jest to wymagane, ponieważ jest skonfigurowany jako niezabezpieczony), zaloguj się.
   - W naszym przypadku lokalny rejestr jest skonfigurowany jako `localhost:5000` i traktowany jako niezabezpieczony, więc nie jest potrzebne dodatkowe logowanie.

### b. Konfiguracja Skryptu PowerShell

1. **Otwórz `deploy_diagnostic.ps1` w edytorze tekstu:**

   - Skrypt został zaktualizowany i nie wymaga już ustawiania zmiennej `$dockerHubUsername`, ponieważ jest ona usunięta.
   - Upewnij się, że zmienne konfiguracyjne na początku skryptu są zgodne z Twoimi potrzebami.

   - **Przykład:**

     ```powershell
     $dockerImageName = "kubediag-toolkit"
     $dockerImageTag = "latest"
     $localRegistry = "localhost:5000"
     $fullImageName = "{0}/{1}:{2}" -f $localRegistry, $dockerImageName, $dockerImageTag
     ```

   - Upewnij się, że `localRegistry` jest ustawiony na adres Twojego lokalnego rejestru Docker (domyślnie `localhost:5000`).

2. **Zapisz i zamknij plik.**

### c. Budowanie i Publikacja Obrazu Docker

1. **Uruchom skrypt PowerShell:**

   Otwórz PowerShell w katalogu zawierającym pliki projektu (`deploy_diagnostic.ps1`, `Dockerfile`, itp.).

2. **Uruchom skrypt:**

   ```powershell
   ./deploy_diagnostic.ps1
   ```

3. **Wybierz opcję budowania i pushowania obrazu Docker:**

   - W menu wpisz `1` i naciśnij `Enter`.
   - Skrypt wykona:
     - Budowę obrazu Docker.
     - Tagowanie obrazu z pełną nazwą lokalnego rejestru.
     - Pushowanie obrazu do lokalnego rejestru Docker.

**Przykładowy wynik:**

```
Budowanie obrazu Docker: kubediag-toolkit ... 
Sending build context to Docker daemon  4.096kB
Step 1/14 : FROM debian:bullseye-slim
 ---> a1b2c3d4e5f6
...
Successfully built f6e5d4c3b2a1
Successfully tagged kubediag-toolkit:latest
Tagowanie obrazu Docker...
Obraz oznaczony jako 'localhost:5000/kubediag-toolkit:latest'.
Pushowanie obrazu Docker do lokalnego rejestru...
The push refers to repository [localhost:5000/kubediag-toolkit]
f6e5d4c3b2a1: Pushed
...
latest: digest: sha256:abcdef1234567890 size: 1234
Obraz Docker 'localhost:5000/kubediag-toolkit:latest' wypchnięty pomyślnie.
```

### d. Wdrożenie KubeDiag Toolkit na Kubernetes

1. **Wybierz opcję wdrożenia na Kubernetes:**

   - W menu skryptu wpisz `2` i naciśnij `Enter`.
   - Skrypt zaktualizuje szablony YAML z pełną nazwą obrazu (`localhost:5000/kubediag-toolkit:latest`).
   - Wdroży Deployment i Service na klaster Kubernetes.

**Przykładowy wynik:**

```
Aktualizacja plików YAML z pełną nazwą obrazu...
Plik Deployment zaktualizowany: C:\Path\To\Project\diagnostic-deployment.yaml
Plik Service zaktualizowany: C:\Path\To\Project\diagnostic-service.yaml
Wdrażanie Deployment na Kubernetes...
deployment.apps/kubediag-deployment created
Deployment wdrożony pomyślnie.
Wdrażanie Service na Kubernetes...
service/kubediag-service created
Service wdrożony pomyślnie.
```

### e. Sprawdzenie Statusu Wdrożenia

Po wdrożeniu sprawdź, czy pod jest uruchomiony i działa poprawnie:

```powershell
kubectl get pods -l app=kubediag
```

**Przykład Wyniku:**

```
NAME                         READY   STATUS    RESTARTS   AGE
kubediag-deployment-abcde     1/1     Running   0          2m
```

---

## 15. Przykładowe Polecenia Diagnostyczne

### a. Sprawdzanie Usługi HTTP za Pomocą `curl`

```bash
curl -I http://10.0.0.1:80
```

### b. Skanowanie Portów za Pomocą `nmap`

```bash
nmap -Pn 10.0.0.2
```

### c. Testowanie Przepustowości Sieci za Pomocą `iperf3`

**Na serwerze:**

```bash
iperf3 -s
```

**Na kliencie:**

```bash
iperf3 -c 10.0.0.3
```

### d. Przechwytywanie Ruchu Sieciowego za Pomocą `tcpdump`

```bash
tcpdump -i eth0 -w /captures/capture.pcap
```

### e. Skanowanie Podatności HTTP za Pomocą `nikto`

```bash
nikto -h http://10.0.0.4
```

### f. Monitorowanie Procesów za Pomocą `htop`

```bash
htop
```

### g. Interakcja z Kubernetes za Pomocą `kubectl`

```bash
kubectl get pods
kubectl describe svc kubediag-service
```

---

## 16. Rozszerzenia i Przyszła Rozbudowa

### a. Dynamiczne Konfiguracje

Możesz dodać możliwość przekazywania parametrów do skryptu, takich jak liczba replik, limity zasobów, itp.

**Przykład: Dodanie Parametrów do Skryptu PowerShell**

```powershell
param (
    [string]$DockerImageName = "kubediag-toolkit",
    [string]$DockerImageTag = "latest",
    [string]$DeploymentFileTemplate = "diagnostic-deployment-template.yaml",
    [string]$ServiceFileTemplate = "diagnostic-service-template.yaml"
)
```

### b. Integracja z CI/CD

Zintegruj skrypt PowerShell z narzędziami CI/CD (np. GitHub Actions, Jenkins) aby automatyzować proces budowy i wdrażania przy każdym pushu do repozytorium.

### c. Bezpieczeństwo

- **Skanowanie Obrazów Docker:** Dodaj skanowanie obrazów Docker pod kątem luk bezpieczeństwa przed ich pushowaniem, wykorzystując narzędzia takie jak **Trivy**.
- **Role-Based Access Control (RBAC):** Implementuj RBAC w Kubernetes, aby kontrolować dostęp do zasobów diagnostycznych.

### d. Logowanie i Monitoring

Dodaj funkcje logowania operacji skryptu oraz integrację z systemami monitoringu (Prometheus, Grafana) dla lepszej widoczności i analizy.

### e. Ulepszone Zarządzanie Błędami

Rozbuduj obsługę błędów o bardziej szczegółowe informacje i automatyczne powiadomienia (np. e-mail, Slack) w przypadku niepowodzeń.

---

## 17. Dodatkowe Zasoby

- [Dokumentacja Docker](https://docs.docker.com/)
- [Dokumentacja Kubernetes](https://kubernetes.io/docs/home/)
- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
- [Trivy - Skanowanie Bezpieczeństwa Obrazów Docker](https://github.com/aquasecurity/trivy)
- [Nmap - Official Site](https://nmap.org/)
- [Nikto - Web Server Scanner](https://cirt.net/Nikto2)
- [iperf3 - Network Performance Tool](https://iperf.fr/)

---