# Broker MQTT w Projekcie Symulacji Rojów Dronów

## 1. Wprowadzenie do MQTT

**MQTT (Message Queuing Telemetry Transport)** to lekki protokół komunikacyjny oparty na modelu publikacji-subskrypcji. Jest szeroko stosowany w projektach IoT (Internet of Things) i systemach rozproszonych ze względu na:

- **Niskie zużycie zasobów** – idealne dla urządzeń z ograniczonymi możliwościami obliczeniowymi.
- **Niskie opóźnienia** – zapewnia szybką transmisję danych.
- **Asynchroniczność** – umożliwia niezależną komunikację między urządzeniami bez konieczności bezpośredniego połączenia.
- **Elastyczność** – obsługuje różne poziomy QoS (Quality of Service).

## 2. Rola Brokera MQTT

Broker MQTT działa jako **centralny punkt komunikacyjny**, który pośredniczy między dronami a innymi komponentami systemu:

- **Drony** publikują swoje dane (np. pozycję) na odpowiednich *topicach* MQTT.
- **Agregator** i inne usługi subskrybują te *topiki* i odbierają dane w czasie rzeczywistym.

### Zalety Komunikacji opartej na MQTT

1. **Luźne powiązanie komponentów** – drony nie muszą znać adresów innych usług.
2. **Skalowalność** – łatwo można dodać nowe drony lub usługi bez zmiany istniejącej konfiguracji.
3. **Niezawodność** – dzięki różnym poziomom QoS można dostosować niezawodność transmisji.
4. **Asynchroniczność** – komponenty działają niezależnie, co poprawia wydajność systemu.

## 3. Konfiguracja Brokera w Kubernetes

### Przykład Deployment dla Mosquitto

Plik `mosquitto-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto-deployment
  labels:
    app: mosquitto
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
        volumeMounts:
        - name: mosquitto-config
          mountPath: /mosquitto/config
      volumes:
      - name: mosquitto-config
        configMap:
          name: mosquitto-config
```

### Znaczenie Parametrów

- **`image`**: Używany obraz kontenera (eclipse-mosquitto).
- **`ports`**: Port 1883, standardowy port dla MQTT.
- **`volumeMounts`**: Montowanie pliku konfiguracyjnego z ConfigMap.

### Przykład Service dla Mosquitto

Plik `mosquitto-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mqtt-service
spec:
  selector:
    app: mosquitto
  ports:
    - protocol: TCP
      port: 1883
      targetPort: 1883
  type: ClusterIP
```

## 4. Przykłady Topiców MQTT

W projekcie wykorzystywane są następujące *topiki*:

- **Publikacja pozycji drona**:
  ```
  drones/{drone_id}/position
  ```
  **Przykładowy payload**:
  ```json
  { "x": 10, "y": 20, "battery": 95 }
  ```

- **Publikacja statusu drona**:
  ```
  drones/{drone_id}/status
  ```

## 5. Scenariusze Użycia

### Przepływ Danych

1. **Dron publikuje dane**:
   ```
   drones/123/position -> { "x": 10, "y": 20, "battery": 95 }
   ```

2. **Broker MQTT** odbiera dane i przesyła je do subskrybentów.

3. **Agregator** subskrybuje topic `drones/+/position` i przetwarza dane.

4. **Aggregator API** udostępnia dane poprzez HTTP:
   ```http
   GET /api/drones/123/status
   ```

## 6. Najlepsze Praktyki

1. **Bezpieczeństwo**:
   - Używaj autoryzacji i TLS do szyfrowania połączeń.
   - Konfiguruj `allow_anonymous false` w pliku `mosquitto.conf`.

2. **Zarządzanie Połączeniami**:
   - Ustawiaj limit liczby połączeń, aby zapobiegać przeciążeniu brokera.

3. **Monitorowanie**:
   - Monitoruj stan brokera MQTT za pomocą Prometheus i Grafana.
   - Analizuj logi przy pomocy ELK Stack.

---

## Podsumowanie

Broker MQTT jest kluczowym elementem komunikacji w projekcie symulacji roju dronów. Zapewnia niezawodną, asynchroniczną wymianę danych pomiędzy dronami a innymi komponentami systemu.


---

**Plik:** `_docs/broker_mqtt.md`

[Powrót do głównej dokumentacji](../README.MD)