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

---

## Zaawansowany Kurs Docker

1. **Podstawowe Komendy** (szybkie przypomnienie)
2. **Zaawansowane Zarządzanie Kontenerami**
3. **Budowanie i Optymalizacja Obrazów**
4. **Docker Compose**
5. **Zarządzanie Woluminami i Sieciami**
6. **Docker w Produkcji i Best Practices**

### 1. Podstawowe Komendy Docker (Szybkie Przypomnienie)

- **Lista kontenerów**:
  ```bash
  docker ps            # Kontenery uruchomione
  docker ps -a         # Wszystkie kontenery
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

- **Uruchomienie kontenera w tle**:
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

- **Logi z kontenera**:
  ```bash
  docker logs my-nginx
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
docker build -t my-python-app .
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
  docker-compose up -d
  ```

- **Zatrzymanie usług**:
  ```bash
  docker-compose down
  ```

---

### 5. Woluminy i Sieci

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
