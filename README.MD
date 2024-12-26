# Laboratorium Bezpieczeństwa Chmurowego: Symulacja Rojów Dronów z AI i Zabezpieczeniami Istio

## Spis Treści

1. [Cele, Kontekst i Zakres Projektu](#1-cele-kontekst-i-zakres-projektu)  
2. [Architektura – Przegląd i Diagram](#2-architektura--przegląd-i-diagram)  
3. [Opis Szczegółowy Komponentów](#3-opis-szczegółowy-komponentów)  
   - [Drony (IoT) – `drones/`](#drony-iot--drones)  
   - [Broker MQTT i `mqtt-aggregator/`](#broker-mqtt-i-mqtt-aggregator)  
   - [Agregator – `aggregator/`](#agregator--aggregator)  
   - [Aggregator API – `aggregator-api/`](#aggregator-api--aggregator-api)  
   - [System AI (ML)](#system-ai-ml)  
   - [Warstwa Skryptów i CI/CD – `scripts/`, `server/`](#warstwa-skryptów-i-cicd--scripts-server)  
4. [Bezpieczeństwo w Kubernetes i Istio](#4-bezpieczeństwo-w-kubernetes-i-istio)  
   - [Warstwa Sieciowa: mTLS, Autoryzacja, Rate Limiting](#warstwa-sieciowa-mtls-autoryzacja-rate-limiting)
   - [Ingress i Egress Gateway – Kontrola Ruchu](#ingress-i-egress-gateway--kontrola-ruchu)
   - [Zarządzanie Politykami (RBAC, NetworkPolicy, AuthorizationPolicy)](#zarządzanie-politykami-rbac-networkpolicy-authorizationpolicy)  
   - [Mechanizmy Monitoringu (Prometheus, Grafana, Kiali, ELK)](#mechanizmy-monitoringu-prometheus-grafana-kiali-elk)  
5. [Zabezpieczenia Chmurowe i IoT w Projekcie](#5-zabezpieczenia-chmurowe-i-iot-w-projekcie)  
   - [MQTT Security (TLS, Hasła, Autoryzacja)](#mqtt-security-tls-hasła-autoryzacja)  
   - [Bezpieczeństwo Kontenerów i Pod Security](#bezpieczeństwo-kontenerów-i-pod-security)  
   - [Hardening Obrazów i Infrastructure as Code](#hardening-obrazów-i-infrastructure-as-code)  
   - [Zaawansowane Mechanizmy DevSecOps](#zaawansowane-mechanizmy-devsecops)  
6. [Bezpieczeństwo Algorytmów AI](#6-bezpieczeństwo-algorytmów-ai)  
   - [Ataki na Modele ML (Adversarial, Data Poisoning)](#ataki-na-modele-ml-adversarial-data-poisoning)  
   - [Mechanizmy Uwierzytelniania i Autoryzacji w Systemach AI](#mechanizmy-uwierzytelniania-i-autoryzacji-w-systemach-ai)  
   - [Model Governance i Ciągła Walidacja](#model-governance-i-ciągła-walidacja)  
7. [Scenariusze Eksperymentalne i Testy Bezpieczeństwa](#7-scenariusze-eksperymentalne-i-testy-bezpieczeństwa)  
   - [Testy Penetracyjne, Fuzzing, Chaos Engineering](#testy-penetracyjne-fuzzing-chaos-engineering)  
   - [Symulacja Awarii i Skalowanie W Górę / W Dół](#symulacja-awarii-i-skalowanie-w-górę--w-dół)  
   - [Ataki na MQTT / Drony / API](#ataki-na-mqtt--drony--api)  
   - [Przykładowe Ćwiczenia Edukacyjne](#przykładowe-ćwiczenia-edukacyjne)  
8. [Perspektywa CI/CD i Pipeline Bezpieczeństwa](#8-perspektywa-cicd-i-pipeline-bezpieczeństwa)  
9. [Rozbudowa, Możliwe Usprawnienia i Dalsze Kierunki](#9-rozbudowa-możliwe-usprawnienia-i-dalsze-kierunki)  
10. [Podsumowanie](#10-podsumowanie)

---

## 1. Cele, Kontekst i Zakres Projektu

1. **Laboratorium Chmurowe**: Projekt stanowi przestrzeń do praktycznego testowania i wdrażania mechanizmów bezpieczeństwa, sieci, monitoringu w kontekście **Cloud Native** (Kubernetes + Istio + kontenery Docker).
2. **Symulacja Rojów Dronów**:
   - Każdy dron publikuje dane (pozycja, stan baterii, parametry lotu), co pozwala generować ruch i zdarzenia IoT w środowisku.
   - Rój dronów (dziesiątki lub setki instancji) pozwala testować skalę, przepustowość i odporność na awarie.
3. **Komponent AI**:
   - Umożliwia tworzenie autonomicznych algorytmów sterowania rojem, zarządzania energią, planowania tras oraz **implementację zabezpieczeń** w warstwie Machine Learning.
   - Badania nad atakami typu adversarial i obrony w systemach AI.
4. **Bezpieczeństwo na wszystkich poziomach**:
   - Zabezpieczenia brokerów MQTT (autoryzacja, TLS).
   - Zabezpieczenia API (JWT, rate limiting).
   - Ochrona danych w ruchu (mTLS w Service Mesh).
   - Bezpieczeństwo kontenerów (skanowanie obrazów, minimalne systemy bazowe, Pod Security).
   - Testy penetracyjne i chaos engineering.
5. **Cel Edukacyjny i Badawczy**:
   - Projekt jest eksperymentalny – ma służyć inżynierom, studentom, badaczom w zakresie **DevSecOps**, IoT, ML i chmury.

---

## 2. Architektura – Przegląd i Diagram

```
                       [Internet]
                            |
                [Ingress Gateway - Istio]  <--->  [Policy / RBAC / mTLS]
                            |
                            v
   +---------------------------------------------------+
   |               [Aggregator API]                    |
   |         (udostępnianie danych i zarządzanie)      |
   +---------------------------------------------------+
                            |
                            v
                 [Aggregator] <---- subskrypcja MQTT ----- [mqtt_aggregator.py]
                            ^                                   ^
                            |                                   |
                            +---------- [Broker MQTT] <---------+

    [System AI] <----- integracja z Aggregator i/lub Broker ----> (analiza ML, trenowanie, symulacje)
         |
         |--> [Model Trener ML], [Analiza Danych], [Symulacje i Eksperymenty], [Interfejs Zarządzania]
         |
         +--> Może wykorzystywać zewnętrzne API (przez Egress Gateway)

                             ^
                             |
                        [Drony - Pody (IoT)]
                             |
                             v
                   (publikacja w MQTT: drones/{id}/position)
```

**Wybrane elementy**:

- **Drony**: generują dane – *topic* `drones/{drone_id}/position`, MQTT.
- **Broker MQTT** (Mosquitto) i **mqtt_aggregator.py**: łącznik, który może wykonywać dodatkowe transformacje lub logowania.
- **Aggregator** i **Aggregator API**: Główna warstwa logiczna – gromadzenie informacji, udostępnianie przez REST.
- **System AI**: Algorytmy uczenia maszynowego do sterowania rojem i/lub wykrywania anomalii.
- **Istio**: Zapewnia spójne bezpieczeństwo (mTLS, polityki) i kontrolę ruchu.
- **Kubernetes**: Orkiestracja kontenerów i skalowanie.

---

## 3. Opis Szczegółowy Komponentów

### Drony (IoT) – `drones/`

1. **Implementacja**: Mogą być napisane w Pythonie, Node.js czy Go – każda instancja „udaje” drona, co kilka sekund publikuje dane telemetryczne.
2. **Parametry**:
   - Pozycja `(x, y)` lub GPS `(lat, lon)`.
   - Poziom baterii, prędkość, status (active, charging).
3. **Konfiguracja w K8s**:
   - Deployment z replikami (np. `replicas: 50`) pozwala wytworzyć 50 dronów.
   - **Zmienne środowiskowe**: `MQTT_HOST`, `MQTT_TOPIC_BASE`, ewentualnie klucze TLS.
4. **Aspekty Bezpieczeństwa**:
   - Drony (pod) powinny działać w restricted policy (non-root user, read-only filesystem).
   - Komunikacja z brokerem przez TLS (port 8883) lub mTLS (bardziej zaawansowane).

### Broker MQTT i `mqtt-aggregator/`

1. **Broker MQTT (Mosquitto)**:
   - Uruchamiany z pliku `mosquitto-deployment.yaml`, z usługą `mosquitto-service.yaml`.
   - Konfiguracja w `mosquitto.conf` (ustawienia TLS, `allow_anonymous false`, hasło, ACL).
   - Odpowiedzialny za przepływ publish/subscribe między dronami a subskrybentami (Aggregator, System AI).
2. **`mqtt_aggregator.py`**:
   - Skrypt Python subskrybujący topiki (np. `drones/+/position`), wstępnie przetwarzający dane, logujący je lub przekierowujący do innych usług.
   - Często odpalany w osobnym kontenerze, aby rozdzielić logikę „odbioru/konwersji danych” od samego brokera.
3. **Aspekty Bezpieczeństwa**:
   - Plik `requirements.txt` – zależności muszą być skanowane (SAST/DAST).
   - Dockerfile – powinien być zbudowany na minimalnym obrazie, unikamy pakietów zbędnych.
   - Broker konfigurowany tak, by nie przyjmował anonimowych połączeń i miał ograniczenia QoS lub liczby połączeń (rate limiting).

### Agregator – `aggregator/`

1. **Subskrypcja**:
   - Odbiera dane z MQTT (przez python `paho-mqtt` lub `mqtt_aggregator.py`).
   - Przetwarza, np. łączy z danymi pogodowymi, filtruje drony offline.
2. **Analiza**:
   - Może analizować w czasie rzeczywistym (np. wykrycie, czy dany dron nie spada poniżej pewnej wysokości).
3. **Zapis / Udostępnianie**:
   - Wewnętrzna baza (np. Redis lub PostgreSQL) lub trzymanie w pamięci.
   - Udostępnianie do **Aggregator API** (REST) albo przekazanie do **Systemu AI**.
4. **Bezpieczeństwo**:
   - Walidacja formatów JSON (zapobieganie wstrzykiwaniom).
   - Odpowiednie polityki w K8s, by tylko aggregator i AI mogły się łączyć z brokerem MQTT.
   - Możliwość wprowadzenia szyfrowania danych at rest, np. w bazie.

### Aggregator API – `aggregator-api/`

1. **Endopointy** (przykłady):
   - `GET /api/drones` – lista dronów, z podstawowymi informacjami.
   - `GET /api/drones/{id}/status` – pełne dane danego drona.
   - `POST /api/drones/{id}/update` – wysyłanie komend, np. zmiana trasy.
2. **Technologie**:
   - Zwykle Python/Flask lub Node.js/Express.
   - Uruchamiane przez `aggregator-api-deployment.yaml`, skalowane w K8s.
3. **Zabezpieczenia**:
   - Autoryzacja JWT (lub OAuth2) – jedynie uprawnione podmioty mogą sterować dronami.
   - Rate limiting i firewall (Istio Envoy) – ograniczanie ilości żądań i blokowanie IP.
   - Logowanie żądań (dla audytu) – **Kibana**/**Grafana**/**Kiali**.

### System AI (ML)

1. **Cel**:
   - Trenowanie modeli sterujących ruchem roju (oszczędzanie energii, unikanie kolizji).
   - Analiza anomalii, wykrywanie dronów z „fałszywymi danymi” (może posłużyć do testów bezpieczeństwa).
2. **Moduły**:
   - **Model Trener ML**: Batch lub online training (np. przy dużym zbiorze historycznym).
   - **Analiza Danych**: Może subskrybować dane w czasie rzeczywistym i wykrywać anomalie.
   - **Symulacje i Eksperymenty**: Zanim nowy model wejdzie na produkcję, testowane są zachowania roju w środowisku wirtualnym.
   - **Interfejs Zarządzania**: Możliwość wizualizacji, wprowadzania scenariuszy testowych.
3. **Bezpieczeństwo AI**:
   - Ochrona przed atakami adversarial (fake sensory, sabotaż danych).
   - Polityki dostępu do modeli – nieautoryzowany dostęp mógłby np. wstrzyknąć złośliwe wagi modelu i przejąć kontrolę nad dronami.
   - Podpisywanie modeli i weryfikacja integralności (tzw. model governance).

### Warstwa Skryptów i CI/CD – `scripts/`, `server/`

1. **`scripts/`**:
   - Mogą zawierać skrypty do automatycznego wdrażania, budowania obrazów, migracji bazy itd.
   - Narzędzia do testów bezpieczeństwa (np. skrypty do fuzzing aggregator-api).
2. **`server/`**:
   - Czasem służy jako centralny serwis konfiguracyjny lub integrujący (ciężko stwierdzić bez zawartości).
   - Może zawierać pipeline’y, klucze do systemu CI/CD, pliki Jenkinsfile, itp.

---

## 4. Bezpieczeństwo w Kubernetes i Istio

### Warstwa Sieciowa: mTLS, Autoryzacja, Rate Limiting

1. **mTLS**:
   - Każda usługa (aggregator, aggregator-api, AI) komunikuje się z innymi poprzez Envoy sidecar.
   - Certyfikaty zarządzane przez Istio Citadel.
   - Zapewnienie poufności i wzajemnego uwierzytelniania.
2. **Autoryzacja**:
   - **Istio AuthorizationPolicy**: definiowanie, które usługi mogą wywoływać które endpointy.
   - Możliwość ograniczenia dronów tylko do publikowania do broker MQTT, a aggregator do subskrypcji.
3. **Rate Limiting** (Envoy):
   - Ochrona przed atakami DDoS, ewentualne limitowanie liczby żądań do aggregator-api.

### Ingress i Egress Gateway – Kontrola Ruchu

1. **Ingress Gateway**:
   - Publikuje aggregator-api (i ewentualnie AI) na zewnątrz.
   - Konfiguracja TLS – hosty, sni.
   - Można wprowadzić JWT authentication, IP whitelisting, WAF (np. ModSecurity) w Envoy.
2. **Egress Gateway**:
   - Kontroluje ruch do zewnętrznych usług (np. chmurowe API do uczenia modeli, serwisy map, pogodowe).
   - ServiceEntry w Istio, aby odblokować/właczyć określone domeny.

### Zarządzanie Politykami (RBAC, NetworkPolicy, AuthorizationPolicy)

1. **RBAC w K8s**:
   - Przydział ról i uprawnień do developerów / testerów – np. operator ML nie może modyfikować broker MQTT.
   - Rozdzielenie namespace (drony w jednym, aggregator w drugim, AI w trzecim).
2. **NetworkPolicy**:
   - Ograniczenie komunikacji na poziomie IP/port – np. aggregator może łączyć się z broker MQTT, ale drony nie mogą kontaktować się z aggregator-api bezpośrednio.
3. **Istio AuthorizationPolicy**:
   - Szczegółowa kontrola, które usługi mają dostęp do endpointów aggregator-api (np. `api/drones/update`).

### Mechanizmy Monitoringu (Prometheus, Grafana, Kiali, ELK)

1. **Prometheus**:
   - Zbiera metryki z Envoy sidecar, aggregator-api, dronów, AI.
   - Dane o latencjach, przepustowości MQTT, wykorzystaniu zasobów.
2. **Grafana**:
   - Wizualizacja – dashboardy z ruchu w MQTT, obciążenia CPU dronów, tworzonych modeli AI.
3. **Kiali**:
   - Podgląd topologii usług w mesh, sprawdzanie mTLS, polityk dostępu.
4. **ELK Stack**:
   - Scalenie logów dronów, aggregator, API, broker, AI, z centralną analizą (np. Kibana).
   - Możliwość wykrywania anomalii w logach (np. próby ataków).

---

## 5. Zabezpieczenia Chmurowe i IoT w Projekcie

### MQTT Security (TLS, Hasła, Autoryzacja)

1. **TLS / SSL**:
   - Port 8883, broker generuje certyfikaty (ConfigMap + Secret w K8s).
   - Drony i aggregator muszą być skonfigurowane do użycia TLS (paho-mqtt).
2. **Hasła i ACL**:
   - `mosquitto.conf` z `allow_anonymous false`.
   - Plik `password_file` – każdy dron ma unikalne hasło.
   - **Access Control List**: drony mogą tylko `publish`, aggregator może `subscribe`.
3. **Inne**:
   - Limit połączeń klienckich, *per IP throttling*, ograniczenie QoS.

### Bezpieczeństwo Kontenerów i Pod Security

1. **Minimalne obrazy**:
   - `FROM python:3.9-slim` lub `FROM distroless/base`.
   - Usuwanie zbędnych pakietów.
2. **Pod Security**:
   - Uruchamianie jako nie-root, read-only filesystem, brak dostępu do host namespaces.
3. **Skanowanie Podatności**:
   - Narzędzia typu **Trivy**, **Clair**, **Anchore** do analizy obrazów.
   - Automatyzacja w pipeline’ach CI/CD.

### Hardening Obrazów i Infrastructure as Code

1. **Infrastructure as Code** (IaC):
   - Pliki YAML K8s przechowywane w repo Git (GitOps).
   - Recenzja, testy i walidacja (np. **OPA Gatekeeper** – sprawdzanie reguł bezpieczeństwa).
2. **Hardening**:
   - Redukcja liczby warstw w Dockerfile.
   - Włączenie SELinux / AppArmor w węzłach K8s.

### Zaawansowane Mechanizmy DevSecOps

1. **SAST/DAST**:
   - SAST: analiza kodu aggregator, aggregator-api, AI (np. SonarQube, Bandit).
   - DAST: symulowanie ataków na endpointy API (OWASP ZAP).
2. **Secret Management**:
   - HashiCorp Vault lub K8s Secrets (z automatyczną rotacją kluczy).
3. **Policy as Code**:
   - OPA (Open Policy Agent), Rego – weryfikowanie czy wdrożenia spełniają standardy (np. nie-root, mTLS).

---

## 6. Bezpieczeństwo Algorytmów AI

### Ataki na Modele ML (Adversarial, Data Poisoning)

1. **Adversarial**:
   - Próba wstrzyknięcia nieznacznych zmian do danych (np. fałszywe parametry dronów) w celu zmylenia modelu.
   - Projekt może symulować takie ataki i testować mechanizmy obronne (detekcja anomalii).
2. **Data Poisoning**:
   - Złośliwe drony publikują sfałszowane dane do broker MQTT → aggregator → AI.
   - Skutkuje „zatruciem” zbioru treningowego i generowaniem błędnych modeli.
3. **Ochrona**:
   - Walidacja danych wejściowych, podpisy cyfrowe, kwarantanna danych.
   - Mechanizmy typu noise detection, RANSAC, filtry statystyczne.

### Mechanizmy Uwierzytelniania i Autoryzacji w Systemach AI

1. **Tokeny JWT**:
   - Gwarancja, że jedynie autoryzowani użytkownicy (np. admin ML) mogą przeprowadzić trening lub wdrożyć nowy model.
2. **Role-based Access**:
   - Operator ML vs. operator systemu – różne uprawnienia.
   - Przykładowo, inżynier modelu może widzieć parametry, ale niekoniecznie zmieniać konfig bazy danych.
3. **Bezpieczne API do przechowywania modeli**:
   - Docker Registry dla modeli ML lub dedykowane rozwiązanie (S3 + podpisy).
   - Walidacja integralności (np. hash modeli).

### Model Governance i Ciągła Walidacja

1. **Model Governance**:
   - Rejestrowanie wersji modeli, audyt, kto i kiedy wdrożył model w klastrze.
   - Testy wydajności i bezpieczeństwa (skrypty do automatycznych testów).
2. **Ciągła Walidacja**:
   - Monitoring jakości modelu w czasie rzeczywistym (czy przewiduje poprawnie?),
   - Mechanizmy rollback w razie wykrycia anomalii.

---

## 7. Scenariusze Eksperymentalne i Testy Bezpieczeństwa

### Testy Penetracyjne, Fuzzing, Chaos Engineering

1. **Testy Penetracyjne** (pentesty):
   - Próba uzyskania nieautoryzowanego dostępu do aggregator-api (SQLi, XSS).
   - Przeciążanie broker MQTT.
   - Odwrócenie komunikacji drona → broker (sniffing, MITM).
2. **Fuzzing**:
   - Losowe payloady do aggregator-api / AI endpoints → wykrycie crashów.
   - Generowanie anomalii w formacie JSON w MQTT.
3. **Chaos Engineering**:
   - Symulacja awarii broker MQTT, aggregator lub masowy pad dronów.
   - Narzędzia: **Litmus**, **Chaos Mesh**.

### Symulacja Awarii i Skalowanie W Górę / W Dół

- **Awaria**: broker mqtt niedostępny; aggregator czeka w kolejce – jak system reaguje?
- **Skalowanie**: dynamicznie zwiększamy liczbę dronów z 50 do 500; czy aggregator jest w stanie przetworzyć strumień?
- **Test obciążeniowy**: saturacja CPU w aggregator + sprawdzanie, czy HPA (Horizontal Pod Autoscaler) zadziała.

### Ataki na MQTT / Drony / API

- **Fałszywe Drony**: Podszywające się drony z niewłaściwym hasłem MQTT – czy broker odrzuca?
- **Brak TLS**: podsłuch danych w locie, przejęcie sterowania rojem.
- **API Attack**: Podmienianie tras dronów, np. `POST /api/drones/123/update` – bez autoryzacji?

### Przykładowe Ćwiczenia Edukacyjne

1. **„Zabezpiecz broker MQTT”**: włączyć TLS i hasła, przetestować atak brute force.
2. **„Zmigruj aggregator do minimalnego obrazu i przeskanuj go w CI/CD”**.  
3. **„Chaos test aggregator – ubij pody losowo i sprawdź dostępność API”**.
4. **„Atak data poisoning na AI”**: wprowadzenie 10% fałszywych danych i analiza wpływu na model.

---

## 8. Perspektywa CI/CD i Pipeline Bezpieczeństwa

1. **Pipeline** (np. GitLab/Jenkins/ArgoCD):
   - Kod (repo Git) → budowanie kontenerów → SAST skany → testy jednostkowe → DAST (opcjonalnie staging environment) → wdrożenie do K8s.
2. **Kontrola wersji** obrazów w rejestrze (np. Harbor, ECR, Artifactory).  
3. **Scan Dependencies** (pip, npm, cargo) – usuwanie podatnych bibliotek.
4. **Monitor Wdrożenia**: Rollout Canary/Blue-Green w Istio + rewizja ruchu.
5. **Automatyzacja**:
   - GitOps z Flux/Argo → każda zmiana w repo YAML => automatyczne wdrożenie.
   - **Policy as Code** – OPA Gatekeeper do weryfikacji reguł (np. brak praw root w dronie).

---

---

## 9. Podsumowanie

Projekt ten stanowi **kompleksowe laboratorium bezpieczeństwa chmurowego**:

1. **Wielowarstwowość**: IoT (drony), broker MQTT, aggregator, aggregator-api, ML – wszystko spięte przez **Kubernetes** i **Istio**.
2. **Pełne spektrum zabezpieczeń**:
   - **Transport** (mTLS, TLS w MQTT, ACL).
   - **Dane** (autoryzacja, walidacja payloadów, minimalne kontenery).
   - **Infrastruktura** (Pod Security, RBAC, NetworkPolicy).
   - **Machine Learning** (atak na modele, governance).
3. **Możliwości edukacyjne i badawcze**:
   - Od pisania prostych dronów w Pythonie, przez wdrażanie kolejnych usług, aż po zaawansowane scenariusze ataków i chaos engineering.
   - Pokazanie w praktyce, jak wygląda DevSecOps i ciągłe zabezpieczanie systemu.
4. **Skalowalność i modularność**:
   - Można łatwo dodawać kolejne moduły (np. integracja z zewnętrzną bazą, system billingowy).
   - Wysoka elastyczność w doborze technologii i usług.

**Dzięki temu laboratorium** uczestnicy mogą uczyć się i eksperymentować z pełnym zestawem narzędzi i technik bezpieczeństwa w chmurze, tworząc w kontrolowanym środowisku system IoT, który **odzwierciedla** współczesne wyzwania przedsiębiorstw w zakresie **bezpieczeństwa, niezawodności i efektywnego zarządzania** chmurą oraz algorytmami sztucznej inteligencji.