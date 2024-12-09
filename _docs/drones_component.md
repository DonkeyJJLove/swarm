
# Dokumentacja Komponentu Dronów

## 1. Wprowadzenie

Komponent **dronów** w projekcie symulacji roju dronów odpowiada za autonomiczne jednostki, które generują dane o swojej pozycji i stanie, a następnie komunikują się z innymi częściami systemu za pomocą brokera MQTT. Drony mogą również odbierać polecenia zwrotne od agregatora lub API, umożliwiając dynamiczne zarządzanie ich zachowaniem.

---

## 2. Szczegółowy Opis Komponentu Dronów

### Struktura Katalogu `drones/`

```
drones/
├── Dockerfile
├── drone_logic.py
├── drone-deployment.yaml
├── drone-service.yaml
└── requirements.txt
```

### Opis Plików

- **`Dockerfile`**: Definiuje środowisko kontenerowe dla drona.
  ```dockerfile
  FROM python:3.9
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["python", "drone_logic.py"]
  ```

- **`drone_logic.py`**: Główna logika drona – generowanie danych o pozycji i publikacja na brokerze MQTT.
  
  ```python
  import paho.mqtt.client as mqtt
  import time
  import random

  BROKER = "mqtt-service"
  TOPIC = "drones/drone1/position"

  client = mqtt.Client()
  client.connect(BROKER)

  while True:
      position = {"x": random.randint(0, 100), "y": random.randint(0, 100), "battery": random.randint(20, 100)}
      client.publish(TOPIC, str(position))
      time.sleep(5)
  ```

- **`drone-deployment.yaml`**: Konfiguracja wdrożenia drona w Kubernetes.
  
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: drone-deployment
  spec:
    replicas: 3
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
          image: drone-simulation:latest
          env:
          - name: MQTT_BROKER
            value: "mqtt-service"
  ```

- **`requirements.txt`**: Zawiera zależności dla drona.
  
  ```
  paho-mqtt==1.6.1
  ```

---

## 3. Przykładowy Kod MQTT

### Publikacja Danych

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("mqtt-service")

client.publish("drones/drone1/position", '{"x": 10, "y": 20, "battery": 95}')
```

### Odbiór Komend

```python
def on_message(client, userdata, message):
    print(f"Received command: {message.payload.decode()}")

client.subscribe("drones/drone1/commands")
client.on_message = on_message
client.loop_forever()
```

---

## 4. Diagram Przepływu Danych

```
+---------------------------+
|         Dron 1           |
| Publikuje dane MQTT      |
+------------+--------------+
             |
             v
+------------+--------------+
|       Broker MQTT         |
|      (Mosquitto)          |
+------------+--------------+
             |
             v
+------------+--------------+
|         Agregator         |
| Subskrybuje topic MQTT    |
+---------------------------+
```

---

## 5. Przykłady Użycia i Scenariusze Testowe

### Przykład Użycia

1. **Symulacja roju dronów**:
   - Uruchom 3 repliki dronów w Kubernetes za pomocą `drone-deployment.yaml`.
   - Każdy dron publikuje swoją pozycję na brokerze MQTT.

2. **Odbiór danych przez agregator**:
   - Agregator subskrybuje topic `drones/+/position` i gromadzi dane o pozycjach dronów.

### Scenariusz Testowy

1. Uruchom brokera MQTT.
2. Wdróż drony w Kubernetes.
3. Sprawdź logi dronów, aby upewnić się, że dane są publikowane.
4. Sprawdź, czy agregator odbiera dane:
   ```bash
   kubectl logs aggregator-pod
   ```

---

## 6. Najlepsze Praktyki

1. **Skalowalność**: Skaluj liczbę replik dronów w Kubernetes w zależności od potrzeb:
   ```bash
   kubectl scale deployment drone-deployment --replicas=10
   ```

2. **Konfiguracja MQTT**:
   - Używaj bezpiecznych połączeń MQTT (TLS) w środowiskach produkcyjnych.

3. **Monitorowanie**:
   - Integruj monitoring za pomocą Prometheus i Grafana, aby śledzić wydajność dronów.

4. **Debugowanie**:
   - Sprawdzaj komunikację MQTT za pomocą narzędzi takich jak `MQTT Explorer`.

---

## Podsumowanie

Komponent dronów stanowi kluczowy element systemu symulacji roju dronów, umożliwiając generowanie danych i elastyczną komunikację z innymi usługami za pomocą MQTT. Dzięki wdrożeniu w Kubernetes drony są łatwo skalowalne i zarządzalne.
