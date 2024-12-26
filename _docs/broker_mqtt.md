# Broker MQTT w Projekcie Symulacji Rojów Dronów

## Spis Treści

1. [Wprowadzenie do MQTT](#1-wprowadzenie-do-mqtt)
2. [Rola Brokera MQTT](#2-rola-brokera-mqtt)
   - [Zalety Komunikacji opartej na MQTT](#zalety-komunikacji-opartej-na-mqtt)
3. [Konfiguracja Brokera w Kubernetes](#3-konfiguracja-brokera-w-kubernetes)
   - [Przykład Deployment dla Mosquitto](#31-przykład-deployment-dla-mosquitto)
   - [Przykład Service dla Mosquitto](#32-przykład-service-dla-mosquitto)
   - [Konfiguracja TLS/mTLS](#33-konfiguracja-tlsmtls)
4. [Przykłady Topiców MQTT](#4-przykłady-topiców-mqtt)
5. [Scenariusze Użycia](#5-scenariusze-użycia)
   - [Przepływ Danych](#51-przepływ-danych)
6. [Najlepsze Praktyki](#6-najlepsze-praktyki)
   - [Bezpieczeństwo](#61-bezpieczeństwo)
   - [Zarządzanie Połączeniami](#62-zarządzanie-połączeniami)
   - [Monitorowanie](#63-monitorowanie)

---

## 1. Wprowadzenie do MQTT

**MQTT (Message Queuing Telemetry Transport)** to lekki protokół komunikacyjny oparty na modelu publikacji-subskrypcji. Jest szeroko stosowany w projektach IoT (Internet of Things) i systemach rozproszonych ze względu na:

- **Niskie zużycie zasobów** – idealne dla urządzeń z ograniczonymi możliwościami obliczeniowymi.
- **Niskie opóźnienia** – zapewnia szybką transmisję danych.
- **Asynchroniczność** – umożliwia niezależną komunikację między urządzeniami bez konieczności bezpośredniego połączenia.
- **Elastyczność** – obsługuje różne poziomy QoS (Quality of Service).

MQTT jest szczególnie użyteczny w systemach, gdzie ważna jest niezawodność i efektywność komunikacji, takich jak symulacje roju dronów.

---

## 2. Rola Brokera MQTT

Broker MQTT działa jako **centralny punkt komunikacyjny**, który pośredniczy między dronami a innymi komponentami systemu. Poniżej przedstawiono główne zadania brokera MQTT:

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

### Opis Roli Brokera MQTT

1. **Drony** publikują swoje dane (np. pozycję) na dedykowanych *topicach* MQTT.
2. **Broker MQTT** odbiera te dane i przekazuje je do **Aggregatora** poprzez subskrypcję MQTT.
3. **Aggregator** przetwarza dane i przekazuje je dalej do innych komponentów systemu, takich jak **Aggregator API** i **System AI (ML)**.

### Zalety Komunikacji opartej na MQTT

1. **Luźne powiązanie komponentów** – drony nie muszą znać adresów innych usług.
2. **Skalowalność** – łatwo można dodać nowe drony lub usługi bez zmiany istniejącej konfiguracji.
3. **Niezawodność** – dzięki różnym poziomom QoS można dostosować niezawodność transmisji.
4. **Asynchroniczność** – komponenty działają niezależnie, co poprawia wydajność systemu.

---

## 3. Konfiguracja Brokera w Kubernetes

Broker MQTT w projekcie **Laboratory Swarm** jest implementowany za pomocą **Mosquitto**, popularnego open-source'owego brokera MQTT. Poniżej znajduje się szczegółowy opis konfiguracji brokera w środowisku Kubernetes.

### 3.1. Przykład Deployment dla Mosquitto

Plik `mosquitto-deployment.yaml` definiuje **Deployment** dla brokera Mosquitto:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto-deployment
  labels:
    app: mosquitto
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mosquitto
  template:
    metadata:
      labels:
        app: mosquitto
    spec:
      containers:
      - name: mosquitto
        image: eclipse-mosquitto:latest
        ports:
        - containerPort: 1883
        volumeMounts:
        - name: mosquitto-config
          mountPath: /mosquitto/config
      volumes:
      - name: mosquitto-config
        configMap:
          name: mosquitto-config
```

#### Znaczenie Parametrów

- **`replicas`**: Liczba replik brokera. Można ją skalować w zależności od obciążenia.
- **`image`**: Używany obraz kontenera (`eclipse-mosquitto`), oficjalny obraz brokera Mosquitto.
- **`ports`**: Port 1883, standardowy port dla MQTT.
- **`volumeMounts`**: Montowanie pliku konfiguracyjnego z ConfigMap do kontenera.
- **`volumes`**: Definicja woluminu `mosquitto-config`, który jest mapowany do ConfigMap o nazwie `mosquitto-config`.

### 3.2. Przykład Service dla Mosquitto

Plik `mosquitto-service.yaml` definiuje **Service**, który eksponuje broker MQTT w klastrze Kubernetes:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mqtt-service
spec:
  selector:
    app: mosquitto
  ports:
    - protocol: TCP
      port: 1883
      targetPort: 1883
  type: ClusterIP
```

#### Znaczenie Parametrów

- **`selector`**: Wybiera pody z etykietą `app: mosquitto`.
- **`ports`**: Definiuje port, na którym usługa jest dostępna (1883), oraz port docelowy w kontenerze.
- **`type`**: `ClusterIP` oznacza, że usługa jest dostępna tylko wewnątrz klastra Kubernetes.

### 3.3. Konfiguracja TLS/mTLS

Aby zapewnić **bezpieczeństwo komunikacji** między dronami a brokerem MQTT, konfigurujemy TLS/mTLS. Poniżej znajduje się przykład konfiguracji pliku `mosquitto.conf`:

```conf
# mosquitto.conf

# Ogólne ustawienia
persistence true
persistence_location /mosquitto/data/
log_dest stdout

# Ustawienia TLS
listener 8883
cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
tlsv1.2

# Ustawienia autoryzacji
allow_anonymous false
password_file /mosquitto/config/passwordfile
acl_file /mosquitto/config/aclfile
```

#### Wyjaśnienie Konfiguracji

- **`listener 8883`**: Konfiguruje brokera do nasłuchiwania na porcie 8883 (standardowy port dla MQTT z TLS).
- **`cafile`**, **`certfile`**, **`keyfile`**: Ścieżki do certyfikatów TLS/mTLS.
- **`tlsv1.2`**: Wymusza użycie TLS w wersji 1.2.
- **`allow_anonymous false`**: Wyłącza anonimowe połączenia, wymagając uwierzytelnienia.
- **`password_file`**: Ścieżka do pliku z hasłami użytkowników.
- **`acl_file`**: Ścieżka do pliku z regułami ACL (Access Control List).

#### Dodanie ConfigMap dla Konfiguracji Mosquitto

Plik `mosquitto-configmap.yaml` definiuje **ConfigMap** zawierający plik konfiguracyjny oraz certyfikaty:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mosquitto-config
data:
  mosquitto.conf: |
    # zawartość mosquitto.conf
  ca.crt: |
    -----BEGIN CERTIFICATE-----
    # certyfikat CA
    -----END CERTIFICATE-----
  server.crt: |
    -----BEGIN CERTIFICATE-----
    # certyfikat serwera
    -----END CERTIFICATE-----
  server.key: |
    -----BEGIN PRIVATE KEY-----
    # klucz prywatny serwera
    -----END PRIVATE KEY-----
  passwordfile: |
    # plik z hasłami użytkowników
    user1:password1
    user2:password2
  aclfile: |
    # plik ACL
    user user1
    topic readwrite drones/+/position
    user user2
    topic read drones/+/status
```

#### Wyjaśnienie ConfigMap

- **`mosquitto.conf`**: Plik konfiguracyjny brokera MQTT.
- **`ca.crt`**, **`server.crt`**, **`server.key`**: Certyfikaty TLS/mTLS.
- **`passwordfile`**: Definicje użytkowników i ich haseł.
- **`aclfile`**: Definicje reguł dostępu dla użytkowników.

---

## 4. Przykłady Topiców MQTT

W projekcie **Laboratory Swarm** wykorzystywane są następujące *topiki* MQTT do komunikacji między dronami a innymi komponentami systemu:

### 4.1. Publikacja Pozycji Drona

```
drones/{drone_id}/position
```

**Przykładowy payload**:

```json
{
  "x": 10,
  "y": 20,
  "battery": 95
}
```

### 4.2. Publikacja Statusu Drona

```
drones/{drone_id}/status
```

**Przykładowy payload**:

```json
{
  "status": "active",
  "speed": 5.5
}
```

### 4.3. Subskrypcja dla Agregatora

Aggregator subskrybuje topiki używając symbolu wieloznacznego `+`:

```
drones/+/position
drones/+/status
```

---

## 5. Scenariusze Użycia

### 5.1. Przepływ Danych

Poniższy diagram ASCII ilustruje **przepływ danych** w systemie:

```
[Drony - Pody]
     |
     | MQTT Publish (drones/123/position)
     v
[Broker MQTT (Mosquitto)]
     |
     | MQTT Subscribe (drones/+/position)
     v
[Aggregator]
     |
     | Przetworzone dane
     v
[Aggregator API]
     |
     | REST API Call (GET /api/drones/123/status)
     v
[Użytkownik/Zewnętrzna Aplikacja]
```

#### Opis Przepływu Danych

1. **Dron** o ID `123` publikuje dane pozycji na topik `drones/123/position`.
2. **Broker MQTT** odbiera te dane i przesyła je do **Aggregatora**, który subskrybuje topiki z użyciem symbolu wieloznacznego `+`.
3. **Aggregator** przetwarza otrzymane dane (np. filtruje, wykrywa anomalie) i przekazuje je do **Aggregator API**.
4. **Aggregator API** udostępnia przetworzone dane poprzez interfejs REST, umożliwiając dostęp użytkownikom lub zewnętrznym aplikacjom.

---

## 6. Najlepsze Praktyki

### 6.1. Bezpieczeństwo

1. **Używaj Autoryzacji i TLS do Szyfrowania Połączeń**
   - Konfiguruj TLS/mTLS, aby zapewnić szyfrowanie komunikacji między dronami a brokerem MQTT.
   - Wyłącz anonimowe połączenia (`allow_anonymous false`) i wymagaj uwierzytelnienia użytkowników.

2. **Konfiguracja ACL (Access Control List)**
   - Definiuj reguły dostępu w pliku `aclfile`, aby kontrolować, które użytkownicy mogą publikować lub subskrybować określone topiki.

3. **Zarządzanie Certyfikatami**
   - Regularnie aktualizuj certyfikaty TLS/mTLS i zarządzaj ich ważnością.
   - Przechowuj certyfikaty w bezpieczny sposób, np. korzystając z Kubernetes Secrets lub HashiCorp Vault.

### 6.2. Zarządzanie Połączeniami

1. **Ustaw Limity Połączeń**
   - Konfiguruj limit liczby jednoczesnych połączeń w `mosquitto.conf`, aby zapobiegać przeciążeniu brokera.

2. **Monitorowanie Zużycia Zasobów**
   - Monitoruj zużycie CPU, pamięci i liczby połączeń do brokera MQTT, aby zapewnić jego wydajność i stabilność.

3. **Zarządzanie Sesjami MQTT**
   - Konfiguruj sesje trwałe (`persistent_sessions true`) dla klientów, aby zapewnić niezawodność dostarczania wiadomości.

### 6.3. Monitorowanie

1. **Monitorowanie Stanu Brokera MQTT za pomocą Prometheus i Grafana**
   - Zbieraj metryki z brokera Mosquitto (np. liczba połączeń, liczba wiadomości) i wizualizuj je w Grafanie.
   
   **Przykładowa konfiguracja Prometheus:**
   
   ```yaml
   scrape_configs:
     - job_name: 'mosquitto'
       static_configs:
         - targets: ['mqtt-service:1883']
   ```

2. **Analiza Logów przy Pomocy ELK Stack**
   - Centralizuj logi brokera MQTT w Elasticsearch, przetwarzaj je za pomocą Logstash i wizualizuj w Kibana.

3. **Alerty i Powiadomienia**
   - Skonfiguruj alerty w Prometheusie i Grafanie, aby być powiadamianym o nietypowych wzorcach zachowań brokera MQTT, takich jak nagły wzrost liczby połączeń.

---

## Podsumowanie

Broker MQTT jest kluczowym elementem komunikacji w projekcie symulacji roju dronów. Zapewnia niezawodną, asynchroniczną wymianę danych pomiędzy dronami a innymi komponentami systemu. Dzięki odpowiedniej konfiguracji, zabezpieczeniom i monitorowaniu, broker MQTT umożliwia efektywne zarządzanie danymi telemetrycznymi, co jest fundamentem dla dalszej analizy i optymalizacji przez system AI.

---

**Plik:** `_docs/broker_mqtt.md`

[Powrót do głównej dokumentacji](../README.MD)

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

Mam nadzieję, że ta rozbudowana dokumentacja spełnia Twoje oczekiwania. Jeśli potrzebujesz dodatkowych informacji lub dalszych poprawek, proszę daj znać!