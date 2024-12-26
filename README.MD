Poniżej znajduje się **obszerna, scalona dokumentacja** opisująca w jednym miejscu wszystkie kluczowe elementy **Laboratorium Bezpieczeństwa Chmurowego** z symulacją roju dronów, mechanizmami MQTT, Service Mesh (Istio), Kubernetes, warstwą AI i kompletnym podejściem DevSecOps. Dokumentacja ta scala dotychczasowe wątki, **odsyła** w odpowiednich miejscach do szczegółowych plików w `_docs/`, oraz przedstawia **spójną koncepcję** architektury i sposobu wdrożenia w środowisku chmurowym – z perspektywą bezpieczeństwa, niezawodności i elastycznej rozbudowy.

---

# Laboratorium Bezpieczeństwa Chmurowego: Symulacja Rojów Dronów z AI, Kubernetes i Istio

## Spis Treści

1. [Kontekst i Cel Projektu](#1-kontekst-i-cel-projektu)  
2. [Struktura Projektu i Kluczowe Foldery](#2-struktura-projektu-i-kluczowe-foldery)  
3. [Opis Architektury i Przepływu Danych](#3-opis-architektury-i-przepływu-danych)  
4. [Omówienie Głównych Komponentów](#4-omówienie-głównych-komponentów)  
   - [Drony (IoT) – `drones/`](#drony-iot--drones)  
   - [Broker MQTT i `mqtt-aggregator/`](#broker-mqtt-i-mqtt-aggregator)  
   - [Agregator – `aggregator/`](#agregator--aggregator)  
   - [Aggregator API – `aggregator-api/`](#aggregator-api--aggregator-api)  
   - [System AI (ML) – `system-ai/`](#system-ai-ml--system-ai)  
   - [Skrypty, Serwer, i Rozszerzenia (StatefulSet, Scripts)](#skrypty-serwer-i-rozszerzenia-statefulset-scripts)  
5. [Bezpieczeństwo w Kubernetes i Istio](#5-bezpieczeństwo-w-kubernetes-i-istio)  
   - [mTLS i Autoryzacja (AuthorizationPolicy)](#mtls-i-autoryzacja-authorizationpolicy)  
   - [Rate Limiting (Envoy)](#rate-limiting-envoy)  
   - [Ingress i Egress Gateway – Kontrola Ruchu](#ingress-i-egress-gateway--kontrola-ruchu)  
6. [Mechanizmy DevSecOps, CI/CD i Testy Bezpieczeństwa](#6-mechanizmy-devsecops-cicd-i-testy-bezpieczeństwa)  
   - [Zarządzanie Obrazami, Pod Security, Hardening](#zarządzanie-obrazami-pod-security-hardening)  
   - [Skany Podatności, Fuzzing, Chaos Engineering](#skany-podatności-fuzzing-chaos-engineering)  
   - [Dokumenty w `_docs/` i Wsparcie Dokumentacyjne](#dokumenty-w-_docs-i-wsparcie-dokumentacyjne)  
7. [Bezpieczeństwo Algorytmów AI i Ataki na Modele](#7-bezpieczeństwo-algorytmów-ai-i-ataki-na-modele)  
8. [Przykładowe Scenariusze Eksperymentalne](#8-przykładowe-scenariusze-eksperymentalne)  
   - [Testy Penetracyjne i Symulacje Awarii](#testy-penetracyjne-i-symulacje-awarii)  
   - [Ćwiczenia Związane z AI Security](#ćwiczenia-związane-z-ai-security)  
9. [Strategie Wdrożeń: Blue-Green i Canary](#9-strategie-wdrożeń-blue-green-i-canary)  
10. [Podsumowanie i Kierunki Rozwoju](#10-podsumowanie-i-kierunki-rozwoju)

---

## 1. Kontekst i Cel Projektu

**Projekt** ma na celu stworzenie **laboratorium bezpieczeństwa chmurowego** (Cloud Security Lab) służącego do:

- **Symulacji Rojów Dronów** (IoT) z wykorzystaniem protokołu MQTT.  
- **Analizy i sterowania** rojem za pomocą agregatorów danych oraz warstwy **AI** (Machine Learning).  
- **Zapewnienia bezpieczeństwa** i kontroli w warstwie sieci (Istio, mTLS, polityki, rate limiting).  
- **Testowania** rozwiązań DevSecOps (skany podatności, automatyczne wdrażanie, testy chaos engineering).  
- **Edukacji** w zakresie **Kubernetes, Service Mesh (Istio)**, i bezpieczeństwa algorytmów ML (adversarial attacks, data poisoning).

Dzięki tej architekturze można w **kontrolowanym środowisku** badać ataki, implementować mechanizmy obronne i realizować **eksperymenty** w środowisku Cloud Native i IoT.

---

## 2. Struktura Projektu i Kluczowe Foldery

Przykładowa struktura (rozszerzona; zawiera nowo utworzone foldery `system-ai/` i `security-tests/`):

```
C:.
│   .gitignore
│   README.MD
│
├───_docs
│       aggregator_api_details.md
│       aggregator_details.md
│       broker_mqtt.md
│       drones_component.md
│       idea-i-koncepcja.md
│       Kubernetes_Istio_Secure_API_Communication_Manual.md
│       readme.md
│       strategia_blue_green_canary.md
│       system_ai_details.md
│       security_tests_details.md
│       ai_security_considerations.md
│
├───aggregator
│       aggregator-deployment.yaml
│       aggregator-service.yaml
│       aggregator.py
│       Dockerfile
│       requirements.txt
│
├───aggregator-api
│       aggregator-api-deployment.yaml
│       aggregator-api-service.yaml
│       aggregator_api.py
│       Dockerfile
│       requirements.txt
│
├───drones
│       Dockerfile
│       drone-deployment.yaml
│       drone-service.yaml
│       drone_logic.py
│       requirements.txt
│
├───mqtt-aggregator
│       Dockerfile
│       mosquitto-deployment.yaml
│       mosquitto-service.yaml
│       mosquitto.conf
│       mqtt_aggregator-deployment.yaml
│       mqtt_aggregator.py
│       requirements.txt
│
├───scripts
│   └───ai
│           DOC_GENERATED.md
│           generate_openai_docs.py
│           generate_openai_script_names.py
│           list_openai_models.py
│           test_openai.py
│
├───security-tests
│       chaos_tests/
│       pentest_mqtt.sh
│       fuzz_aggregator_api.py
│       scan_containers.sh
│       README.md
│
├───server
│       app.py
│       requirements.txt
│       visualization.py
│
├───statefulset
│       drone-service.yaml
│       drone-statefulset.yaml
│
└───system-ai
        Dockerfile
        main_ai.py
        requirements.txt
        system_ai_deployment.yaml
        system_ai_service.yaml
        notebooks/
        simulation/
```

### Krótki opis:

- **`_docs/`**: Zawiera pliki dokumentacji (szczegółowy opis aggregator, aggregator-api, broker MQTT, koncepcje, strategie wdrożeń, itp.).  
- **`aggregator/`** i **`aggregator-api/`**: Kod i definicje wdrożenia do agregowania danych i ich udostępniania.  
- **`drones/`**: Konteneryzacja „dronów” symulujących urządzenia IoT.  
- **`mqtt-aggregator/`**: Broker MQTT (Mosquitto) + skrypt `mqtt_aggregator.py` do wstępnego przetwarzania wiadomości.  
- **`system-ai/`**: Nowy folder z modułem AI (trenowanie, analiza anomalii, symulacje).  
- **`security-tests/`**: Skrypty do testów bezpieczeństwa (fuzzing aggregator-api, pentesty MQTT, chaos engineering).  
- **`server/`**: Aplikacje pomocnicze (np. panel wizualizacji).  
- **`statefulset/`**: Przykładowe manifesty do wdrożenia dronów jako StatefulSet.  

---

## 3. Opis Architektury i Przepływu Danych

Poniższy diagram przedstawia przepływ danych i relacje między usługami:

```
                       [Internet]
                            |
                [Ingress Gateway - Istio]  <--->  [Polityki Bezpieczeństwa]
                            |
                            v
                 +------------------------------+
                 |       [Aggregator API]       |
                 | (REST: /api/drones, /update) |
                 +------------------------------+
                            |
                            v
   [Aggregator] <----- subskrypcja ----- [Broker MQTT] <---- [Drony - Pody]
      |                                       (Mosquitto)
      |---> ewent. zapis w bazie
      |
      +-------> [System AI] (analiza online lub offline)
                |  - main_ai.py
                |  - subskrypcja MQTT lub pobieranie z aggregator
                |
                +---- [Symulacje, Trenowanie Modeli]

        (Dodatkowo Ingress/Egress Gateway - kontrola ruchu z/do świata zewn.)
```

1. **Drony** (pody) publikują dane do brokera MQTT (Mosquitto).  
2. **Aggregator** subskrybuje topiki i przetwarza dane, udostępniane dalej przez **Aggregator API**.  
3. **System AI** może subskrybować dane z MQTT lub pobierać przez Aggregator API.  
4. **Istio** zapewnia kontrolę ruchu, mTLS, polityki autoryzacji, rate limiting.  
5. **security-tests** folder umożliwia testy bezpieczeństwa i jakości wdrożenia.

Szczegółowe opisy znajdują się w `_docs/aggregator_details.md` (dla aggregator) oraz `_docs/aggregator_api_details.md` (dla aggregator-api) i `_docs/broker_mqtt.md` (dla brokera).

---

## 4. Omówienie Głównych Komponentów

### Drony (IoT) – `drones/`

- **`drone_logic.py`** publikuje dane:  
  - Temat: `drones/{drone_id}/position`.  
  - Format JSON, np. `{"x":10,"y":20,"battery":95}`.  
- **`drone-deployment.yaml`** i **`drone-service.yaml`** definiują sposób uruchomienia w K8s.  
- Skalowalne do setek replik (symulacja dużego roju).

Dokładniejszy opis w `_docs/drones_component.md`.

### Broker MQTT i `mqtt-aggregator/`

- **Broker MQTT** – Pliki: `mosquitto-deployment.yaml`, `mosquitto-service.yaml`, `mosquitto.conf`.  
  - Realizuje publish/subscribe.  
  - Patrz `_docs/broker_mqtt.md` dla szczegółów.  
- **`mqtt_aggregator.py`** – Skrypt Pythona, może nasłuchiwać topików (`drones/+/position`), a następnie przekazywać je do aggregator (HTTP) lub logować do pliku/bazy.

### Agregator – `aggregator/`

- **`aggregator.py`**: Subskrybuje MQTT (lub przyjmuje dane z `mqtt_aggregator.py`), obrabia je (filtr, walidacja), ewentualnie przechowuje w pamięci lub bazie.  
- **`aggregator-deployment.yaml`** – Definiuje wdrożenie w K8s (replikacja, environment).  
- **`aggregator-service.yaml`** – Udostępnianie w ramach cluster IP.  
- Dokumentacja: `_docs/aggregator_details.md`.

### Aggregator API – `aggregator-api/`

- **`aggregator_api.py`**: Endpointy REST (np. `GET /api/drones`, `GET /api/drones/{id}/status`, `POST /api/drones/{id}/update`).  
- **`aggregator-api-deployment.yaml`** i **`aggregator-api-service.yaml`** – manifesty K8s.  
- Z reguły zabezpieczone przez Ingress Gateway + mTLS i autoryzację w Istio.  
- Dokumentacja: `_docs/aggregator_api_details.md`.

### System AI (ML) – `system-ai/`

- **Nowy folder**, zawiera:
  - **`main_ai.py`**: Główny skrypt – subskrypcja MQTT i/lub pobieranie batch danych z aggregator.  
  - **`system_ai_deployment.yaml`, `system_ai_service.yaml`**: Wdrożenie do K8s (np. Flask lub FastAPI na porcie 8080).  
  - **`notebooks/`, `simulation/`**: Materiały do symulacji offline, trenowania modeli ML.  
  - Dokumentacja: `_docs/system_ai_details.md`.

### Skrypty, Serwer, i Rozszerzenia (StatefulSet, Scripts)

- **`scripts/ai/*`**: Zawiera narzędzia do generowania dokumentacji, testów OpenAI, itp.  
- **`server/`**: Może pełnić rolę panelu wizualizacji (`app.py`, `visualization.py`).  
- **`statefulset/`**: Eksperymentalne wdrożenie dronów w formie StatefulSet, jeśli potrzebują utrzymywać stabilny ID.

---

## 5. Bezpieczeństwo w Kubernetes i Istio

### mTLS i Autoryzacja (AuthorizationPolicy)

- **mTLS**:  
  - Istio Citadel wydaje certyfikaty sidecar Envoy.  
  - Ruch między aggregator, aggregator-api, system-ai i broker MQTT jest szyfrowany i uwierzytelniany.  
- **AuthorizationPolicy**:  
  - Definiuje, kto może komunikować się z kim: np. drony mogą jedynie publish do broker, aggregator subskrybuje, aggregator-api zezwala tylko aggregatorowi i system-ai na `/update`.  
  - Przykładowe reguły opisane w `_docs/Kubernetes_Istio_Secure_API_Communication_Manual.md`.

### Rate Limiting (Envoy)

- **EnvoyFilter** lub globalny limit w Istio: Ogranicza ilość żądań w czasie (np. 50 RPS do aggregator-api).  
- Chroni przed atakami DDoS i przed przeciążeniem usług.

### Ingress i Egress Gateway – Kontrola Ruchu

- **Ingress Gateway**:  
  - Publikuje `aggregator-api` (np. `aggregator.example.com`) i ewentualnie `system-ai`.  
  - Możemy włączyć SSL/TLS i wymagać JWT.  
  - Możliwe wstawienie WAF (np. ModSecurity w Envoy).  
- **Egress Gateway**:  
  - Kontroluje wyjścia do zewnętrznych usług (API pogodowe, mapowe, zewnętrzne platformy AI).  
  - Definiujemy *ServiceEntry*, *VirtualService* aby odblokować określone domeny, resztę blokować.

Więcej przykładów w `_docs/Kubernetes_Istio_Secure_API_Communication_Manual.md`.

---

## 6. Mechanizmy DevSecOps, CI/CD i Testy Bezpieczeństwa

### Zarządzanie Obrazami, Pod Security, Hardening

- **Dockerfile** w każdym folderze – budujemy minimalne obrazy (np. `FROM python:3.9-slim`).  
- **Skanowanie** (Trivy, Clair) w pipeline CI/CD.  
- **Pod Security**: Włączony tryb `restricted`, kontenery działają jako non-root.  
- **Secrets Management**: K8s Secrets lub HashiCorp Vault do przechowywania haseł i kluczy.

### Skany Podatności, Fuzzing, Chaos Engineering

- **`security-tests/`** zawiera:
  - `pentest_mqtt.sh` – test ataków na broker MQTT (brute force, port scanning).  
  - `fuzz_aggregator_api.py` – fuzzing endpointów aggregator-api.  
  - `chaos_tests/` – definicje scenariuszy Litmus/Chaos Mesh (np. ubijanie aggregator pody).  
  - `scan_containers.sh` – przykładowy skrypt integrujący się z narzędziem do skanowania obrazów.  
- Dokumentacja w `_docs/security_tests_details.md`.

### Dokumenty w `_docs/` i Wsparcie Dokumentacyjne

W `_docs/` znajdują się m.in.:

- **`aggregator_details.md`** – opis mechanizmów agregacji i subskrypcji MQTT.  
- **`broker_mqtt.md`** – konfiguracja Mosquitto, topiców, best practices w bezpieczeństwie MQTT.  
- **`readme.md`, `idea-i-koncepcja.md`** – ogólna wizja projektu.  
- **`strategia_blue_green_canary.md`** – opis strategii wdrożeń.  
- **`Kubernetes_Istio_Secure_API_Communication_Manual.md`** – zasady integracji z Istio, mTLS, polityki autoryzacji.  
- **`system_ai_details.md`** (NOWY) – szczegółowy opis modułu AI, subskrypcji, endpointów.  
- **`security_tests_details.md`** (NOWY) – opis scenariuszy testów bezpieczeństwa i chaos engineering.

---

## 7. Bezpieczeństwo Algorytmów AI i Ataki na Modele

1. **Ataki Adversarial**:  
   - Dodawanie niewielkich „szumów” w danych sensorycznych, by zmylić model sterowania.  
2. **Data Poisoning**:  
   - Złośliwe drony publikują fałszywe dane, psując zbiór treningowy.  
3. **Mechanizmy Obronne**:  
   - Filtry anomalii w aggregator (walidacja), kwarantanna w system AI (np. potwierdzanie danych z wielu źródeł).  
   - Podpisy cyfrowe modeli, by nie można było wstrzykiwać złośliwych wag.  
   - Szczegóły w `_docs/ai_security_considerations.md`.

---

## 8. Przykładowe Scenariusze Eksperymentalne

### Testy Penetracyjne i Symulacje Awarii

1. **Pentest aggregator-api**: Uruchamiamy `fuzz_aggregator_api.py` i obserwujemy logi w Kibana/Grafana.  
2. **Chaos engineering**: W `security-tests/chaos_tests` mamy definicje do wstrzykiwania awarii w aggregator, broker MQTT.  
3. **Brak TLS**: Porównanie podsłuchiwania Wireshark, gdy mTLS jest wyłączone vs włączone.

### Ćwiczenia Związane z AI Security

- **Atak data poisoning**: Niektóre drony generują dziwne wartości baterii. Sprawdzamy, czy System AI potrafi je wykryć.  
- **Adversarial**: Symulujemy błędne sensory w parametrach środowiskowych.  
- **Ochrona**: W `system_ai/main_ai.py` dodajemy moduł weryfikacji integralności i statystyczne filtry.

---

## 9. Strategie Wdrożeń: Blue-Green i Canary

W `_docs/strategia_blue_green_canary.md` opisano, jak wdrażać nowe wersje aggregator czy system AI:

- **Blue-Green**:  
  - Dwóch równoległych środowisk – „Blue” (obecny) i „Green” (nowy). Przełączenie ruchu jest natychmiastowe w Ingress Gateway.  
- **Canary**:  
  - Stopniowe przekierowanie ruchu (np. 10% do nowej wersji), monitorowanie stabilności, następnie 50%, 100%.

Pozwala to testować nowe modele AI czy nową wersję aggregator-api bez ryzyka całkowitego przestoju.

---

## 10. Podsumowanie i Kierunki Rozwoju

Dzięki opisanej **scalonej koncepcji** i strukturze katalogów, projekt stanowi **wielowarstwowe laboratorium** do nauki i testów:

1. **Symulacja IoT** (roje dronów, broker MQTT).  
2. **Cloud Native** (Kubernetes, mikroserwisy, kontenery).  
3. **Service Mesh (Istio)** – mTLS, autoryzacja, rate limiting, gateway.  
4. **Warstwa AI** – trenowanie modeli, analiza anomalii, symulacje.  
5. **Bezpieczeństwo** – testy penetracyjne, fuzzing, chaos engineering, DevSecOps, bezpieczeństwo AI.  
6. **Strategie wdrożeń** (blue-green, canary) – ciągły rozwój bez przestojów.

**Kierunki dalszego rozwoju**:

- **Integracja z Helm Chart** – uproszczenie wdrożenia.  
- **Rozszerzone testy AI** – np. Kubeflow, MLFlow do zarządzania cyklem życia modeli.  
- **Edge Computing** – migracja dronów do klastrów brzegowych.  
- **Pełne Zero Trust** – wprowadzenie OPA/Gatekeeper i rozbudowanych polityk.  
- **SIEM** – integracja z narzędziami do Security Information & Event Management (np. Splunk, Wazuh).

W efekcie laboratorium pozwala **utrzymać stabilną, dobrze zabezpieczoną koncepcję chmurową** w świecie ciągłych zmian i zagrożeń – umożliwia praktyczne ćwiczenia, rozwijanie umiejętności DevSecOps oraz testowanie algorytmów sztucznej inteligencji w środowisku przypominającym realne wyzwania przedsiębiorstw i aplikacji IoT.