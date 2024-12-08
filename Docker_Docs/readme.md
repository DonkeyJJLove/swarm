# Wprowadzenie do Docker i Kubernetes w Kontekście Chmur Hybrydowych

## Spis Treści
1. [Zaawansowany Kurs Docker](#zaawansowany-kurs-docker)
    - [1. Podstawowe Komendy Docker (Szybkie Przypomnienie)](#1-podstawowe-komendy-docker-szybkie-przypomnienie)
    - [2. Zaawansowane Zarządzanie Kontenerami](#2-zaawansowane-zarządzanie-kontenerami)
    - [3. Budowanie i Optymalizacja Obrazów](#3-budowanie-i-optymalizacja-obrazów)
    - [4. Docker Compose](#4-docker-compose)
    - [5. Woluminy i Sieci](#5-woluminy-i-sieci)
    - [6. Docker w Produkcji i Best Practices](#6-docker-w-produkcji-i-best-practices)
    - [Podsumowanie](#podsumowanie)
2. [Kubernetes – Orkiestracja Kontenerów](#kubernetes---orkiestracja-kontenerow)
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
    - [3. Przykłady Zastosowań](#3-przyklady-zastosowan)
    - [4. Integracja Docker z Platformami Chmurowymi](#4-integracja-docker-z-platformami-chmurowymi)
    - [Podsumowanie Docker w Chmurach Hybrydowych](#podsumowanie-docker-w-chmurach-hybrydowych)
4. [Zaawansowane Zarządzanie Rojem Dronów w Kubernetes](#zaawansowane-zarzadzanie-rojem-dronow-w-kubernetes)
    - [1. Wprowadzenie](#1-wprowadzenie)
    - [2. Konfiguracja Headless Service dla Rojów Dronów](#2-konfiguracja-headless-service-dla-rojow-dronow)
        - [Definicja Headless Service](#definicja-headless-service)
        - [Ograniczenia Headless Service w Komunikacji UDP](#ograniczenia-headless-service-w-komunikacji-udp)
    - [3. Implementacja Centralnego Agregatora Danych](#3-implementacja-centralnego-agregatora-danych)
        - [Tworzenie Skryptu Agregatora](#tworzenie-skryptu-agregatora)
        - [Dockerfile dla Agregatora](#dockerfile-dla-agregatora)
        - [Deployment i Service dla Agregatora](#deployment-i-service-dla-agregatora)
        - [Modyfikacja Logiki Drona](#modyfikacja-logiki-drona)
        - [Aktualizacja Deployment dla Dronów](#aktualizacja-deployment-dla-dronow)
        - [Wdrożenie Konfiguracji w Kubernetes](#wdrozenie-konfiguracji-w-kubernetes)
        - [Weryfikacja Działania Agregatora](#weryfikacja-dzialania-agregatora)
    - [4. Usuwanie Usługi Mosquitto](#4-usuwanie-uslugi-mosquitto)
        - [Sprawdzenie Istniejących Zasobów Mosquitto](#sprawdzenie-istniejacych-zasobow-mosquitto)
        - [Usunięcie Deployment i Service dla Mosquitto](#usuniecie-deployment-i-service-dla-mosquitto)
        - [Weryfikacja Usunięcia Zasobów](#weryfikacja-usuniecia-zasobow)
    - [5. Alternatywne Podejścia do Agregacji Danych](#5-alternatywne-podejscia-do-agregacji-danych)
        - [Użycie Message Broker (MQTT)](#uzycie-message-broker-mqtt)
        - [Użycie HTTP REST API](#uzycie-http-rest-api)
    - [6. Rozwiązywanie Problemów w PowerShell](#6-rozwiazywanie-problemow-w-powershell)
        - [Zastąpienie `grep` w PowerShell](#zastapienie-grep-w-powershell)
    - [7. Podsumowanie](#7-podsumowanie)
```

## Zaawansowany Kurs Docker

### 1. Podstawowe Komendy Docker (Szybkie Przypomnienie)

- **Lista kontenerów**:
  ```bash
  docker ps            # Kontenery uruchomione
  docker ps -a         # Wszystkie kontenery
  ```

- **Uruchomienie kontenera**:
  ```bash
  drones run -it --name my-container ubuntu:latest bash
  ```

- **Zatrzymanie i usunięcie kontenera**:
  ```bash
  drones stop my-container
  drones rm my-container
  ```

- **Lista obrazów**:
  ```bash
  drones images
  ```

---

### 2. Zaawansowane Zarządzanie Kontenerami

- **Uruchomienie kontenera w tle**:
  ```bash
  drones run -d --name my-nginx -p 8080:80 nginx:latest
  ```

- **Wejście do działającego kontenera**:
  ```bash
  drones exec -it my-nginx bash
  ```

- **Zatrzymanie wszystkich kontenerów**:
  ```bash
  drones stop $(drones ps -q)
  ```

- **Usunięcie wszystkich kontenerów**:
  ```bash
  drones rm $(drones ps -aq)
  ```

- **Logi z kontenera**:
  ```bash
  drones logs my-nginx
  ```

---

### 3. Budowanie i Optymalizacja Obrazów

#### Przykładowy `Dockerfile`

```dockerfile
# Bazowy obraz
FROM python:3.10

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików
COPY . /app

# Instalacja zależności
RUN pip install -r requirements.txt

# Domyślne polecenie
CMD ["python", "app.py"]
```

#### Budowanie Obrazu

```bash
drones build -t my-python-app .
```

#### Optymalizacja Obrazów

- **Używaj wieloetapowego budowania**:
  ```dockerfile
  FROM python:3.10 AS builder
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt

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

#### `docker-compose.yml` – Przykład

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
  drones-compose up -d
  ```

- **Zatrzymanie usług**:
  ```bash
  drones-compose down
  ```

---

### 5. Woluminy i Sieci

#### Woluminy

- **Tworzenie woluminu**:
  ```bash
  drones volume create my-volume
  ```

- **Używanie woluminu w kontenerze**:
  ```bash
  drones run -d -v my-volume:/data ubuntu
  ```

#### Sieci

- **Tworzenie sieci**:
  ```bash
  drones network create my-network
  ```

- **Podłączanie kontenerów do sieci**:
  ```bash
  drones run -d --name app1 --network my-network nginx
  drones run -d --name app2 --network my-network nginx
  ```

---

### 6. Docker w Produkcji i Best Practices

- **Minimalizuj rozmiar obrazów**: Używaj obrazów typu `alpine` lub `slim`.
- **Używaj `docker-compose` lub `Docker Swarm`** do zarządzania wieloma kontenerami.
- **Logowanie i monitorowanie**: Używaj `ELK Stack`, `Prometheus` + `Grafana`.
- **Bezpieczeństwo**:
  - Nie uruchamiaj kontenerów jako `root`.
  - Ustaw limity zasobów (`--memory`, `--cpus`).
  - Skanuj obrazy za pomocą `docker scan`.

---

### Podsumowanie

Ten turbo-przyspieszony kurs Dockera obejmował najważniejsze zagadnienia:

1. Podstawowe komendy
2. Zaawansowane zarządzanie kontenerami
3. Budowanie i optymalizacja obrazów
4. Docker Compose
5. Woluminy i sieci
6. Best practices dla produkcji

Jeśli masz pytania lub chcesz pogłębić konkretny temat, daj znać! 😊

---

## Kubernetes – Orkiestracja Kontenerów

### 1. Wprowadzenie do Kubernetes

Kubernetes to otwartoźródłowa platforma do automatyzacji wdrażania, skalowania i zarządzania aplikacjami kontenerowymi. Zapewnia mechanizmy do zarządzania kontenerami w środowiskach rozproszonych, co jest kluczowe w chmurach hybrydowych.

### 2. Podstawowe Komponenty Kubernetes

- **Pod**: Najmniejsza jednostka w Kubernetes, zawierająca jeden lub więcej kontenerów.
- **Service**: Abstrakcja definiująca zestaw Podów i politykę dostępu.
- **Deployment**: Zarządza deklaratywnym wdrażaniem aplikacji.
- **ReplicaSet**: Zapewnia określoną liczbę replik Podów.
- **Namespace**: Izoluje zasoby w klastrze.

### 3. Deployment i Service

#### Przykład Deployment

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

- **Skalowanie ręczne**:
  ```bash
  kubectl scale deployment nginx-deployment --replicas=5
  ```
- **Autoskalowanie**:
  ```bash
  kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80
  ```

### 5. Monitoring i Logowanie

- **Prometheus i Grafana**: Do monitorowania wydajności i zasobów klastrów.
- **ELK Stack**: Do zarządzania logami i analizy.

### 6. Best Practices w Kubernetes

- **Używaj deklaratywnych konfiguracji**: Zapisuj konfiguracje w plikach YAML.
- **Zarządzaj konfiguracją i sekretami**: Używaj ConfigMaps i Secrets.
- **Implementuj polityki bezpieczeństwa**: Kontroluj dostęp i uprawnienia.
- **Optymalizuj zasoby**: Ustaw limity i prośby zasobów dla kontenerów.

### Podsumowanie Kubernetes

Kubernetes jest potężnym narzędziem do zarządzania kontenerami w skali, oferując automatyzację wdrażania, skalowania i operacji. Jego integracja z Dockerem umożliwia efektywne zarządzanie aplikacjami w chmurach hybrydowych.

### Zarządzanie Deploymentami w Kubernetes

Aby wyłączyć (zatrzymać) Pody Kubernetes o nazwach `drone-swarm-b4cf65d45-*`, możesz usunąć ich Deployment, który je zarządza. Poniżej kroki, jak to zrobić:

#### 1. Znajdź nazwę Deploymentu

Z podanych nazw można wywnioskować, że Deployment nazywa się `drone-swarm`.

Sprawdź nazwę Deploymentu za pomocą:

```bash
kubectl get deployments
```

Powinno wyświetlić coś podobnego do:

```
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm    5/5     5            5           92m
```

#### 2. Usuń Deployment

Aby usunąć Deployment `drone-swarm`, wykonaj:

```bash
kubectl delete deployment drone-swarm
```

To polecenie usunie Deployment oraz wszystkie Pody nim zarządzane.

#### 3. Sprawdź status Podów

Możesz upewnić się, że Pody zostały usunięte, wykonując:

```bash
kubectl get pods
```

Jeśli Pody zostały usunięte, nie powinny już być widoczne na liście.

---

#### Alternatywnie: Skalowanie Deploymentu do zera

Jeśli nie chcesz usuwać Deploymentu, ale chcesz zatrzymać Pody, możesz zmniejszyć liczbę replik do zera:

```bash
kubectl scale deployment drone-swarm --replicas=0
```

To polecenie zatrzyma wszystkie Pody, ale zachowa Deployment, co pozwala później łatwo zwiększyć liczbę replik:

```bash
kubectl scale deployment drone-swarm --replicas=5
```

---

## Docker w Chmurach Hybrydowych

### 1. Co to jest Chmura Hybrydowa?

Chmura hybrydowa łączy zasoby chmury publicznej i prywatnej, umożliwiając płynne przenoszenie aplikacji i danych między nimi. To podejście zapewnia elastyczność, skalowalność i optymalizację kosztów.

### 2. Zalety Docker w Chmurach Hybrydowych

- **Portabilność**: Kontenery Docker działają spójnie w różnych środowiskach, co ułatwia migrację między chmurami.
- **Skalowalność**: Docker umożliwia łatwe skalowanie aplikacji w zależności od zapotrzebowania.
- **Efektywność**: Kontenery są lekkie i szybkie, co pozwala na lepsze wykorzystanie zasobów.

### 3. Przykłady Zastosowań

- **Mikroserwisy**: Budowanie i zarządzanie mikroserwisami w różnych środowiskach chmurowych.
- **DevOps**: Integracja Docker z pipeline CI/CD w chmurach hybrydowych.
- **Migracja Aplikacji**: Przenoszenie aplikacji z lokalnych serwerów do chmur publicznych lub odwrotnie.

### 4. Integracja Docker z Platformami Chmurowymi

- **AWS ECS/EKS**: Zarządzanie kontenerami Docker na Amazon Web Services.
- **Azure Kubernetes Service (AKS)**: Orkiestracja kontenerów Docker na Microsoft Azure.
- **Google Kubernetes Engine (GKE)**: Zarządzanie kontenerami Docker na Google Cloud Platform.

### Podsumowanie Docker w Chmurach Hybrydowych

Docker odgrywa kluczową rolę w implementacji rozwiązań chmur hybrydowych, oferując portabilność, skalowalność i efektywność. Dzięki integracji z platformami chmurowymi, Docker umożliwia elastyczne zarządzanie aplikacjami w różnych środowiskach, co jest niezbędne w nowoczesnych architekturach IT.

---

## Zaawansowane Zarządzanie Rojem Dronów w Kubernetes

### 1. Wprowadzenie

Zarządzanie rojem dronów w Kubernetes wymaga efektywnych metod komunikacji oraz centralizacji zbierania danych. W tym artykule przedstawimy zaawansowane techniki konfiguracji Kubernetes i Docker, które pozwolą na skuteczne zarządzanie dronami oraz zbieranie danych z każdego z nich. Omówimy także alternatywne podejścia oraz rozwiązania problemów związanych z komunikacją i zarządzaniem zasobami.

### 2. Konfiguracja Headless Service dla Rojów Dronów

#### Definicja Headless Service

Headless Service w Kubernetes jest definiowany poprzez ustawienie `clusterIP: None`. Służy on głównie do:

- **Service Discovery**: Umożliwia bezpośredni dostęp do poszczególnych podów za pomocą DNS.
- **Stateful Applications**: Idealny dla aplikacji, które wymagają bezpośredniego połączenia z konkretnym podem.

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

Headless Service nie zapewnia mechanizmu multicastingu UDP do wszystkich podów. Oznacza to, że każda wiadomość UDP jest kierowana tylko do jednego z podów, często do samego nadawcy. To ograniczenie uniemożliwia centralne zbieranie danych od wszystkich dronów.

### 3. Implementacja Centralnego Agregatora Danych

Aby skutecznie zbierać dane od wszystkich dronów, konieczne jest stworzenie centralnego agregatora, który będzie odbierał dane od wszystkich dronów w roju.

#### Tworzenie Skryptu Agregatora

Stwórz skrypt `aggregator.py`, który będzie nasłuchiwał na określonym porcie UDP i zbierał dane od wszystkich dronów.

```python
#aggregator.py
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

Utwórz oddzielny `Dockerfile` dla agregatora, aby móc go wdrożyć jako osobny pod w Kubernetes.

```dockerfile
#aggregator/Dockerfile
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

Upewnij się, że obrazy Docker dla dronów i agregatora są zbudowane i przesłane do rejestru Docker (`localhost:5000` w tym przypadku).

```bash
# Budowanie obrazu drona
cd drones/
drones build -t localhost:5000/mydrone:latest .

# Budowanie obrazu agregatora
cd ../aggregator/
drones build -t localhost:5000/aggregator:latest .

# Push obrazów do lokalnego rejestru
drones push localhost:5000/mydrone:latest
drones push localhost:5000/aggregator:latest
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

### 4. Usuwanie Usługi Mosquitto

Jeśli zdecydujesz się usunąć Mosquitto z klastra Kubernetes, wykonaj poniższe kroki.

#### Sprawdzenie Istniejących Zasobów Mosquitto

Najpierw upewnij się, jakie zasoby są związane z Mosquitto w Twoim klastrze.

##### Wyświetlenie Deployments

```powershell
kubectl get deployments
```

Powinieneś zobaczyć coś takiego:

```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm       0/0     0            0           147m
mosquitto         1/1     1            1           35m
mqtt-aggregator   0/1     1            0           23m
```

##### Wyświetlenie Services

```powershell
kubectl get services
```

Powinieneś zobaczyć coś takiego:

```
NAME            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
drone-service   ClusterIP   None             <none>        5000/TCP   3h36m
kubernetes      ClusterIP   10.96.0.1        <none>        443/TCP    4h3m
mqtt-broker     ClusterIP   10.100.174.192   <none>        1883/TCP   4m41s
```

#### Usunięcie Deployment i Service dla Mosquitto

Aby usunąć Mosquitto, musisz usunąć zarówno **Deployment**, jak i **Service** związane z tym brokerem MQTT.

##### Usunięcie Deployment Mosquitto

```powershell
kubectl delete deployment mosquitto
```

##### Usunięcie Service Mosquitto

```powershell
kubectl delete service mosquitto
```

##### Alternatywnie: Usunięcie Deployment i Service Jednocześnie

Możesz również usunąć oba zasoby jednocześnie za pomocą jednego polecenia:

```powershell
kubectl delete deployment mosquitto service mosquitto
```

#### Weryfikacja Usunięcia Zasobów

Po wykonaniu powyższych kroków, sprawdź, czy zasoby zostały pomyślnie usunięte.

##### Sprawdzenie Deployments

```powershell
kubectl get deployments
```

Powinieneś zobaczyć, że `mosquitto` nie jest już na liście:

```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm       0/0     0            0           147m
mqtt-aggregator   0/1     1            0           23m
```

##### Sprawdzenie Services

```powershell
kubectl get services
```

Powinieneś zobaczyć, że `mosquitto` został usunięty:

```
NAME            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
drone-service   ClusterIP   None             <none>        5000/TCP   3h36m
kubernetes      ClusterIP   10.96.0.1        <none>        443/TCP    4h3m
mqtt-broker     ClusterIP   10.100.174.192   <none>        1883/TCP   4m41s
```

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

Stwórz osobny pod lub aplikację, która subskrybuje na temat `drone/positions` i zbiera dane.

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
drones build -t localhost:5000/mqtt-aggregator:latest .

# Push obrazu do lokalnego rejestru
drones push localhost:5000/mqtt-aggregator:latest

# Zastosowanie konfiguracji w Kubernetes
kubectl apply -f mqtt-aggregator-deployment.yaml
kubectl apply -f mqtt-aggregator-service.yaml
```

### Zalety Użycia MQTT

- **Skalowalność:** MQTT jest zaprojektowany do obsługi dużej liczby klientów.
- **Efektywność:** Lekki protokół, idealny dla IoT i aplikacji z ograniczonymi zasobami.
- **Elastyczność:** Możliwość subskrybowania różnych tematów i filtrowania danych.

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
kubectl apply -f aggregator-api-deployment.yaml
kubectl apply -f aggregator-api-service.yaml
kubectl apply -f drone-deployment.yaml
```

### 6. Rozwiązywanie Problemów w PowerShell

#### Zastąpienie `grep` w PowerShell

W PowerShell zamiast `grep` używamy `Select-String` lub filtrujemy wyniki za pomocą `Where-Object`. Oto jak możesz to zrobić:

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

## Podsumowanie

W tym artykule omówiliśmy zaawansowane techniki zarządzania rojem dronów w Kubernetes, w tym konfigurację headless service, implementację centralnego agregatora danych oraz alternatywne metody agregacji za pomocą message brokerów (MQTT) i HTTP REST API. Przedstawiliśmy także, jak usuwać zasoby w Kubernetes oraz jak rozwiązywać problemy związane z użyciem PowerShell.

### Kluczowe Punkty:

1. **Headless Service** w Kubernetes umożliwia service discovery, ale nie jest odpowiedni do centralnego zbierania danych w przypadku komunikacji UDP.
2. **Centralny Agregator** może skutecznie zbierać dane od wszystkich dronów, zapewniając centralizację i łatwość przetwarzania danych.
3. **Message Brokers** takie jak MQTT oferują skalowalne i efektywne metody publikacji/subskrypcji, idealne do komunikacji IoT.
4. **HTTP REST API** jest prostym i wszechstronnym rozwiązaniem do zbierania danych, umożliwiając łatwą integrację z innymi systemami.
5. **PowerShell** wymaga użycia alternatywnych komend do `grep`, takich jak `Select-String` lub `Where-Object`.

Dzięki tym technikom możesz efektywnie zarządzać rojem dronów w Kubernetes, centralizować dane i zapewnić skalowalność oraz niezawodność swojego systemu.

---
```