## **I. Budowanie i Zarządzanie Obrazami Dockerowymi**

### **Krok 1: Pobieranie Obrazu Bazowego**

Pobierz obraz bazowy dla środowiska Python 3.11.

```bash
docker pull python:3.11-slim
```

---

### **Krok 2: Struktura Projektu**

Przygotuj strukturę projektu z następującymi katalogami i plikami:

```
dockerBotnet/
│-- aggregator/
│   └── aggregator.py
│   └── Dockerfile
│-- drones/
│   └── drone_service.py
│   └── Dockerfile
│-- server/
│   └── mqtt/
│       └── mqtt_aggregator.py
│       └── Dockerfile
│-- .dockerignore
│-- requirements.txt
```

---

### **Krok 3: Plik `.dockerignore`**

Stwórz plik `.dockerignore`, aby wykluczyć niepotrzebne pliki z budowania obrazu.

**Przykładowa zawartość `.dockerignore`:**

```
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.env
```

---

### **Krok 4: Tworzenie `Dockerfile`**

#### **`Dockerfile` dla Agregatora**

**Lokalizacja:** `aggregator/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY aggregator.py /app/aggregator.py
COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "aggregator.py"]
```

#### **`Dockerfile` dla Drona**

**Lokalizacja:** `drones/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY drone_service.py /app/drone_service.py
COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "drone_service.py"]
```

#### **`Dockerfile` dla Brokera MQTT**

**Lokalizacja:** `server/mqtt/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY mqtt_aggregator.py /app/mqtt_aggregator.py
COPY ../../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "mqtt_aggregator.py"]
```

---

### **Krok 5: Budowanie Obrazów Dockerowych**

#### **Budowanie Obrazu Agregatora**

```bash
docker build -t data-aggregator:1.0 -f aggregator/Dockerfile .
```

#### **Budowanie Obrazu Drona**

```bash
docker build -t drone-service:1.0 -f drones/Dockerfile .
```

#### **Budowanie Obrazu Brokera MQTT**

```bash
docker build -t mqtt-broker:1.0 -f server/mqtt/Dockerfile .
```

---

### **Krok 6: Sprawdzanie Dostępnych Obrazów**

```bash
docker images
```

**Przykładowy wynik:**

```
REPOSITORY        TAG     IMAGE ID       CREATED         SIZE
data-aggregator   1.0     2f794fd50176   13 minutes ago  194MB
drone-service     1.0     eae909d517a4   2 hours ago     194MB
mqtt-broker       1.0     48fc7ef99f73   3 hours ago     212MB
```

---

### **Krok 7: Uruchamianie Kontenerów**

#### **Uruchomienie Agregatora**

```bash
docker run -d --name data-aggregator-container -p 5001:5001 data-aggregator:1.0
```

#### **Uruchomienie Drona**

```bash
docker run -d --name drone-service-container -p 5000:5000 drone-service:1.0
```

#### **Uruchomienie Brokera MQTT**

```bash
docker run -d --name mqtt-broker-container -p 1883:1883 mqtt-broker:1.0
```

---

### **Krok 8: Sprawdzanie Uruchomionych Kontenerów**

```bash
docker ps
```

---

### **Krok 9: Usuwanie Kontenerów i Obrazów**

#### **Usuwanie Kontenera**

```bash
docker rm -f data-aggregator-container
```

#### **Usuwanie Obrazu**

```bash
docker rmi data-aggregator:1.0
```

---

## **2. Wdrażanie do Kubernetes**

### **Manifest Deployment dla Agregatora**

**Plik:** `aggregator-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator-deployment
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
          image: localhost:5000/data-aggregator:1.0
          ports:
            - containerPort: 5001
```

### **Manifest Service dla Agregatora**

**Plik:** `aggregator-service.yaml`

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
```

### **Zastosowanie Manifestów**

```bash
kubectl apply -f aggregator-deployment.yaml
kubectl apply -f aggregator-service.yaml
```

---

## **3. Monitorowanie i Debugowanie**

### **Sprawdzenie Statusu Podów**

```bash
kubectl get pods
```

### **Logi Podów**

```bash
kubectl logs <nazwa-poda>
```

### **Szczegółowy Opis Podów**

```bash
kubectl describe pods
```

---

### **Podsumowanie Kroków**

1. **Budowanie obrazów Dockerowych**:

   ```bash
   docker build -t data-aggregator:1.0 -f aggregator/Dockerfile .
   docker build -t drone-service:1.0 -f drones/Dockerfile .
   docker build -t mqtt-broker:1.0 -f server/mqtt/Dockerfile .
   ```

2. **Wdrażanie do Kubernetes**:

   ```bash
   kubectl apply -f aggregator-deployment.yaml
   kubectl apply -f aggregator-service.yaml
   ```

3. **Monitorowanie i debugowanie**:

   ```bash
   kubectl get pods
   kubectl logs <nazwa-poda>
   ``` 

### **Dodanie Skalowania w Kubernetes**

---

## **II. Skalowanie Deploymentów w Kubernetes**

Skalowanie pozwala dostosować liczbę replik do potrzeb wydajnościowych. Możemy to zrobić na dwa sposoby:

1. **Statyczne skalowanie za pomocą deklaracji w manifeście.**
2. **Dynamiczne skalowanie za pomocą komendy `kubectl scale`.**

---

### **1. Statyczne Skalowanie w Manifeście**

Możesz ustawić liczbę replik w pliku `Deployment`.

#### **Przykład Skalowalnego Deploymentu dla Agregatora**

**Plik:** `aggregator-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator-deployment
spec:
  replicas: 3  # Skalowanie na 3 repliki
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
          image: localhost:5000/data-aggregator:1.0
          ports:
            - containerPort: 5001
```

---

### **2. Dynamiczne Skalowanie z `kubectl`**

Możesz również skalować Deployment w czasie rzeczywistym za pomocą komendy `kubectl scale`.

#### **Skalowanie na 5 Replik**

```bash
kubectl scale deployment aggregator-deployment --replicas=5
```

#### **Sprawdzenie Aktualnej Liczby Replik**

```bash
kubectl get deployment aggregator-deployment
```

**Przykładowy wynik:**

```
NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
aggregator-deployment  5/5     5            5           2m
```

---

### **Automatyczne Skalowanie (HPA - Horizontal Pod Autoscaler)**

Możesz również skonfigurować automatyczne skalowanie na podstawie zużycia zasobów (CPU i RAM).

#### **Utworzenie Autoscalera**

**Przykład:** Skalowanie od 2 do 10 replik, gdy użycie CPU przekroczy 80%.

```bash
kubectl autoscale deployment aggregator-deployment --min=2 --max=10 --cpu-percent=80
```

#### **Sprawdzenie Statusu Autoscalera**

```bash
kubectl get hpa
```

**Przykładowy wynik:**

```
NAME                   REFERENCE                         TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
aggregator-deployment  Deployment/aggregator-deployment 70%/80%   2         10        4          5m
```

---

## **Podsumowanie Skalowania**

1. **Statyczne skalowanie** w pliku `Deployment` (`replicas`).
2. **Dynamiczne skalowanie** za pomocą komendy `kubectl scale`.
3. **Automatyczne skalowanie** z użyciem Horizontal Pod Autoscaler (HPA).

Dzięki tym metodom możesz dostosować wydajność swojej aplikacji do aktualnych potrzeb.