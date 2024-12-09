# Dokumentacja Projektu: Symulacja Rojów Dronów w Architekturze Kontenerowej

Zarządzanie rojem dronów w środowisku chmurowym to złożony, wielowymiarowy proces, który integruje zaawansowane techniki konteneryzacji, orkiestracji, komunikacji oraz inteligentnego sterowania. Głównym celem jest traktowanie każdego drona jako niezależnego kontenera, co umożliwia jego autonomiczne działanie oraz płynną komunikację z innymi dronami i komponentami systemu. Wykorzystanie podejścia chmurowego pozwala na dynamiczne skalowanie liczby dronów w zależności od aktualnych potrzeb, automatyzację procesów wdrażania i aktualizacji oraz zastosowanie zaawansowanych narzędzi do monitoringu i analizy danych.

### **Zalety Takiego Rozwiązania**

- **Skalowalność:**
  - **Dynamiczne Przydzielanie Zasobów:** W środowisku chmurowym liczba aktywnych dronów może być elastycznie dostosowywana do bieżącego zapotrzebowania. Wzrost obciążenia umożliwia łatwe dodawanie nowych instancji, natomiast spadek – redukcję ich liczby.
  - **Horizontalne Skalowanie:** Kubernetes ułatwia skalowanie poziome, co pozwala systemowi obsługiwać zmienne obciążenia poprzez rozdzielanie dronów na wiele węzłów.

- **Elastyczność i Modularność:**
  - **Niezależny Rozwój:** Konteneryzacja umożliwia niezależny rozwój, testowanie i wdrażanie poszczególnych komponentów systemu, co zwiększa modularność i ułatwia integrację nowych funkcjonalności bez wpływu na działające elementy.
  - **Architektura Mikroserwisów:** Przyjęcie podejścia mikroserwisowego pozwala na rozwój, wdrażanie i skalowanie każdego serwisu niezależnie, co zwiększa ogólną elastyczność systemu.

- **Automatyzacja:**
  - **Continuous Integration/Continuous Deployment (CI/CD):** Zautomatyzowane pipeline'y CI/CD usprawniają proces budowania, testowania i wdrażania aplikacji, co pozwala na szybkie i niezawodne przenoszenie zmian kodu do środowisk produkcyjnych.
  - **Infrastructure as Code (IaC):** Narzędzia takie jak Terraform i Helm Charts umożliwiają automatyzację provisioning’u infrastruktury oraz zarządzanie konfiguracją, minimalizując ręczne interwencje i potencjalne błędy.

- **Oszczędność Zasobów:**
  - **Optymalne Wykorzystanie Chmury:** Efektywne zarządzanie zasobami chmurowymi oraz automatyczne skalowanie pozwala na minimalizację kosztów poprzez płacenie tylko za faktycznie wykorzystywaną infrastrukturę.
  - **Zarządzanie Kosztami:** Dostawcy chmury oferują różnorodne modele cenowe oraz narzędzia do zarządzania kosztami, które pomagają monitorować i optymalizować wydatki w zależności od wzorców wykorzystania.

### **Wyzwania i Ograniczenia**

- **Złożoność Architektury:**
  - **Wymagania Techniczne:** Zarządzanie dużym rojem kontenerów wymaga dogłębnej wiedzy na temat technologii chmurowych, protokołów komunikacyjnych oraz narzędzi do monitoringu i zabezpieczeń.
  - **Integracja Systemów:** Zapewnienie płynnej integracji między różnymi komponentami i usługami zwiększa złożoność architektoniczną systemu.

- **Nadmiarowe Koszty i Opóźnienia:**
  - **Koszty Operacyjne:** Chociaż elastyczność chmury jest korzystna, może prowadzić do wyższych kosztów operacyjnych, jeśli nie jest odpowiednio zarządzana.
  - **Opóźnienia Sieciowe:** Zwiększony ruch sieciowy oraz czas reakcji brokerów MQTT, baz danych czy systemów monitoringu mogą wprowadzać opóźnienia w komunikacji, co może negatywnie wpływać na operacje w czasie rzeczywistym.

