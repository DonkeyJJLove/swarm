# Symulacja Rojów Dronów w Architekturze Kontenerowej z Bezpiecznym Dostępem (Ingress/Egress) przy użyciu Istio

## Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)  
2. [Architektura Systemu](#2-architektura-systemu)  
   - [Diagram Architektury](#diagram-architektury)  
   - [Opis Komponentów](#opis-komponentów)  
     - [Drony (`drones/`)](#drony-drones)  
     - [Broker MQTT (`server/mqtt/`)](#broker-mqtt-servermqtt)  
     - [Agregator (`aggregator/`)](#agregator-aggregator)  
     - [Aggregator API (`aggregator-api/`)](#aggregator-api-aggregator-api)  
3. [Komunikacja Sieciowa: MQTT i Aggregator API](#3-komunikacja-sieciowa-mqtt-i-aggregator-api)  
4. [Wdrożenie w Kubernetes](#4-wdrożenie-w-kubernetes)  
   - [Przykłady Deployment i Service](#przykłady-deployment-i-service)  
   - [Skalowalność i Odporność na Awarie](#skalowalność-i-odporność-na-awarie)  
5. [Integracja z Istio: Ingress i Egress Gateway](#5-integracja-z-istio-ingress-i-egress-gateway)  
   - [Wprowadzenie do Ingress i Egress Gateway](#wprowadzenie-do-ingress-i-egress-gateway)  
   - [Konfiguracja Ingress Gateway](#konfiguracja-ingress-gateway)  
   - [Konfiguracja Egress Gateway](#konfiguracja-egress-gateway)  
   - [mTLS, JWT, Rate Limiting, Blokowanie IP](#mtls-jwt-rate-limiting-blokowanie-ip)  
   - [Monitorowanie i Audyt Ruchu](#monitorowanie-i-audyt-ruchu)  
6. [CI/CD, Monitoring i Logowanie](#6-cicd-monitoring-i-logowanie)  
7. [Strategie Wdrożeń (Blue-Green, Canary)](#7-strategie-wdrożeń-blue-green-canary)  
8. [Informacje z Istniejących Plików i Rozszerzenia](#8-informacje-z-istniejących-plików-i-rozszerzenia)  
9. [Podsumowanie](#9-podsumowanie)

---

## 1. Wprowadzenie

Projekt ma na celu symulację i zarządzanie rojem dronów działających w środowisku chmurowym, wykorzystując technologie konteneryzacji (Docker), orkiestracji (Kubernetes) oraz komunikację opartą na protokole MQTT. Każdy dron działa jako niezależny kontener, autonomicznie generujący dane o swojej pozycji i stanie. Dane te są publikowane do brokera MQTT, a następnie agregowane przez specjalny komponent – **Agregator**, który może je przetwarzać, a następnie udostępniać na zewnątrz poprzez **Aggregator API (REST)**.

Dzięki wykorzystaniu **Istio Service Mesh** oraz **Ingress i Egress Gateway**, zapewniono zaawansowane mechanizmy bezpieczeństwa, obserwowalności oraz kontroli ruchu przychodzącego i wychodzącego z klastra Kubernetes. Umożliwia to m.in. wdrożenie mTLS, autoryzacji JWT, kontrolowania dostępu do zewnętrznych API, monitorowanie ruchu i szybkie reagowanie na incydenty bezpieczeństwa.

Cele projektu:  
- **Symulacja koordynacji roju dronów**  
- **Modularność i skalowalność dzięki Kubernetes**  
- **Bezpieczna i kontrolowana komunikacja sieciowa (MQTT + Istio)**  
- **Agregacja, analiza danych w czasie rzeczywistym + REST API**  
- **Najlepsze praktyki CI/CD, monitoring, logging, bezpieczeństwo**

---

## 2. Architektura Systemu

### Diagram Architektury

```
[Internet]
     |
 [Ingress Gateway - Istio] --> [Aggregator API]
                |                      
                v                      
           [Aggregator] <--- subskrypcja MQTT --- [Broker MQTT]
                                     ^
                                     |
                                [Drony - Pody]
                                     |
                                     v
                             [Egress Gateway - Istio]
                                     |
                                  [External APIs]
```

### Opis Komponentów

#### Drony (`drones/`)

- **Rola**: Każdy dron to autonomiczny kontener symulujący urządzenie IoT.
- **Funkcjonalność**:
  - Generuje dane o pozycji (x,y), stanie baterii i ewentualnych innych parametrach (np. prędkość, wysokość).
  - Publikuje dane na brokerze MQTT pod tematem:
    ```
    drones/{drone_id}/position
    ```
  - Może nasłuchiwać na komendy zwrotne (opcjonalnie) wysyłane przez agregator lub inne komponenty.
- **Skalowalność**: Liczbę dronów można łatwo zwiększać, zmieniając liczbę replik w Deployment Kubernetes.
- **Kod i Konfiguracja**:  
  Pliki znajdują się w katalogu `drones/`. Drony mają prosty skrypt (np. `drone_logic.py`), który co pewien czas publikuje dane na MQTT.

Przykładowy pseudokod `drone_logic.py`:
```python
import os
import time
import random
import paho.mqtt.client as mqtt

DRONE_ID = os.getenv("DRONE_ID", f"drone_{random.randint(1000,9999)}")
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-service")
MQTT_PORT = 1883

client = mqtt.Client(DRONE_ID)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

position = [random.randint(0,100), random.randint(0,100)]

while True:
    data = {
        "x": position[0],
        "y": position[1],
        "battery": random.randint(30,100)
    }
    client.publish(f"drones/{DRONE_ID}/position", str(data))
    # Prostą symulacją może być lekkie przesunięcie pozycji:
    position[0] += random.randint(-1,1)
    position[1] += random.randint(-1,1)
    time.sleep(5)
```

#### Broker MQTT (`server/mqtt/`)

- **Rola**: Centralny punkt komunikacyjny oparty o model publish/subscribe.
- **Funkcjonalność**:
  - Odbiera dane publikowane przez drony.
  - Rozsyła je do subskrybentów, np. agregatora.
- **Technologia**: Mosquitto.
- **Konfiguracja**: Pliki w `server/mqtt/`.
- **Bezpieczeństwo**: W trybie produkcyjnym zaleca się TLS i uwierzytelnianie. W środowisku deweloperskim może być `allow_anonymous true`.

Przykładowy `mosquitto.conf`:
```plaintext
listener 1883
allow_anonymous true
```

#### Agregator (`aggregator/`)

- **Rola**: Subskrybuje dane od wszystkich dronów i je przetwarza.
- **Funkcjonalność**:
  - Subskrybuje temat `drones/+/position`, co umożliwia odbiór danych od wszystkich dronów jednocześnie.
  - Agreguje dane, może je filtrować, analizować, zapisywać do bazy danych.
  - Przygotowuje dane do udostępnienia przez Aggregator API.
- **Kod i Konfiguracja**: W katalogu `aggregator/`.
- **Dokumentacja Szczegółowa**: [_docs/aggregator_details.md](./_docs/aggregator_details.md)

Przykładowy pseudokod `aggregator.py`:
```python
import paho.mqtt.client as mqtt

AGGREGATOR_PORT = 5001
MQTT_BROKER = "mqtt-service"
MQTT_PORT = 1883

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    # Przetwarzanie danych drona
    # Zapisy do pamięci/bazy, przygotowanie do udostępnienia przez API.

client = mqtt.Client("aggregator")
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe("drones/+/position")
client.loop_forever()
```

#### Aggregator API (`aggregator-api/`)

- **Rola**: REST API do interakcji zewnętrznych systemów z danymi agregatora.
- **Funkcjonalność**:
  - Endpointy:  
    ```http
    GET /api/drones            # Lista dronów i ich ostatnie dane
    GET /api/drones/{drone_id}/status  # Szczegóły pojedynczego drona
    POST /api/drones/{drone_id}/update # Wysyłanie komend
    ```
- **Kod i Konfiguracja**: W `aggregator-api/`.
- **Dokumentacja Szczegółowa**: [_docs/aggregator_api_details.md](./_docs/aggregator_api_details.md)

Przykładowy pseudokod `aggregator_api.py`:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# Załóżmy, że agregator zapisuje dane w pamięci lub w bazie:
drones_data = {}

@app.route("/api/drones", methods=["GET"])
def list_drones():
    return jsonify(drones_data), 200

@app.route("/api/drones/<drone_id>/status", methods=["GET"])
def drone_status(drone_id):
    return jsonify(drones_data.get(drone_id, {})), 200

@app.route("/api/drones/<drone_id>/update", methods=["POST"])
def update_drone(drone_id):
    command = request.json
    # Wysyłanie komendy do drona (może przez inny topic MQTT)
    return jsonify({"status": "command sent"}), 200
```

---

## 3. Komunikacja Sieciowa: MQTT i Aggregator API

**Przepływ Danych:**
1. **Drony** publikują dane na brokerze MQTT, np.:
   ```json
   Topic: drones/drone_1234/position
   Payload: {"x":10,"y":20,"battery":95}
   ```
2. **Agregator** subskrybuje `drones/+/position`, odbiera dane od wszystkich dronów.
3. **Aggregator API** udostępnia przetworzone dane przez REST:
   ```http
   GET /api/drones/drone_1234/status
   ```
   
**Zalety MQTT:**  
- Asynchroniczne, lekkie, idealne dla IoT.  
- Prosty model publish/subscribe.

**Integracja z API:**  
- API zapewnia dostęp do aktualnych danych dronów oraz umożliwia sterowanie rojem przez zewnętrzne systemy.

---

## 4. Wdrożenie w Kubernetes

Kubernetes umożliwia deklaratywne zarządzanie infrastrukturą oraz skalowalność wszystkich komponentów (dronów, brokera, agregatora, API).

**Przykład Deployment dla Dronów:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drone-deployment
spec:
  replicas: 5
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
        image: localhost:5000/mydrone:latest
        env:
        - name: MQTT_BROKER
          value: "mqtt-service"
```

**Przykład Service dla MQTT:**
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

### Skalowalność i Odporność na Awarie

- **Skalowalność:** Możemy zwiększyć `replicas` dla dronów lub agregatora, gdy rośnie obciążenie.
- **Odporność:** Jeśli pod z dronem lub agregatorem padnie, Kubernetes automatycznie uruchomi nowy.

---

## 5. Integracja z Istio: Ingress i Egress Gateway

### Wprowadzenie do Ingress i Egress Gateway

**Ingress Gateway (Istio):**  
- Kontroluje ruch przychodzący do klastra.  
- Zapewnia mTLS, autoryzację JWT i inne polityki bezpieczeństwa.

**Egress Gateway (Istio):**  
- Kontroluje ruch wychodzący z klastra do zewnętrznych usług.  
- Ogranicza dostęp tylko dla określonych podów i domen.

### Konfiguracja Ingress Gateway

1. **Instalacja Istio:**  
```bash
istioctl install --set profile=demo -y
```

2. **Certyfikaty TLS:**  
```bash
kubectl create -n istio-system secret tls aggregator-ingress-credential \
  --key /path/to/tls.key \
  --cert /path/to/tls.crt
```

3. **Definicja Gateway:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: aggregator-ingress-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: aggregator-ingress-credential
    hosts:
    - "aggregator.example.com"
```

4. **VirtualService:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: aggregator-virtualservice
  namespace: default
spec:
  hosts:
  - "aggregator.example.com"
  gateways:
  - istio-system/aggregator-ingress-gateway
  http:
  - match:
    - uri:
        prefix: /api
    route:
    - destination:
        host: aggregator-api-service.default.svc.cluster.local
        port:
          number: 80
```

### Konfiguracja Egress Gateway

1. **ServiceEntry:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: external-api-service
  namespace: default
spec:
  hosts:
  - "api.external-payments.com"
  ports:
  - number: 443
    name: https
    protocol: TLS
  resolution: DNS
  location: MESH_EXTERNAL
```

2. **VirtualService dla Egress:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: external-api-route
  namespace: default
spec:
  hosts:
  - "api.external-payments.com"
  gateways:
  - istio-egressgateway
  - mesh
  tls:
  - match:
    - sniHosts:
      - "api.external-payments.com"
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        port:
          number: 443
```

3. **DestinationRule dla mTLS:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: external-api-mtls
  namespace: default
spec:
  host: istio-egressgateway.istio-system.svc.cluster.local
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
      credentialName: egressgateway-certs
      sni: api.external-payments.com
```

### mTLS, JWT, Rate Limiting, Blokowanie IP

- **mTLS:** Zapewnia szyfrowanie i wzajemne uwierzytelnianie (Zero Trust).
- **JWT:** Autoryzacja użytkowników, np. dla dostępu do Aggregator API.
- **Rate Limiting:** Ochrona przed DDoS i nadużyciami.
- **Blokowanie IP:** Odrzucanie ruchu z podejrzanych źródeł.

Przykład autoryzacji JWT:
```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: aggregator-jwt
  namespace: default
spec:
  jwtRules:
  - issuer: "https://identity.provider.com/"
    jwksUri: "https://identity.provider.com/.well-known/jwks.json"
```

Blokowanie IP:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: block-suspicious-ips
  namespace: default
spec:
  action: DENY
  rules:
  - from:
    - source:
        ipBlocks: ["192.168.1.100/32"]
```

### Monitorowanie i Audyt Ruchu

Istio integruje się z Prometheus, Grafana, Kiali, co pozwala monitorować ruch, metryki, kody statusów, opóźnienia. Logi z Ingress i Egress Gateway można analizować w ELK Stack, co ułatwia audyt i detekcję incydentów.

---

## 6. CI/CD, Monitoring i Logowanie

**CI/CD:**
- Budowanie obrazów Docker, testy, wdrożenia manifestów Kubernetes przez pipeline CI/CD.
- Narzędzia: GitLab CI/CD, Jenkins, ArgoCD.

**Monitoring (Prometheus/Grafana):**
- Prometheus zbiera metryki, Grafana wizualizuje.
- Metryki: zużycie zasobów, opóźnienia, liczba przetworzonych komunikatów.

**Logowanie (ELK Stack):**
- Elasticsearch + Logstash + Kibana do zbierania i analizy logów.
- Centralne logowanie dronów, agregatora, API i gatewayów Istio.

---

## 7. Strategie Wdrożeń (Blue-Green, Canary)

**Blue-Green:**
- Dwie wersje aplikacji (stara i nowa) działają równolegle.
- Szybkie przełączenie ruchu na nową wersję bez przestoju.

**Canary:**
- Stopniowe wdrażanie nowej wersji do części ruchu (np. 5%).
- Minimalizacja ryzyka awarii w całym systemie.

Dokumentacja strategii wdrożeń: [_docs/strategia_blue_green_canary.md](./_docs/strategia_blue_green_canary.md)

---

## 8. Informacje z Istniejących Plików i Rozszerzenia

**W `_docs/` znajdują się:**  
- `broker_mqtt.md`: Szczegóły o brokerze MQTT.  
- `aggregator_details.md`: Szczegółowy opis agregatora.  
- `aggregator_api_details.md`: Szczegóły Aggregator API.  
- `readme.md`: Ogólny opis projektu, chmury hybrydowe, CI/CD, monitoringu.  
- `strategia_blue_green_canary.md`: Strategie wdrożeń.  
- Dokumentacja budowania i zarządzania obrazami dockerowymi, best practices produkcyjnych.

---

## 9. Podsumowanie

Projekt łączy zaawansowane technologie chmurowe, IoT i najlepsze praktyki bezpieczeństwa:  
- **Drony** publikują dane do **Brokera MQTT**.  
- **Agregator** subskrybuje i przetwarza dane, udostępnia je przez **Aggregator API**.  
- **Kubernetes** zapewnia skalowalność, deklaratywne zarządzanie, automatyczne restarty.  
- **Istio** (Ingress/Egress Gateway) wnosi zaawansowane bezpieczeństwo, mTLS, autoryzację JWT, monitorowanie i kontrolę ruchu.  
- **CI/CD**, **Monitoring** i **Logowanie** zapewniają ciągłe dostarczanie, łatwą diagnostykę i reakcję na problemy.

Dzięki tym elementom system jest skalowalny, odporny na awarie, bezpieczny i łatwo zarządzalny. Możliwość rozbudowy o nowe funkcje (np. sztuczną inteligencję do optymalizacji lotu dronów) jest prosta dzięki modularnej architekturze.

Projekt stanowi solidną bazę do eksperymentów z komunikacją IoT, orkiestracją kontenerów, bezpieczeństwem sieciowym oraz najlepszymi praktykami wdrożeń chmurowych.