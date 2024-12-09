# Dokumentacja Zarządzania Ekosystemem MQTT (Broker & Aggregator) w Docker i Kubernetes

## Spis treści

1. [Wprowadzenie](#wprowadzenie)  
2. [Zarządzanie Obrazami i Rejestrem Docker](#zarządzanie-obrazami-i-rejestrem-docker)  
    - [Uruchomienie Lokalnego Rejestru Docker](#uruchomienie-lokalnego-rejestru-docker)  
    - [Budowanie Obrazów](#budowanie-obrazów)  
    - [Tagowanie i Push Obrazów do Rejestru](#tagowanie-i-push-obrazów-do-rejestru)  
    - [Czyszczenie Obrazów i Kontenerów](#czyszczenie-obrazów-i-kontenerów)
3. [Struktura Projektu i Pliki Konfiguracyjne](#struktura-projektu-i-pliki-konfiguracyjne)  
    - [Dockerfile, requirements.txt, mqtt_aggregator.py, mosquitto.conf](#dockerfile-requirementstxt-mqtt_aggregatorpy-mosquittoconf)
4. [Wdrażanie do Kubernetes](#wdrażanie-do-kubernetes)  
    - [Zastosowanie ConfigMap dla Mosquitto](#zastosowanie-configmap-dla-mosquitto)  
    - [Deployment i Service dla mqtt-broker](#deployment-i-service-dla-mqtt-broker)  
    - [Deployment dla mqtt-aggregator z initContainer](#deployment-dla-mqtt-aggregator-z-initcontainer)
5. [Monitorowanie i Debugowanie w Kubernetes](#monitorowanie-i-debugowanie-w-kubernetes)  
    - [Sprawdzanie Podów i Usług](#sprawdzanie-podów-i-usług)  
    - [Logi Podów i Deploymentów](#logi-podów-i-deploymentów)  
    - [Describe i Debugowanie Problemów z Połączeniem](#describe-i-debugowanie-problemów-z-połączeniem)
6. [Aktualizacja i Rollout](#aktualizacja-i-rollout)  
    - [Aktualizacja Obrazu w Deployment](#aktualizacja-obrazu-w-deployment)  
    - [Rollback do Poprzedniej Wersji](#rollback-do-poprzedniej-wersji)
7. [Skalowanie Deploymentów w Kubernetes](#skalowanie-deploymentów-w-kubernetes)  
    - [Statyczne Skalowanie](#statyczne-skalowanie)  
    - [Dynamiczne Skalowanie za pomocą kubectl scale](#dynamiczne-skalowanie-za-pomocą-kubectl-scale)  
    - [Automatyczne Skalowanie (HPA)](#automatyczne-skalowanie-hpa)
8. [Troubleshooting i Najlepsze Praktyki](#troubleshooting-i-najlepsze-praktyki)  
    - [Brak Logów w Kontenerze](#brak-logów-w-kontenerze)  
    - [Problemy z Połączeniem MQTT](#problemy-z-połączeniem-mqtt)  
    - [Nadpisywanie Komend Startowych](#nadpisywanie-komend-startowych)

---

## Wprowadzenie

Dokument ten prezentuje kompleksowy zestaw instrukcji i najlepszych praktyk dotyczących zarządzania ekosystemem aplikacji w oparciu o Docker i Kubernetes. W przykładzie wykorzystujemy `mqtt-broker` (Mosquitto) i `mqtt-aggregator` do ilustrowania procesów tworzenia obrazów, wdrażania w Kubernetes, skalowania i debugowania.

---

## Zarządzanie Obrazami i Rejestrem Docker

### Uruchomienie Lokalnego Rejestru Docker

Aby korzystać z własnego, lokalnego rejestru obrazów:

```bash
docker run -d -p 5000:5000 --restart always --name registry registry:2
```

Sprawdzenie zawartości rejestru:

```bash
curl http://localhost:5000/v2/_catalog
```

---

### Budowanie Obrazów

Przykładowe polecenie budowania obrazu `mqtt-aggregator`:

```bash
docker build -t mqtt-aggregator:latest .
```

Upewnij się, że posiadasz odpowiednie `Dockerfile` oraz pozostałe pliki źródłowe w tym samym katalogu.

---

### Tagowanie i Push Obrazów do Rejestru

Po zbudowaniu obrazu otaguj go, aby wskazać lokalny rejestr:

```bash
docker tag mqtt-aggregator:latest localhost:5000/mqtt-aggregator:latest
docker push localhost:5000/mqtt-aggregator:latest
```

---

### Czyszczenie Obrazów i Kontenerów

Usuwanie nieużywanych obrazów i kontenerów:

```bash
docker rm -f <nazwa_kontenera>       # usuwa kontener
docker rmi <nazwa_obrazu>:<tag>      # usuwa obraz
docker image prune -a -f             # usuwa wszystkie nieużywane obrazy
```

---

## Struktura Projektu i Pliki Konfiguracyjne

Przykładowa struktura katalogu:

```
dockerBotnet/
├─ server/
│  └─ mqtt/
│     ├─ mqtt_aggregator.py
│     ├─ requirements.txt
│     ├─ Dockerfile
│     ├─ mosquitto.conf
│     ├─ mosquitto-deployment.yaml
│     ├─ mosquitto-service.yaml
│     └─ mqtt_aggregator-deployment.yaml
```

### Dockerfile, requirements.txt, mqtt_aggregator.py, mosquitto.conf

- **`requirements.txt`**: zawiera zależności np. `paho-mqtt==1.6.1`
- **`mqtt_aggregator.py`**: skrypt Python łączący się z brokerem, subskrybujący tematy i logujący otrzymane wiadomości.
- **`mosquitto.conf`**: konfiguracja Mosquitto (np. `listener 1883` i `allow_anonymous true`), aby broker akceptował połączenia spoza localhost.
- **`Dockerfile`**: definiuje proces budowy obrazu zawierającego kod `mqtt_aggregator.py` i instalującego zależności.

---

## Wdrażanie do Kubernetes

### Zastosowanie ConfigMap dla Mosquitto

Tworzenie ConfigMap z pliku `mosquitto.conf`:

```bash
kubectl create configmap mosquitto-config --from-file=mosquitto.conf
```

### Deployment i Service dla mqtt-broker

**`mosquitto-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mqtt-broker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mqtt-broker
  template:
    metadata:
      labels:
        app: mqtt-broker
    spec:
      volumes:
        - name: config-volume
          configMap:
            name: mosquitto-config
      containers:
        - name: mqtt-broker
          image: eclipse-mosquitto:latest
          volumeMounts:
            - name: config-volume
              mountPath: /mosquitto/config
          ports:
            - containerPort: 1883
```

**`mosquitto-service.yaml`:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mqtt-broker
spec:
  selector:
    app: mqtt-broker
  ports:
    - port: 1883
      targetPort: 1883
```

Zastosowanie:

```bash
kubectl apply -f mosquitto-deployment.yaml
kubectl apply -f mosquitto-service.yaml
```

### Deployment dla mqtt-aggregator z initContainer

**`mqtt_aggregator-deployment.yaml`:**

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
      initContainers:
        - name: wait-for-mqtt
          image: nicolaka/netshoot
          command: ['sh', '-c', 'until nc -z mqtt-broker 1883; do echo waiting for mqtt-broker; sleep 2; done']
      containers:
        - name: mqtt-aggregator
          image: localhost:5000/mqtt-aggregator:latest
          env:
            - name: MQTT_BROKER
              value: "mqtt-broker"
            - name: MQTT_PORT
              value: "1883"
```

Zastosowanie:

```bash
kubectl apply -f mqtt_aggregator-deployment.yaml
```

---

## Monitorowanie i Debugowanie w Kubernetes

### Sprawdzanie Podów i Usług

```bash
kubectl get pods
kubectl get services
```

### Logi Podów i Deploymentów

```bash
kubectl logs deployment/mqtt-aggregator
kubectl logs pod/<nazwa-poda>
```

### Describe i Debugowanie Problemów z Połączeniem

```bash
kubectl describe pod <nazwa-poda>
```

Pozwala zdiagnozować problemy z uruchamianiem, volumeMountami, itp.

---

## Aktualizacja i Rollout

### Aktualizacja Obrazu w Deployment

Po zbudowaniu nowego obrazu:

```bash
docker push localhost:5000/mqtt-aggregator:latest

kubectl set image deployment/mqtt-aggregator mqtt-aggregator=localhost:5000/mqtt-aggregator:latest
```

### Rollback do Poprzedniej Wersji

Jeśli aktualizacja powoduje problemy:

```bash
kubectl rollout undo deployment/mqtt-aggregator
```

---

## Skalowanie Deploymentów w Kubernetes

### Statyczne Skalowanie

Modyfikacja `replicas` w manifeście `Deployment`:

```yaml
spec:
  replicas: 3
```

### Dynamiczne Skalowanie za pomocą `kubectl scale`

```bash
kubectl scale deployment mqtt-aggregator --replicas=5
```

### Automatyczne Skalowanie (HPA)

```bash
kubectl autoscale deployment mqtt-aggregator --min=2 --max=10 --cpu-percent=80
```

---

## Troubleshooting i Najlepsze Praktyki

### Brak Logów w Kontenerze

- Dodaj `ENV PYTHONUNBUFFERED=1` w `Dockerfile` aby wymusić natychmiastowe wypisywanie logów.
- Upewnij się, że kod został zaktualizowany i wdrożony (`kubectl rollout restart ...`).
- Dodaj `print()` na początku skryptu, aby sprawdzić, czy skrypt w ogóle startuje.

### Problemy z Połączeniem MQTT

- Sprawdź ConfigMap i `mosquitto.conf`, aby broker akceptował połączenia spoza localhost.
- Sprawdź `initContainer` z `nc`, czy może połączyć się z `mqtt-broker`.
- Upewnij się, że `mqtt-broker` i `mqtt-aggregator` są w tym samym namespace.

### Nadpisywanie Komend Startowych

- Sprawdź, czy w `yaml` dla Deploymentów nie ma `command` lub `args` nadpisujących `CMD` z Dockerfile.

---
