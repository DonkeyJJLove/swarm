# Dokumentacja Zarządzania Ekosystemem MQTT (Broker & Aggregator) w Docker i Kubernetes

## Spis treści

1. [Wprowadzenie](#wprowadzenie)  
2. [Struktura Projektu i Pliki Konfiguracyjne](#struktura-projektu-i-pliki-konfiguracyjne)  
    - [Dockerfile, requirements.txt, mqtt_aggregator.py, mosquitto.conf](#dockerfile-requirementstxt-mqtt_aggregatorpy-mosquittoconf)
3. [Zarządzanie Obrazami i Rejestrem Docker](#zarządzanie-obrazami-i-rejestrem-docker)  
    - [Uruchomienie Lokalnego Rejestru Docker](#uruchomienie-lokalnego-rejestru-docker)  
    - [Budowanie Obrazów](#budowanie-obrazy)  
    - [Tagowanie i Push Obrazów do Rejestru](#tagowanie-i-push-obrazy-do-rejestru)  
    - [Czyszczenie Obrazów i Kontenerów](#czyszczenie-obrazy-i-kontenerów)
4. [Wdrażanie do Kubernetes](#wdrażanie-do-kubernetes)  
    - [Zastosowanie ConfigMap dla Mosquitto](#zastosowanie-configmap-dla-mosquitto)  
    - [Deployment i Service dla mqtt-broker](#deployment-i-service-dla-mqtt-broker)  
    - [Deployment dla mqtt-aggregator z initContainer](#deployment-dla-mqtt-aggregator-z-initcontainer)
5. [Monitorowanie i Debugowanie w Kubernetes](#monitorowanie-i-debugowanie-w-kubernetes)  
    - [Sprawdzanie Podów i Usług](#sprawdzanie-podów-i-usług)  
    - [Logi Podów i Deploymentów](#logi-podów-i-deploymentów)  
    - [Diagnostyka i Debugowanie Problemów z Siecią](#diagnostyka-i-debugowanie-problemów-z-siecią)
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

Witaj w samouczku dotyczącym zarządzania ekosystemem MQTT przy użyciu Docker i Kubernetes. Ten przewodnik krok po kroku pokaże Ci, jak skonfigurować i zarządzać brokerem MQTT (Mosquitto) oraz agregatorem MQTT w środowisku kontenerowym. Dowiesz się, jak budować obrazy Docker, wdrażać je w Kubernetes, skalować aplikacje oraz efektywnie monitorować i debugować swoje wdrożenia.

---

## Struktura Projektu i Pliki Konfiguracyjne

Zanim przejdziemy do zarządzania obrazami i wdrażania aplikacji, warto zrozumieć strukturę projektu oraz pliki konfiguracyjne, które będziemy wykorzystywać.

### Dockerfile, requirements.txt, mqtt_aggregator.py, mosquitto.conf

- **`requirements.txt`**: Zawiera listę zależności Pythona, np. `paho-mqtt==1.6.1`.
  
  ```plaintext
  paho-mqtt==1.6.1
  ```
  
- **`mqtt_aggregator.py`**: Skrypt Python, który łączy się z brokerem MQTT, subskrybuje określone tematy i loguje otrzymane wiadomości.
  
  ```python
  import paho.mqtt.client as mqtt
  import os

  def on_connect(client, userdata, flags, rc):
      print("Connected with result code " + str(rc))
      client.subscribe("test/topic")

  def on_message(client, userdata, msg):
      print(f"Message received on {msg.topic}: {msg.payload.decode()}")

  if __name__ == "__main__":
      broker = os.getenv("MQTT_BROKER", "mqtt-broker")
      port = int(os.getenv("MQTT_PORT", "1883"))

      client = mqtt.Client()
      client.on_connect = on_connect
      client.on_message = on_message

      client.connect(broker, port, 60)
      client.loop_forever()
  ```
  
- **`mosquitto.conf`**: Konfiguracja Mosquitto, np. ustawia nasłuchiwanie na porcie 1883 i pozwala na anonimowe połączenia.
  
  ```conf
  listener 1883
  allow_anonymous true
  ```
  
- **`Dockerfile`**: Definiuje proces budowy obrazu Docker zawierającego `mqtt_aggregator.py` oraz instalację niezbędnych zależności.
  
  ```dockerfile
  FROM python:3.9-slim

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY mqtt_aggregator.py .

  ENV PYTHONUNBUFFERED=1

  CMD ["python", "mqtt_aggregator.py"]
  ```

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

---

## Zarządzanie Obrazami i Rejestrem Docker

W tej sekcji dowiesz się, jak zarządzać obrazami Docker oraz skonfigurować lokalny rejestr Docker do przechowywania i dystrybucji obrazów.

### Uruchomienie Lokalnego Rejestru Docker

Aby korzystać z własnego, lokalnego rejestru obrazów Docker, wykonaj poniższe kroki:

1. **Uruchomienie rejestru Docker:**

    ```bash
    docker run -d -p 5000:5000 --restart always --name registry registry:2
    ```

2. **Sprawdzenie zawartości rejestru:**

    ```bash
    curl http://localhost:5000/v2/_catalog
    ```

   Powinieneś zobaczyć listę dostępnych repozytoriów w rejestrze.

---

### Budowanie Obrazów

Zbudowanie obrazu Docker dla `mqtt-aggregator` jest prostym procesem. Upewnij się, że znajdujesz się w katalogu zawierającym `Dockerfile` oraz pozostałe pliki źródłowe.

**Przykładowe polecenie budowania obrazu:**

```bash
docker build -t mqtt-aggregator:latest .
```

---

### Tagowanie i Push Obrazów do Rejestru

Po zbudowaniu obrazu należy go otagować, aby wskazać lokalny rejestr, a następnie przesłać (push) do niego.

1. **Tagowanie obrazu:**

    ```bash
    docker tag mqtt-aggregator:latest localhost:5000/mqtt-aggregator:latest
    ```

2. **Push obrazu do rejestru:**

    ```bash
    docker push localhost:5000/mqtt-aggregator:latest
    ```

---

### Czyszczenie Obrazów i Kontenerów

Aby utrzymać środowisko Docker w czystości, regularnie usuwaj nieużywane obrazy i kontenery.

1. **Usuwanie konkretnego kontenera:**

    ```bash
    docker rm -f <nazwa_kontenera>
    ```

2. **Usuwanie konkretnego obrazu:**

    ```bash
    docker rmi <nazwa_obrazu>:<tag>
    ```

3. **Usuwanie wszystkich nieużywanych obrazów:**

    ```bash
    docker image prune -a -f
    ```

---

## Wdrażanie do Kubernetes

Teraz, gdy masz przygotowane obrazy Docker, czas przejść do wdrożenia aplikacji w Kubernetes. Poniżej znajdziesz kroki do skonfigurowania ConfigMap, Deploymentów oraz Service'ów dla brokerów MQTT i agregatora.

### Zastosowanie ConfigMap dla Mosquitto

ConfigMap umożliwia przechowywanie konfiguracji Mosquitto, którą można następnie wykorzystać w Deploymentach.

1. **Tworzenie ConfigMap z pliku `mosquitto.conf`:**

    ```bash
    kubectl create configmap mosquitto-config --from-file=mosquitto.conf
    ```

### Deployment i Service dla mqtt-broker

1. **Plik `mosquitto-deployment.yaml`:**

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

2. **Plik `mosquitto-service.yaml`:**

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

3. **Zastosowanie Deploymentu i Service:**

    ```bash
    kubectl apply -f mosquitto-deployment.yaml
    kubectl apply -f mosquitto-service.yaml
    ```

### Deployment dla mqtt-aggregator z initContainer

Aby upewnić się, że agregator MQTT nie uruchomi się przed brokerem MQTT, używamy `initContainer`, który czeka na dostępność brokera.

1. **Plik `mqtt_aggregator-deployment.yaml`:**

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

2. **Zastosowanie Deploymentu:**

    ```bash
    kubectl apply -f mqtt_aggregator-deployment.yaml
    ```

---

## Monitorowanie i Debugowanie w Kubernetes

Po wdrożeniu aplikacji ważne jest monitorowanie jej działania oraz umiejętność debugowania ewentualnych problemów.

### Sprawdzanie Podów i Usług

Aby zweryfikować status podów i usług:

```bash
kubectl get pods
kubectl get services
```

### Logi Podów i Deploymentów

Aby uzyskać logi z podów lub Deploymentów:

1. **Logi z Deploymentu:**

    ```bash
    kubectl logs deployment/mqtt-aggregator
    ```

2. **Logi z konkretnego poda:**

    ```bash
    kubectl logs pod/<nazwa-poda>
    ```

### Diagnostyka i Debugowanie Problemów z Siecią

Problemy z siecią mogą powodować trudności w komunikacji między podami, usługami lub z zewnętrznymi zasobami. Poniżej przedstawiam szczegółowe kroki oraz narzędzia pomocne w diagnozowaniu takich problemów.

#### 1. Sprawdzenie Podstawowych Informacji o Podzie

```bash
kubectl describe pod <nazwa-poda>
```

**Zwróć uwagę na:**

- **Adres IP poda:** Sprawdź, czy pod ma przypisany adres IP w sekcji `IP`.
- **Zdarzenia (Events):** Szukaj komunikatów o błędach związanych z siecią, takich jak `FailedScheduling` z powodu problemów z siecią.

---

#### 2. Sprawdzenie Adresacji i Łączności Między Podami

Możesz użyć prostych komend `ping` lub `curl` do sprawdzenia, czy pod może komunikować się z innymi podami.

**Przykład:**

```bash
kubectl exec <nazwa-poda> -- ping <IP-innego-poda>
```

**Diagnostyka problemów:**

- Jeśli `ping` się nie powodzi, problem może leżeć w konfiguracji sieci lub `NetworkPolicy`.
- Upewnij się, że sieć między podami pozwala na komunikację.

---

#### 3. Debugowanie Usług (Service)

Sprawdź, czy usługa (`Service`) działa prawidłowo i czy pod jest do niej przypisany:

```bash
kubectl describe service <nazwa-uslugi>
```

**Kroki diagnostyczne:**

- **ClusterIP:** Sprawdź, czy usługa ma przypisany `ClusterIP`.
- **Endpoints:** Zobacz, czy usługa ma przypisane endpointy. Brak endpointów oznacza, że żaden pod nie jest dostępny pod usługą.

    ```bash
    kubectl get endpoints <nazwa-uslugi>
    ```

    Jeśli wynik to `No endpoints available`, pod może nie działać prawidłowo lub nie spełniać selektorów usługi.

---

#### 4. Sprawdzanie NetworkPolicy

Jeśli używasz `NetworkPolicy`, może ona ograniczać ruch między podami.

**Wyświetlanie NetworkPolicy:**

```bash
kubectl get networkpolicy -n <nazwa-namespace>
```

**Szczegóły polityki:**

```bash
kubectl describe networkpolicy <nazwa-networkpolicy> -n <nazwa-namespace>
```

**Diagnostyka:**

- Sprawdź, czy reguły pozwalają na ruch przychodzący (`ingress`) i wychodzący (`egress`).
- Upewnij się, że pod ma odpowiednie etykiety (`labels`), aby pasował do reguł polityki.

---

#### 5. Sprawdzanie DNS

Problemy z DNS mogą uniemożliwiać podom komunikację z innymi zasobami poprzez nazwy hostów.

**Sprawdzenie konfiguracji DNS w podzie:**

```bash
kubectl exec <nazwa-poda> -- cat /etc/resolv.conf
```

**Testowanie rozwiązywania nazw:**

```bash
kubectl exec <nazwa-poda> -- nslookup <nazwa-uslugi>
```

Jeśli `nslookup` się nie powodzi:

- Sprawdź, czy usługa `kube-dns` lub `CoreDNS` działa:

    ```bash
    kubectl get pods -n kube-system -l k8s-app=kube-dns
    ```

---

#### 6. Narzędzia do Diagnostyki Sieci

- **`kubectl debug`**: Tworzy tymczasowy pod do diagnostyki.

    ```bash
    kubectl debug <nazwa-poda> -it --image=busybox -- bash
    ```

- **`k9s`**: Interaktywne narzędzie do zarządzania Kubernetes z funkcjami diagnostycznymi.
- **`netshoot`**: Pod z zaawansowanymi narzędziami sieciowymi (`tcpdump`, `curl`, `nmap`).

    **Przykład użycia:**

    ```bash
    kubectl run -it --rm netshoot --image=nicolaka/netshoot -- bash
    ```

---

### Podsumowanie Diagnostyki Sieci

1. **Sprawdź status poda i jego IP.**
2. **Testuj łączność między podami za pomocą `ping` lub `curl`.**
3. **Weryfikuj konfigurację usług (`Service`) i endpointów.**
4. **Analizuj `NetworkPolicy`, jeśli używasz reguł sieciowych.**
5. **Diagnozuj problemy z DNS za pomocą `nslookup`.**
6. **Używaj specjalistycznych narzędzi, takich jak `netshoot` lub `k9s`** do bardziej zaawansowanej analizy.

Jeśli problem nadal występuje, warto sprawdzić logi komponentów `kube-proxy` oraz węzłów (`node`) dla bardziej szczegółowych informacji.

---

## Aktualizacja i Rollout

Zarządzanie wersjami aplikacji jest kluczowe dla zapewnienia ciągłości działania i szybkiego reagowania na problemy.

### Aktualizacja Obrazu w Deployment

Po zbudowaniu nowego obrazu i wypchnięciu go do rejestru, zaktualizuj Deployment, aby używał najnowszej wersji obrazu.

1. **Push nowego obrazu:**

    ```bash
    docker push localhost:5000/mqtt-aggregator:latest
    ```

2. **Aktualizacja Deploymentu:**

    ```bash
    kubectl set image deployment/mqtt-aggregator mqtt-aggregator=localhost:5000/mqtt-aggregator:latest
    ```

### Rollback do Poprzedniej Wersji

Jeśli aktualizacja powoduje problemy, możesz szybko wrócić do poprzedniej stabilnej wersji.

```bash
kubectl rollout undo deployment/mqtt-aggregator
```

---

## Skalowanie Deploymentów w Kubernetes

Skalowanie aplikacji pozwala na dostosowanie się do zmieniających się obciążeń. Kubernetes oferuje różne metody skalowania, zarówno statyczne, jak i dynamiczne.

### Statyczne Skalowanie

Możesz ręcznie określić liczbę replik w manifeście `Deployment`.

1. **Modyfikacja `replicas` w manifeście `Deployment`:**

    ```yaml
    spec:
      replicas: 3
    ```

2. **Zastosowanie zmian:**

    ```bash
    kubectl apply -f mqtt_aggregator-deployment.yaml
    ```

### Dynamiczne Skalowanie za pomocą `kubectl scale`

Korzystając z komendy `kubectl scale`, możesz szybko zmienić liczbę replik bez modyfikowania pliku manifestu.

```bash
kubectl scale deployment mqtt-aggregator --replicas=5
```

### Automatyczne Skalowanie (HPA)

Horizontal Pod Autoscaler (HPA) automatycznie skaluje liczbę replik na podstawie metryk, takich jak zużycie CPU.

1. **Utworzenie HPA:**

    ```bash
    kubectl autoscale deployment mqtt-aggregator --min=2 --max=10 --cpu-percent=80
    ```

2. **Sprawdzenie statusu HPA:**

    ```bash
    kubectl get hpa
    ```

---

## Troubleshooting i Najlepsze Praktyki

W tej sekcji omówimy najczęstsze problemy oraz najlepsze praktyki, które pomogą Ci efektywnie zarządzać i utrzymywać środowisko Kubernetes.

### Brak Logów w Kontenerze

Jeśli nie widzisz logów z kontenera, wykonaj następujące kroki:

- **Dodaj `ENV PYTHONUNBUFFERED=1` w `Dockerfile`:** Umożliwia to natychmiastowe wypisywanie logów bez buforowania.

    ```dockerfile
    ENV PYTHONUNBUFFERED=1
    ```

- **Upewnij się, że kod został zaktualizowany i wdrożony:**

    ```bash
    kubectl rollout restart deployment/mqtt-aggregator
    ```

- **Dodaj `print()` na początku skryptu:** Sprawdź, czy skrypt w ogóle się uruchamia.

    ```python
    print("MQTT Aggregator starting...")
    ```

### Problemy z Połączeniem MQTT

Jeśli agregator nie może połączyć się z brokerem MQTT, wykonaj następujące kroki:

- **Sprawdź ConfigMap i `mosquitto.conf`:** Upewnij się, że broker akceptuje połączenia spoza localhost.

    ```conf
    listener 1883
    allow_anonymous true
    ```

- **Sprawdź `initContainer` z `nc`:** Upewnij się, że może połączyć się z `mqtt-broker`.

    ```yaml
    initContainers:
      - name: wait-for-mqtt
        image: nicolaka/netshoot
        command: ['sh', '-c', 'until nc -z mqtt-broker 1883; do echo waiting for mqtt-broker; sleep 2; done']
    ```

- **Upewnij się, że `mqtt-broker` i `mqtt-aggregator` są w tym samym namespace:**

    ```bash
    kubectl get pods -n <nazwa-namespace>
    ```

### Nadpisywanie Komend Startowych

Czasami komendy startowe mogą być nadpisane w plikach YAML, co prowadzi do nieoczekiwanego zachowania kontenerów.

- **Sprawdź, czy w `yaml` dla Deploymentów nie ma `command` lub `args` nadpisujących `CMD` z Dockerfile:**

    ```yaml
    containers:
      - name: mqtt-aggregator
        image: localhost:5000/mqtt-aggregator:latest
        command: ["python", "mqtt_aggregator.py"]  # Upewnij się, że nie nadpisuje to CMD w Dockerfile
    ```

---

## Podsumowanie

Ten samouczek przeprowadził Cię przez proces zarządzania ekosystemem MQTT w środowisku Docker i Kubernetes. Omówiliśmy:

- **Strukturę projektu i kluczowe pliki konfiguracyjne.**
- **Zarządzanie obrazami Docker oraz konfigurację lokalnego rejestru.**
- **Wdrażanie aplikacji w Kubernetes, w tym konfigurację ConfigMap, Deploymentów oraz Service'ów.**
- **Monitorowanie, debugowanie oraz diagnostykę problemów z siecią w Kubernetes.**
- **Aktualizację i rollback Deploymentów oraz skalowanie aplikacji.**
- **Najlepsze praktyki i rozwiązywanie najczęstszych problemów.**

Dzięki tym informacjom jesteś dobrze przygotowany, aby skutecznie zarządzać i skalować swoje aplikacje MQTT w Kubernetes. Pamiętaj o regularnym monitorowaniu swojego środowiska oraz stosowaniu najlepszych praktyk, aby zapewnić stabilność i wydajność swoich usług.