- **Bezpieczeństwo:**
  - **Ochrona Danych:** Autonomiczne drony komunikujące się w rozproszonym środowisku chmurowym muszą być chronione przed nieautoryzowanym dostępem, atakami i wyciekami danych.
  - **Zaawansowane Środki Bezpieczeństwa:** Konieczne jest wdrożenie solidnych polityk bezpieczeństwa, mechanizmów uwierzytelniania oraz technik szyfrowania, aby zabezpieczyć system przed potencjalnymi zagrożeniami.

Projekt symulacji roju dronów ma na celu zaprezentowanie podejścia do zarządzania wieloma urządzeniami IoT w architekturze kontenerowej i chmurowej. Integruje on konteneryzację (Docker), orkiestrację (Kubernetes), komunikację (MQTT), pipeline'y CI/CD, monitoring (Prometheus, Grafana, ELK) oraz strategie wdrożeń (Blue-Green, Canary), tworząc kompletne i skalowalne środowisko dla roju dronów.

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

- **Rola:** Symulacja autonomicznych dronów w systemie.
- **Funkcje:**
  - **Generowanie Danych:** Każdy dron generuje informacje dotyczące swojej pozycji, stanu baterii oraz innych istotnych parametrów.
  - **Publikowanie Danych:** Dane są publikowane na brokerze MQTT, umożliwiając ich dalszą dystrybucję.
  - **Odbiór Komend:** Drony odbierają komendy sterujące z agregatora lub API, co pozwala na ich zdalne kontrolowanie.
- **MQTT Topic:**
  ```plaintext
  drones/{drone_id}/position
  ```
- **Szczegółowa Dokumentacja:** [Dokumentacja Dronów](./_docs/drones_component.md)
- **Pliki:** [Kod drona i konfiguracja](drones/)

#### 2. **Broker MQTT (`server/mqtt/`)**

- **Rola:** Centralny węzeł komunikacyjny systemu.
- **Funkcje:**
  - **Odbieranie Danych:** Broker MQTT odbiera dane publikowane przez drony.
  - **Dystrybucja Danych:** Rozsyła odebrane dane do subskrybujących komponentów, takich jak agregator.
- **Konfiguracja:**
  - **Deployment:** Wdrażany w Kubernetes jako usługa z wykorzystaniem Mosquitto, co zapewnia skalowalność i niezawodność.
- **Pliki:** [Konfiguracja MQTT](server/mqtt/)
- **Szczegółowe Wyjaśnienie:** [Dokumentacja Brokera MQTT](./_docs/broker_mqtt.md)

#### 3. **Agregator (`aggregator/`)**

- **Rola:** Zbieranie i przetwarzanie danych od dronów.
- **Funkcje:**
  - **Subskrypcja Danych:** Subskrybuje odpowiednie topiki MQTT, aby odbierać dane publikowane przez drony.
  - **Agregacja i Analiza:** Agreguje i analizuje dane w czasie rzeczywistym, umożliwiając natychmiastową reakcję na zmieniające się warunki.
  - **Przechowywanie i Przekazywanie Danych:** Może zapisywać dane do bazy danych lub przekazywać je dalej do API, w zależności od potrzeb.
- **MQTT Subskrypcja:**
  ```plaintext
  drones/+/position
  ```
- **Pliki:** [Kod agregatora](aggregator/)
- **Szczegółowe Wyjaśnienie:** [Szczegółowy opis agregatora](./_docs/aggregator_details.md)

#### 4. **Aggregator API (`aggregator-api/`)**

- **Rola:** Interfejs do komunikacji zewnętrznej.
- **Funkcje:**
  - **Udostępnianie Danych:** Dostarcza zebrane dane z agregatora za pomocą REST API, umożliwiając dostęp do nich zewnętrznym aplikacjom.
  - **Zarządzanie Roju Dronów:** Umożliwia zarządzanie dronami, w tym aktualizację ich parametrów oraz wysyłanie komend sterujących.
  - **Monitorowanie Statusu:** Obsługuje żądania dotyczące statusu dronów, co pozwala na monitorowanie ich bieżącego stanu.
- **Endpointy API:**
  ```http
  GET /api/drones/{drone_id}/status
  POST /api/drones/{drone_id}/update
  GET /api/drones
  ```
- **Pliki:** [Kod API](aggregator-api/)
- **Szczegółowe Wyjaśnienie:** [Szczegółowy opis Aggregator API](./_docs/aggregator_api_details.md)

