
# Dokumentacja Projektu: Symulacja Rojów Dronów w Architekturze Kontenerowej

## Wprowadzenie

Projekt symulacji roju dronów wykorzystuje technologie konteneryzacji **Docker** oraz orkiestracji **Kubernetes**. Każdy dron działa jako niezależny kontener, który komunikuje się z innymi komponentami za pomocą protokołu **MQTT**. Celem jest stworzenie systemu umożliwiającego:

- **Symulację koordynacji roju dronów**
- **Modularność i skalowalność dzięki Kubernetes**
- **Elastyczną komunikację sieciową**
- **Agregację i analizę danych w czasie rzeczywistym**

---

## Architektura Systemu

### Diagram Architektury

```
                       +-------------------------------+
                       |         Broker MQTT          |
                       |         (Mosquitto)          |
                       +-------------------------------+
                                     ^
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
+----------v----------+   +----------v----------+   +----------v----------+
|       Dron 1        |   |       Dron 2        |   |       Dron N        |
| Publikuje dane MQTT |   | Publikuje dane MQTT |   | Publikuje dane MQTT |
+---------------------+   +---------------------+   +---------------------+
                                     |
                                     v
                       +-------------------------------+
                       |          Agregator           |
                       |   (Subskrybuje topic MQTT)   |
                       +-------------------------------+
                                     |
                                     v
                       +-------------------------------+
                       |        Aggregator API        |
                       |    (REST API dla danych)     |
                       +-------------------------------+
```

### Opis Komponentów

#### 1. **Drony (`drones/`)**

- **Rola**: Symulacja autonomicznych dronów.
- **Funkcja**:
  - Generują dane o swojej pozycji, stanie baterii i innych parametrach.
  - Publikują dane na brokerze MQTT.
  - Odbierają komendy zwrotne z agregatora lub API.
- **MQTT Topic**:
  ```
  drones/{drone_id}/position
  ```
- **Szczegółowa Dokumentacja**: [Dokumentacja Dronów](./_docs/drones_component.md)  
- **Pliki**: [Kod drona i konfiguracja](drones/).

#### 2. **Broker MQTT (`server/mqtt/`)**

- **Rola**: Centralny węzeł komunikacyjny.
- **Funkcja**:
  - Odbiera dane publikowane przez drony.
  - Rozsyła dane do subskrybujących komponentów (np. agregatora).
- **Konfiguracja**:
  - **Deployment**: Wdrażany w Kubernetes jako usługa z wykorzystaniem Mosquitto.
- **Pliki**: [Konfiguracja MQTT](server/mqtt/).

#### 3. **Agregator (`aggregator/`)**

- **Rola**: Zbieranie i przetwarzanie danych od dronów.
- **Funkcja**:
  - Subskrybuje dane z MQTT.
  - Agreguje i analizuje dane w czasie rzeczywistym.
  - Może zapisywać dane do bazy danych lub przekazywać je dalej do API.
- **MQTT Subskrypcja**:
  ```
  drones/+/position
  ```
- **Pliki**: [Kod agregatora](aggregator/).

#### 4. **Aggregator API (`aggregator-api/`)**

- **Rola**: Interfejs do komunikacji zewnętrznej.
- **Funkcja**:
  - Udostępnia dane z agregatora za pomocą REST API.
  - Umożliwia zarządzanie rojem dronów i ich parametrami.
- **Przykład endpointu**:
  ```http
  GET /api/drones/{drone_id}/status
  ```
- **Pliki**: [Kod API](aggregator-api/).

---

## Szczegóły Komunikacji Sieciowej

### Przepływ Danych

1. **Drony** publikują dane na brokerze MQTT:
   ```json
   Topic: drones/{drone_id}/position
   Payload: { "x": 10, "y": 20, "battery": 95 }
   ```

2. **Agregator** subskrybuje odpowiednie topiki i odbiera dane:
   ```
   Subskrypcja: drones/+/position
   ```

3. **Aggregator API** umożliwia dostęp do zebranych danych:
   ```http
   GET /api/drones/{drone_id}/status
   ```

### Przykład Konfiguracji Mosquitto

Plik `mosquitto.conf`:
```
listener 1883
allow_anonymous true
```

---

## Wdrożenie w Kubernetes

### Zasoby Kubernetes

#### Przykład Deployment dla Dronów

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

#### Przykład Service dla MQTT

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mqtt-service
spec:
  selector:
    app: mqtt
  ports:
    - protocol: TCP
      port: 1883
      targetPort: 1883
```

---

## CI/CD i Monitoring

### CI/CD

- **Pipeline** automatyzuje budowanie obrazów Docker, testowanie i wdrożenie w Kubernetes.
- Narzędzia: **GitLab CI/CD**, **Jenkins**, **ArgoCD**.

### Monitoring

- **Prometheus** i **Grafana** do monitorowania metryk.
- **ELK Stack** do logowania i analizy zdarzeń.

---

## Podsumowanie

Projekt łączy konteneryzację, orkiestrację Kubernetes oraz komunikację MQTT do symulacji i zarządzania rojem dronów. System jest modularny, skalowalny i umożliwia rozbudowę o dodatkowe funkcje, takie jak optymalizacja wielokryterialna czy analiza danych w czasie rzeczywistym.
