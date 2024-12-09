# Agregator Danych (`aggregator/`)

## Wprowadzenie

Agregator jest kluczowym komponentem systemu symulacji roju dronów. Jego głównym zadaniem jest zbieranie danych od wszystkich dronów publikujących swoje pozycje i stany poprzez brokera MQTT. Agregator przetwarza te dane w czasie rzeczywistym i udostępnia je za pośrednictwem API dla innych usług lub użytkowników.

Bez agregatora system nie mógłby efektywnie analizować danych z wielu źródeł jednocześnie, co uniemożliwiłoby skuteczne zarządzanie rojem dronów.

---

## Architektura i Funkcjonalność

### Działanie Agregatora

1. **Subskrypcja MQTT**: Agregator subskrybuje wiadomości publikowane przez drony na określonych *topicach*. 
2. **Agregacja Danych**: Otrzymane dane są agregowane, filtrowane i przetwarzane na potrzeby dalszej analizy.
3. **Analiza Danych**: Agregator może analizować dane pod kątem określonych kryteriów (np. lokalizacja, stan baterii).
4. **Przekazywanie Danych**: Przetworzone dane są udostępniane za pomocą API dla innych komponentów systemu lub użytkowników.

### Przykłady Subskrybowanych Topiców MQTT

```
drones/{drone_id}/position
drones/{drone_id}/status
```

Przykładowa wiadomość MQTT publikowana przez drona:

```json
{
  "drone_id": "drone_1",
  "x": 10,
  "y": 20,
  "battery": 95
}
```

### Proces Agregacji

1. **Odbiór danych z MQTT**.
2. **Przekształcenie danych do ujednoliconego formatu**.
3. **Zapis danych do bazy danych lub pamięci podręcznej**.
4. **Udostępnienie danych przez API**.

---

## Diagram Przepływu Danych

```
+----------------------+       +----------------------+       +----------------------+
|        Dron          | ----> |      Broker MQTT     | ----> |      Agregator       |
| (Publikuje dane)     |       | (Odbiera wiadomości) |       | (Przetwarza dane)    |
+----------------------+       +----------------------+       +----------------------+
                                                                   |
                                                                   v
                                                      +----------------------+
                                                      |    Aggregator API    |
                                                      | (Udostępnia dane)    |
                                                      +----------------------+
```

---

## Przykłady Kodów

### Subskrypcja MQTT

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Otrzymano wiadomość: {msg.payload.decode()} z topiku: {msg.topic}")

client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt-broker", 1883, 60)
client.subscribe("drones/+/position")

client.loop_forever()
```

### Przetwarzanie Danych

```python
def process_data(message):
    data = json.loads(message)
    print(f"Przetwarzanie danych drona {data['drone_id']}: ({data['x']}, {data['y']})")
    # Zapis do bazy danych lub dalsza analiza

process_data('{"drone_id": "drone_1", "x": 10, "y": 20, "battery": 95}')
```

---

## Przykład Konfiguracji w Kubernetes

Plik `aggregator-deployment.yaml`:

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
        image: aggregator:latest
        env:
        - name: MQTT_BROKER
          value: "mqtt-service"
        ports:
        - containerPort: 5000
```

---

## Najczęstsze Problemy i Rozwiązania

1. **Brak połączenia z brokerem MQTT**:
   - **Rozwiązanie**: Sprawdź, czy broker MQTT działa i jest dostępny na właściwym porcie.

2. **Niepoprawne dane z dronów**:
   - **Rozwiązanie**: Dodaj walidację danych w funkcji przetwarzającej.

3. **Agregator nie przetwarza wiadomości**:
   - **Rozwiązanie**: Sprawdź konfigurację subskrypcji MQTT i upewnij się, że drony publikują dane na właściwych *topicach*.

---

[Powrót do głównej dokumentacji](../README.MD)