---

# Szczegóły Komunikacji Sieciowej i Wdrożenia

## 1. Szczegóły Komunikacji Sieciowej

W projekcie wykorzystujemy protokół MQTT do realizacji komunikacji pomiędzy dronami a agregatorem danych. Drony publikują informacje o swojej pozycji oraz stanie baterii do brokera MQTT, a agregator subskrybuje te dane, przetwarza je i udostępnia za pośrednictwem API.

### Przepływ Danych

1. **Drony** publikują dane na brokerze MQTT:
   ```json
   Topic: drones/{drone_id}/position
   Payload: { "x": 10, "y": 20, "battery": 95 }
   ```

2. **Agregator** subskrybuje odpowiednie topiki i odbiera dane:
   ```plaintext
   Subskrypcja: drones/+/position
   ```

3. **Aggregator API** umożliwia dostęp do zebranych danych:
   ```http
   GET /api/drones/{drone_id}/status
   ```

### Przykład Konfiguracji Mosquitto

Plik `mosquitto.conf`:
```plaintext
listener 1883
allow_anonymous true
```

### Wyjaśnienie MQTT

- **Jak działa komunikacja MQTT w projekcie?**
  MQTT to lekki protokół publikacja/subskrypcja, idealny dla środowisk IoT. Drony, działające jako klienci MQTT, publikują dane o swojej pozycji i stanie baterii na określonych tematach. Broker MQTT, taki jak Mosquitto, odpowiada za dystrybucję tych danych do subskrybentów.

- **Zalety użycia MQTT:**
  - **Niski Narzut Danych:** MQTT jest lekki, co czyni go odpowiednim dla środowisk IoT z ograniczoną przepustowością.
  - **Asynchroniczność:** Umożliwia komunikację bez konieczności jednoczesnej obecności nadawcy i odbiorcy, co zwiększa elastyczność systemu.
  - **Elastyczne Wzorce Subskrypcji:** Pozwalają na precyzyjną filtrację danych na podstawie struktury topików, co ułatwia zarządzanie dużymi ilościami danych.

- **Topiki MQTT i Wzorce Subskrypcji:**
  Topiki w MQTT są hierarchiczne i pozwalają na efektywne filtrowanie danych. Wzorce z użyciem symbolu `+` umożliwiają subskrypcję wielu dronów bez konieczności definiowania każdego drona osobno, np. `drones/+/position` subskrybuje pozycje wszystkich dronów.

---

## 2. Wdrożenie w Kubernetes

Wykorzystanie Kubernetes do wdrożenia dronów, agregatora oraz brokera MQTT zapewnia skalowalność, automatyzację i niezawodność całego systemu.

### Zasoby Kubernetes

#### Przykład Deployment dla Dronów

**Plik:** `deployments/drone-deployment.yaml`
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
        ports:
        - containerPort: 8080
```

#### Przykład Service dla MQTT

**Plik:** `services/mqtt-service.yaml`
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
  type: ClusterIP
```

### Korzyści ze Stosowania Kubernetes

- **Skalowalność:**
  - **Auto-Scaling:** Kubernetes może automatycznie dostosowywać liczbę instancji dronów na podstawie aktualnego obciążenia i wykorzystania zasobów.
  - **Load Balancing:** Równoważy ruch sieciowy między instancjami dronów, zapewniając optymalną wydajność i dostępność.

- **Odporność na Awarie:**
  - **Self-Healing:** Kubernetes automatycznie restartuje awaryjne pody oraz zastępuje uszkodzone instancje, co zapewnia ciągłość działania systemu.
  - **Rolling Updates:** Umożliwia płynne aktualizacje aplikacji z minimalnym czasem przestoju poprzez stopniową wymianę starych podów na nowe wersje.

- **Prostota Zarządzania:**
  - **Deklaratywne Manifesty:** Definicje zasobów w postaci plików YAML pozwalają na łatwe zarządzanie stanem systemu oraz wersjonowanie konfiguracji.
  - **Infrastruktura jako Kod (IaC):** Umożliwia automatyzację provisioning’u i zarządzania infrastrukturą, co zwiększa efektywność i zmniejsza ryzyko błędów ludzkich.

---

## 3. CI/CD i Monitoring

