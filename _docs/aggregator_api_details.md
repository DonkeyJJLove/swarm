# **`aggregator_api_details.md`**  
Dokumentacja Szczegółowa Komponentu **Aggregator API**

## Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)  
2. [Cele i Zakres](#2-cele-i-zakres)  
3. [Architektura i Kontekst](#3-architektura-i-kontekst)  
4. [Implementacja: `aggregator_api.py`](#4-implementacja-aggregator_apipy)  
   - [4.1 Struktura Kodowa](#41-struktura-kodowa)  
   - [4.2 Główne Endpointy i Przykłady](#42-główne-endpointy-i-przykłady)  
   - [4.3 Połączenie z Agregatorem / Bazą](#43-połączenie-z-agregatorem--bazą)  
5. [Wdrożenie w Kubernetes](#5-wdrożenie-w-kubernetes)  
   - [5.1 Manifest `aggregator-api-deployment.yaml`](#51-manifest-aggregator-api-deploymentyaml)  
   - [5.2 Manifest `aggregator-api-service.yaml`](#52-manifest-aggregator-api-serviceyaml)  
6. [Bezpieczeństwo i Uwagi Dotyczące Istio](#6-bezpieczeństwo-i-uwagi-dotyczące-istio)  
7. [Konfiguracja i Zmienne Środowiskowe](#7-konfiguracja-i-zmienne-środowiskowe)  
8. [Scenariusze Rozszerzeń](#8-scenariusze-rozszerzeń)  
9. [Typowe Problemy i Rozwiązywanie](#9-typowe-problemy-i-rozwiązywanie)  
10. [Odnośniki](#10-odnośniki)

---

## 1. Wprowadzenie
**Aggregator API** to moduł zapewniający **warstwę REST** do komunikowania się z danymi przetwarzanymi w **Aggregator** (drony, stany, pozycje) i potencjalnie innymi mikrousługami. Można go traktować jako:

- **Interfejs dla operatorów / dashboardów**: Pozwala na podejrzenie aktualnego stanu roju, wysyłanie komend do dronów.  
- **Warstwa integracji**: Może być używany przez zewnętrzne systemy (np. system AI, monitorowanie floty w real time) do pobierania danych o dronach i zdarzeniach.

**Główne atuty**:  
- Oddzielenie logiki zbierania danych (Aggregator) od warstwy REST (Aggregator API).  
- Skalowalność: Można replikować aggregator-api w Kubernetes, dzięki czemu obsługuje większą liczbę żądań REST.

---

## 2. Cele i Zakres
1. **Zarządzanie Rojem**:  
   - Pozwala operatorom wywoływać np. `POST /api/drones/{id}/update`, by zmienić trasę drona lub jego parametry.  
   - Wersjonowanie i obserwacja historii zmian (opcjonalnie).

2. **Dostęp do Aktualnych Danych**:  
   - `GET /api/drones` — zwraca listę dronów i podstawowe atrybuty (pozycja, bateria).  
   - `GET /api/drones/{id}/status` — bardziej szczegółowe informacje o jednym dronie.

3. **Bezpieczeństwo**:  
   - Możliwość integracji z **Istio** (Ingress Gateway) do uwierzytelniania JWT, rate limiting.  
   - RBAC i autoryzacja – ograniczenie, kto może sterować dronami / modyfikować parametry.

---

## 3. Architektura i Kontekst
**Aggregator API** zwykle działa w parze z:

- **Aggregator**: skąd pobiera dane – czy to przez wewnętrzne wywołania (np. Python function call, lub gRPC) czy REST.  
- **Baza danych** (opcjonalnie): jeśli aggregator zapisuje dane w DB, aggregator-api może się z nią łączyć.  
- **Istio Ingress Gateway**: jeśli chcemy wystawiać aggregator-api na zewnątrz klastra, typowo jest dołączany do gateway (TLS, autoryzacja JWT, itp.).

Diagram (uproszczony):

```
 [External Users]  --- (TLS/HTTP) --->  [Istio Ingress Gateway] ---> [Aggregator API]
                                                     | 
                                                     v
                                                 [Aggregator]
                                                     |
                                                     v
                                         [Baza lub Bezpośrednio w pamieci]
```

---

## 4. Implementacja: `aggregator_api.py`

### 4.1 Struktura Kodowa
Najczęściej tworzymy **prosty** serwer REST w Pythonie (Flask, FastAPI). Przykładowo:

```python
# aggregator_api.py
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Przykładowa pamięć podręczna (lub wywołania do aggregator)
DRONES_DATA = {
    "drone_1": {"x": 10, "y": 20, "battery": 95, "status": "active"},
    "drone_2": {"x": 5,  "y": 7,  "battery": 80, "status": "charging"}
}

@app.route("/api/drones", methods=["GET"])
def get_all_drones():
    # Zwraca listę dronów
    return jsonify(DRONES_DATA)

@app.route("/api/drones/<drone_id>/status", methods=["GET"])
def get_drone_status(drone_id):
    # Zwraca status pojedynczego drona
    if drone_id in DRONES_DATA:
        return jsonify({drone_id: DRONES_DATA[drone_id]})
    else:
        return jsonify({"error": "Drone not found"}), 404

@app.route("/api/drones/<drone_id>/update", methods=["POST"])
def update_drone(drone_id):
    # Aktualizuje dane drona - np. nowa trasa, status
    # Przykład: JSON body: {"x": 15, "y": 25, "battery": 90}
    if drone_id not in DRONES_DATA:
        return jsonify({"error": "Drone not found"}), 404

    new_data = request.get_json()
    DRONES_DATA[drone_id].update(new_data)
    return jsonify({"message": f"Drone {drone_id} updated", "data": DRONES_DATA[drone_id]})

if __name__ == "__main__":
    port = int(os.getenv("AGGREGATOR_API_PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
```

### 4.2 Główne Endpointy i Przykłady
1. **`GET /api/drones`**  
   - Zwraca listę wszystkich dronów i ich podstawowych danych.  
   - **Kod**: 200 OK, body JSON.

2. **`GET /api/drones/{drone_id}/status`**  
   - Szczegóły pojedynczego drona (pozycja, bateria, status).  
   - **Kod**: 200 lub 404 (gdy dron nie istnieje).

3. **`POST /api/drones/{drone_id}/update`**  
   - Pozwala zmienić parametry drona (np. trasę, status).  
   - **Kod**: 200 OK, body JSON z aktualnymi danymi drona, lub 404 jeśli dron nie istnieje.

### 4.3 Połączenie z Agregatorem / Bazą
**W realnym scenariuszu** aggregator-api nie powinien trzymać stanu w słowniku Python (`DRONES_DATA`), tylko:

- Wewnętrzny REST lub gRPC do **Aggregator** (np. `GET /internal/aggregator/drones`),
- **Baza danych** (MongoDB, Redis, SQL) – aggregator zapisuje tam dane, aggregator-api je odczytuje,
- Komunikacja typu Pub/Sub (np. aggregator wysyła zmiany do aggregator-api przez kolejkę, a aggregator-api trzyma je w pamięci lub w DB).

---

## 5. Wdrożenie w Kubernetes

### 5.1 Manifest `aggregator-api-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aggregator-api
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
        image: myrepo/aggregator-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: AGGREGATOR_API_PORT
          value: "5000"
```

- **replicas: 2** – Dwie kopie aggregator-api dla obciążenia lub wysokiej dostępności.

### 5.2 Manifest `aggregator-api-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aggregator-api-service
spec:
  selector:
    app: aggregator-api
  ports:
    - name: http
      port: 80
      targetPort: 6001
  type: ClusterIP
```

- Aby wystawić aggregator-api poza klaster, używamy Istio Ingress Gateway (lub innego mechanizmu).

---

## 6. Bezpieczeństwo i Uwagi Dotyczące Istio
- **Ingress Gateway**:  
  - Można skonfigurować `Gateway` + `VirtualService`, by np. `aggregator.example.com/api` trafiało do `aggregator-api-service:80`.
- **mTLS**:  
  - Ruch aggregator-api ↔ aggregator (jeśli aggregator jest np. wystawiony na innym wewnętrznym serwisie) może być szyfrowany i autoryzowany w obrębie mesha.
- **Rate Limiting, JWT**:
  - Zaletą posiadania aggregator-api wystawionego przez Istio jest możliwość skonfigurowania mechanizmów Envoy: np. token JWT do uwierzytelniania, EnvoyFilter do limitowania żądań.

---

## 7. Konfiguracja i Zmienne Środowiskowe
- **`AGGREGATOR_API_PORT`** (domyślnie 5000): Na którym porcie aggregator-api nasłuchuje wewnątrz kontenera.
- **`DEBUG`** (opcjonalnie): Włączenie dodatkowych logów Flask.
- **`DB_HOST`, `DB_PORT`** (opcjonalnie): jeśli aggregator-api pobiera dane z bazy.

W **Dockerfile** można użyć:

```dockerfile
ENV AGGREGATOR_API_PORT=6001
EXPOSE 6001
```

---

## 8. Scenariusze Rozszerzeń

1. **Autentykacja i Autoryzacja**:  
   - Włączenie JWT / OAuth2, by tylko zalogowani użytkownicy mogli wywoływać `POST /api/drones/{id}/update`.
   - Integracja z kluczem API w nagłówkach, itp.

2. **Baza danych**:  
   - Zamiast przechowywać dane w pamięci, aggregator-api może czytać z bazy (np. PostgreSQL, Redis).  
   - Każdy dron = wiersz w tabeli / klucz w Redis, z aktualną pozycją.

3. **Wzorce**:  
   - **CQRS**: aggregator-api jedynie wystawia endpointy do odczytu, a zapisy robi aggregator → DB.  
   - **Event sourcing**: Każda zmiana stanu drona to event zapisywany w logach / strumieniu.

4. **Notyfikacje**:  
   - aggregator-api może np. wysyłać WebHook do innego systemu, gdy dron ma niski poziom baterii.

---

## 9. Typowe Problemy i Rozwiązywanie

1. **Błąd 404** przy `GET /api/drones/{id}`:
   - Upewnij się, że aggregator-api zna/posiada dane o danym `drone_id`. Możliwe, że dron nigdy się nie zarejestrował.

2. **Brak danych**:  
   - Sprawdź, czy aggregator faktycznie przekazuje dane do aggregator-api lub do bazy.  
   - Ewentualnie czy aggregator-api ma poprawną konfigurację bazy (jeśli używamy DB).

3. **Zbyt długie czasy odpowiedzi**:  
   - Skaluj replik aggregator-api (Horizontal Pod Autoscaler).  
   - Szybki mechanizm cache (Redis?), zamiast czekać na aggregator za każdym razem.

4. **Problemy z TLS / Istio**:
   - Upewnij się, że port 80 (w Service aggregator-api) jest obsługiwany przez VirtualService, a sidecar Envoy ma rule do przepuszczania ruchu.  
   - W logach aggregator-api (lub w Kiali) zobacz, czy nie dochodzi do błędów TLS handshake.

---

## 10. Odnośniki
- **Główny README**: [README.MD](../README.MD) – Ogólny opis projektu i architektury.  
- **`aggregator_details.md`**: Wewnętrzne mechanizmy aggregator.  
- **`broker_mqtt.md`**: Konfiguracja brokera MQTT (Mosquitto).  
- **`system_ai_details.md`**: Warstwa AI, jeśli aggregator-api ma dostarczać dane do trenowania modeli.  
- **`security_tests_details.md`**: Scenariusze ataków i testów penetracyjnych w warstwie API.  
- **`strategia_blue_green_canary.md`**: Metody wdrażania aggregator-api w sposób bezinwazyjny, z minimalnym ryzykiem.

---

**Podsumowanie**  
Komponent **Aggregator API** w projekcie **Laboratory Swarm** stanowi **kluczowe ogniwo** między danymi dronów (przetwarzanych przez aggregator) a światem zewnętrznym (użytkownicy, systemy AI, panele zarządzania). Jego odpowiednia konfiguracja w Kubernetes (plus wykorzystanie Istio do bezpieczeństwa i kontroli ruchu) pozwala na **skalowalne**, **bezpieczne** i **intuicyjne** udostępnianie informacji i funkcji zarządzania rojem IoT.