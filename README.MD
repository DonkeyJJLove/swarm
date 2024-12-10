## Dokumentacja Zarządzania Ekosystemem MQTT (Broker & Aggregator) w Docker i Kubernetes

### Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)
2. [Zaawansowany Kurs Docker](#2-zaawansowany-kurs-docker)
3. [Kubernetes – Orkiestracja Kontenerów](#3-kubernetes---orkiestracja-kontenerow)
4. [Docker w Chmurach Hybrydowych](#4-docker-w-chmurach-hybrydowych)
5. [Zarządzanie Rojem Dronów w Kubernetes](#5-zarz%C4%85dzanie-rojem-dron%C3%B3w-w-kubernetes)
6. [Opis Projektu](#6-opis-projektu)
7. [Podsumowanie](#7-podsumowanie)

---

## 1. Wprowadzenie

Witaj w dokumentacji dotyczącej zarządzania ekosystemem MQTT (Broker & Aggregator) w środowisku Docker i Kubernetes. Projekt koncentruje się na symulacji roju dronów, gdzie każdy dron jest traktowany jako niezależny kontener. Dzięki temu podejściu możliwe jest autonomiczne działanie każdego drona oraz efektywna komunikacja z innymi elementami systemu.

### **Dlaczego MQTT i Kubernetes?**

- **MQTT (Message Queuing Telemetry Transport)**: Lekki protokół komunikacyjny idealny dla środowisk IoT, takich jak roje dronów. Umożliwia efektywną wymianę danych pomiędzy dużą liczbą urządzeń.
- **Kubernetes**: Potężna platforma do orkiestracji kontenerów, która zapewnia skalowalność, niezawodność oraz automatyzację zarządzania aplikacjami kontenerowymi.

### **Cel Dokumentacji**

Dokumentacja jest podzielona na dwie główne części:

- **`README.MD`**: Ogólny opis projektu, jego celów oraz struktury.
- **`_docs/readme.md`**: Szczegółowe informacje dotyczące implementacji, konfiguracji i zarządzania poszczególnymi komponentami projektu.

Aby przejść do bardziej szczegółowej dokumentacji, kliknij [tutaj](./_docs/readme.md).

---

## 2. Zaawansowany Kurs Docker

Aby lepiej zrozumieć zarządzanie kontenerami w projekcie, zalecamy zapoznanie się z [Zaawansowanym Kursem Docker](./_docs/readme.md#2-zaawansowany-kurs-docker).

---

## 3. Kubernetes – Orkiestracja Kontenerów

Kubernetes jest kluczowym elementem orkiestracji kontenerów w naszym projekcie. Szczegółowe informacje znajdziesz w sekcji [Kubernetes – Orkiestracja Kontenerów](./_docs/readme.md#3-kubernetes---orkiestracja-kontenerow).

---

## 4. Docker w Chmurach Hybrydowych

Docker w połączeniu z chmurami hybrydowymi umożliwia elastyczne zarządzanie zasobami. Dowiedz się więcej w [Sekcji Docker w Chmurach Hybrydowych](./_docs/readme.md#4-docker-w-chmurach-hybrydowych).

---

## 5. Zarządzanie Rojem Dronów w Kubernetes

Zarządzanie dużą liczbą dronów wymaga zaawansowanych technik orkiestracji. Przeczytaj więcej w [Zarządzanie Rojem Dronów w Kubernetes](./_docs/readme.md#5-zarz%C4%85dzanie-rojem-dron%C3%B3w-w-kubernetes).

---

## 6. Opis Projektu

Opis projektu, jego idea, koncepcja oraz integracja komponentów znajduje się w [Sekcji Opis Projektu](./_docs/readme.md#6-opis-projektu).

---

## 7. Podsumowanie

Dokumentacja ta dostarcza kompleksowego przewodnika po zarządzaniu ekosystemem MQTT oraz rojem dronów w środowisku Docker i Kubernetes. Dla bardziej szczegółowych informacji, odwiedź [Dokumentację Szczegółową](./_docs/readme.md).

---

**Pliki Dokumentacji:**

- [_docs/readme.md](./_docs/readme.md)
- [_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md)
- [_docs/aggregator_api_details.md](./_docs/aggregator_api_details.md)
- [_docs/aggregator_details.md](./_docs/aggregator_details.md)
- [_docs/broker_mqtt.md](./_docs/broker_mqtt.md)
- [_docs/drones_component.md](./_docs/drones_component.md)
- [_docs/idea-i-koncepcja.md](./_docs/idea-i-koncepcja.md)
- [_docs/strategia_blue_green_canary.md](./_docs/strategia_blue_green_canary.md)

---

[Powrót do głównej dokumentacji](./README.MD)

---

## Idea i Koncepcja

W centrum projektu znajduje się symulacja roju dronów działających w środowisku chmurowym i kontenerowym. Każdy dron funkcjonuje jako autonomiczny kontener, komunikujący się z pozostałymi elementami systemu za pomocą protokołu MQTT. Wspólna komunikacja oparta o model publikacja-subskrypcja (publish-subscribe) zapewnia luźne powiązanie komponentów, elastyczność i skalowalność.

### **Dlaczego Roj Dronów?**

- **Efektywność Operacyjna**: Roj dronów umożliwia jednoczesne wykonywanie wielu zadań, co zwiększa efektywność operacyjną w porównaniu do pojedynczych jednostek.
- **Redundancja**: W przypadku awarii jednego drona, pozostałe jednostki mogą przejąć jego zadania, co zwiększa niezawodność systemu.
- **Skalowalność**: Możliwość łatwego dodawania lub usuwania dronów w zależności od potrzeb operacyjnych.

### **Główne założenia:**

1. **Autonomiczne Kontenery/Drony** – Każdy dron jest kontenerem, generującym dane o swojej pozycji, stanie baterii i innych parametrach.
2. **Komunikacja MQTT** – Drony publikują dane do brokera MQTT, a inne komponenty, takie jak agregator, subskrybują te informacje.
3. **Architektura Kontenerowa w Kubernetes** – Całość wdrożenia opiera się na orkiestracji Kubernetes, zapewniając skalowalność, niezawodność, elastyczność i prostotę zarządzania.
4. **Agregacja i Dostęp do Danych** – Agregator zbiera dane z dronów, przetwarza je i udostępnia zewnętrznemu światu poprzez REST API (aggregator-api), co umożliwia zarządzanie rojem i analizę danych.
5. **Monitorowanie, CI/CD, Bezpieczeństwo** – Projekt uwzględnia pipeline’y CI/CD, monitoring (Prometheus, Grafana), logowanie (ELK), strategie wdrożeń (Blue-Green, Canary), bezpieczeństwo (RBAC, Network Policies, szyfrowanie).

---

## Poziomy Architektoniczne i Komponenty

### Poziom 1: Fundamenty Komunikacji i Orkiestracji

**MQTT Broker** (`server/mqtt/`)  
- *Rola:* Centralny punkt komunikacji w stylu publish-subscribe.  
- *Zasoby:*  
  - `mosquitto.conf` – konfiguracja brokera MQTT (Mosquitto).  
  - `mosquitto-deployment.yaml`, `mosquitto-service.yaml` – wdrożenie brokera do klastra Kubernetes.  
- *Idea:* Broker MQTT umożliwia luźne powiązanie dronów (publisherów) z agregatorem (subscriberem) i innymi komponentami.

**Kubernetes i Konteneryzacja**  
- *Rola:* Orkiestracja wszystkich usług, ich skalowanie, resiliencja, load balancing.  
- *Zasoby:* Manifesty YAML (deployment, service, statefulset) dla każdego komponentu.  
- *Idea:* Kubernetes zapewnia infrastrukturę do uruchamiania i zarządzania wieloma dronami-kontenerami, brokerem MQTT, agregatorem i API.

---

### Poziom 2: Drony i Generowanie Danych

**Drony** (`drones/`)  
- *Rola:* Autonomiczne generowanie danych o stanie drona (pozycja, bateria) i publikacja ich do MQTT.  
- *Pliki i Konfiguracja:*  
  - `drone_logic.py` – Logika generowania danych i komunikacji z brokerem.  
  - `Dockerfile`, `requirements.txt` – Budowa obrazu kontenera drona.  
  - `drone-deployment.yaml`, `drone-service.yaml` – Skrypty wdrażające flotę dronów do Kubernetes.  
- *Idea:* Każdy dron jest niezależnym podeinem w Kubernetes, który publikuje dane do brokera MQTT na topiki `drones/{drone_id}/position`. Daje to możliwość łatwego skalowania liczby dronów poprzez modyfikację `replicas`.

---

### Poziom 3: Agregacja Danych i API

**Agregator** (`aggregator/`)  
- *Rola:* Subskrybent wiadomości MQTT publikowanych przez drony. Zbiera dane, przetwarza je i przygotowuje do udostępnienia przez API.  
- *Pliki i Konfiguracja:*  
  - `aggregator.py` – Kod logiki subskrypcji i przetwarzania danych z topików `drones/+/position`.  
  - `aggregator-deployment.yaml`, `aggregator-service.yaml` – Wdrożenie agregatora do klastrów Kubernetes.  
  - `Dockerfile`, `requirements.txt` – Budowa obrazu.  
- *Idea:* Agregator to centralny element logiki biznesowej – odbiera dane z roju i umożliwia ich dalszą analizę i magazynowanie.

**Aggregator API** (`aggregator-api/`)  
- *Rola:* Interfejs REST do dostępu do przetworzonych danych dronów. Umożliwia zewnętrznym systemom i użytkownikom pobieranie informacji o stanie dronów, wysyłanie komend i zarządzanie rojem.  
- *Pliki i Konfiguracja:*  
  - `aggregator_api.py` – Kod implementujący REST endpointy (np. `GET /api/drones/{drone_id}/status`).  
  - `aggregator-api-deployment.yaml`, `aggregator-api-service.yaml` – Wdrożenie API do Kubernetes.  
  - `Dockerfile`, `requirements.txt` – Obraz kontenera API.  
- *Idea:* API tworzy warstwę integracyjną, dzięki której systemy zewnętrzne mają dostęp do aktualnego stanu roju oraz możliwość sterowania dronami.

---

### Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD

**Monitoring i Wizualizacja**  
- *Prometheus, Grafana:* Zbierają metryki z dronów, agregatora, API oraz brokera, wizualizując obciążenie, wykorzystanie zasobów, poziom baterii dronów.  
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów systemu, wspierając diagnozę i debugowanie.

**CI/CD**  
- *Idea:* Automatyczne pipeline’y (GitLab CI, Jenkins, ArgoCD) kompilują i testują kod, budują obrazy Docker, wdrażają je do Kubernetes.  
- *Korzyści:* Szybkie reagowanie na zmiany, zwinność w dostarczaniu nowych funkcji, minimalizacja błędów ręcznej konfiguracji.

**Strategie Wdrożeń (Blue-Green, Canary)**  
- *Idea:* Bezpieczne aktualizacje pozwalają wdrażać nowe wersje dronów lub agregatora bez przestojów. Stopniowe przełączanie ruchu (canary) lub równoległe utrzymywanie dwóch wersji (blue-green) minimalizuje ryzyko awarii.

---

### Poziom 5: Bezpieczeństwo i Izolacja

**RBAC i Network Policies**  
- *Idea:* Kubernetes RBAC kontroluje, którzy użytkownicy mogą czytać, pisać czy wdrażać zasoby w klastrze. Network Policies ograniczają komunikację między podami, zapewniając izolację i minimalizując wektory ataku.

**Secrets Management**  
- *Idea:* Dane wrażliwe (klucze API, hasła) przechowywane w Kubernetes Secrets, podłączane do podów w sposób bezpieczny. Szyfrowanie TLS dla komunikacji MQTT i API zwiększa poufność i integralność danych.

---

## Integracja i Przepływ

1. **Drony** publikują dane o swojej pozycji i stanie przez MQTT:
   - **MQTT Broker** (Mosquitto) odbiera i przechowuje te informacje tymczasowo.
   
2. **Agregator** subskrybuje temat `drones/+/position`:
   - Przetwarza dane i agreguje je, tworząc jednolitą bazę informacji o stanie całego roju.
   
3. **Aggregator API** zapewnia interfejs REST:
   - Użytkownicy i zewnętrzne systemy pobierają informacje (`GET /api/drones/...`) lub wysyłają komendy sterujące do dronów.
   
4. **Monitorowanie i Logi** śledzą cały przepływ:
   - Prometheus i Grafana zbierają metryki.
   - ELK pozwala na analizę logów.
   
5. **CI/CD i Skalowalność**:
   - W przypadku zwiększonego obciążenia (np. potrzeby większej liczby dronów), Kubernetes umożliwia skalowanie replik.
   - CI/CD zapewnia szybkie wprowadzenie poprawek i nowych funkcjonalności.
   
6. **Bezpieczeństwo** chroni cały ekosystem:
   - RBAC ogranicza dostęp.
   - Secrets i szyfrowane połączenia chronią wrażliwe dane.

---

## Rola dla Modeli AI

Ten opis służy jako główny punkt odniesienia dla modeli AI, które mają operować na kodzie i logice projektu. Dzięki niemu:

- **Modele językowe** mogą łatwiej zrozumieć kontekst, rolę i powiązania między elementami kodu.  
- **Generatory kodu** opierają się na wspólnych założeniach architektonicznych, mając mapę połączeń i zrozumienie, gdzie wdrożyć nowe funkcjonalności.  
- **Analityczne modele AI** łatwiej identyfikują punkty wejścia do optymalizacji (np. poprawa wydajności MQTT, zwiększenie bezpieczeństwa) i wiedzą, gdzie ingerować w kod lub konfigurację.

---

## Podsumowanie

Przedstawiona architektura to kompleksowa platforma symulująca rozproszony system dronów zarządzanych i monitorowanych w środowisku chmurowym. Opiera się na konteneryzacji, komunikacji MQTT, orkiestracji Kubernetes, agregacji danych i udostępnianiu ich przez API. Zapewnia skalowalność, elastyczność, bezpieczeństwo, a także instrumenty do integracji z modelami AI, które mogą rozwijać i optymalizować kod na podstawie klarownej mapy funkcjonalnej i architektonicznej.

### **Kluczowe Zalety Rozwiązania**

- **Skalowalność i Elastyczność**: Dzięki Kubernetes możliwe jest dynamiczne skalowanie liczby dronów w zależności od potrzeb operacyjnych.
- **Autonomia i Redundancja**: Każdy dron działa autonomicznie, co zapewnia ciągłość działania systemu nawet w przypadku awarii poszczególnych jednostek.
- **Efektywna Komunikacja**: MQTT umożliwia szybką i niezawodną wymianę danych pomiędzy dronami a centralnymi komponentami systemu.
- **Bezpieczeństwo**: Implementacja RBAC, Network Policies oraz szyfrowanie danych zapewnia wysoki poziom bezpieczeństwa całego ekosystemu.
- **Monitorowanie i Analiza**: Integracja z Prometheus, Grafana oraz ELK Stack pozwala na bieżące monitorowanie stanu systemu oraz efektywne rozwiązywanie problemów.

Aby dowiedzieć się więcej o konkretnych aspektach implementacji, takich jak zaawansowane zarządzanie kontenerami, budowanie obrazów Docker czy orkiestracja za pomocą Kubernetes, zapraszamy do zapoznania się z wcześniejszymi sekcjami dokumentacji.

---

## Informacje z Istniejących Plików

Poniżej znajduje się tabela zawierająca odnośniki do istniejących dokumentów w katalogu `_docs/` oraz ich opisy:

| **Dokument**                                       | **Link**                                                                                   | **Opis**                                                         |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Budowanie i zarządzanie obrazami Dockerowymi       | [budowanie-i-zarządzanie-obrazami-dockerowymi.md](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md) | Budowanie i zarządzanie obrazami Docker (multi-stage builds, versioning, repozytoria). |
| Strategie wdrożeń Blue-Green i Canary             | [strategia_blue_green_canary.md](./_docs/strategia_blue_green_canary.md)                  | Strategie wdrożeń Blue-Green i Canary.                          |
| Ogólny opis projektu                               | [readme.md](./_docs/readme.md)                                                            | Ogólny opis projektu: symulacja roju, komunikacja MQTT, wdrożenie, monitoring, CI/CD. |
| Dokumentacja Brokera MQTT                          | [broker_mqtt.md](./_docs/broker_mqtt.md)                                                  | Szczegółowa Dokumentacja Brokera MQTT.                           |
| Szczegółowy opis agregatora                        | [aggregator_details.md](./_docs/aggregator_details.md)                                    | Szczegółowy opis agregatora.                                     |
| Szczegółowy opis Aggregator API                    | [aggregator_api_details.md](./_docs/aggregator_api_details.md)                            | Szczegółowy opis Aggregator API.                                 |
| Dokumentacja Bazy Danych                           | [database.md](./_docs/database.md)                                                        | Dokumentacja Bazy Danych.                                        |
| Dokumentacja Frontend                               | [frontend.md](./_docs/frontend.md)                                                        | Dokumentacja Frontend.                                            |

---

## Odnośniki

- [Wprowadzenie do Docker i Kubernetes - Chmury Hybrydowe](./_docs/readme.md)
- [Kubernetes – Orkiestracja Kontenerów](#3-kubernetes---orkiestracja-kontenerow)
- [Docker w Chmurach Hybrydowych](#4-docker-w-chmurach-hybrydowych)
- [Strategia Blue-Green i Canary](./_docs/strategia_blue_green_canary.md)
- [Budowanie i Zarządzanie Obrazami Dockerowymi](./_docs/budowanie-i-zarządzanie-obrazami-dockerowymi.md)
- [Ogólny Opis Projektu](./_docs/readme.md#6-opis-projektu)
- [Dokumentacja Brokera MQTT](./_docs/broker_mqtt.md)
- [Szczegółowy opis agregatora](./_docs/aggregator_details.md)
- [Szczegółowy opis Aggregator API](./_docs/aggregator_api_details.md)
- [Dokumentacja Bazy Danych](./_docs/database.md)
- [Dokumentacja Frontend](./_docs/frontend.md)