### Continuous Integration/Continuous Deployment (CI/CD)

- **Pipeline CI/CD:** Automatyzuje cały proces budowania, testowania i wdrażania aplikacji, zapewniając szybkie i niezawodne dostarczanie nowych funkcjonalności.
- **Narzędzia Używane:** 
  - **GitLab CI/CD:** Integruje się z systemem kontroli wersji, automatyzując procesy pipeline.
  - **Jenkins:** Oferuje elastyczność w automatyzacji budowania i wdrażania aplikacji.
  - **ArgoCD:** Zarządza wdrożeniami na Kubernetes zgodnie z zasadami GitOps.
- **Etapy Pipeline:**
  1. **Budowanie Obrazów Docker:** Automatyczne skrypty kompilują i pakują aplikacje w kontenery Docker.
  2. **Testowanie:** Przeprowadzane są automatyczne testy, które weryfikują funkcjonalność i niezawodność kodu.
  3. **Wdrożenie:** Udało się pomyślnie zbudować aplikacje, które są automatycznie wdrażane do klastra Kubernetes.

### Monitoring

- **Prometheus i Grafana:**
  - **Prometheus:** Zbiera i przechowuje metryki z różnych komponentów systemu.
  - **Grafana:** Wizualizuje metryki poprzez konfigurowalne dashboardy, dostarczając wglądu w wydajność i stan systemu.
- **ELK Stack:**
  - **Elasticsearch:** Przechowuje i indeksuje logi, umożliwiając efektywne wyszukiwanie i analizę.
  - **Logstash:** Agreguje i przetwarza logi z różnych źródeł.
  - **Kibana:** Wizualizuje dane logów, umożliwiając szczegółową analizę i rozwiązywanie problemów.
- **Kluczowe Metryki Monitorowane:**
  - **Wykorzystanie Zasobów:** Zużycie CPU i pamięci przez drony oraz komponenty systemu.
  - **Stan Baterii:** Monitorowanie poziomów baterii dronów w czasie rzeczywistym, aby zapewnić ich gotowość operacyjną.
  - **Dostępność Usług:** Śledzenie czasu działania i responsywności wdrożonych usług.

---

## 4. Informacje z Istniejących Plików

- **`_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md`**  
  Szczegółowy przewodnik dotyczący budowania i zarządzania obrazami Docker, w tym multi-stage builds, strategie wersjonowania oraz zarządzanie repozytoriami.

- **`_docs/strategia_blue_green_canary.md`**  
  Kompleksowy przegląd strategii wdrożeń Blue-Green oraz Canary, włączając kroki implementacji i najlepsze praktyki.

- **`_docs/readme.md`**  
  Ogólny opis projektu obejmujący symulację roju dronów, komunikację MQTT, wdrożenie w Kubernetes, konfigurację monitoringu oraz konfigurację pipeline'ów CI/CD.

---

## 5. Implementacja Logiki i Sterowania

Po skonfigurowaniu klastra Kubernetes oraz stworzeniu i skalowaniu dronów, następnym krokiem jest implementacja logiki zarządzającej oraz sterującej dronami za pomocą niskopoziomowych API.

### Komponenty Zaangażowane

- **Decyzje Autonomiczne:**
  - **Wbudowana Logika:** Każdy dron (pod) posiada własną logikę, która umożliwia podejmowanie decyzji na podstawie danych wejściowych oraz warunków środowiskowych.
  - **Algorytmy Zachowań:** Algorytmy decydują o ruchach drona, priorytetyzacji zadań oraz reakcjach na zewnętrzne komendy.

- **Bezpieczeństwo Kontenerów:**
  - **Izolacja:** Zapewnienie, że każdy kontener drona działa w izolacji, co chroni przed nieautoryzowanym dostępem i utrzymuje integralność systemu.
  - **Polityki Bezpieczeństwa:** Implementacja ścisłych polityk bezpieczeństwa, które zabezpieczają kontenery przed podatnościami i atakami.

- **Monitorowanie i Logowanie:**
  - **Integracja z Prometheus:** Zbieranie metryk dotyczących wydajności dronów oraz stanu systemu.
  - **Dashboardy Grafana:** Tworzenie wizualizacji metryk w czasie rzeczywistym dla efektywnego monitorowania i analizy.
  - **Centralne Logowanie:** Agregacja logów ze wszystkich dronów i komponentów systemu w celu kompleksowego rozwiązywania problemów.

