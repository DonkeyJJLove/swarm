# Dokumentacja Zarządzania Ekosystemem MQTT (Broker & Aggregator) w Docker i Kubernetes

## Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)
2. [Zaawansowany Kurs Docker](#2-zaawansowany-kurs-docker)
    - [2.1 Podstawowe Komendy Docker (Szybkie Przypomnienie)](#21-podstawowe-komendy-docker-szybkie-przypomnienie)
    - [2.2 Zarządzanie Kontenerami](#22-zarz%C4%85dzanie-kontenerami)
    - [2.3 Budowanie i Optymalizacja Obrazów](#23-budowanie-i-optymalizacja-obra%C5%BC%C3%B3w)
        - [2.3.1 Przykładowy `Dockerfile`](#231-przyk%C5%82adowy-dockerfile)
        - [2.3.2 Budowanie Obrazu](#232-budowanie-obrazu)
        - [2.3.3 Optymalizacja Obrazów](#233-optymalizacja-obra%C5%BC%C3%B3w)
    - [2.4 Docker Compose](#24-docker-compose)
        - [2.4.1 `docker-compose.yml` – Przykład](#241-docker-composeyml-przyk%C5%82ad)
        - [2.4.2 Uruchamianie Docker Compose](#242-uruchamianie-docker-compose)
    - [2.5 Woluminy i Sieci](#25-woluminy-i-sieci)
        - [2.5.1 Woluminy](#251-woluminy)
        - [2.5.2 Sieci](#252-sieci)
    - [2.6 Docker w Produkcji i Best Practices](#26-docker-w-produkcji-i-best-practices)
    - [Podsumowanie](#2-podsumowanie)
3. [Kubernetes – Orkiestracja Kontenerów](#3-kubernetes---orkiestracja-kontenerow)
    - [3.1 Wprowadzenie do Kubernetes](#31-wprowadzenie-do-kubernetes)
    - [3.2 Podstawowe Komponenty Kubernetes](#32-podstawowe-komponenty-kubernetes)
    - [3.3 Deployment i Service](#33-deployment-i-service)
        - [3.3.1 Przykład Deployment](#331-przyk%C5%82ad-deployment)
        - [3.3.2 Przykład Service](#332-przyk%C5%82ad-service)
    - [3.4 Skalowanie Aplikacji](#34-skalowanie-aplikacji)
        - [3.4.1 Skalowanie ręczne](#341-skalowanie-r%C4%99czne)
        - [3.4.2 Autoskalowanie (Horizontal Pod Autoscaler)](#342-autoskalowanie-horizontal-pod-autoscaler)
    - [3.5 Monitoring i Logowanie](#35-monitorowanie-i-logowanie)
    - [3.6 Best Practices w Kubernetes](#36-best-practices-w-kubernetes)
    - [Podsumowanie Kubernetes](#3-podsumowanie-kubernetes)
    - [3.7 Zarządzanie Deploymentami w Kubernetes](#37-zarz%C4%85dzanie-deploymentami-w-kubernetes)
4. [Docker w Chmurach Hybrydowych](#4-docker-w-chmurach-hybrydowych)
    - [4.1 Co to jest Chmura Hybrydowa?](#41-co-to-jest-chmura-hybrydowa)
    - [4.2 Zalety Docker w Chmurach Hybrydowych](#42-zalety-docker-w-chmurach-hybrydowych)
    - [4.3 Przykłady Zastosowań](#43-przyk%C5%82ady-zastosowa%C5%84)
    - [4.4 Integracja Docker z Platformami Chmurowymi](#44-integracja-docker-z-platformami-chmurowymi)
    - [Podsumowanie Docker w Chmurach Hybrydowych](#4-podsumowanie-docker-w-chmurach-hybrydowych)
5. [Zarządzanie Rojem Dronów w Kubernetes](#5-zarz%C4%85dzanie-rojem-dron%C3%B3w-w-kubernetes)
    - [5.1 Wprowadzenie](#51-wprowadzenie)
    - [5.2 Konfiguracja Headless Service dla Rojów Dronów](#52-konfiguracja-headless-service-dla-roj%C3%B3w-dron%C3%B3w)
        - [5.2.1 Definicja Headless Service](#521-definicja-headless-service)
        - [5.2.2 Ograniczenia Headless Service w Komunikacji UDP](#522-ograniczenia-headless-service-w-komunikacji-udp)
    - [5.3 Implementacja Centralnego Agregatora Danych](#53-implementacja-centralnego-agregatora-danych)
        - [5.3.1 Tworzenie Skryptu Agregatora](#531-tworzenie-skryptu-agregatora)
        - [5.3.2 Dockerfile dla Agregatora](#532-dockerfile-dla-agregatora)
        - [5.3.3 Deployment i Service dla Agregatora](#533-deployment-i-service-dla-agregatora)
        - [5.3.4 Modyfikacja Logiki Drona](#534-modyfikacja-logiki-drona)
        - [5.3.5 Aktualizacja Deployment dla Dronów](#535-aktualizacja-deployment-dla-dron%C3%B3w)
        - [5.3.6 Wdrożenie Konfiguracji w Kubernetes](#536-wdro%C5%BCenie-konfiguracji-w-kubernetes)
        - [5.3.7 Weryfikacja Działania Agregatora](#537-weryfikacja-dzia%C5%82ania-agregatora)
    - [5.4 Usuwanie Usługi Mosquitto](#54-usuwanie-us%C5%82ugi-mosquitto)
        - [5.4.1 Sprawdzenie Istniejących Zasobów Mosquitto](#541-sprawdzenie-istniej%C4%85cych-zasob%C3%B3w-mosquitto)
        - [5.4.2 Usunięcie Deployment i Service dla Mosquitto](#542-usuni%C4%99cie-deployment-i-service-dla-mosquitto)
        - [5.4.3 Weryfikacja Usunięcia Zasobów](#543-weryfikacja-usuni%C4%99cia-zasob%C3%B3w)
    - [5.5 Alternatywne Podejścia do Agregacji Danych](#55-alternatywne-podej%C4%85cia-do-agregacji-danych)
        - [5.5.1 Użycie Message Broker (MQTT)](#551-u%C5%BCycie-message-broker-mqtt)
        - [5.5.2 Użycie HTTP REST API](#552-u%C5%BCycie-http-rest-api)
    - [5.6 Rozwiązywanie Problemów w PowerShell](#56-rozwiazywanie-problem%C3%B3w-w-powershell)
        - [5.6.1 Zastąpienie `grep` w PowerShell](#561-zast%C4%85pienie-grep-w-powershell)
    - [5.7 Podsumowanie](#57-podsumowanie)
6. [Opis Projektu](#6-opis-projektu)
    - [6.1 Idea i Koncepcja](#61-idea-i-koncepcja)
    - [6.2 Poziomy Architektoniczne i Komponenty](#62-poziomy-architektoniczne-i-komponenty)
        - [Poziom 1: Fundamenty Komunikacji i Orkiestracji](#poziom-1-fundamenty-komunikacji-i-orkiestracji)
        - [Poziom 2: Drony i Generowanie Danych](#poziom-2-drony-i-generowanie-danych)
        - [Poziom 3: Agregacja Danych i API](#poziom-3-agregacja-danych-i-api)
        - [Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD](#poziom-4-narz%C4%99dzia-wspomagaj%C4%85ce-monitoring-cicd)
        - [Poziom 5: Bezpieczeństwo i Izolacja](#poziom-5-bezpiecze%C5%84stwo-i-izolacja)
    - [6.3 Integracja i Przepływ](#63-integracja-i-przep%C5%82yw)
    - [6.4 Rola dla Modeli AI](#64-rola-dla-modeli-ai)
7. [Podsumowanie](#7-podsumowanie)
8. [Informacje z Istniejących Plików](#8-informacje-z-istniej%C4%85cych-plik%C3%B3w)
9. [Odnośniki](#9-odno%C5%9Bniki)

---

## 1. Wprowadzenie

Zarządzanie rojem dronów w środowisku chmurowym to złożony, wielowymiarowy proces, który integruje zaawansowane techniki konteneryzacji, orkiestracji, komunikacji oraz inteligentnego sterowania. Głównym celem jest traktowanie każdego drona jako niezależnego kontenera, co umożliwia jego autonomiczne działanie oraz płynną komunikację z innymi dronami i komponentami systemu. Wykorzystanie podejścia chmurowego pozwala na dynamiczne skalowanie liczby dronów w zależności od aktualnych potrzeb, automatyzację procesów wdrażania i aktualizacji oraz zastosowanie zaawansowanych narzędzi do monitoringu i analizy danych.

---

## 2. Zaawansowany Kurs Docker

### 2.1 Podstawowe Komendy Docker (Szybkie Przypomnienie)

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

### 2.2 Zarządzanie Kontenerami

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

### 2.3 Budowanie i Optymalizacja Obrazów

Tworzenie własnych obrazów Docker pozwala na pełną kontrolę nad środowiskiem aplikacji.

#### 2.3.1 Przykładowy `Dockerfile`

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

#### 2.3.2 Budowanie Obrazu

Aby zbudować obraz Docker na podstawie `Dockerfile`, użyj poniższej komendy:

```bash
docker build -t my-python-app:latest .
```

#### 2.3.3 Optymalizacja Obrazów

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

### 2.4 Docker Compose

Docker Compose umożliwia definiowanie i uruchamianie wielu kontenerów jako jednej usługi.

#### 2.4.1 `docker-compose.yml` – Przykład

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

#### 2.4.2 Uruchamianie Docker Compose

- **Uruchomienie usług**:
  ```bash
  docker-compose up -d
  ```

- **Zatrzymanie usług**:
  ```bash
  docker-compose down
  ```

---

### 2.5 Woluminy i Sieci

Woluminy i sieci w Docker pozwalają na trwałe przechowywanie danych oraz komunikację między kontenerami.

#### 2.5.1 Woluminy

- **Tworzenie woluminu**:
  ```bash
  docker volume create my-volume
  ```

- **Używanie woluminu w kontenerze**:
  ```bash
  docker run -d -v my-volume:/data ubuntu
  ```

#### 2.5.2 Sieci

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

### 2.6 Docker w Produkcji i Best Practices

Przygotowanie kontenerów Docker do środowiska produkcyjnego wymaga przestrzegania najlepszych praktyk.

- **Minimalizuj rozmiar obrazów**: Używaj obrazów typu `alpine` lub `slim`, które są lekkie i szybkie.
  
- **Używaj `docker-compose` lub `Docker Swarm`** do zarządzania wieloma kontenerami, co ułatwia orkiestrację i skalowanie.
  
- **Logowanie i monitorowanie**: Implementuj rozwiązania takie jak `ELK Stack` (Elasticsearch, Logstash, Kibana) oraz `Prometheus` + `Grafana` do monitorowania i analizy logów.
  
- **Bezpieczeństwo**:
  - **Nie uruchamiaj kontenerów jako `root`**: Twórz użytkowników o ograniczonych uprawnieniach w `Dockerfile`.
  - **Ustaw limity zasobów**: Określ limity pamięci i CPU (`--memory`, `--cpus`) podczas uruchamiania kontenerów.
  - **Skanuj obrazy za pomocą `docker scan`**: Regularnie sprawdzaj obrazy pod kątem luk bezpieczeństwa.

---

### 2.7 Podsumowanie

Ten zaawansowany kurs Dockera obejmował kluczowe zagadnienia niezbędne do efektywnego zarządzania kontenerami w środowisku produkcyjnym:

1. **Podstawowe komendy Docker**
2. **Zarządzanie kontenerami**
3. **Budowanie i optymalizacja obrazów**
4. **Docker Compose**
5. **Woluminy i sieci**
6. **Best practices dla produkcji**

Opanowanie tych tematów pozwoli Ci na pełne wykorzystanie możliwości Dockera w projektach kontenerowych, takich jak zarządzanie rojem dronów w Kubernetes.

---

## 3. Kubernetes – Orkiestracja Kontenerów

### 3.1 Wprowadzenie do Kubernetes

Kubernetes to otwartoźródłowa platforma do automatyzacji wdrażania, skalowania i zarządzania aplikacjami kontenerowymi. Umożliwia efektywne zarządzanie dużymi środowiskami kontenerowymi, co jest kluczowe w kontekście chmur hybrydowych.

### 3.2 Podstawowe Komponenty Kubernetes

Zrozumienie podstawowych komponentów Kubernetes jest niezbędne do efektywnego zarządzania klastrem.

- **Pod**: Najmniejsza jednostka w Kubernetes, zawierająca jeden lub więcej kontenerów.
- **Service**: Abstrakcja definiująca zestaw Podów i politykę dostępu.
- **Deployment**: Zarządza deklaratywnym wdrażaniem aplikacji, automatyzując proces aktualizacji.
- **ReplicaSet**: Zapewnia określoną liczbę replik Podów, zapewniając wysoką dostępność.
- **Namespace**: Izoluje zasoby w klastrze, umożliwiając podział środowiska na różne obszary.

### 3.3 Deployment i Service

#### 3.3.1 Przykład Deployment

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

#### 3.3.2 Przykład Service

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

### 3.4 Skalowanie Aplikacji

Kubernetes oferuje różne metody skalowania aplikacji, aby dostosować się do zmieniających się obciążeń.

- **Skalowanie ręczne**:
  ```bash
  kubectl scale deployment nginx-deployment --replicas=5
  ```

- **Autoskalowanie (Horizontal Pod Autoscaler)**:
  ```bash
  kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80
  ```

### 3.5 Monitoring i Logowanie

Monitorowanie i logowanie są kluczowe dla utrzymania zdrowia klastrów i aplikacji.

- **Prometheus i Grafana**: Do monitorowania wydajności i zasobów klastrów oraz wizualizacji danych.
- **ELK Stack (Elasticsearch, Logstash, Kibana)**: Do zarządzania logami i ich analizy.

### 3.6 Best Practices w Kubernetes

Przestrzeganie najlepszych praktyk zapewnia stabilność, bezpieczeństwo i efektywność środowiska Kubernetes.

- **Używaj deklaratywnych konfiguracji**: Zapisuj konfiguracje w plikach YAML, co ułatwia wersjonowanie i zarządzanie zmianami.
- **Zarządzaj konfiguracją i sekretami**: Używaj ConfigMaps i Secrets do przechowywania konfiguracji aplikacji oraz danych wrażliwych.
- **Implementuj polityki bezpieczeństwa**: Kontroluj dostęp i uprawnienia za pomocą RBAC (Role-Based Access Control) oraz Network Policies.
- **Optymalizuj zasoby**: Ustaw limity i prośby zasobów (`requests` i `limits`) dla kontenerów, aby efektywnie wykorzystywać zasoby klastrów.

### 3.7 Zarządzanie Deploymentami w Kubernetes

Zarządzanie Deploymentami pozwala na efektywne kontrolowanie liczby replik Podów oraz aktualizowanie aplikacji bez przestojów.

#### 3.7.1 Znajdź nazwę Deploymentu

Aby zarządzać Deploymentem, najpierw zidentyfikuj jego nazwę:

```bash
kubectl get deployments
```

Przykładowy wynik:

```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
drone-swarm       5/5     5            5           92m
```

#### 3.7.2 Usuń Deployment

Aby usunąć Deployment i wszystkie przez niego zarządzane Pody:

```bash
kubectl delete deployment drone-swarm
```

#### 3.7.3 Sprawdź status Podów

Upewnij się, że Pody zostały usunięte:

```bash
kubectl get pods
```

Pody zarządzane przez usunięty Deployment nie powinny już być widoczne na liście.

---

### 3.8 Skalowanie Deploymentu do zera

Jeśli nie chcesz usuwać Deploymentu, ale chcesz zatrzymać Pody, możesz zmniejszyć liczbę replik do zera:

```bash
kubectl scale deployment drone-swarm --replicas=0
```

To polecenie zatrzyma wszystkie Pody, ale zachowa Deployment, umożliwiając późniejsze łatwe zwiększenie liczby replik:

```bash
kubectl scale deployment drone-swarm --replicas=5
```

---

## 4. Docker w Chmurach Hybrydowych

### 4.1 Co to jest Chmura Hybrydowa?

Chmura hybrydowa łączy zasoby chmury publicznej i prywatnej, umożliwiając płynne przenoszenie aplikacji i danych między nimi. To podejście zapewnia elastyczność, skalowalność oraz optymalizację kosztów, umożliwiając korzystanie z najlepszych cech obu typów chmur.

### 4.2 Zalety Docker w Chmurach Hybrydowych

Docker odgrywa kluczową rolę w implementacji rozwiązań chmur hybrydowych dzięki swoim unikalnym cechom:

- **Portabilność**: Kontenery Docker działają spójnie w różnych środowiskach, co ułatwia migrację aplikacji między chmurami publicznymi, prywatnymi i lokalnymi.
  
- **Skalowalność**: Docker umożliwia łatwe skalowanie aplikacji w zależności od zapotrzebowania, zarówno w środowiskach chmurowych, jak i lokalnych.
  
- **Efektywność**: Kontenery są lekkie i szybkie, co pozwala na lepsze wykorzystanie zasobów w różnych środowiskach chmurowych.

### 4.3 Przykłady Zastosowań

- **Mikroserwisy**: Docker ułatwia budowanie i zarządzanie mikroserwisami w różnych środowiskach chmurowych, zapewniając niezależność i łatwość skalowania poszczególnych komponentów.
  
- **DevOps**: Integracja Docker z pipeline CI/CD (Continuous Integration/Continuous Deployment) w chmurach hybrydowych umożliwia automatyczne testowanie, budowanie i wdrażanie aplikacji.
  
- **Migracja Aplikacji**: Docker ułatwia przenoszenie aplikacji z lokalnych serwerów do chmur publicznych lub odwrotnie, minimalizując problemy związane z kompatybilnością środowisk.

### 4.4 Integracja Docker z Platformami Chmurowymi

Docker można łatwo zintegrować z różnymi platformami chmurowymi, co umożliwia efektywne zarządzanie i wdrażanie kontenerów.

- **AWS ECS/EKS**: Zarządzanie kontenerami Docker na Amazon Web Services za pomocą Amazon Elastic Container Service (ECS) lub Amazon Elastic Kubernetes Service (EKS).
  
- **Azure Kubernetes Service (AKS)**: Orkiestracja kontenerów Docker na Microsoft Azure za pomocą AKS, co umożliwia łatwe zarządzanie klastrami Kubernetes.
  
- **Google Kubernetes Engine (GKE)**: Zarządzanie kontenerami Docker na Google Cloud Platform za pomocą GKE, oferując automatyzację i skalowanie klastrów Kubernetes.

### 4.5 Podsumowanie Docker w Chmurach Hybrydowych

Docker odgrywa kluczową rolę w implementacji rozwiązań chmur hybrydowych, oferując portabilność, skalowalność i efektywność. Dzięki integracji z platformami chmurowymi, Docker umożliwia elastyczne zarządzanie aplikacjami w różnych środowiskach, co jest niezbędne w nowoczesnych architekturach IT. To podejście zapewnia elastyczność, skalowalność oraz optymalizację kosztów, umożliwiając korzystanie z najlepszych cech chmur publicznych i prywatnych.

---

## 5. Zarządzanie Rojem Dronów w Kubernetes

### 5.1 Wprowadzenie

Zarządzanie rojem dronów w Kubernetes wymaga efektywnych metod komunikacji oraz centralizacji zbierania danych. W tym przewodniku przedstawimy zaawansowane techniki konfiguracji Kubernetes i Docker, które pozwolą na skuteczne zarządzanie dronami oraz zbieranie danych z każdego z nich. Omówimy także alternatywne podejścia oraz rozwiązania problemów związanych z komunikacją i zarządzaniem zasobami.

### 5.2 Konfiguracja Headless Service dla Rojów Dronów

#### 5.2.1 Definicja Headless Service

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

#### 5.2.2 Ograniczenia Headless Service w Komunikacji UDP

Headless Service nie zapewnia mechanizmu multicastingu UDP do wszystkich Podów. Oznacza to, że każda wiadomość UDP jest kierowana tylko do jednego z Podów, często do samego nadawcy. To ograniczenie uniemożliwia centralne zbieranie danych od wszystkich dronów.

### 5.3 Implementacja Centralnego Agregatora Danych

Aby skutecznie zbierać dane od wszystkich dronów, konieczne jest stworzenie centralnego agregatora, który będzie odbierał dane od wszystkich dronów w roju.

#### 5.3.1 Tworzenie Skryptu Agregatora

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

#### 5.3.2 Dockerfile dla Agregatora

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

#### 5.3.3 Deployment i Service dla Agregatora

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

#### 5.3.4 Modyfikacja Logiki Drona

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

#### 5.3.5 Aktualizacja Deployment dla Dronów

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

#### 5.3.6 Wdrożenie Konfiguracji w Kubernetes

Upewnij się, że obrazy Docker dla dronów i agregatora są zbudowane i przesłane do rejestru Docker (`localhost:5000` w tym przypadku).

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

### 5.4 Usuwanie Usługi Mosquitto

Jeśli zdecydujesz się usunąć Mosquitto z klastra Kubernetes, wykonaj poniższe kroki.

#### 5.4.1 Sprawdzenie Istniejących Zasobów Mosquitto

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

#### 5.4.2 Usunięcie Deployment i Service dla Mosquitto

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

#### 5.4.3 Weryfikacja Usunięcia Zasobów

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

### 5.5 Alternatywne Podejścia do Agregacji Danych

Oprócz centralnego agregatora UDP, istnieją inne metody centralizacji danych od dronów, takie jak użycie message brokerów (np. MQTT) lub HTTP REST API.

#### 5.5.1 Użycie Message Broker (MQTT)

**MQTT** jest lekkim protokołem publikacja/subskrypcja, idealnym do komunikacji IoT. Każdy dron może publikować swoje dane na określonym temacie, a agregator/subskrybent może odbierać te dane.

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

---

### 5.6 Rozwiązywanie Problemów w PowerShell

PowerShell nie posiada bezpośredniego odpowiednika `grep`, ale można użyć `Select-String` lub `Where-Object` do filtrowania wyników.

#### 5.6.1 Zastąpienie `grep` w PowerShell

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

### 5.7 Podsumowanie

W tej sekcji omówiliśmy zaawansowane techniki zarządzania rojem dronów w Kubernetes, w tym:

1. **Konfigurację Headless Service**: Umożliwiającą bezpośrednią komunikację między Podami.
2. **Implementację centralnego agregatora danych**: Odbierającego i przetwarzającego dane z dronów.
3. **Usuwanie usług Mosquitto**: Jeśli zdecydujesz się na alternatywne metody agregacji danych.
4. **Alternatywne podejścia do agregacji danych**: Takie jak MQTT i HTTP REST API.
5. **Rozwiązywanie problemów w PowerShell**: Jak zastąpić `grep` w środowisku PowerShell.

Dzięki tym technikom możesz efektywnie zarządzać rojem dronów, zbierać i analizować dane oraz zapewnić stabilność i skalowalność swojego środowiska Kubernetes.

---

## 6. Opis Projektu

### 6.1 Idea i Koncepcja

W centrum projektu znajduje się symulacja roju dronów działających w środowisku chmurowym i kontenerowym. Każdy dron funkcjonuje jako autonomiczny kontener, komunikujący się z pozostałymi elementami systemu za pomocą protokołu MQTT. Wspólna komunikacja oparta o model publikacja-subskrypcja (publish-subscribe) zapewnia luźne powiązanie komponentów, elastyczność i skalowalność.

**Główne założenia:**

1. **Autonomiczne Kontenery/Drony** – Każdy dron jest kontenerem, generującym dane o swojej pozycji, stanie baterii i innych parametrach.
2. **Komunikacja MQTT** – Drony publikują dane do brokera MQTT, a inne komponenty, takie jak agregator, subskrybują te informacje.
3. **Architektura Kontenerowa w Kubernetes** – Całość wdrożenia opiera się na orkiestracji Kubernetes, zapewniając skalowalność, niezawodność, elastyczność i prostotę zarządzania.
4. **Agregacja i Dostęp do Danych** – Agregator zbiera dane z dronów, przetwarza je i udostępnia zewnętrznemu światu poprzez REST API (aggregator-api), co umożliwia zarządzanie rojem i analizę danych.
5. **Monitorowanie, CI/CD, Bezpieczeństwo** – Projekt uwzględnia pipeline’y CI/CD, monitoring (Prometheus, Grafana), logowanie (ELK), strategie wdrożeń (Blue-Green, Canary), bezpieczeństwo (RBAC, Network Policies, szyfrowanie).

### 6.2 Poziomy Architektoniczne i Komponenty

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
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów systemu, wspierając diagnozę i debugowanie.

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

## 6. Integracja i Przepływ

1. **Drony** publikują dane o swojej pozycji i stanie przez MQTT:
   - **MQTT Broker** (Mosquitto) odbiera i przechowuje te informacje tymczasowo.
   
2. **Agregator** subskrybuje temat `drones/+/position`:
   - Przetwarza dane i agreguje je, tworząc jednolitą bazę informacji o stanie całego roju.
   - Agregator może również zapisywać dane do bazy danych oraz przekazywać je dalej do Aggregator API.
   
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

## 7. Rola dla Modeli AI

Ten opis służy jako główny punkt odniesienia dla modeli AI, które mają operować na kodzie i logice projektu. Dzięki niemu:

- **Modele językowe** mogą łatwiej zrozumieć kontekst, rolę i powiązania między elementami kodu.
- **Generatory kodu** opierają się na wspólnych założeniach architektonicznych, mając mapę połączeń i zrozumienie, gdzie wdrożyć nowe funkcjonalności.
- **Analityczne modele AI** łatwiej identyfikują punkty wejścia do optymalizacji (np. poprawa wydajności MQTT, zwiększenie bezpieczeństwa) i wiedzą, gdzie ingerować w kod lub konfigurację.

---

## 8. Informacje z Istniejących Plików

Poniżej znajduje się tabela zawierająca odnośniki do istniejących dokumentów w katalogu `_docs/` oraz ich opisy:

| **Dokument**                                       | **Link**                                                                                   | **Opis**                                                         |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Strategie wdrożeń Blue-Green i Canary             | [strategia_blue_green_canary.md](./strategia_blue_green_canary.md)                        | Strategie wdrożeń Blue-Green i Canary.                          |
| Ogólny opis projektu                               | [readme.md](./readme.md)                                                                  | Ogólny opis projektu: symulacja roju, komunikacja MQTT, wdrożenie, monitoring, CI/CD. |
| Dokumentacja Brokera MQTT                          | [broker_mqtt.md](./broker_mqtt.md)                                                        | Szczegółowa Dokumentacja Brokera MQTT.                           |
| Szczegółowy opis agregatora                        | [aggregator_details.md](./aggregator_details.md)                                          | Szczegółowy opis agregatora.                                     |
| Szczegółowy opis Aggregator API                    | [aggregator_api_details.md](./aggregator_api_details.md)                                  | Szczegółowy opis Aggregator API.                                 |
| Dokumentacja Bazy Danych                           | [database.md](./database.md)                                                                | Dokumentacja Bazy Danych.                                        |
| Dokumentacja Frontend                               | [frontend.md](./frontend.md)                                                                | Dokumentacja Frontend.                                            |

---

## 9. Odnośniki

- [Wprowadzenie do Docker i Kubernetes - Chmury Hybrydowe](./readme.md)
- [Kubernetes – Orkiestracja Kontenerów](./readme.md#3-kubernetes---orkiestracja-kontenerow)
- [Docker w Chmurach Hybrydowych](./readme.md#4-docker-w-chmurach-hybrydowych)
- [Strategia Blue-Green i Canary](./strategia_blue_green_canary.md)
- [Ogólny Opis Projektu](./readme.md#6-opis-projektu)
- [Dokumentacja Brokera MQTT](./broker_mqtt.md)
- [Szczegółowy opis agregatora](./aggregator_details.md)
- [Szczegółowy opis Aggregator API](./aggregator_api_details.md)
- [Dokumentacja Bazy Danych](./database.md)
- [Dokumentacja Frontend](./frontend.md)

---
