
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
- **Szczegółowe wyjaśnienie**: [Dokumentacja Brokera MQTT](./_docs/broker_mqtt.md)

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
- **Szczegółowe wyjaśnienie**: - **Dokumentacja**: [Szczegółowy opis agregatora](./_docs/aggregator_details.md)

Oto zaktualizowana wersja punktu 4 w formie spójnej z punktem 3:

---

#### 4. **Aggregator API (`aggregator-api/`)**

- **Rola**: Interfejs do komunikacji zewnętrznej.
- **Funkcja**:
  - Udostępnia dane z agregatora za pomocą REST API.
  - Umożliwia zarządzanie rojem dronów i ich parametrami.
  - Obsługuje żądania pobierania statusu dronów oraz wysyłania komend sterujących.
- **Endpointy API**:
  ```http
  GET /api/drones/{drone_id}/status
  POST /api/drones/{drone_id}/update
  GET /api/drones
  ```
- **Pliki**: [Kod API](aggregator-api/)
- **Szczegółowe wyjaśnienie**: [Szczegółowy opis Aggregator API](./_docs/aggregator_api_details.md)

---

```markdown
# Szczegóły Komunikacji Sieciowej i Wdrożenia

## 1. Szczegóły Komunikacji Sieciowej

W projekcie wykorzystujemy protokół MQTT do realizacji komunikacji pomiędzy dronami a agregatorem danych. Drony publikują informacje o swojej pozycji oraz stanie baterii do brokera MQTT, a agregator subskrybuje te dane, przetwarza je i udostępnia za pośrednictwem API.

### Przepływ Danych

1. **Drony** publikują dane na brokerze MQTT:
   ```json
   Topic: drones/{drone_id}/position
   Payload: { "x": 10, "y": 20, "battery": 95 }
   ```
   W powyższym przykładzie `{drone_id}` reprezentuje unikalny identyfikator drona. Dron przekazuje informacje o swojej pozycji w formie współrzędnych `x`, `y` oraz o stanie baterii.

2. **Agregator** subskrybuje odpowiednie topiki i odbiera dane:
   ```plaintext
   Subskrypcja: drones/+/position
   ```
   Wzorzec `+/position` pozwala na odbiór komunikatów od wszystkich dronów publikujących swoją pozycję (znak `+` zastępuje jedno z poziomów tematu, w tym przypadku identyfikator drona).

3. **Aggregator API** umożliwia dostęp do zebranych danych:
   ```http
   GET /api/drones/{drone_id}/status
   ```
   Dzięki temu interfejsowi klienci zewnętrzni mogą pobierać aktualne informacje o stanie drona, takie jak jego pozycja czy poziom baterii.

### Przykład Konfiguracji Mosquitto

Plik `mosquitto.conf`:
```plaintext
listener 1883
allow_anonymous true
```

Konfiguracja powyżej uruchamia brokera MQTT na porcie `1883` i zezwala na anonimowy dostęp (co może być przydatne w środowiskach testowych lub w ramach klastra Kubernetes, ale w środowisku produkcyjnym warto rozważyć mechanizmy uwierzytelniania i autoryzacji).

### Wyjaśnienie

- **Jak działa komunikacja MQTT w projekcie?**  
  MQTT to lekki protokół publikacja/subskrypcja. Drony (klienci MQTT) publikują dane o pozycji i stanie baterii na zdefiniowanych tematach. Broker MQTT odpowiada za dystrybucję tych danych do subskrybentów (np. agregatora), którzy chcą je odbierać.

- **Zalety użycia MQTT w rozproszonej komunikacji:**  
  - **Mały narzut danych** – idealny dla urządzeń IoT i środowisk o ograniczonej przepustowości.
  - **Asynchroniczna komunikacja** – nadawca i odbiorca nie muszą być aktywni w tym samym czasie.
  - **Elastyczne wzorce subskrypcji** – dzięki topikom możliwe jest filtrowanie i grupowanie komunikatów pochodzących od wielu źródeł.
  
- **Znaczenie topików MQTT i wzorców subskrypcji:**  
  Topiki stanowią hierarchiczne adresy dla wiadomości. Dzięki nim można precyzyjnie określić, które dane chcemy odbierać. Wzorce, takie jak `+/position`, pozwalają na subskrybowanie wielu dronów jednocześnie bez konieczności ich indywidualnej konfiguracji.

---

## 2. Wdrożenie w Kubernetes

Wykorzystanie Kubernetes do wdrożenia dronów, agregatora oraz brokera MQTT zapewnia skalowalność, automatyzację i niezawodność. Kubernetes umożliwia łatwe zarządzanie kontenerami, skalowanie replik, a także automatyczne restarty i aktualizacje.

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

- **Co to jest Deployment?**  
  Deployment zarządza cyklem życia zestawu replik (ReplicaSet) dla danej aplikacji. W powyższym przykładzie uruchamiamy 3 repliki kontenera `drone-simulation`. Kubernetes zapewnia utrzymanie stałej liczby replik, ich automatyczne restarty w przypadku awarii oraz wdrażanie aktualizacji bez przestojów.

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

- **Co to jest Service?**  
  Service w Kubernetes definiuje stały punkt dostępu (DNS i port) do zestawu kontenerów (podów). W naszym przypadku `mqtt-service` kieruje ruch do podów z etykietą `app: mqtt`, które uruchamiają brokera MQTT. Dzięki temu drony i agregator mogą łączyć się z brokerem bez względu na to, jakie konkretnie pody aktualnie go obsługują.

### Korzyści ze stosowania Kubernetes

- **Skalowalność:** Możemy łatwo zwiększać lub zmniejszać liczbę replik dronów czy brokera MQTT w zależności od obciążenia.
- **Odporność na awarie:** W razie padnięcia kontenera Kubernetes automatycznie uruchomi nowy.
- **Prostota zarządzania:** Infrastruktura jako kod oraz deklaratywne podejście ułatwiają wdrażanie, aktualizacje oraz utrzymanie aplikacji.

---

## 3. CI/CD i Monitoring

### CI/CD

W projekcie wykorzystywany jest pipeline CI/CD do automatyzacji procesu budowania, testowania oraz wdrażania aplikacji na klaster Kubernetes. 

- **Jak działa pipeline CI/CD?**  
  Pipeline CI/CD, np. oparty o GitLab CI/CD, Jenkins czy ArgoCD, automatyzuje kolejne kroki:  
  1. **Budowanie:** Tworzenie obrazów Docker z kodu źródłowego.
  2. **Testowanie:** Uruchamianie testów jednostkowych, integracyjnych i wydajnościowych.
  3. **Wdrożenie:** Aktualizacja zasobów w klastrze Kubernetes (Deployment, Service itp.).

- **Narzędzia:**  
  - **GitLab CI/CD:** Integracja z repozytorium kodu, uruchamianie pipeline po każdym pushu.
  - **Jenkins:** Elastyczny serwer CI, możliwość integracji z wieloma środowiskami.
  - **ArgoCD:** Narzędzie do ciągłego wdrażania (CD) w Kubernetes, deklaratywne zarządzanie stanem aplikacji.

- **Konfiguracja pipeline:**  
  Pipeline można skonfigurować poprzez pliki YAML (np. `.gitlab-ci.yml` lub pliki konfiguracyjne Jenkins/ArgoCD). W nich określamy kolejne kroki, obraz bazowy, komendy budowania i testowania oraz działania wdrożeniowe (aplikacja manifestów Kubernetes).

### Monitoring

W celu monitorowania stanu dronów, brokerów MQTT oraz agregatora wykorzystujemy narzędzia do zbierania i wizualizacji metryk oraz logów:

- **Prometheus i Grafana:**  
  Prometheus zbiera metryki z aplikacji i infrastruktury, a Grafana umożliwia ich wizualizację w formie dashboardów. Monitorowane metryki obejmują m.in. zużycie CPU, pamięci, stan baterii dronów, liczbę przetworzonych komunikatów MQTT czy dostępność usług.

- **ELK Stack (Elasticsearch, Logstash, Kibana):**  
  ELK Stack umożliwia zbieranie, przetwarzanie i analizę logów. Dzięki Logstash logi są parsowane i przekazywane do Elasticsearch, gdzie mogą być przeszukiwane i analizowane. Kibana umożliwia wygodne przeglądanie logów oraz tworzenie wizualizacji i dashboardów analitycznych.

- **Konfiguracja monitoringu:**  
  - **Prometheus:** Wdrażany jako Deployment w Kubernetes, poprzez `ServiceMonitor` może automatycznie wykrywać usługi do monitorowania.
  - **Grafana:** Instaluje się poprzez helm chart lub manifesty YAML, konfigurując dashboardy do wizualizacji metryk.
  - **ELK Stack:** Wdrażany przy pomocy manifestów Kubernetes (lub operatorów), zapewnia centralne miejsce do gromadzenia i analizy logów z dronów, agregatora i brokera.

---

### **Dokumentacja Projektu: Symulacja Rojów Dronów**

---

## **4. Informacje dodatkowe**

Projekt jest kompleksowym rozwiązaniem do symulacji roju dronów w środowisku kontenerowym i chmurowym. Poniżej znajdują się odnośniki do istniejących dokumentów oraz ich krótki opis:

---

### **[`_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md`](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md)**

- **Zawartość**:
  - Szczegółowe instrukcje dotyczące tworzenia obrazów Docker dla dronów, serwera wizualizacyjnego i brokera MQTT.
  - Wskazówki na temat **versioningu**, korzystania z rejestrów obrazów takich jak **Docker Hub** lub prywatne repozytoria.
  - Najlepsze praktyki, w tym:
    - **Minimalizacja rozmiaru obrazów**.
    - **Wieloetapowe budowanie** (multi-stage builds).
- **Zastosowanie**:
  - Pomaga w efektywnym budowaniu i zarządzaniu obrazami Docker dla różnych komponentów projektu.

---

### **[`_docs/strategia_blue_green_canary.md`](./_docs/strategia_blue_green_canary.md)**

- **Zawartość**:
  - Opisuje strategie wdrożeń w środowisku produkcyjnym:
    - **Blue-Green Deployment**:
      - Równoległe wdrożenie nowej wersji aplikacji obok starej z możliwością bezprzerwowego przełączenia ruchu.
    - **Canary Deployment**:
      - Stopniowe wdrażanie nowej wersji do niewielkiej grupy użytkowników, co pozwala na wczesne wykrycie problemów.
- **Zastosowanie**:
  - Minimalizowanie ryzyka podczas wdrożeń nowych wersji aplikacji dla systemu zarządzającego rojem dronów.
  - Optymalizacja procesów CI/CD.

---

### **[`_docs/readme.md`](./_docs/readme.md)**

- **Zawartość**:
  - Ogólny opis projektu, jego **cele** i **architekturę**.
  - Szczegółowe omówienie kluczowych elementów:
    - **Symulacja roju dronów** za pomocą kontenerów Docker.
    - **Komunikacja** między dronami z wykorzystaniem protokołu MQTT lub DDS.
    - **Wdrożenie** w środowisku Kubernetes.
    - **Monitoring** i integracja z pipeline CI/CD.
- **Zastosowanie**:
  - Punkt wyjścia do zrozumienia projektu.
  - Przewodnik dla nowych użytkowników i deweloperów.

---

## Podsumowanie

Projekt łączy konteneryzację, orkiestrację Kubernetes oraz komunikację MQTT do symulacji i zarządzania rojem dronów. System jest modularny, skalowalny i umożliwia rozbudowę o dodatkowe funkcje, takie jak optymalizacja wielokryterialna czy analiza danych w czasie rzeczywistym.