- **Skalowalność:**
  - **Polityki Auto-Scaling:** Automatyczne dostosowywanie liczby instancji dronów w odpowiedzi na bieżące metryki i zdefiniowane progi.
  - **Optymalizacja Zasobów:** Zapewnienie optymalnego wykorzystania zasobów chmurowych poprzez skalowanie dronów w zależności od zmieniających się warunków i obciążeń.

---

## 6. Bezpieczeństwo w Klastrze Kubernetes

Bezpieczeństwo jest kluczowym aspektem zarządzania klastrem Kubernetes, zwłaszcza gdy drony działają autonomicznie i komunikują się w rozproszonym środowisku chmurowym. Wdrożenie solidnych środków bezpieczeństwa zapewnia integralność, poufność i dostępność systemu.

### Kluczowe Praktyki Bezpieczeństwa

- **Role-Based Access Control (RBAC):**
  - **Definicje Ról:** Określanie ról z określonymi uprawnieniami dostosowanymi do potrzeb użytkowników i aplikacji.
  - **Ograniczenia Dostępu:** Ograniczenie dostępu do zasobów na podstawie zasady najmniejszego przywileju, co zapewnia, że użytkownicy i usługi mają dostęp tylko do niezbędnych komponentów.

- **Network Policies:**
  - **Kontrola Ruchu:** Definiowanie polityk, które kontrolują przepływ ruchu między podami, ograniczając nieautoryzowaną komunikację.
  - **Segmentacja:** Izolowanie różnych komponentów systemu, co minimalizuje wpływ potencjalnych naruszeń bezpieczeństwa.

- **Secrets Management:**
  - **Bezpieczne Przechowywanie:** Przechowywanie wrażliwych informacji, takich jak klucze API, hasła i certyfikaty, w sposób bezpieczny przy użyciu Kubernetes Secrets.
  - **Kontrola Dostępu:** Ograniczenie dostępu do sekretów tylko do tych usług i użytkowników, którzy ich potrzebują.

- **Pod Security Policies (PSP):**
  - **Reguły Bezpieczeństwa:** Definiowanie i egzekwowanie reguł bezpieczeństwa dla tworzenia podów, takich jak zakaz uruchamiania kontenerów jako root czy wymóg używania nieuprzywilejowanych użytkowników.
  - **Zgodność:** Zapewnienie, że wszystkie pody przestrzegają standardów bezpieczeństwa organizacji i najlepszych praktyk.

- **Szyfrowanie:**
  - **Danych w Transporcie:** Szyfrowanie całej komunikacji między dronami, brokerami i innymi usługami za pomocą TLS, co zapobiega podsłuchiwaniu i modyfikacjom danych.
  - **Danych w Spoczynku:** Szyfrowanie wrażliwych danych przechowywanych w systemie, aby chronić je przed nieautoryzowanym dostępem.

- **Regularne Audyty i Zgodność:**
  - **Audyty Bezpieczeństwa:** Regularne przeprowadzanie audytów bezpieczeństwa w celu identyfikacji i usunięcia luk w zabezpieczeniach.
  - **Standardy Zgodności:** Przestrzeganie odpowiednich standardów branżowych i regulacji prawnych, co zwiększa poziom bezpieczeństwa systemu.

---

## Podsumowanie

Projekt integruje technologie konteneryzacji, orkiestracji, komunikacji i monitoringu w celu stworzenia skalowalnej i elastycznej platformy do zarządzania rojem dronów. Przyjęte podejście opiera się na protokole MQTT, wdrożeniu na Kubernetes, automatyzacji procesów CI/CD, monitoringu metryk oraz logów, a także zastosowaniu strategii wdrożeń Blue-Green i Canary. Szczególny nacisk został położony na kwestie bezpieczeństwa, implementację logiki oraz sterowanie dronami. W rezultacie powstaje system zdolny do autonomicznego działania, efektywnego wykorzystania zasobów chmurowych oraz szybkiego reagowania na zmiany w środowisku, co zapewnia skuteczne zarządzanie rojem dronów w rozproszonym i dynamicznym środowisku.

```