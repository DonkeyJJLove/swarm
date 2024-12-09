## Architektura Systemu

Architektura systemu symulacji roju dronów w środowisku kontenerowym i chmurowym została zaprojektowana w celu zapewnienia skalowalności, elastyczności oraz niezawodności. System składa się z kilku kluczowych komponentów, które współpracują ze sobą, umożliwiając efektywne zarządzanie dronami, komunikację oraz analizę danych.

### **Diagram Architektury**

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
                                         |
                                         v
                           +-------------------------------+
                           |          Baza Danych          |
                           |      (PostgreSQL/MySQL)       |
                           +-------------------------------+
                                         |
                                         v
                           +-------------------------------+
                           |      Interfejs Użytkownika    |
                           |        (Web Dashboard)        |
                           +-------------------------------+
```

### **Opis Komponentów**

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

#### 5. **Baza Danych (`database/`)**

- **Rola:** Przechowywanie zebranych danych z dronów.
- **Funkcje:**
  - **Przechowywanie Danych:** Gromadzi i przechowuje dane dotyczące pozycji, stanu baterii oraz innych parametrów dronów.
  - **Zapytania i Analizy:** Umożliwia wykonywanie zapytań oraz analizowanie danych w celu optymalizacji działania roju.
- **Technologie:** PostgreSQL, MySQL lub inne relacyjne bazy danych.
- **Pliki:** [Konfiguracja bazy danych](database/)
- **Szczegółowe Wyjaśnienie:** [Dokumentacja Bazy Danych](./_docs/database.md)

#### 6. **Interfejs Użytkownika (`frontend/`)**

- **Rola:** Dostarczanie wizualizacji i interakcji dla użytkowników systemu.
- **Funkcje:**
  - **Web Dashboard:** Wizualizacja danych z roju dronów, monitorowanie ich stanu w czasie rzeczywistym.
  - **Interakcje:** Umożliwia użytkownikom wysyłanie komend sterujących, zarządzanie dronami oraz analizowanie zgromadzonych danych.
- **Technologie:** React, Angular, Vue.js lub inne frameworki frontendowe.
- **Pliki:** [Kod interfejsu użytkownika](frontend/)
- **Szczegółowe Wyjaśnienie:** [Dokumentacja Frontend](./_docs/frontend.md)

### **Interakcje i Przepływ Danych**

1. **Generowanie i Publikowanie Danych przez Drony:**
   - Każdy dron generuje dane dotyczące swojej pozycji, stanu baterii oraz innych parametrów.
   - Dane te są publikowane na brokerze MQTT pod określonym topikiem `drones/{drone_id}/position`.

2. **Odbieranie i Przetwarzanie Danych przez Agregator:**
   - Agregator subskrybuje topiki MQTT za pomocą wzorca `drones/+/position`, co pozwala na odbieranie danych od wszystkich dronów.
   - Otrzymane dane są analizowane i agregowane w czasie rzeczywistym.
   - Agregator może również zapisywać dane do bazy danych oraz przekazywać je dalej do Aggregator API.

3. **Udostępnianie Danych poprzez Aggregator API:**
   - Aggregator API udostępnia zebrane dane za pomocą REST API, umożliwiając dostęp do nich zewnętrznym aplikacjom oraz interfejsowi użytkownika.
   - Użytkownicy mogą za pomocą API monitorować stan roju, zarządzać dronami oraz wykonywać inne operacje.

4. **Przechowywanie Danych w Bazie Danych:**
   - Zebrane dane są przechowywane w bazie danych, co umożliwia ich późniejszą analizę, raportowanie oraz wykorzystanie w różnych procesach biznesowych.

5. **Interakcja Użytkownika z Systemem:**
   - Użytkownik korzysta z web dashboardu do monitorowania roju dronów w czasie rzeczywistym.
   - Dashboard umożliwia również wysyłanie komend sterujących, zarządzanie dronami oraz przeglądanie historii danych.

### **Integracja z Innych Dokumentów**

Architektura systemu jest szczegółowo opisana w różnych dokumentach, które można znaleźć w katalogu `_docs/`. Poniżej znajdują się odnośniki do kluczowych dokumentów:

- [Zaawansowany Kurs Docker](#zaawansowany-kurs-docker)
- [Kubernetes – Orkiestracja Kontenerów](#kubernetes---orkiestracja-kontenerow)
- [Docker w Chmurach Hybrydowych](#docker-w-chmurach-hybrydowych)
- [Strategia Blue-Green i Canary](./_docs/strategia_blue_green_canary.md)
- [Budowanie i Zarządzanie Obrazami Dockerowymi](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md)
- [Ogólny Opis Projektu](./_docs/readme.md)
- [Dokumentacja Brokera MQTT](./_docs/broker_mqtt.md)
- [Szczegółowy opis agregatora](./_docs/aggregator_details.md)
- [Szczegółowy opis Aggregator API](./_docs/aggregator_api_details.md)
- [Dokumentacja Bazy Danych](./_docs/database.md)
- [Dokumentacja Frontend](./_docs/frontend.md)
  
### **Podsumowanie Architektury Systemu**

Architektura systemu symulacji roju dronów w środowisku kontenerowym i chmurowym została zaprojektowana tak, aby zapewnić:

- **Skalowalność i Elastyczność:** Dzięki Kubernetes możliwe jest dynamiczne skalowanie roju dronów oraz łatwe wdrażanie nowych komponentów.
- **Automatyzację Procesów:** Pipeline’y CI/CD oraz Infrastructure as Code umożliwiają automatyzację budowania, testowania i wdrażania aplikacji, co zwiększa efektywność operacyjną.
- **Zaawansowane Monitorowanie i Analizę Danych:** Integracja z narzędziami monitorującymi oraz systemami do analizy logów pozwala na bieżące monitorowanie stanu systemu i szybkie reagowanie na potencjalne problemy.
- **Bezpieczeństwo:** Implementacja najlepszych praktyk bezpieczeństwa, takich jak RBAC, Network Policies oraz szyfrowanie danych, zapewnia ochronę systemu przed nieautoryzowanym dostępem i innymi zagrożeniami.
- **Modularność i Niezależność Komponentów:** Architektura mikroserwisów oraz konteneryzacja umożliwiają niezależny rozwój i wdrażanie poszczególnych komponentów systemu, co zwiększa elastyczność i ułatwia integrację nowych funkcjonalności.

Dzięki tak zaprojektowanej architekturze, system jest w stanie efektywnie zarządzać dużą flotą dronów, centralizować ich dane oraz zapewniać niezawodne i skalowalne środowisko operacyjne.

