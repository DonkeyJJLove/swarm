# **`aggregator_details.md`**  
Dokumentacja Szczegółowa Komponentu **Aggregator**

## Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)  
2. [Główne Zadania i Zakres Odpowiedzialności](#2-główne-zadania-i-zakres-odpowiedzialności)  
3. [Architektura i Schemat Komunikacji](#3-architektura-i-schemat-komunikacji)  
4. [Implementacja: `aggregator.py`](#4-implementacja-aggregatorpy)  
   - [4.1 Obsługa UDP](#41-obsługa-udp)  
   - [4.2 Forwardowanie / Obróbka Danych](#42-forwardowanie--obróbka-danych)  
   - [4.3 Integracja z Infrastrukturalnymi Usługami](#43-integracja-z-infrastrukturalnymi-usługami)  
5. [Wdrożenie w Kubernetes](#5-wdrożenie-w-kubernetes)  
   - [5.1 Struktura Plików w Katalogu `aggregator/`](#51-struktura-plików-w-katalogu-aggregator)  
   - [5.2 Manifest `aggregator-deployment.yaml`](#52-manifest-aggregator-deploymentyaml)  
   - [5.3 Manifest `aggregator-service.yaml`](#53-manifest-aggregator-serviceyaml)  
6. [Konfiguracja i Zmienne Środowiskowe](#6-konfiguracja-i-zmienne-środowiskowe)  
7. [Potencjalne Scenariusze Użycia](#7-potencjalne-scenariusze-użycia)  
8. [Typowe Błędy i Rozwiązywanie Problemów](#8-typowe-błędy-i-rozwiązywanie-problemów)  
9. [Rozwój i Integracje Przyszłościowe](#9-rozwój-i-integracje-przyszłościowe)  
10. [Odnośniki](#10-odnośniki)

---

## 1. Wprowadzenie
Komponent **Aggregator** to **centralny punkt** do zbierania i wstępnego przetwarzania danych generowanych przez drony oraz ewentualnie inne źródła. W zależności od używanego protokołu:

- Może **subskrybować** dane z broker MQTT (topiki dronów),
- Może nasłuchiwać w trybie **UDP** (port 5001) i odbierać pakiety od dronów,
- Może zapisywać dane do bazy lub kierować je dalej, np. do **Aggregator API**, **systemu AI** czy innych usług.

**Cel**: Umożliwić skalowalne, niezawodne i elastyczne gromadzenie telemetrii roju IoT (dronów) w środowisku Kubernetes, z zachowaniem dobrych praktyk DevSecOps (skanowanie obrazów, replikacja, mTLS przy użyciu Istio itp.).

---

## 2. Główne Zadania i Zakres Odpowiedzialności
1. **Odbiór danych**:   
   - Przede wszystkim dane o pozycji i stanie baterii dronów.  
   - Format (JSON, surowy tekst) może się różnić w zależności od implementacji dronów.

2. **Przetwarzanie wstępne** (opcjonalne):  
   - Walidacja i parsowanie danych (np. JSON),
   - Filtrowanie duplikatów, odrzucanie błędnych komunikatów,
   - Agregacja — np. łączenie danych z wielu dronów w jedną strukturę.

3. **Forwardowanie / integracja**:  
   - Możliwe wysyłanie do **Aggregator API** (REST),
   - Możliwe publikowanie na innych topikach MQTT (w architekturze pub/sub),
   - Ewentualna komunikacja z **systemem AI** (np. gRPC lub kolejny broker).

4. **Zgodność z DevSecOps**:  
   - Umożliwienie łatwej modyfikacji (CI/CD), testów bezpieczeństwa, chaos engineering, skalowania w Kubernetes.

---

## 3. Architektura i Schemat Komunikacji

Przykładowy, uproszczony przepływ danych z dronów do aggregator:

```
       [Drony - Pody]
       Publikacja UDP / MQTT
             |
             v
+-----------------------------+
|         [Aggregator]       |  <--- aggregator.py
|  - Odbiór pakietów (UDP)   |
|  - lub subskrypcja MQTT    |
|  - Walidacja i Agregacja   |
+-------------+--------------+
              |
              v
      [Integrator / Storage / API]
```

- Jeśli drony wysyłają dane przez **UDP**: aggregator nasłuchuje na `AGGREGATOR_PORT` (domyślnie 5001).
- Jeśli drony publikują przez **MQTT**: aggregator subskrybuje topik np. `drone/positions` (za pośrednictwem paho-mqtt lub innego klienta).

---

## 4. Implementacja: `aggregator.py`

### 4.1 Obsługa UDP

W typowym scenariuszu aggregator **nasłuchuje** na porcie UDP, używając gniazda (`socket.AF_INET, socket.SOCK_DGRAM`). Przykładowy kod:

```python
import socket
import threading
import os

AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "5001"))

def handle_message(data, addr):
    message = data.decode(errors='replace')
    print(f"[aggregator] Received from {addr}: {message}")
    # Możemy tu dodać: walidację, przetwarzanie, forward do bazy / aggregator-api

def run_aggregator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", AGGREGATOR_PORT))
    print(f"[aggregator] Listening on port {AGGREGATOR_PORT} (UDP)")

    while True:
        data, addr = sock.recvfrom(1024)
        # Każde odebrane dane obsługujemy w osobnym wątku
        threading.Thread(target=handle_message, args=(data, addr), daemon=True).start()

if __name__ == "__main__":
    run_aggregator()
```

### 4.2 Forwardowanie / Obróbka Danych

W zależności od potrzeb:

- Możemy dopisać w `handle_message()` fragment `requests.post()` do innego serwisu (np. aggregator-api, system AI),
- Można wstawić logikę zapisu do bazy (Redis, PostgreSQL, InfluxDB) – konieczne wtedy zainstalowanie biblioteki w `requirements.txt`.

### 4.3 Integracja z Infrastrukturalnymi Usługami

- **Istio**: Jeśli aggregator działa wewnątrz mesha, komunikacja z aggregator-api czy innymi usługami może być szyfrowana mTLS.  
- **Skanowanie obrazów**: Dockerfile w aggregator/ powinien być przetestowany pod kątem luk (np. `trivy aggregator-image`).  
- **Pods**: Zaleca się ustawić `resources.requests` i `resources.limits` w manifeście K8s, np. `CPU: 0.1, memory: 128Mi`.

---

## 5. Wdrożenie w Kubernetes

### 5.1 Struktura Plików w Katalogu `aggregator/`

```
aggregator/
├── aggregator.py
├── aggregator-deployment.yaml
├── aggregator-service.yaml
├── Dockerfile
└── requirements.txt
```

- **`aggregator.py`**: Kod główny, uruchamia nasłuch UDP (lub subskrypcję MQTT, w innej gałęzi).
- **`aggregator-deployment.yaml`** i **`aggregator-service.yaml`**: Manifesty K8s.
- **`Dockerfile`**: Budowa obrazu kontenera.
- **`requirements.txt`**: Ewentualne zależności Python (np. `requests`, `paho-mqtt`).

### 5.2 Manifest `aggregator-deployment.yaml`

Przykład (UDP scenario):

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
        image: myrepo/aggregator:latest
        ports:
          - containerPort: 5001
            protocol: UDP
        env:
          - name: AGGREGATOR_PORT
            value: "5001"
```

### 5.3 Manifest `aggregator-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aggregator-service
spec:
  selector:
    app: aggregator
  ports:
    - name: aggregator-udp
      port: 5001
      targetPort: 5001
      protocol: UDP
  type: ClusterIP
```

**Uwaga**: Drony powinny wysyłać dane do `aggregator-service:5001` (jeśli w tym samym namespace). W protokole UDP kluczowe, by `protocol: UDP` było ustawione.

---

## 6. Konfiguracja i Zmienne Środowiskowe

- **`AGGREGATOR_PORT`**: Domyślnie `5001`; port do nasłuchu UDP.  
- **`MQTT_BROKER`** i **`MQTT_PORT`**: Jeśli aggregator w innej gałęzi subskrybuje z MQTT, te zmienne określą adres brokera.  
- **`DEBUG`** (opcjonalnie): Flaga do włączania dodatkowych logów.

W pliku `aggregator-deployment.yaml` można konfigurować env, np.:

```yaml
env:
  - name: AGGREGATOR_PORT
    value: "5001"
  - name: MQTT_BROKER
    value: "mqtt-broker"
  - name: MQTT_PORT
    value: "1883"
```

---

## 7. Potencjalne Scenariusze Użycia

1. **Zbieranie danych w czasie rzeczywistym**:  
   - Drony publikują co 5 sekund parametry lotu (UDP). Aggregator odbiera i przekazuje do bazy (np. InfluxDB) do wizualizacji.

2. **Forward do aggregator-api**:  
   - Każda odebrana wiadomość jest walidowana i wysyłana metodą `POST /api/ingest` w aggregator-api.

3. **Integracja z systemem AI**:  
   - Aggregator może publikować przetworzone dane (średnia, max, alarmy) do topiku `aggregator/processed`, który subskrybuje warstwa ML.

4. **Funkcja bridging**:  
   - W niektórych scenariuszach aggregator może pełnić rolę “bridge” z UDP do MQTT lub odwrotnie.

---

## 8. Typowe Błędy i Rozwiązywanie Problemów

1. **Brak danych**:  
   - Sprawdź, czy drony wysyłają do poprawnej nazwy serwisu: `aggregator-service:5001` (UDP).  
   - Zweryfikuj `protocol: UDP` w `Service` i `Deployment`.

2. **Wielokrotne przetwarzanie**:  
   - Jeżeli replik aggregator > 1, a komunikaty nie są deduplikowane, może być chaos.  
   - Rozważ HPA i sticky logic (np. prosta baza do oznaczania co już obsłużono).

3. **Zbyt duży ruch**:  
   - Modyfikacja replik aggregator, rate limiting w dronach (mniej często wysyłać?),  
   - Ewentualnie integracja z kolejkowaniem (np. Kafka).

4. **Kwestie bezpieczeństwa**:  
   - Brak TLS w UDP – można wdrożyć Istio i sidecar, lub inne mechanizmy szyfrujące.  
   - W subskrypcji MQTT – sprawdź ACL w Mosquitto, czy aggregator ma uprawnienia do subskrybowania topiku.

---

## 9. Rozwój i Integracje Przyszłościowe

- **Przechowywanie w bazie**:  
  - Implementacja zapisu do NoSQL / TSDB (InfluxDB) w `handle_message()`.  
  - Możliwość tworzenia dashboardów w Grafanie.

- **Rozszerzona logika**:  
  - Walidacja zaawansowana (np. schema JSON, thresholdy).  
  - Wykrywanie anomalii (podstawowe) lub alarmy push do aggregator-api.

- **mTLS i Istio**:  
  - Dla protokołu UDP standardowy sidecar Envoy może być wyzwaniem (częściej sprawdza się TCP).  
  - Możliwe przejście aggregator → aggregator-api w sieci mesh, z zachowaniem mTLS.

- **Możliwość przełączenia** z UDP na MQTT lub odwrotnie, w zależności od gałęzi projektu.  

---

## 10. Odnośniki

- **Główny README**: [README.MD](../README.MD) – Ogólny opis projektu (architektura, AI, DevSecOps).  
- **`broker_mqtt.md`**: Opis konfiguracji Mosquitto i topików MQTT.  
- **`aggregator_api_details.md`**: Szczegóły modułu aggregator-api (REST).  
- **`security_tests_details.md`**: Testy bezpieczeństwa (fuzzing, chaos).  
- **`system_ai_details.md`**: Integracja z warstwą ML (trenowanie modeli, subskrypcja strumieni danych).  

---

**Podsumowanie**  
Komponent **Aggregator** stanowi kluczowy element przepływu danych: odbiera komunikaty z roju dronów (UDP lub MQTT), a następnie przetwarza je i udostępnia do dalszych modułów (API, AI, bazy). W połączeniu z Kubernetes (dla skalowalności) i Istio (dla bezpieczeństwa i kontroli ruchu) pozwala stworzyć **hiperelastyczne laboratorium** do eksperymentów IoT, DevSecOps i ML.