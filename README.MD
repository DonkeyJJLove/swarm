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
9. [Implementacja Logiki, Sterowania i Bezpieczeństwo w Klastrze](#9-implementacja-logiki-sterowania-i-bezpieczeństwo-w-klastrze)  
10. [Podsumowanie](#10-podsumowanie)

---

## 1. Wprowadzenie

Projekt ma na celu symulację i zarządzanie rojem dronów działających w środowisku chmurowym. Wykorzystuje on konteneryzację (Docker), orkiestrację (Kubernetes) oraz komunikację opartą na protokole MQTT. Każdy dron działa jako niezależny kontener i autonomicznie generuje dane o swojej pozycji oraz stanie baterii. Dane te są publikowane do brokera MQTT, a następnie zbierane i przetwarzane przez komponent **Agregator**, który udostępnia je poprzez **Aggregator API (REST)**.

Dzięki integracji z Istio Service Mesh oraz użyciu Ingress i Egress Gateway, możliwe jest zapewnienie zaawansowanych mechanizmów bezpieczeństwa (mTLS, JWT, blokowanie IP), obserwowalności (monitoring, logging) i kontroli ruchu sieciowego (rate limiting, polityki dostępu).

**Cele projektu:**
- Symulacja koordynacji roju dronów.
- Modularność i skalowalność dzięki Kubernetes.
- Bezpieczna i kontrolowana komunikacja (MQTT + Istio).
- Agregacja i analiza danych w czasie rzeczywistym (Aggregator API).
- CI/CD, monitoring, logging oraz strategie wdrożeń (Blue-Green, Canary).

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

- **Rola**: Każdy dron to kontener symulujący urządzenie IoT.
- **Funkcjonalność**:
  - Publikuje dane o położeniu i stanie baterii na brokerze MQTT.
  - Temat (topic) MQTT: `drones/{drone_id}/position`.
- **Skalowalność**: Zmiana liczby replik w Deployment Kubernetes.
- **Kod i Konfiguracja**: Katalog `drones/`.

#### Broker MQTT (`server/mqtt/`)

- **Rola**: Centralny punkt komunikacji (publish/subscribe).
- **Funkcjonalność**:
  - Odbiera dane od dronów.
  - Rozsyła dane do subskrybentów (np. agregatora).
- **Technologia**: Mosquitto.
- **Konfiguracja**: Katalog `server/mqtt/`.

Przykładowa konfiguracja `mosquitto.conf`:
```plaintext
listener 1883
allow_anonymous true
```

#### Agregator (`aggregator/`)

- **Rola**: Subskrybuje dane z MQTT i je przetwarza.
- **Funkcjonalność**:
  - Subskrypcja `drones/+/position`.
  - Agregacja i analiza danych, ewentualne zapisy do bazy.
- **Kod i Konfiguracja**: Katalog `aggregator/`.
- **Dokumentacja**: [aggregator_details.md](./_docs/aggregator_details.md).

#### Aggregator API (`aggregator-api/`)

- **Rola**: Udostępnia dane z agregatora poprzez REST API.
- **Funkcjonalność**:
  - `GET /api/drones` – lista dronów i ich status.
  - `GET /api/drones/{drone_id}/status` – dane wybranego drona.
  - `POST /api/drones/{drone_id}/update` – wysyłanie komend.
- **Kod i Konfiguracja**: Katalog `aggregator-api/`.
- **Dokumentacja**: [aggregator_api_details.md](./_docs/aggregator_api_details.md).

---

## 3. Komunikacja Sieciowa: MQTT i Aggregator API

1. **Drony** publikują dane na brokerze MQTT:
   ```json
   Topic: drones/{drone_id}/position
   Payload: {"x":10,"y":20,"battery":95}
   ```
2. **Agregator** subskrybuje `drones/+/position` i odbiera dane od wszystkich dronów jednocześnie.
3. **Aggregator API** udostępnia dane przez REST:
   ```http
   GET /api/drones/{drone_id}/status
   ```

**Zalety MQTT**:
- Lekkość i asynchroniczność.
- Łatwość skalowania na wiele urządzeń IoT.

**Integrator (Aggregator API)**:
- Zapewnia dostęp do danych dla użytkowników końcowych, systemów analitycznych lub interfejsów sterujących.

---

## 4. Wdrożenie w Kubernetes

Wykorzystanie Kubernetes pozwala na łatwe zarządzanie kontenerami, skalowanie aplikacji i zapewnienie wysokiej dostępności.

### Przykłady Deployment i Service

**Deployment dronów:**
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
        image: drone-simulation:latest
        env:
        - name: MQTT_BROKER
          value: "mqtt-service"
```

**Service dla MQTT:**
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

- **Skalowalność:** Zwiększanie liczby replik dronów lub agregatora w zależności od obciążenia.
- **Odporność:** Kubernetes automatycznie restartuje pody i zapewnia ciągłość działania.

---

## 5. Integracja z Istio: Ingress i Egress Gateway

Istio Service Mesh zapewnia rozbudowane funkcje bezpieczeństwa, kontroli i obserwowalności ruchu sieciowego.

### Wprowadzenie do Ingress i Egress Gateway

- **Ingress Gateway:** Kontroluje ruch przychodzący do klastra, pozwala na wdrożenie mTLS, autoryzacji JWT.
- **Egress Gateway:** Kontroluje ruch wychodzący z klastra, zapewniając kontrolę nad połączeniami do zewnętrznych usług.

### Konfiguracja Ingress Gateway

Przykładowy Gateway:
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

VirtualService dla Aggregator API:
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

Przykładowy ServiceEntry:
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

Dalsza konfiguracja VirtualService i DestinationRule umożliwia kontrolę i uwierzytelnianie ruchu wychodzącego.

### mTLS, JWT, Rate Limiting, Blokowanie IP

- **mTLS:** Wzajemne uwierzytelnianie między usługami w klastrze.
- **JWT:** Autoryzacja użytkowników do Aggregator API.
- **Rate Limiting:** Ograniczanie liczby żądań, ochrona przed DDoS.
- **Blokowanie IP:** Odmawianie dostępu ruchowi z podejrzanych źródeł.

### Monitorowanie i Audyt Ruchu

- Integracja z Prometheus, Grafana, Kiali do monitorowania ruchu, metryk, logów.
- Audyt i analiza zdarzeń bezpieczeństwa, wykrywanie anomalii.

---

## 6. CI/CD, Monitoring i Logowanie

- **CI/CD:**  
  Automatyzacja budowy obrazów Docker, testów, wdrożeń do Kubernetes.  
  Narzędzia: GitLab CI/CD, Jenkins, ArgoCD.

- **Monitoring (Prometheus/Grafana):**  
  Zbiór metryk i wizualizacja w Grafanie. Monitorowanie zużycia zasobów, stanu dronów, opóźnień.

- **Logowanie (ELK Stack):**  
  Elasticsearch, Logstash, Kibana do centralnej analizy logów dronów, agregatora, API i gatewayów Istio.

---

## 7. Strategie Wdrożeń (Blue-Green, Canary)

- **Blue-Green:**  
  Dwie wersje działają równolegle, szybkie przełączenie ruchu na nową wersję.

- **Canary:**  
  Stopniowe kierowanie części ruchu do nowej wersji w celu testowania jej stabilności przed pełnym wdrożeniem.

Dokumentacja: [strategia_blue_green_canary.md](./_docs/strategia_blue_green_canary.md)

---

## 8. Informacje z Istniejących Plików i Rozszerzenia

- [**`_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md`**](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md)  
  Budowanie i zarządzanie obrazami Docker (multi-stage builds, versioning, repozytoria).

- [**`_docs/strategia_blue_green_canary.md`**](./_docs/strategia_blue_green_canary.md)  
  Strategie wdrożeń Blue-Green i Canary.

- [**`_docs/readme.md`**](./_docs/readme.md)  
  Ogólny opis projektu: symulacja roju, komunikacja MQTT, wdrożenie, monitoring, CI/CD.

Dodatkowe dokumenty w `_docs/` omawiają szczegółowo komponenty takie jak broker MQTT, agregator, API oraz najlepsze praktyki w budowaniu obrazów i wdrożeniach.

---

## 9. Implementacja Logiki, Sterowania i Bezpieczeństwo w Klastrze

Po skonfigurowaniu klastra i uruchomieniu dronów oraz agregatora, kolejnym krokiem jest implementacja logiki zarządzającej dronami:

- **Decyzje Autonomiczne:**  
  Każdy dron (pod) może podejmować decyzje na podstawie otrzymywanych danych i warunków środowiskowych.

- **Bezpieczeństwo Kontenerów:**  
  Zasady bezpieczeństwa (np. Pod Security Policies lub obecnie Pod Security Admission), RBAC, Network Policies oraz Secrets Management chronią kontenery przed nieautoryzowanym dostępem.

- **Monitorowanie i Logowanie:**  
  Narzędzia jak Prometheus, Grafana, ELK Stack zapewniają wgląd w stan klastra, logi i metryki dronów oraz pozwalają na szybką reakcję na incydenty.

- **Skalowalność:**  
  Automatyczne skalowanie dronów w odpowiedzi na zmieniające się warunki obciążenia.

---

## 10. Podsumowanie

Całość projektu stanowi kompleksowe rozwiązanie do symulacji i zarządzania rojem dronów w chmurowej infrastrukturze kontenerowej. Dzięki wykorzystaniu MQTT, Kubernetes, Istio, CI/CD, monitoringu i strategii wdrożeń Blue-Green i Canary, system jest skalowalny, odporny, bezpieczny i łatwy w utrzymaniu. Rozbudowa o nowe funkcje, jak autonomiczne algorytmy sterowania czy integracje z zewnętrznymi usługami, jest prosta dzięki modularnej architekturze.

Projekt ten stanowi bazę do dalszych eksperymentów i wdrożeń w obszarach IoT, chmury i mikrousług, demonstrując najlepsze praktyki w zarządzaniu środowiskiem wielokontenerowym i wysoce skalowalnym.  
```