# **Laboratory Swarm**  
**Laboratorium Bezpieczeństwa Chmurowego: Symulacja Rojów Dronów z AI i Zabezpieczeniami Istio**

## Spis Treści

1. [Wprowadzenie i Cel](#1-wprowadzenie-i-cel)
2. [Architektura Systemu](#2-architektura-systemu)
   - [Wysokopoziomowy Diagram Architektury](#wysokopoziomowy-diagram-architektury)
   - [Opis Przepływu Danych](#opis-przepływu-danych)
3. [Komponenty Systemu](#3-komponenty-systemu)
   - [Drony (IoT) – `drones/`](#drony-iot---drones)
   - [Broker MQTT i `mqtt_bridge/`](#broker-mqtt-i-mqtt_bridge)
   - [Agregator – `aggregator/`](#agregator---aggregator)
   - [Aggregator API – `aggregator-api/`](#aggregator-api---aggregator-api)
   - [System AI (ML) – `system-ai/`](#system-ai-ml---system-ai)
   - [Warstwa Skryptów i CI/CD – `scripts/`, `server/`](#warstwa-skryptów-i-cicd---scripts-server)
4. [Funkcje i Scenariusze Użycia](#4-funkcje-i-scenariusze-użycia)
5. [Kluczowe Założenia Technologiczne](#5-kluczowe-założenia-technologiczne)
6. [Integracja z Kubernetes i Istio](#6-integracja-z-kubernetes-i-istio)
7. [Bezpieczeństwo, CI/CD, Testy i Monitoring](#7-bezpieczeństwo-cicd-testy-i-monitoring)
   - [Bezpieczeństwo](#bezpieczeństwo)
   - [CI/CD](#cicd)
   - [Testy](#testy)
   - [Monitoring](#monitoring)
8. [Instrukcje Uruchomienia](#8-instrukcje-uruchomienia)
9. [Dalsza Dokumentacja](#9-dalsza-dokumentacja)
10. [Wsparcie i Rozwój](#10-wsparcie-i-rozwój)

---

## 1. Wprowadzenie i Cel

**Laboratory Swarm** to **eksperymentalny projekt** mający na celu stworzenie **laboratorium bezpieczeństwa chmurowego**, które integruje **IoT (drony)**, **Machine Learning (AI)** oraz **mechanizmy bezpieczeństwa** w środowisku **Cloud Native** (Kubernetes + Istio + Docker). Projekt umożliwia:

- **Symulację roju dronów** publikujących dane telemetryczne.
- **Zarządzanie i analizę** tych danych poprzez agregatory i system AI.
- **Implementację zaawansowanych zabezpieczeń** na różnych poziomach infrastruktury i aplikacji.
- **Praktyczne testowanie** mechanizmów DevSecOps, testów penetracyjnych oraz chaos engineering.

Celem jest stworzenie **modularnej, skalowalnej i bezpiecznej platformy**, która pozwoli na **badanie i naukę** w obszarach związanych z **IoT**, **bezpieczeństwem chmurowym**, **ML** oraz **DevSecOps**.

---

## 2. Architektura Systemu

### Wysokopoziomowy Diagram Architektury

Poniższy diagram przedstawia ogólny zarys architektury systemu **Laboratory Swarm**. Pokazuje główne komponenty oraz ich interakcje.

```
                    [Internet]
                         |
            [Ingress Gateway - Istio]
                         |
                         v
               [Aggregator API]
                         |
                         v
                  [Aggregator] 
                         |
                         v
                  [System AI - ML]
                         |
                         v
              [Egress Gateway - Istio]
                         |
                  [External APIs]
        
                      ^
                      |
                 [Drony - Pody]
                      |
                      v
              (publikacja MQTT)
```

### Opis Przepływu Danych

1. **Drony (IoT)**
    - **Opis**: Symulowane drony generują dane telemetryczne, takie jak pozycja, stan baterii i prędkość.
    - **Działanie**:
        - Publikują dane na dedykowane topiki MQTT (np. `drones/{id}/position`).
        - Działają jako wewnętrzne komponenty systemu, uruchamiane jako osobne pody w Kubernetes.

2. **Broker MQTT (Mosquitto)**
    - **Opis**: Centralny serwer MQTT, który odbiera dane publikowane przez drony.
    - **Działanie**:
        - Odbiera dane telemetryczne od dronów.
        - Przekazuje dane do **Aggregatora** poprzez subskrypcję MQTT.
    - **Zabezpieczenia**:
        - Komunikacja zabezpieczona TLS/mTLS.
        - Autoryzacja użytkowników i ograniczenia dostępu za pomocą ACL.

3. **Aggregator**
    - **Opis**: Komponent odpowiedzialny za zbieranie i wstępne przetwarzanie danych z brokera MQTT.
    - **Działanie**:
        - Subskrybuje odpowiednie topiki MQTT.
        - Przetwarza dane (np. filtruje, wykrywa anomalie).
        - Przekazuje przetworzone dane do **Aggregator API** oraz **Systemu AI**.
    - **Zabezpieczenia**:
        - Walidacja danych wejściowych.
        - Ograniczenie dostępu do brokera MQTT tylko dla agregatora i bridge.

4. **Aggregator API**
    - **Opis**: Interfejs RESTful, który udostępnia przetworzone dane dla zewnętrznych aplikacji.
    - **Działanie**:
        - Obsługuje endpointy takie jak `GET /api/drones`, `GET /api/drones/{id}/status`.
        - Zapewnia autoryzację użytkowników za pomocą JWT/OAuth2.
    - **Zabezpieczenia**:
        - Autoryzacja i uwierzytelnianie użytkowników.
        - Rate limiting i logowanie żądań.
        - Ograniczenie dostępu przez **Istio AuthorizationPolicy**.

5. **System AI (ML)**
    - **Opis**: Analizuje dane w czasie rzeczywistym, trenuje modele ML i podejmuje decyzje dotyczące sterowania ruchem dronów.
    - **Działanie**:
        - Trenowanie modeli na danych historycznych i bieżących.
        - Wykrywanie anomalii i optymalizacja tras dronów.
        - Reagowanie na sytuacje awaryjne (np. niska bateria, kolizje).
    - **Zabezpieczenia**:
        - Ochrona przed atakami adversarial i data poisoning.
        - Zarządzanie wersjami modeli (model governance).
        - Autoryzacja dostępu do modeli i interfejsów zarządzania.

6. **Istio Service Mesh**
    - **Ingress Gateway - Istio**
        - **Opis**: Punkt wejścia dla ruchu zewnętrznego do systemu.
        - **Funkcje**:
            - Zapewnienie mTLS dla komunikacji.
            - Polityki autoryzacji dostępu do **Aggregator API**.
            - Monitoring ruchu przychodzącego.
    - **Egress Gateway - Istio**
        - **Opis**: Kontroluje i zabezpiecza ruch wychodzący z klastra.
        - **Funkcje**:
            - Kontrola dostępu do **External APIs** (np. serwisy mapowe, pogodowe).
            - Zapewnienie mTLS dla komunikacji wychodzącej.
            - Monitoring ruchu wychodzącego.
    - **Funkcje Ogólne**:
        - **mTLS**: Szyfrowanie komunikacji między usługami.
        - **Polityki Autoryzacji**: Definiowanie reguł dostępu między usługami.
        - **Monitoring**: Zbieranie metryk i logów ruchu między usługami.

### Szczegółowe Diagramy ASCII

#### 2.1. Komunikacja Między Dronami a Brokerem MQTT

```
    [Drony - Pody]
         |
         | MQTT Publish
         v
    [Broker MQTT (Mosquitto)]
         |
         | MQTT Subscribe
         v
    [Aggregator]
```

**Opis**:
- **Drony** publikują dane telemetryczne na broker MQTT.
- **Broker MQTT** odbiera te dane i przekazuje je do **Aggregatora** poprzez subskrypcję MQTT.

#### 2.2. Przepływ Danych do Aggregator API

```
    [Aggregator]
         |
         | REST API Call
         v
    [Aggregator API]
         |
         | HTTP Response
         v
    [Użytkownik/Zewnętrzna Aplikacja]
```

**Opis**:
- **Aggregator** przekazuje przetworzone dane do **Aggregator API**.
- **Aggregator API** udostępnia te dane poprzez interfejs REST dla użytkowników lub zewnętrznych aplikacji.

#### 2.3. Integracja z Systemem AI (ML)

```
    [Aggregator]
         |
         | API Call / Data Stream
         v
    [System AI - ML]
         |
         | Decisions / Models
         v
    [Drony - Pody]
```

**Opis**:
- **Aggregator** przekazuje dane do **Systemu AI** w celu analizy.
- **System AI** trenuje modele ML i podejmuje decyzje dotyczące sterowania ruchem dronów.
- Decyzje są przekazywane z powrotem do **Dronów** w celu optymalizacji ich tras i działań.

#### 2.4. Kontrola Ruchu Wychodzącego przez Egress Gateway

```
    [System AI - ML]
         |
         | External API Calls
         v
    [Egress Gateway - Istio]
         |
         | External APIs
         v
    [External Services]
```

**Opis**:
- **System AI** może wymagać danych z zewnętrznych API (np. pogodowe, mapowe).
- **Egress Gateway** kontroluje i zabezpiecza te połączenia, zapewniając mTLS i polityki autoryzacji.
- Dane są pobierane z **External Services** i wykorzystywane przez **System AI**.

### Uwagi dotyczące architektury

- **Drony** są komponentami wewnętrznymi systemu, publikującymi dane do **Broker MQTT**, który jest zarządzany wewnątrz klastra Kubernetes.
- **Egress Gateway - Istio** służy do kontrolowania i zabezpieczania ruchu wychodzącego z klastra do zewnętrznych usług, takich jak API pogodowe czy serwisy mapowe, nie jest bezpośrednio związany z kontrolą dronów.
- **Ingress Gateway - Istio** umożliwia zewnętrzny dostęp do **Aggregator API**, zapewniając jednocześnie bezpieczeństwo poprzez **mTLS** i **polityki autoryzacji**.
- **System AI (ML)** integruje się z **Aggregatorem** i **Aggregator API**, umożliwiając zaawansowaną analizę danych i podejmowanie decyzji w czasie rzeczywistym.
- **Istio** zapewnia kompleksowe zarządzanie ruchem między usługami, zabezpieczając komunikację i umożliwiając monitorowanie oraz audyt ruchu.

### Podsumowanie

Architektura systemu **Laboratory Swarm** jest zaprojektowana z myślą o skalowalności, bezpieczeństwie i efektywnej analizie danych. Integracja z **Istio Service Mesh** zapewnia zaawansowane mechanizmy zabezpieczeń i monitorowania, a **System AI (ML)** umożliwia inteligentne zarządzanie ruchem dronów na podstawie analizowanych danych.

---

## 3. Komponenty Systemu

### Drony (IoT) – `drones/`

- **Zadanie**: Symulacja dronów generujących dane telemetryczne.
- **Implementacja**:
  - Każdy dron działa jako osobny pod w Kubernetes.
  - Publikuje dane na topiki MQTT (np. `drones/{id}/position`).
- **Funkcje**:
  - Publikacja pozycji, stanu baterii, prędkości.
  - Skalowanie poprzez zwiększanie liczby replik w Deployment.
- **Bezpieczeństwo**:
  - Uruchamiane jako nie-root użytkownik.
  - Komunikacja z brokerem MQTT zabezpieczona TLS/mTLS.

### Broker MQTT i `mqtt_bridge/`

- **Broker MQTT (Mosquitto)**:
  - **Pliki**:
    - `mosquitto.conf`: Konfiguracja brokera (porty, TLS, ACL).
    - `mosquitto-deployment.yaml`: Deployment Mosquitto w Kubernetes.
    - `mosquitto-service.yaml`: Service eksponujące broker.
  - **Funkcje**:
    - Obsługuje publish-subscribe dla dronów i agregatorów.
    - Zabezpieczony autoryzacją i TLS.

- **`mqtt_bridge.py`**:
  - **Opis**: Klient MQTT w Pythonie, subskrybuje topiki, przetwarza dane i przekazuje je dalej.
  - **Pliki**:
    - `mqtt_bridge.py`: Skrypt klienta.
    - `mqtt_bridge-deployment.yaml`: Deployment skryptu bridge.
    - `Dockerfile`, `requirements.txt`: Budowa obrazu Docker dla bridge.
  - **Funkcje**:
    - Subskrybuje topiki dronów.
    - Przetwarza dane (np. filtruje, loguje, przekazuje do aggregator).
    - Może forwardować dane do innych usług lub systemów AI.

### Agregator – `aggregator/`

- **Zadanie**: Zbieranie i wstępne przetwarzanie danych z dronów.
- **Implementacja**:
  - Subskrybuje dane z `mqtt_bridge.py` lub bezpośrednio z brokera MQTT.
  - Przetwarza dane (np. wykrywa anomalie, filtruje dane).
  - Przekazuje przetworzone dane do **Aggregator API** i **System AI**.
- **Pliki**:
  - `aggregator.py`: Główny skrypt agregatora.
  - `aggregator-deployment.yaml`, `aggregator-service.yaml`: Manifesty Kubernetes.
  - `Dockerfile`, `requirements.txt`: Budowa obrazu Docker.
- **Bezpieczeństwo**:
  - Walidacja danych wejściowych.
  - Ograniczenia dostępu do broker MQTT tylko dla agregatora i bridge.

### Aggregator API – `aggregator-api/`

- **Zadanie**: Udostępnianie danych z agregatora poprzez interfejs REST.
- **Implementacja**:
  - API napisane w Pythonie (Flask) lub Node.js.
  - Obsługuje endpointy do pobierania danych, zarządzania dronami.
- **Pliki**:
  - `aggregator_api.py`: Główny skrypt API.
  - `aggregator-api-deployment.yaml`, `aggregator-api-service.yaml`: Manifesty Kubernetes.
  - `Dockerfile`, `requirements.txt`: Budowa obrazu Docker.
- **Funkcje**:
  - Endpointy REST (`GET /api/drones`, `GET /api/drones/{id}/status`, `POST /api/drones/{id}/update`).
  - Autoryzacja JWT/OAuth2.
  - Rate limiting, logowanie żądań.
- **Bezpieczeństwo**:
  - Autoryzacja i uwierzytelnianie użytkowników.
  - Ograniczenia dostępu przez Istio AuthorizationPolicy.

### System AI (ML) – `system-ai/`

- **Zadanie**: Analiza danych z agregatora, trenowanie modeli ML, podejmowanie decyzji sterujących ruchem dronów.
- **Implementacja**:
  - **Moduły**:
    1. **Model Trener ML**: Trenuje modele na danych historycznych lub w czasie rzeczywistym.
    2. **Analiza Danych**: Subskrybuje dane z agregatora, wykrywa anomalie, optymalizuje ruch dronów.
    3. **Symulacje i Eksperymenty**: Testowanie modeli w środowiskach wirtualnych.
    4. **Interfejs Zarządzania**: GUI lub API do zarządzania modelami i eksperymentami.
- **Pliki**:
  - `main_ai.py`: Główny skrypt AI.
  - `system_ai_deployment.yaml`, `system_ai_service.yaml`: Manifesty Kubernetes.
  - `Dockerfile`, `requirements.txt`: Budowa obrazu Docker.
  - `notebooks/`: Notebooks do eksploracji danych i trenowania modeli.
  - `simulation/`: Skrypty do symulacji i testów.
- **Funkcje**:
  - Trenowanie modeli ML do sterowania ruchem dronów.
  - Wykrywanie anomalii w danych telemetrycznych.
  - Reagowanie na sytuacje awaryjne (np. niska bateria, kolizje).
- **Bezpieczeństwo AI**:
  - Ochrona przed atakami adversarial i data poisoning.
  - Model governance: wersjonowanie, audyt, podpisywanie modeli.
  - Autoryzacja dostępu do modeli i interfejsów zarządzania.

### Warstwa Skryptów i CI/CD – `scripts/`, `server/`

- **`scripts/`**:
  - **ai/**: Skrypty wspierające działanie systemu AI (np. automatyzacja trenowania modeli).
  - **security-tests/**: Narzędzia do testów bezpieczeństwa, fuzzing, chaos engineering.
- **`server/`**:
  - **app.py**: Dodatkowe usługi, np. panel wizualizacji danych.
  - **visualization.py**: Skrypty do wizualizacji danych w czasie rzeczywistym.
- **Funkcje**:
  - Automatyzacja procesów budowania, testowania i wdrażania.
  - Narzędzia do monitorowania i zarządzania systemem.

---

## 4. Funkcje i Scenariusze Użycia

### 1. Symulacja Rojów IoT

- **Uruchamianie Dronów**: 
  - Skalowanie liczby dronów poprzez Deployment w Kubernetes.
  - Każdy dron publikuje dane telemetryczne na dedykowane topiki MQTT.
  
- **Testy Skalowalności**:
  - Zwiększanie liczby replik dronów do setek.
  - Monitorowanie wydajności brokera MQTT i agregatora.

### 2. Monitorowanie i Analiza

- **Zbieranie Danych**:
  - Agregator zbiera dane z dronów, przetwarza je i udostępnia przez Aggregator API.
  
- **Wizualizacja**:
  - Dane wizualizowane w Grafanie, monitorowane przez Prometheus.
  
- **Analiza Predykcyjna**:
  - System AI analizuje dane, trenuje modele do optymalizacji ruchu dronów i wykrywania anomalii.

### 3. Bezpieczeństwo i DevSecOps

- **Testowanie Bezpieczeństwa**:
  - Fuzzing aggregator-api, brute force ataki na broker MQTT.
  - Chaos engineering: symulacja awarii, zabijanie podów.
  
- **Pipeline CI/CD**:
  - Automatyczne budowanie i skanowanie obrazów Docker (Trivy, Clair).
  - Automatyczne wdrażanie do Kubernetes za pomocą ArgoCD/GitLab CI.

### 4. Sterowanie i AI

- **Optymalizacja Ruchu**:
  - System AI podejmuje decyzje dotyczące tras dronów na podstawie analizy danych.
  
- **Reagowanie na Anomalie**:
  - Wykrywanie niskiego poziomu baterii, kolizji, nieprawidłowych danych telemetrycznych.

### 5. Strategie Wdrożeń

- **Blue-Green Deployment**:
  - Równoległe środowiska do testowania nowych wersji bez przestojów.
  
- **Canary Deployment**:
  - Stopniowe wdrażanie nowych wersji do niewielkiej części ruchu, monitorowanie stabilności.

---

## 5. Kluczowe Założenia Technologiczne

1. **Kubernetes**:
   - Orkiestracja wszystkich komponentów: drony, aggregator, broker MQTT, aggregator-api, system AI.
   - Skalowalność, wysoką dostępność, automatyzację wdrożeń.

2. **Istio**:
   - Service Mesh zapewniający **mTLS**, **polityki autoryzacji**, **Ingress/Egress Gateway**, **monitoring** ruchu.
   - Kontrola i zabezpieczenie komunikacji pomiędzy usługami.

3. **MQTT (Mosquitto)**:
   - Model komunikacji publish-subscribe.
   - Scentralizowany broker do zarządzania danymi z dronów.

4. **DevSecOps**:
   - Pipeline CI/CD integrujący budowanie, testowanie, skanowanie i wdrażanie.
   - Automatyzacja zabezpieczeń na każdym etapie.

5. **Machine Learning (AI)**:
   - System AI do analizy danych, trenowania modeli i podejmowania decyzji.
   - Integracja ML z resztą systemu poprzez Aggregator i Aggregator API.

---

## 6. Integracja z Kubernetes i Istio

### Wdrożenie Kubernetes

- **Przygotowanie Klastra**:
  - Uruchomienie klastrów lokalnych (minikube/kind/k3s) lub korzystanie z publicznych usług (EKS, GKE, AKS).

### Instalacja Istio

```bash
# Instalacja Istio z profilem demo
istioctl install --set profile=demo -y

# Włączenie automatycznego wstrzykiwania sidecarów w namespace
kubectl label namespace default istio-injection=enabled
```

### Wdrożenie Komponentów

1. **Broker MQTT (Mosquitto)**

```bash
kubectl apply -f mqtt_bridge/mosquitto-deployment.yaml
kubectl apply -f mqtt_bridge/mosquitto-service.yaml
```

2. **mqtt_bridge**

```bash
kubectl apply -f mqtt_bridge/mqtt_bridge-deployment.yaml
```

3. **Agregator**

```bash
kubectl apply -f aggregator/aggregator-deployment.yaml
kubectl apply -f aggregator/aggregator-service.yaml
```

4. **Aggregator API**

```bash
kubectl apply -f aggregator-api/aggregator-api-deployment.yaml
kubectl apply -f aggregator-api/aggregator-api-service.yaml
```

5. **Drony**

```bash
kubectl apply -f drones/drone-deployment.yaml
kubectl apply -f drones/drone-service.yaml
```

6. **System AI**

```bash
kubectl apply -f system-ai/system_ai_deployment.yaml
kubectl apply -f system-ai/system_ai_service.yaml
```

### Konfiguracja Istio dla Bezpieczeństwa

- **mTLS**: Wszystkie usługi komunikują się przez mTLS, zapewniając szyfrowanie i wzajemną autoryzację.
- **Authorization Policies**: Definiowanie reguł dostępu między usługami.
- **Ingress/Egress Gateways**: Kontrola ruchu przychodzącego i wychodzącego.

---

## 7. Bezpieczeństwo, CI/CD, Testy i Monitoring

### Bezpieczeństwo

1. **MQTT Security**:
   - **TLS/SSL**: Szyfrowanie komunikacji między dronami a brokerem MQTT.
   - **Autoryzacja**: Plik haseł i ACL w `mosquitto.conf` ograniczający dostęp.
   - **Rate Limiting**: Ograniczenie liczby połączeń i wiadomości na topik.

2. **Kontenery i Pod Security**:
   - **Minimalne obrazy**: Używanie lekkich obrazów bazowych (np. `python:3.11-slim`).
   - **Non-root Users**: Uruchamianie kontenerów jako użytkownik nie-root.
   - **Read-Only Filesystem**: Zamontowane filesystemy jako tylko do odczytu.
   - **Pod Security Policies**: Definiowanie restrykcyjnych polityk dla podów.

3. **Hardening Obrazów i Infrastructure as Code (IaC)**:
   - **Redukcja Warstw w Dockerfile**: Minimalizacja liczby warstw w obrazach Docker.
   - **Skanowanie Podatności**: Automatyczne skanowanie obrazów (Trivy, Clair, Anchore).
   - **Polityki IaC**: Używanie OPA Gatekeeper do wymuszania reguł bezpieczeństwa na manifestach Kubernetes.

4. **Zaawansowane Mechanizmy DevSecOps**:
   - **SAST/DAST**: Analiza statyczna kodu (Bandit, SonarQube) i dynamiczna (OWASP ZAP).
   - **Secret Management**: Przechowywanie tajemnic w HashiCorp Vault lub Kubernetes Secrets z rotacją.
   - **Policy as Code**: Definiowanie i egzekwowanie polityk bezpieczeństwa za pomocą OPA/Rego.

### CI/CD

1. **Pipeline Budowania i Wdrażania**:
   - **Automatyczne Budowanie**: Budowanie obrazów Docker po commitach.
   - **Testowanie**: Wykonywanie testów jednostkowych, integracyjnych, SAST i DAST.
   - **Skanowanie Obrazów**: Integracja z narzędziami do skanowania podatności.
   - **Wdrożenie**: Automatyczne wdrażanie do Kubernetes za pomocą ArgoCD/GitLab CI.

2. **GitOps**:
   - **ArgoCD/Flux**: Synchronizacja stanu repozytorium Git z klastrem Kubernetes.
   - **Automatyzacja**: Każda zmiana w repozytorium YAML jest automatycznie wdrażana.

### Testy

1. **Testy Penetracyjne (Pentesty)**:
   - Ataki na broker MQTT (brute force haseł, MITM).
   - Ataki na Aggregator API (SQL Injection, XSS).

2. **Fuzzing**:
   - Generowanie losowych danych wejściowych do Aggregator API i topików MQTT.
   - Wykrywanie crashów i błędów.

3. **Chaos Engineering**:
   - Symulacja awarii podów (aggregator, broker, drony).
   - Testowanie odporności na błędy sieciowe.

### Monitoring

1. **Prometheus + Grafana**:
   - Zbieranie metryk z usług, brokerów, systemu AI.
   - Tworzenie dashboardów wizualizujących kluczowe wskaźniki.

2. **Kiali**:
   - Wizualizacja topologii usług w Istio.
   - Monitorowanie stanu mTLS, polityk autoryzacji.

3. **ELK Stack (Elasticsearch, Logstash, Kibana)**:
   - Centralizacja logów z wszystkich komponentów.
   - Analiza i wykrywanie anomalii w logach.

4. **Distributed Tracing (Jaeger/Zipkin)**:
   - Śledzenie przepływu żądań pomiędzy usługami.
   - Analiza opóźnień i wąskich gardeł.

---

## 8. Instrukcje Uruchomienia

### Krok 1: Przygotowanie Klastra Kubernetes

- **Lokalny Klastr**: Użyj narzędzi takich jak **minikube**, **kind**, lub **k3s**.
- **Publiczny Klastr**: Skorzystaj z usług takich jak **EKS**, **GKE**, **AKS**.

### Krok 2: Instalacja Istio

```bash
# Instalacja Istio z profilem demo
istioctl install --set profile=demo -y

# Włączenie automatycznego wstrzykiwania sidecarów w namespace
kubectl label namespace default istio-injection=enabled
```

### Krok 3: Budowanie Obrazów Docker

Zbuduj obrazy Docker dla wszystkich komponentów:

```bash
# Broker MQTT (Mosquitto) - oficjalny obraz, nie wymaga budowania

# mqtt_bridge
cd mqtt_bridge/
docker build -t myrepo/mqtt-bridge:latest .
docker push myrepo/mqtt-bridge:latest

# Agregator
cd ../aggregator/
docker build -t myrepo/aggregator:latest .
docker push myrepo/aggregator:latest

# Aggregator API
cd ../aggregator-api/
docker build -t myrepo/aggregator-api:latest .
docker push myrepo/aggregator-api:latest

# Drony
cd ../drones/
docker build -t myrepo/drones:latest .
docker push myrepo/drones:latest

# System AI
cd ../system-ai/
docker build -t myrepo/system-ai:latest .
docker push myrepo/system-ai:latest
```

### Krok 4: Wdrożenie Komponentów do Kubernetes

Wdróż wszystkie komponenty w odpowiedniej kolejności:

```bash
# Broker MQTT (Mosquitto)
kubectl apply -f mqtt_bridge/mosquitto-deployment.yaml
kubectl apply -f mqtt_bridge/mosquitto-service.yaml

# mqtt_bridge
kubectl apply -f mqtt_bridge/mqtt_bridge-deployment.yaml

# Agregator
kubectl apply -f aggregator/aggregator-deployment.yaml
kubectl apply -f aggregator/aggregator-service.yaml

# Aggregator API
kubectl apply -f aggregator-api/aggregator-api-deployment.yaml
kubectl apply -f aggregator-api/aggregator-api-service.yaml

# Drony
kubectl apply -f drones/drone-deployment.yaml
kubectl apply -f drones/drone-service.yaml

# System AI
kubectl apply -f system-ai/system_ai_deployment.yaml
kubectl apply -f system-ai/system_ai_service.yaml
```

### Krok 5: Weryfikacja Wdrożenia

- **Sprawdzenie Statusu Podów**:

  ```bash
  kubectl get pods
  ```

- **Przeglądanie Logów**:

  ```bash
  kubectl logs <aggregator-pod-name>
  kubectl logs <mqtt-bridge-pod-name>
  ```

- **Dostęp do Aggregator API**:
  - Użyj Ingress Gateway Istio do wystawienia API na zewnątrz.
  - Przykładowe polecenie port-forward:

    ```bash
    kubectl port-forward svc/aggregator-api 8080:80
    ```

  - Testowanie endpointów:

    ```bash
    curl http://localhost:8080/api/drones
    ```

---

## 9. Dalsza Dokumentacja

W folderze **`_docs/`** znajdziesz szczegółowe opisy poszczególnych komponentów oraz ich konfiguracji:

- **`aggregator_details.md`**: Szczegółowy opis agregatora, jego funkcji i integracji.
- **`aggregator_api_details.md`**: Opis endpointów REST API, przykłady zapytań i odpowiedzi.
- **`broker_mqtt.md`**: Szczegółowa konfiguracja brokera MQTT, zabezpieczenia, ACL.
- **`drones_component.md`**: Logika działania dronów, skalowanie, bezpieczeństwo.
- **`system_ai_details.md`**: Opis warstwy AI, trenowanie modeli, analiza danych.
- **`security_tests_details.md`**: Opisy przeprowadzanych testów bezpieczeństwa, fuzzing, chaos engineering.
- **`strategia_blue_green_canary.md`**: Strategie wdrożeń bez przestojów, konfiguracja Istio dla blue-green i canary deployments.

---

## 10. Wsparcie i Rozwój

- **Autorzy**: Zespół `d2j3`, `CloudOps`, `IoT-SecDev` oraz inni kontrybutorzy.
- **Wsparcie**:
  - **Issues**: Zgłaszaj problemy w repozytorium.
  - **Pull Requests**: Zachęcamy do wprowadzania poprawek i nowych funkcjonalności.
  - **Kontakt**: Kontaktuj się przez kanały komunikacji zespołu (Slack, email).

- **Perspektywy Rozwojowe**:
  - **Integracja z Kubeflow/MLFlow**: Automatyzacja trenowania modeli ML.
  - **Rozszerzenie funkcji dronów**: Dodanie symulacji sensorów Lidar, danych wideo.
  - **Zero Trust Security**: Implementacja OPA Gatekeeper, Pod Security Admission.
  - **SIEM (Wazuh, Splunk)**: Analiza zdarzeń bezpieczeństwa w czasie rzeczywistym.
  - **Edge Computing**: Rozproszona infrastruktura z użyciem K3s.

---

**Dziękujemy za zainteresowanie projektem Laboratory Swarm!**  
Zapraszamy do eksploracji, testowania i rozwoju systemu. Szczegółowe instrukcje i przykłady znajdują się w kolejnych dokumentach w katalogu **`_docs/`** oraz w plikach źródłowych poszczególnych komponentów.

\#IoT \#Kubernetes \#Istio \#ML \#DevSecOps \#ChaosEngineering \#MQTT

---

**Nota dla Użytkownika**:  
Dokumentacja jest żywym dokumentem i będzie aktualizowana wraz z rozwojem projektu. Zachęcamy do regularnego przeglądania najnowszych zmian i dodawania własnych uwag poprzez **Issues** lub **Pull Requests** w repozytorium.

---

## Dodatkowe Wyjaśnienia

### Poprawki Architektury

- **Egress Gateway - Istio** nie jest bezpośrednio związany ze sterowaniem dronów. Jego głównym celem jest kontrolowanie i zabezpieczanie ruchu wychodzącego z klastra do zewnętrznych API, takich jak serwisy mapowe czy pogodowe.
- **Drony** są komponentami wewnętrznymi systemu, publikującymi dane do **Broker MQTT**. Wszystkie operacje związane z dronami odbywają się wewnątrz klastra Kubernetes, bez potrzeby bezpośredniego dostępu przez **Egress Gateway**.

### Bezpieczeństwo Komunikacji

- **Ingress Gateway - Istio** umożliwia bezpieczny dostęp do **Aggregator API** z zewnątrz, zapewniając szyfrowanie i autoryzację.
- **mTLS** między usługami wewnątrz klastra zapewnia poufność i integralność danych oraz wzajemne uwierzytelnianie usług.

### Machine Learning (AI)

- **System AI (ML)** analizuje dane telemetryczne z dronów, trenuje modele do optymalizacji ruchu i wykrywania anomalii.
- **Model Trener ML** może korzystać z danych historycznych lub danych w czasie rzeczywistym, umożliwiając adaptacyjne zarządzanie rojem dronów.
- **Symulacje i Eksperymenty** pozwalają na testowanie modeli w kontrolowanym środowisku przed ich wdrożeniem.

### DevSecOps

- **Pipeline CI/CD** integruje budowanie, testowanie, skanowanie i wdrażanie komponentów, zapewniając automatyzację i bezpieczeństwo na każdym etapie.
- **GitOps** z narzędziami takimi jak **ArgoCD** czy **Flux** umożliwia synchronizację stanu klastra z repozytorium Git, co ułatwia zarządzanie i audyt zmian.
