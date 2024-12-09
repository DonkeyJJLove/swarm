# Szczegółowa Dokumentacja Aggregator API

## 1. Wprowadzenie

**Aggregator API** to komponent odpowiedzialny za interakcję z rojem dronów w projekcie symulacji. Umożliwia zewnętrznym systemom oraz użytkownikom dostęp do danych zbieranych przez agregator oraz zarządzanie parametrami dronów za pomocą żądań HTTP.

API pełni kluczową rolę jako warstwa komunikacyjna pomiędzy agregatorem danych a użytkownikami końcowymi, umożliwiając monitorowanie, sterowanie i analizę danych w czasie rzeczywistym.

---

## 2. Główne Funkcje

### Pobieranie Statusu Dronów

- **Endpoint**: `GET /api/drones/{drone_id}/status`
- **Opis**: Zwraca aktualny stan drona, w tym jego pozycję i poziom baterii.

### Aktualizacja Parametrów Dronów

- **Endpoint**: `POST /api/drones/{drone_id}/update`
- **Opis**: Aktualizuje parametry drona, takie jak nowa trasa lub inne ustawienia operacyjne.

### Pobieranie Listy Dronów

- **Endpoint**: `GET /api/drones`
- **Opis**: Zwraca listę wszystkich aktywnych dronów wraz z ich podstawowymi informacjami.

---

## 3. Przykłady Użycia

### Pobieranie Statusu Drona

**Żądanie**:
```http
GET /api/drones/123/status
```

**Odpowiedź**:
```json
{
  "drone_id": "123",
  "position": { "x": 10, "y": 20 },
  "battery": 85,
  "status": "active"
}
```

### Aktualizacja Parametrów Drona

**Żądanie**:
```http
POST /api/drones/123/update
Content-Type: application/json

{
  "new_route": [ { "x": 15, "y": 25 }, { "x": 20, "y": 30 } ]
}
```

**Odpowiedź**:
```json
{
  "message": "Drone route updated successfully."
}
```

---

## 4. Znaczenie w Architekturze

Aggregator API integruje się z następującymi komponentami systemu:

- **Drony**: Publikują dane na brokerze MQTT, które są następnie dostępne przez API.
- **Broker MQTT**: Przechowuje dane publikowane przez drony.
- **Agregator**: Subskrybuje dane z MQTT i przekazuje je do API, które udostępnia je użytkownikom końcowym.

Aggregator API stanowi zatem centralny punkt dostępu do danych roju dronów oraz mechanizmów zarządzania nimi.

---

## 5. Diagram Komunikacji

```
+----------------------+          +----------------------+
|       Drony          |          |      Aggregator      |
| (Publikują dane MQTT)| ----->   | (Subskrybuje MQTT)   |
+----------------------+          +----------------------+
                                      |
                                      v
                            +----------------------+
                            |    Aggregator API    |
                            |  (Udostępnia dane)   |
                            +----------------------+
                                      |
                                      v
                            +----------------------+
                            |  Użytkownik/Zewnętrzne |
                            |      Systemy          |
                            +----------------------+
```

---

## 6. Pliki i Konfiguracja

- **Kod API**: `aggregator-api/aggregator_api.py`
- **Dockerfile**: `aggregator-api/Dockerfile`
- **Deployment Kubernetes**: `aggregator-api/aggregator-api-deployment.yaml`

Przykład fragmentu `aggregator-api-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator-api-deployment
spec:
  replicas: 2
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
        image: aggregator-api:latest
        ports:
        - containerPort: 5000
```

---

## 7. Przykładowy Kod Endpointu w Flask

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/drones/<drone_id>/status', methods=['GET'])
def get_drone_status(drone_id):
    # Przykładowe dane
    data = {
        "drone_id": drone_id,
        "position": {"x": 10, "y": 20},
        "battery": 85,
        "status": "active"
    }
    return jsonify(data)

@app.route('/api/drones/<drone_id>/update', methods=['POST'])
def update_drone(drone_id):
    new_data = request.get_json()
    return jsonify({"message": f"Drone {drone_id} updated successfully", "data": new_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

**Plik:** `_docs/aggregator_api_details.md`

[Powrót do głównej dokumentacji](../README.MD)