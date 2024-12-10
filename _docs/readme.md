# Wprowadzenie do Docker i Kubernetes - Chmury Hybrydowe

## Spis Treści

1. [Zaawansowany Kurs Docker](#zaawansowany-kurs-docker)
    - [1. Podstawowe Komendy Docker (Szybkie Przypomnienie)](#1-podstawowe-komendy-docker-szybkie-przypomnienie)
    - [2. Zaawansowane Zarządzanie Kontenerami](#2-zaawansowane-zarządzanie-kontenerami)
    - [3. Budowanie i Optymalizacja Obrazów](#3-budowanie-i-optymalizacja-obrazów)
    - [4. Docker Compose](#4-docker-compose)
    - [5. Woluminy i Sieci](#5-woluminy-i-sieci)
    - [6. Docker w Produkcji i Best Practices](#6-docker-w-produkcji-i-best-practices)
    - [Podsumowanie](#podsumowanie)
2. [Kubernetes – Orkiestracja Kontenerów](#kubernetes---orkiestracja-kontenerów)
    - [1. Wprowadzenie do Kubernetes](#1-wprowadzenie-do-kubernetes)
    - [2. Podstawowe Komponenty Kubernetes](#2-podstawowe-komponenty-kubernetes)
    - [3. Deployment i Service](#3-deployment-i-service)
    - [4. Skalowanie Aplikacji](#4-skalowanie-aplikacji)
    - [5. Monitoring i Logowanie](#5-monitoring-i-logowanie)
    - [6. Best Practices w Kubernetes](#6-best-practices-w-kubernetes)
    - [Podsumowanie Kubernetes](#podsumowanie-kubernetes)
    - [Zarządzanie Deploymentami w Kubernetes](#zarzadzanie-deploymentami-w-kubernetes)
3. [Docker w Chmurach Hybrydowych](#docker-w-chmurach-hybrydowych)
    - [1. Co to jest Chmura Hybrydowa?](#1-co-to-jest-chmura-hybrydowa)
    - [2. Zalety Docker w Chmurach Hybrydowych](#2-zalety-docker-w-chmurach-hybrydowych)
    - [3. Przykłady Zastosowań](#3-przyklady-zastosowań)
    - [4. Integracja Docker z Platformami Chmurowymi](#4-integracja-docker-z-platformami-chmurowymi)
    - [Podsumowanie Docker w Chmurach Hybrydowych](#podsumowanie-docker-w-chmurach-hybrydowych)
4. [Zaawansowane Zarządzanie Rojem Dronów w Kubernetes](#zaawansowane-zarzadzanie-rojem-dronow-w-kubernetes)
    - [1. Wprowadzenie](#1-wprowadzenie)
    - [2. Konfiguracja Headless Service dla Rojów Dronów](#2-konfiguracja-headless-service-dla-rojóow-dronów)
        - [Definicja Headless Service](#definicja-headless-service)
        - [Ograniczenia Headless Service w Komunikacji UDP](#ograniczenia-headless-service-w-komunikacji-udp)
    - [3. Implementacja Centralnego Agregatora Danych](#3-implementacja-centralnego-agregatora-danych)
        - [Tworzenie Skryptu Agregatora](#tworzenie-skryptu-agregatora)
        - [Dockerfile dla Agregatora](#dockerfile-dla-agregatora)
        - [Deployment i Service dla Agregatora](#deployment-i-service-dla-agregatora)
        - [Modyfikacja Logiki Drona](#modyfikacja-logiki-drona)
        - [Aktualizacja Deployment dla Dronów](#aktualizacja-deployment-dla-dronów)
        - [Wdrożenie Konfiguracji w Kubernetes](#wdrożenie-konfiguracji-w-kubernetes)
        - [Weryfikacja Działania Agregatora](#weryfikacja-działania-agregatora)
    - [4. Usuwanie Usługi Mosquitto](#4-usuwanie-uslugi-mosquitto)
        - [Sprawdzenie Istniejących Zasobów Mosquitto](#sprawdzenie-istniejących-zasobów-mosquitto)
        - [Usunięcie Deployment i Service dla Mosquitto](#usunięcie-deployment-i-service-dla-mosquitto)
        - [Weryfikacja Usunięcia Zasobów](#weryfikacja-usunięcia-zasobów)
    - [5. Alternatywne Podejścia do Agregacji Danych](#5-alternatywne-podejscia-do-agregacji-danych)
        - [Użycie Message Broker (MQTT)](#uzycie-message-broker-mqtt)
        - [Użycie HTTP REST API](#uzycie-http-rest-api)
    - [6. Rozwiązywanie Problemów w PowerShell](#6-rozwiazywanie-problemów-w-powershell)
        - [Zastąpienie `grep` w PowerShell](#zastapienie-grep-w-powershell)
    - [7. Podsumowanie](#7-podsumowanie)
5. [Opis Projektu](#opis-projektu)
    - [Idea i Koncepcja](#idea-i-koncepcja)
    - [Poziomy Architektoniczne i Komponenty](#poziomy-architektoniczne-i-komponenty)
    - [Integracja i Przepływ](#integracja-i-przeplyw)
    - [Rola dla Modeli AI](#rola-dla-modeli-ai)
6. [Podsumowanie](#podsumowanie)

---

## Zaawansowany Kurs Docker

### 1. Podstawowe Komendy Docker (Szybkie Przypomnienie)

Zacznijmy od przypomnienia najważniejszych komend Docker, które są fundamentem pracy z kontenerami.

- **Lista kontenerów**:
  ```bash
  docker ps            # Wyświetla uruchomione kontenery
  docker ps -a         # Wyświetla wszystkie kontenery, w tym zatrzymane
  ```

- **Uruchomienie kontenera**:
  ```bash
  docker run -it --name my-container ubuntu:latest bash
  ```

- **Zatrzymanie i usunięcie kontenera**:
  ```bash
  docker stop my-container
  docker rm my-container
  ```

- **Lista obrazów**:
  ```bash
  docker images
  ```

---

### 2. Zaawansowane Zarządzanie Kontenerami

Przechodzimy do bardziej zaawansowanych technik zarządzania kontenerami Docker.

- **Uruchomienie kontenera w tle (detached mode)**:
  ```bash
  docker run -d --name my-nginx -p 8080:80 nginx:latest
  ```

- **Wejście do działającego kontenera**:
  ```bash
  docker exec -it my-nginx bash
  ```

- **Zatrzymanie wszystkich kontenerów**:
  ```bash
  docker stop $(docker ps -q)
  ```

- **Usunięcie wszystkich kontenerów**:
  ```bash
  docker rm $(docker ps -aq)
  ```

- **Wyświetlanie logów z kontenera**:
  ```bash
  docker logs my-nginx
  ```

---

### 3. Budowanie i Optymalizacja Obrazów

Tworzenie własnych obrazów Docker pozwala na pełną kontrolę nad środowiskiem aplikacji.

#### Przykładowy `Dockerfile`

Oto podstawowy `Dockerfile` dla aplikacji Python.

```dockerfile
# Bazowy obraz
FROM python:3.10

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików aplikacji
COPY . /app

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Domyślne polecenie
CMD ["python", "app.py"]
```

#### Budowanie Obrazu

Aby zbudować obraz Docker na podstawie `Dockerfile`, użyj poniższej komendy:

```bash
docker build -t my-python-app:latest .
```

#### Optymalizacja Obrazów

Optymalizacja obrazów Docker może znacznie zmniejszyć ich rozmiar i poprawić wydajność.

- **Używaj wieloetapowego budowania**:
  ```dockerfile
  FROM python:3.10 AS builder
  WORKDIR /app
  COPY . .
  RUN pip install --no-cache-dir -r requirements.txt

  FROM python:3.10-slim
  WORKDIR /app
  COPY --from=builder /app /app
  CMD ["python", "app.py"]
  ```

- **Minimalizuj liczbę warstw**:
  ```dockerfile
  RUN apt-get update && apt-get install -y package && rm -rf /var/lib/apt/lists/*
  ```

---

### 4. Docker Compose

Docker Compose umożliwia definiowanie i uruchamianie wielu kontenerów jako jednej usługi.

#### `docker-compose.yml` – Przykład

Poniżej znajduje się przykładowy plik `docker-compose.yml` dla aplikacji webowej i backendu.

```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"

  app:
    build: .
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
```

#### Uruchamianie Docker Compose

- **Uruchomienie usług**:
  ```bash
  docker-compose up -d
  ```

- **Zatrzymanie usług**:
  ```bash
  docker-compose down
  ```

---

### 5. Woluminy i Sieci

Woluminy i sieci w Docker pozwalają na trwałe przechowywanie danych oraz komunikację między kontenerami.

#### Woluminy

- **Tworzenie woluminu**:
  ```bash
  docker volume create my-volume
  ```

- **Używanie woluminu w kontenerze**:
  ```bash
  docker run -d -v my-volume:/data ubuntu
  ```

#### Sieci

- **Tworzenie sieci**:
  ```bash
  docker network create my-network
  ```

- **Podłączanie kontenerów do sieci**:
  ```bash
  docker run -d --name app1 --network my-network nginx
  docker run -d --name app2 --network my-network nginx
  ```

---

### 6. Docker w Produkcji i Best Practices

Przygotowanie kontenerów Docker do środowiska produkcyjnego wymaga przestrzegania najlepszych praktyk.

- **Minimalizuj rozmiar obrazów**: Używaj obrazów typu `alpine` lub `slim`, które są lekkie i szybkie.
  
- **Używaj `docker-compose` lub `Docker Swarm`** do zarządzania wieloma kontenerami, co ułatwia orkiestrację i skalowanie.

- **Logowanie i monitorowanie**: Implementuj rozwiązania takie jak `ELK Stack` (Elasticsearch, Logstash, Kibana) oraz `Prometheus` + `Grafana` do monitorowania i analizy logów.

- **Bezpieczeństwo**:
  - **Nie uruchamiaj kontenerów jako `root`**: Twórz użytkowników o ograniczonych uprawnieniach w `Dockerfile`.
  - **Ustaw limity zasobów**: Określ limity pamięci i CPU (`--memory`, `--cpus`) podczas uruchamiania kontenerów.
  - **Skanuj obrazy za pomocą `docker scan`**: Regularnie sprawdzaj obrazy pod kątem luk bezpieczeństwa.

---

### Podsumowanie

Ten zaawansowany kurs Dockera obejmował kluczowe zagadnienia niezbędne do efektywnego zarządzania kontenerami w środowisku produkcyjnym:

1. **Podstawowe komendy Docker**
2. **Zaawansowane zarządzanie kontenerami**
3. **Budowanie i optymalizacja obrazów**
4. **Docker Compose**
5. **Woluminy i sieci**
6. **Best practices dla produkcji**

Opanowanie tych tematów pozwoli Ci na pełne wykorzystanie możliwości Dockera w projektach kontenerowych, takich jak zarządzanie rojem dronów w Kubernetes.

---

## Kubernetes – Orkiestracja Kontenerów

### 1. Wprowadzenie do Kubernetes

Kubernetes to otwartoźródłowa platforma do automatyzacji wdrażania, skalowania i zarządzania aplikacjami kontenerowymi. Umożliwia efektywne zarządzanie dużymi środowiskami kontenerowymi, co jest kluczowe w kontekście chmur hybrydowych.

### 2. Podstawowe Komponenty Kubernetes

Zrozumienie podstawowych komponentów Kubernetes jest niezbędne do efektywnego zarządzania klastrem.

- **Pod**: Najmniejsza jednostka w Kubernetes, zawierająca jeden lub więcej kontenerów.
- **Service**: Abstrakcja definiująca zestaw Podów i politykę dostępu.
- **Deployment**: Zarządza deklaratywnym wdrażaniem aplikacji, automatyzując proces aktualizacji.
- **ReplicaSet**: Zapewnia określoną liczbę replik Podów, zapewniając wysoką dostępność.
- **Namespace**: Izoluje zasoby w klastrze, umożliwiając podział środowiska na różne obszary.

### 3. Deployment i Service

#### Przykład Deployment

Deployment umożliwia zarządzanie cyklem życia aplikacji, automatyzując wdrażanie, skalowanie i aktualizacje.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

#### Przykład Service

Service zapewnia stały punkt dostępu do zestawu Podów, niezależnie od ich zmieniających się adresów IP.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

### 4. Skalowanie Aplikacji

Kubernetes oferuje różne metody skalowania aplikacji, aby dostosować się do zmieniających się obciążeń.

- **Skalowanie ręczne**:
  ```bash
  kubectl scale deployment nginx-deployment --replicas=5
  ```

- **Autoskalowanie (Horizontal Pod Autoscaler)**:
  ```bash
  kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80
  ```

### 5. Monitoring i Logowanie

Monitorowanie i logowanie są kluczowe dla utrzymania zdrowia klastrów i aplikacji.

- **Prometheus i Grafana**: Do monitorowania wydajności i zasobów klastrów oraz wizualizacji danych.
- **ELK Stack (Elasticsearch, Logstash, Kibana)**: Do zarządzania logami i ich analizy.

### 6. Best Practices w Kubernetes

Przestrzeganie najlepszych praktyk zapewnia stabilność, bezpieczeństwo i efektywność środowiska Kubernetes.

- **Używaj deklaratywnych konfiguracji**: Zapisuj konfiguracje w plikach YAML, co ułatwia wersjonowanie i zarządzanie zmianami.
- **Zarządzaj konfiguracją i sekretami**: Używaj ConfigMaps i Secrets do przechowywania konfiguracji aplikacji oraz danych wrażliwych.
- **Implementuj polityki bezpieczeństwa**: Kontroluj dostęp i uprawnienia za pomocą RBAC (Role-Based Access Control) oraz Network Policies.
- **Optymalizuj zasoby**: Ustaw limity i prośby zasobów (`requests` i `limits`) dla kontenerów, aby efektywnie wykorzystywać zasoby klastrów.

### Podsumowanie Kubernetes

Kubernetes jest potężnym narzędziem do zarządzania kontenerami na dużą skalę, oferując automatyzację wdrażania, skalowania i operacji. Jego integracja z Dockerem umożliwia efektywne zarządzanie aplikacjami w środowiskach chmur hybrydowych, zapewniając elastyczność i niezawodność.

### Zarządzanie Deploymentami w Kubernetes

Zarządzanie Deploymentami pozwala na efektywne kontrolowanie liczby replik Podów oraz aktualizowanie aplikacji bez przestojów.

#### 1. Znajdź nazwę Deploymentu

Aby zarządzać Deploymentem, najpierw zidentyfikuj jego nazwę:

```bash
kubectl get deployments
```

Przykładowy wynik:

```
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm    5/5     5            5           92m
```

#### 2. Usuń Deployment

Aby usunąć Deployment i wszystkie przez niego zarządzane Pody:

```bash
kubectl delete deployment drone-swarm
```

#### 3. Sprawdź status Podów

Upewnij się, że Pody zostały usunięte:

```bash
kubectl get pods
```

Pody zarządzane przez usunięty Deployment nie powinny już być widoczne na liście.

---

#### Alternatywnie: Skalowanie Deploymentu do zera

Jeśli nie chcesz usuwać Deploymentu, ale chcesz zatrzymać Pody, możesz zmniejszyć liczbę replik do zera:

```bash
kubectl scale deployment drone-swarm --replicas=0
```

To polecenie zatrzyma wszystkie Pody, ale zachowa Deployment, umożliwiając późniejsze łatwe zwiększenie liczby replik:

```bash
kubectl scale deployment drone-swarm --replicas=5
```

---

## Docker w Chmurach Hybrydowych

### 1. Co to jest Chmura Hybrydowa?

Chmura hybrydowa łączy zasoby chmury publicznej i prywatnej, umożliwiając płynne przenoszenie aplikacji i danych między nimi. To podejście zapewnia elastyczność, skalowalność oraz optymalizację kosztów, umożliwiając korzystanie z najlepszych cech obu typów chmur.

### 2. Zalety Docker w Chmurach Hybrydowych

Docker odgrywa kluczową rolę w implementacji rozwiązań chmur hybrydowych dzięki swoim unikalnym cechom:

- **Portabilność**: Kontenery Docker działają spójnie w różnych środowiskach, co ułatwia migrację aplikacji między chmurami publicznymi, prywatnymi i lokalnymi.
  
- **Skalowalność**: Docker umożliwia łatwe skalowanie aplikacji w zależności od zapotrzebowania, zarówno w środowiskach chmurowych, jak i lokalnych.

- **Efektywność**: Kontenery są lekkie i szybkie, co pozwala na lepsze wykorzystanie zasobów w różnych środowiskach chmurowych.

### 3. Przykłady Zastosowań

- **Mikroserwisy**: Docker ułatwia budowanie i zarządzanie mikroserwisami w różnych środowiskach chmurowych, zapewniając niezależność i łatwość skalowania poszczególnych komponentów.

- **DevOps**: Integracja Docker z pipeline CI/CD (Continuous Integration/Continuous Deployment) w chmurach hybrydowych umożliwia automatyczne testowanie, budowanie i wdrażanie aplikacji.

- **Migracja Aplikacji**: Docker ułatwia przenoszenie aplikacji z lokalnych serwerów do chmur publicznych lub odwrotnie, minimalizując problemy związane z kompatybilnością środowisk.

### 4. Integracja Docker z Platformami Chmurowymi

Docker można łatwo zintegrować z różnymi platformami chmurowymi, co umożliwia efektywne zarządzanie i wdrażanie kontenerów.

- **AWS ECS/EKS**: Zarządzanie kontenerami Docker na Amazon Web Services za pomocą Amazon Elastic Container Service (ECS) lub Amazon Elastic Kubernetes Service (EKS).

- **Azure Kubernetes Service (AKS)**: Orkiestracja kontenerów Docker na Microsoft Azure za pomocą AKS, co umożliwia łatwe zarządzanie klastrami Kubernetes.

- **Google Kubernetes Engine (GKE)**: Zarządzanie kontenerami Docker na Google Cloud Platform za pomocą GKE, oferując automatyzację i skalowanie klastrów Kubernetes.

### Podsumowanie Docker w Chmurach Hybrydowych

Docker odgrywa kluczową rolę w implementacji rozwiązań chmur hybrydowych, oferując portabilność, skalowalność i efektywność. Dzięki integracji z platformami chmurowymi, Docker umożliwia elastyczne zarządzanie aplikacjami w różnych środowiskach, co jest niezbędne w nowoczesnych architekturach IT. To podejście zapewnia elastyczność, skalowalność oraz optymalizację kosztów, umożliwiając korzystanie z najlepszych cech chmur publicznych i prywatnych.

---

## Zaawansowane Zarządzanie Rojem Dronów w Kubernetes

### 1. Wprowadzenie

Zarządzanie rojem dronów w Kubernetes wymaga efektywnych metod komunikacji oraz centralizacji zbierania danych. W tym przewodniku przedstawimy zaawansowane techniki konfiguracji Kubernetes i Docker, które pozwolą na skuteczne zarządzanie dronami oraz zbieranie danych z każdego z nich. Omówimy także alternatywne podejścia oraz rozwiązania problemów związanych z komunikacją i zarządzaniem zasobami.

### 2. Konfiguracja Headless Service dla Rojów Dronów

#### Definicja Headless Service

Headless Service w Kubernetes jest definiowany poprzez ustawienie `clusterIP: None`. Służy on głównie do:

- **Service Discovery**: Umożliwia bezpośredni dostęp do poszczególnych Podów za pomocą DNS.
- **Stateful Applications**: Idealny dla aplikacji, które wymagają bezpośredniego połączenia z konkretnym Podem.

**Przykład Definicji Headless Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: drone-service
spec:
  clusterIP: None
  selector:
    app: drone
  ports:
    - port: 5000
      targetPort: 5000
```

#### Ograniczenia Headless Service w Komunikacji UDP

Headless Service nie zapewnia mechanizmu multicastingu UDP do wszystkich Podów. Oznacza to, że każda wiadomość UDP jest kierowana tylko do jednego z Podów, często do samego nadawcy. To ograniczenie uniemożliwia centralne zbieranie danych od wszystkich dronów.

### 3. Implementacja Centralnego Agregatora Danych

Aby skutecznie zbierać dane od wszystkich dronów, konieczne jest stworzenie centralnego agregatora, który będzie odbierał dane od wszystkich dronów w roju.

#### Tworzenie Skryptu Agregatora

Stwórz skrypt `aggregator.py`, który będzie nasłuchiwał na określonym porcie UDP i zbierał dane od wszystkich dronów.

```python
# aggregator.py
import socket
import threading

AGGREGATOR_PORT = 5001  # Port dla agregatora

def handle_message(data, addr):
    message = data.decode()
    print(f"Received from {addr}: {message}")
    # Tu możesz dodać logikę zapisu danych do bazy, przetwarzania, itp.

def run_aggregator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", AGGREGATOR_PORT))
    print(f"Aggregator listening on port {AGGREGATOR_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        threading.Thread(target=handle_message, args=(data, addr)).start()

if __name__ == "__main__":
    run_aggregator()
```

#### Dockerfile dla Agregatora

Utwórz oddzielny `Dockerfile` dla agregatora, aby móc go wdrożyć jako osobny Pod w Kubernetes.

```dockerfile
# aggregator/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY aggregator.py /app/aggregator.py

# Instalacja zależności, jeśli są potrzebne
# RUN pip install <pakiety>

ENV AGGREGATOR_PORT=5001

CMD ["python", "aggregator.py"]
```

#### Deployment i Service dla Agregatora

Zdefiniuj Deployment i Service dla agregatora, aby był dostępny w klastrze.

**Plik: `aggregator-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aggregator
  template:
    metadata:
      labels:
        app: aggregator
    spec:
      containers:
        - name: aggregator
          image: localhost:5000/aggregator:latest
          ports:
            - containerPort: 5001
          env:
            - name: AGGREGATOR_PORT
              value: "5001"
```

**Plik: `aggregator-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aggregator-service
spec:
  selector:
    app: aggregator
  ports:
    - port: 5001
      targetPort: 5001
  type: ClusterIP
```

#### Modyfikacja Logiki Drona

Zaktualizuj `drone_logic.py`, aby drony wysyłały dane do `aggregator-service` zamiast do `drone-service`.

```python
import os
import socket
import time
import random

DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{random.randint(1000, 9999)}")
AGGREGATOR_HOST = os.getenv("AGGREGATOR_HOST", "aggregator-service")  # Nazwa DNS agregatora w Kubernetes
AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "5001"))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    # Tworzenie wiadomości
    message = f"{DRONE_NAME} at position {position[0]}, {position[1]}"
    try:
        # Wysyłanie danych do agregatora
        sock.sendto(message.encode(), (AGGREGATOR_HOST, AGGREGATOR_PORT))
    except Exception as e:
        print(f"Error sending data: {e}")

    # Odbiór wiadomości od innych (opcjonalne)
    sock.settimeout(1.0)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"[{DRONE_NAME}] received from {addr}: {data.decode()}")
    except socket.timeout:
        pass

    # Prosta symulacja ruchu
    position[0] += random.randint(-1, 1)
    position[1] += random.randint(-1, 1)
    time.sleep(5)
```

#### Aktualizacja Deployment dla Dronów

Zaktualizuj plik Deployment dla dronów, aby ustawić zmienne środowiskowe `AGGREGATOR_HOST` i `AGGREGATOR_PORT`.

**Zaktualizowany `drone-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drone-swarm
spec:
  replicas: 5
  selector:
    matchLabels:
      app: drone
  template:
    metadata:
      labels:
        app: drone
    spec:
      containers:
        - name: drone
          image: localhost:5000/mydrone:latest
          imagePullPolicy: IfNotPresent
          env:
            - name: DRONE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: AGGREGATOR_HOST
              value: "aggregator-service"  # Adres agregatora
            - name: AGGREGATOR_PORT
              value: "5001"
          ports:
            - containerPort: 5000
```

#### Wdrożenie Konfiguracji w Kubernetes

Upewnij się, że obrazy Docker dla dronów i agregatora są zbudowane i przesłane do rejestru Docker (`localhost:5000` w tym przypadku - [Zarządzanie Obrazami i Rejestrem Docker](budowanie-i-zarządzanie-obrazami-dockerowymi.md#uruchomienie-lokalnego-rejestru-docker).

```bash
# Budowanie obrazu drona
cd drones/
docker build -t localhost:5000/mydrone:latest .
docker push localhost:5000/mydrone:latest

# Budowanie obrazu agregatora
cd ../aggregator/
docker build -t localhost:5000/aggregator:latest .
docker push localhost:5000/aggregator:latest
```

Następnie zastosuj konfiguracje YAML w Kubernetes:

```bash
kubectl apply -f aggregator-deployment.yaml
kubectl apply -f aggregator-service.yaml
kubectl apply -f drone-deployment.yaml
```

### Weryfikacja Działania Agregatora

Sprawdź logi agregatora, aby upewnić się, że odbiera on dane od wszystkich dronów.

```bash
kubectl logs deployment/aggregator
```

Powinieneś zobaczyć coś podobnego do:

```
Aggregator listening on port 5001
Received from ('10.1.0.198', 5001): drone_1 at position 50, 60
Received from ('10.1.0.199', 5001): drone_2 at position 45, 55
...
```

---

### 4. Usuwanie Usługi Mosquitto

Jeśli zdecydujesz się usunąć Mosquitto z klastra Kubernetes, wykonaj poniższe kroki.

#### Sprawdzenie Istniejących Zasobów Mosquitto

Najpierw upewnij się, jakie zasoby są związane z Mosquitto w Twoim klastrze.

##### Wyświetlenie Deployments

```bash
kubectl get deployments
```

Przykładowy wynik:

```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm       0/0     0            0           147m
mosquitto         1/1     1            1           35m
mqtt-aggregator   0/1     1            0           23m
```

##### Wyświetlenie Services

```bash
kubectl get services
```

Przykładowy wynik:

```
NAME             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
drone-service    ClusterIP   None             <none>        5000/TCP   3h36m
kubernetes       ClusterIP   10.96.0.1        <none>        443/TCP    4h3m
mqtt-broker      ClusterIP   10.100.174.192   <none>        1883/TCP   4m41s
```

#### Usunięcie Deployment i Service dla Mosquitto

Aby usunąć Mosquitto, musisz usunąć zarówno **Deployment**, jak i **Service** związane z tym brokerem MQTT.

##### Usunięcie Deployment Mosquitto

```bash
kubectl delete deployment mosquitto
```

##### Usunięcie Service Mosquitto

```bash
kubectl delete service mosquitto
```

##### Alternatywnie: Usunięcie Deployment i Service Jednocześnie

Możesz również usunąć oba zasoby jednocześnie za pomocą jednego polecenia:

```bash
kubectl delete deployment mosquitto service mosquitto
```

#### Weryfikacja Usunięcia Zasobów

Po wykonaniu powyższych kroków, sprawdź, czy zasoby zostały pomyślnie usunięte.

##### Sprawdzenie Deployments

```bash
kubectl get deployments
```

Przykładowy wynik:

```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm       0/0     0            0           147m
mqtt-aggregator   0/1     1            0           23m
```

##### Sprawdzenie Services

```bash
kubectl get services
```

Przykładowy wynik:

```
NAME             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
drone-service    ClusterIP   None             <none>        5000/TCP   3h36m
kubernetes       ClusterIP   10.96.0.1        <none>        443/TCP    4h3m
mqtt-broker      ClusterIP   10.100.174.192   <none>        1883/TCP   4m41s
```

---

### 5. Alternatywne Podejścia do Agregacji Danych

Oprócz centralnego agregatora UDP, istnieją inne metody centralizacji danych od dronów, takie jak użycie message brokerów (np. MQTT) lub HTTP REST API.

#### Użycie Message Broker (MQTT)

**MQTT** jest lekkim protokołem publikacji/subskrypcji, idealnym do komunikacji IoT. Każdy dron może publikować swoje dane na określonym temacie, a agregator/subskrybent może odbierać te dane.

##### Instalacja MQTT Broker (np. Mosquitto)

**Plik: `mosquitto-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mosquitto
  template:
    metadata:
      labels:
        app: mosquitto
    spec:
      containers:
        - name: mosquitto
          image: eclipse-mosquitto:latest
          ports:
            - containerPort: 1883
---
apiVersion: v1
kind: Service
metadata:
  name: mqtt-broker
spec:
  selector:
    app: mosquitto
  ports:
    - port: 1883
      targetPort: 1883
  type: ClusterIP
```

**Zastosowanie:**

```bash
kubectl apply -f mosquitto-deployment.yaml
```

##### Konfiguracja Dronów do Publikowania na MQTT

Zaktualizuj `drone_logic.py`, aby drony publikowały dane na brokerze MQTT.

```python
import os
import time
import random
import paho.mqtt.client as mqtt

DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{random.randint(1000, 9999)}")
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5.0"))

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    message = f"{DRONE_NAME} at position {position[0]}, {position[1]}"
    client.publish("drone/positions", message)
    print(f"[{DRONE_NAME}] Published: {message}")

    # Prosta symulacja ruchu
    position[0] += random.randint(-1, 1)
    position[1] += random.randint(-1, 1)
    time.sleep(PUBLISH_INTERVAL)
```

##### Agregacja Danych z MQTT

Stwórz osobny Pod lub aplikację, która subskrybuje na temat `drone/positions` i zbiera dane.

**Przykładowy Skrypt `mqtt_aggregator.py`:**

```python
import os
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("drone/positions")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received: {message}")
    # Tu możesz dodać logikę zapisu danych do bazy, przetwarzania, itp.

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
```

##### Dockerfile dla Agregatora MQTT

**Plik: `mqtt_aggregator/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY mqtt_aggregator.py /app/mqtt_aggregator.py

RUN pip install paho-mqtt

ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883

CMD ["python", "mqtt_aggregator.py"]
```

##### Deployment i Service dla Agregatora MQTT

**Plik: `mqtt-aggregator-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mqtt-aggregator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mqtt-aggregator
  template:
    metadata:
      labels:
        app: mqtt-aggregator
    spec:
      containers:
        - name: mqtt-aggregator
          image: localhost:5000/mqtt-aggregator:latest
          env:
            - name: MQTT_BROKER
              value: "mqtt-broker"
            - name: MQTT_PORT
              value: "1883"
```

**Plik: `mqtt-aggregator-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mqtt-aggregator-service
spec:
  selector:
    app: mqtt-aggregator
  ports:
    - port: 1884
      targetPort: 1883
  type: ClusterIP
```

**Zastosowanie:**

```bash
# Budowanie obrazu agregatora MQTT
cd mqtt_aggregator/
docker build -t localhost:5000/mqtt-aggregator:latest .
docker push localhost:5000/mqtt-aggregator:latest

# Zastosowanie konfiguracji w Kubernetes
kubectl apply -f mqtt-aggregator-deployment.yaml
kubectl apply -f mqtt-aggregator-service.yaml
```

### Zalety Użycia MQTT

- **Skalowalność**: MQTT jest zaprojektowany do obsługi dużej liczby klientów, co jest idealne dla roju dronów.
  
- **Efektywność**: Lekki protokół, który minimalizuje zużycie pasma i zasobów, co jest kluczowe dla aplikacji IoT.
  
- **Elastyczność**: Możliwość subskrybowania różnych tematów i filtrowania danych umożliwia precyzyjne zarządzanie informacjami.

#### Użycie HTTP REST API

Każdy dron może wysyłać dane za pomocą żądań HTTP POST do centralnego serwera API.

##### Implementacja Serwera API

**Plik: `aggregator_api.py`**

```python
from flask import Flask, request
app = Flask(__name__)

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.json
    print(f"Received from {data['name']}: position {data['x']}, {data['y']}")
    return {"status": "success"}, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
```

##### Dockerfile dla Serwera API

**Plik: `aggregator_api/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY aggregator_api.py /app/aggregator_api.py

RUN pip install flask

ENV FLASK_APP=aggregator_api.py

CMD ["python", "aggregator_api.py"]
```

##### Konfiguracja Dronów do Wysyłania HTTP POST

**Zaktualizowany `drone_logic.py`:**

```python
import os
import time
import random
import requests

DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{random.randint(1000, 9999)}")
AGGREGATOR_API = os.getenv("AGGREGATOR_API", "http://aggregator-service:5001/update_position")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5.0"))

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    data = {
        "name": DRONE_NAME,
        "x": position[0],
        "y": position[1]
    }
    try:
        response = requests.post(AGGREGATOR_API, json=data)
        print(f"[{DRONE_NAME}] Sent data: {data}, Response: {response.status_code}")
    except Exception as e:
        print(f"[{DRONE_NAME}] Error sending data: {e}")

    # Prosta symulacja ruchu
    position[0] += random.randint(-1, 1)
    position[1] += random.randint(-1, 1)
    time.sleep(PUBLISH_INTERVAL)
```

##### Deployment i Service dla Serwera API

**Plik: `aggregator-api-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aggregator-api
  template:
    metadata:
      labels:
        app: aggregator-api
    spec:
      containers:
        - name: aggregator-api
          image: localhost:5000/aggregator-api:latest
          ports:
            - containerPort: 5001
```

**Plik: `aggregator-api-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aggregator-service
spec:
  selector:
    app: aggregator-api
  ports:
    - port: 5001
      targetPort: 5001
  type: ClusterIP
```

**Zastosowanie:**

```bash
# Budowanie obrazu serwera API
cd aggregator_api/
docker build -t localhost:5000/aggregator-api:latest .
docker push localhost:5000/aggregator-api:latest

# Zastosowanie konfiguracji w Kubernetes
kubectl apply -f aggregator-api-deployment.yaml
kubectl apply -f aggregator-api-service.yaml
kubectl apply -f drone-deployment.yaml
```

### 6. Rozwiązywanie Problemów w PowerShell

PowerShell nie posiada bezpośredniego odpowiednika `grep`, ale można użyć `Select-String` lub `Where-Object` do filtrowania wyników.

#### Zastąpienie `grep` w PowerShell

- **Filtrowanie usług zawierających "mqtt-broker":**

```powershell
kubectl get svc -n default | Select-String "mqtt-broker"
```

lub

```powershell
kubectl get svc -n default | Where-Object { $_ -match "mqtt-broker" }
```

- **Użycie `-o` z `kubectl` do uzyskania bardziej strukturalnych danych:**

```powershell
kubectl get svc -n default -o json | ConvertFrom-Json | Select-Object -ExpandProperty items | Where-Object { $_.metadata.name -eq "mqtt-broker" }
```

---

### 7. Podsumowanie

W tej sekcji omówiliśmy zaawansowane techniki zarządzania rojem dronów w Kubernetes, w tym:

1. **Konfigurację Headless Service**: Umożliwiającą bezpośrednią komunikację między Podami.
2. **Implementację centralnego agregatora danych**: Odbierającego i przetwarzającego dane z dronów.
3. **Usuwanie usług Mosquitto**: Jeśli zdecydujesz się na alternatywne metody agregacji danych.
4. **Alternatywne podejścia do agregacji danych**: Takie jak MQTT i HTTP REST API.
5. **Rozwiązywanie problemów w PowerShell**: Jak zastąpić `grep` w środowisku PowerShell.

Dzięki tym technikom możesz efektywnie zarządzać rojem dronów, zbierać i analizować dane oraz zapewnić stabilność i skalowalność swojego środowiska Kubernetes.

---

## Opis Projektu

### Idea i Koncepcja

W centrum projektu znajduje się symulacja roju dronów działających w środowisku chmurowym i kontenerowym. Każdy dron funkcjonuje jako autonomiczny kontener, komunikujący się z pozostałymi elementami systemu za pomocą protokołu MQTT. Wspólna komunikacja oparta o model publikacja-subskrypcja (publish-subscribe) zapewnia luźne powiązanie komponentów, elastyczność i skalowalność.

**Główne założenia:**

1. **Autonomiczne Kontenery/Drony** – Każdy dron jest kontenerem, generującym dane o swojej pozycji, stanie baterii i innych parametrach.
2. **Komunikacja MQTT** – Drony publikują dane do brokera MQTT, a inne komponenty, takie jak agregator, subskrybują te informacje.
3. **Architektura Kontenerowa w Kubernetes** – Całość wdrożenia opiera się na orkiestracji Kubernetes, zapewniając skalowalność, niezawodność, elastyczność i prostotę zarządzania.
4. **Agregacja i Dostęp do Danych** – Agregator zbiera dane z dronów, przetwarza je i udostępnia zewnętrznemu światu poprzez REST API (aggregator-api), co umożliwia zarządzanie rojem i analizę danych.
5. **Monitorowanie, CI/CD, Bezpieczeństwo** – Projekt uwzględnia pipeline’y CI/CD, monitoring (Prometheus, Grafana), logowanie (ELK), strategie wdrożeń (Blue-Green, Canary), bezpieczeństwo (RBAC, Network Policies, szyfrowanie).

---

### Poziomy Architektoniczne i Komponenty

#### Poziom 1: Fundamenty Komunikacji i Orkiestracji

**MQTT Broker** (`server/mqtt/`)  
- *Rola:* Centralny punkt komunikacji w stylu publish-subscribe.  
- *Zasoby:*  
  - `mosquitto.conf` – konfiguracja brokera MQTT (Mosquitto).  
  - `mosquitto-deployment.yaml`, `mosquitto-service.yaml` – wdrożenie brokera do klastra Kubernetes.  
- *Idea:* Broker MQTT umożliwia luźne powiązanie dronów (publisherów) z agregatorem (subscriberem) i innymi komponentami.

**Kubernetes i Konteneryzacja**  
- *Rola:* Orkiestracja wszystkich usług, ich skalowanie, resiliencja, load balancing.  
- *Zasoby:* Manifesty YAML (deployment, service, statefulset) dla każdego komponentu.  
- *Idea:* Kubernetes zapewnia infrastrukturę do uruchamiania i zarządzania wieloma dronami-kontenerami, brokerem MQTT, agregatorem i API.

---

#### Poziom 2: Drony i Generowanie Danych

**Drony** (`drones/`)  
- *Rola:* Autonomiczne generowanie danych o stanie drona (pozycja, bateria) i publikacja ich do MQTT.  
- *Pliki i Konfiguracja:*  
  - `drone_logic.py` – Logika generowania danych i komunikacji z brokerem.  
  - `Dockerfile`, `requirements.txt` – Budowa obrazu kontenera drona.  
  - `drone-deployment.yaml`, `drone-service.yaml` – Skrypty wdrażające flotę dronów do Kubernetes.  
- *Idea:* Każdy dron jest niezależnym Podem w Kubernetes, który publikuje dane do brokera MQTT na topiki `drones/{drone_id}/position`. Daje to możliwość łatwego skalowania liczby dronów poprzez modyfikację `replicas`.

---

#### Poziom 3: Agregacja Danych i API

**Agregator** (`aggregator/`)  
- *Rola:* Subskrybent wiadomości MQTT publikowanych przez drony. Zbiera dane, przetwarza je i przygotowuje do udostępnienia przez API.  
- *Pliki i Konfiguracja:*  
  - `aggregator.py` – Kod logiki subskrypcji i przetwarzania danych z topików `drones/+/position`.  
  - `aggregator-deployment.yaml`, `aggregator-service.yaml` – Wdrożenie agregatora do klastrów Kubernetes.  
  - `Dockerfile`, `requirements.txt` – Budowa obrazu.  
- *Idea:* Agregator to centralny element logiki biznesowej – odbiera dane z roju i umożliwia ich dalszą analizę i magazynowanie.

**Aggregator API** (`aggregator-api/`)  
- *Rola:* Interfejs REST do dostępu do przetworzonych danych dronów. Umożliwia zewnętrznym systemom i użytkownikom pobieranie informacji o stanie dronów, wysyłanie komend i zarządzanie rojem.  
- *Pliki i Konfiguracja:*  
  - `aggregator_api.py` – Kod implementujący REST endpointy (np. `GET /api/drones/{drone_id}/status`).  
  - `aggregator-api-deployment.yaml`, `aggregator-api-service.yaml` – Wdrożenie API do Kubernetes.  
  - `Dockerfile`, `requirements.txt` – Obraz kontenera API.  
- *Idea:* API tworzy warstwę integracyjną, dzięki której systemy zewnętrzne mają dostęp do aktualnego stanu roju oraz możliwość sterowania dronami.

---

#### Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD

**Monitoring i Wizualizacja**  
- *Prometheus, Grafana:* Zbierają metryki z dronów, agregatora, API oraz brokera, wizualizując obciążenie, wykorzystanie zasobów, poziom baterii dronów.  
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów, wspierając diagnozę i debugowanie.

**CI/CD**  
- *Idea:* Automatyczne pipeline’y (GitLab CI, Jenkins, ArgoCD) kompilują i testują kod, budują obrazy Docker, wdrażają je do Kubernetes.  
- *Korzyści:* Szybkie reagowanie na zmiany, zwinność w dostarczaniu nowych funkcji, minimalizacja błędów ręcznej konfiguracji.

**Strategie Wdrożeń (Blue-Green, Canary)**  
- *Idea:* Bezpieczne aktualizacje pozwalają wdrażać nowe wersje dronów lub agregatora bez przestojów. Stopniowe przełączanie ruchu (canary) lub równoległe utrzymywanie dwóch wersji (blue-green) minimalizuje ryzyko awarii.

---

#### Poziom 5: Bezpieczeństwo i Izolacja

**RBAC i Network Policies**  
- *Idea:* Kubernetes RBAC kontroluje, którzy użytkownicy mogą czytać, pisać czy wdrażać zasoby w klastrze. Network Policies ograniczają komunikację między Podami, zapewniając izolację i minimalizując wektory ataku.

**Secrets Management**  
- *Idea:* Dane wrażliwe (klucze API, hasła) przechowywane w Kubernetes Secrets, podłączane do Podów w sposób bezpieczny. Szyfrowanie TLS dla komunikacji MQTT i API zwiększa poufność i integralność danych.

---

## Integracja i Przepływ

1. **Drony** publikują dane o swojej pozycji i stanie przez MQTT:
   - **MQTT Broker** (Mosquitto) odbiera i przechowuje te informacje tymczasowo.
   
2. **Agregator** subskrybuje temat `drones/+/position`:
   - Przetwarza dane i agreguje je, tworząc jednolitą bazę informacji o stanie całego roju.
   
3. **Aggregator API** zapewnia interfejs REST:
   - Użytkownicy i zewnętrzne systemy pobierają informacje (`GET /api/drones/...`) lub wysyłają komendy sterujące do dronów.
   
4. **Monitorowanie i Logi** śledzą cały przepływ:
   - Prometheus i Grafana zbierają metryki.
   - ELK pozwala na analizę logów.
   
5. **CI/CD i Skalowalność**:
   - W przypadku zwiększonego obciążenia (np. potrzeby większej liczby dronów), Kubernetes umożliwia skalowanie replik.
   - CI/CD zapewnia szybkie wprowadzenie poprawek i nowych funkcjonalności.
   
6. **Bezpieczeństwo** chroni cały ekosystem:
   - RBAC ogranicza dostęp.
   - Secrets i szyfrowane połączenia chronią wrażliwe dane.

---

## Rola dla Modeli AI

Ten opis służy jako główny punkt odniesienia dla modeli AI, które mają operować na kodzie i logice projektu. Dzięki niemu:

- **Modele językowe** mogą łatwiej zrozumieć kontekst, rolę i powiązania między elementami kodu.
- **Generatory kodu** opierają się na wspólnych założeniach architektonicznych, mając mapę połączeń i zrozumienie, gdzie wdrożyć nowe funkcjonalności.
- **Analityczne modele AI** łatwiej identyfikują punkty wejścia do optymalizacji (np. poprawa wydajności MQTT, zwiększenie bezpieczeństwa) i wiedzą, gdzie ingerować w kod lub konfigurację.

---

## Podsumowanie

Przedstawiona architektura to kompleksowa platforma symulująca rozproszony system dronów zarządzanych i monitorowanych w środowisku chmurowym. Opiera się na konteneryzacji, komunikacji MQTT, orkiestracji Kubernetes, agregacji danych i udostępnianiu ich przez API. Zapewnia skalowalność, elastyczność, bezpieczeństwo, a także instrumenty do integracji z modelami AI, które mogą rozwijać i optymalizować kod na podstawie klarownej mapy funkcjonalnej i architektonicznej.

Dzięki temu projektowi jesteś w stanie efektywnie zarządzać dużymi flotami dronów, centralizować ich dane oraz zapewniać ich niezawodne działanie w środowisku chmurowym i kontenerowym.

---

## Podsumowanie

W tej dokumentacji przeanalizowaliśmy zaawansowane aspekty zarządzania ekosystemem MQTT oraz rojem dronów przy użyciu Docker i Kubernetes w kontekście chmur hybrydowych. Omówiliśmy:

- **Zaawansowany kurs Dockera**: Od podstawowych komend po optymalizację obrazów i zarządzanie kontenerami.
- **Orkiestrację kontenerów z Kubernetes**: Podstawowe komponenty, deployment, skalowanie, monitoring i najlepsze praktyki.
- **Docker w chmurach hybrydowych**: Zalety, przykłady zastosowań oraz integracja z głównymi platformami chmurowymi.
- **Zaawansowane zarządzanie rojem dronów**: Konfiguracja headless service, implementacja agregatora danych, usuwanie usług Mosquitto oraz alternatywne podejścia do agregacji danych.
- **Opis projektu**: Idea, koncepcja, architektura, integracja oraz rola modeli AI w projekcie.

---

**Plik:** `_docs/readme.md`

[Powrót do głównej dokumentacji](../README.MD)