# Symulacja Rojów Dronów w Architekturze Kontenerowej

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

Projekt symulacji roju dronów ma na celu zaprezentowanie podejścia do zarządzania wieloma urządzeniami IoT w architekturze kontenerowej i chmurowej. Integruje on konteneryzację ([Docker](#2-zaawansowany-kurs-docker)), orkiestrację ([Kubernetes](#3-kubernetes---orkiestracja-kontenerow)), komunikację ([MQTT](#komunikacja-dron%C3%B3w)), pipeline'y CI/CD, monitoring ([Prometheus i Grafana](#monitoring-i-ci-cd)) oraz strategie wdrożeń ([Blue-Green, Canary](#strategia-blue-green-i-canary)), tworząc kompletne i skalowalne środowisko dla roju dronów.

---

## Spis Treści

1. [Wprowadzenie](#1-wprowadzenie)
2. [Zaawansowany Kurs Docker](#2-zaawansowany-kurs-docker)
3. [Kubernetes – Orkiestracja Kontenerów](#3-kubernetes---orkiestracja-kontenerow)
4. [Docker w Chmurach Hybrydowych](#4-docker-w-chmurach-hybrydowych)
5. [Zarządzanie Rojem Dronów w Kubernetes](#5-zarz%C4%85dzanie-rojem-dron%C3%B3w-w-kubernetes)
6. [Opis Projektu](#6-opis-projektu)
    - [Kontekst i Motywacja](#kontekst-i-motywacja)
    - [Główne Cele Projektu](#g%C5%82%C3%B3wne-cele-projektu)
    - [Architektura Systemu](#architektura-systemu)
        - [Poziom 1: Fundamenty Komunikacji i Orkiestracji](#poziom-1-fundamenty-komunikacji-i-orkiestracji)
        - [Poziom 2: Drony i Generowanie Danych](#poziom-2-drony-i-generowanie-danych)
        - [Poziom 3: Agregacja Danych i API](#poziom-3-agregacja-danych-i-api)
        - [Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD](#poziom-4-narz%C4%99dzia-wspomagaj%C4%85ce-monitoring-ci-cd)
        - [Poziom 5: Bezpieczeństwo i Izolacja](#poziom-5-bezpiecze%C5%84stwo-i-izolacja)
    - [Integracja i Przepływ Danych](#integracja-i-przep%C5%82yw-danych)
    - [Korzyści z Implementacji](#korzy%C5%9Bci-z-implementacji)
    - [Wyzwania i Rozwiązania](#wyzwania-i-rozwiazania)
    - [Przyszłe Rozszerzenia](#przysz%C5%BCe-rozszerzenia)
7. [Podsumowanie](#7-podsumowanie)
8. [Informacje z Istniejących Plików](#8-informacje-z-istniejących-plikow)
9. [Odnośniki](#9-odno%C5%9Bniki)

---

## 1. Wprowadzenie

Witaj w dokumentacji dotyczącej zarządzania ekosystemem MQTT (Broker & Aggregator) w środowisku Docker i Kubernetes. Projekt ten koncentruje się na symulacji roju dronów, gdzie każdy dron jest traktowany jako niezależny kontener. Dzięki temu podejściu możliwe jest autonomiczne działanie każdego drona oraz efektywna komunikacja z innymi elementami systemu.

### **Dlaczego MQTT i Kubernetes?**

- **MQTT (Message Queuing Telemetry Transport):** Lekki protokół komunikacyjny idealny dla środowisk IoT, takich jak roje dronów. Umożliwia efektywną wymianę danych pomiędzy dużą liczbą urządzeń.
- **Kubernetes:** Potężna platforma do orkiestracji kontenerów, która zapewnia skalowalność, niezawodność oraz automatyzację zarządzania aplikacjami kontenerowymi.

### **Cel Dokumentacji**

Dokumentacja jest podzielona na dwie główne części:

- **`README.MD`:** Ogólny opis projektu, jego celów oraz struktury.
- **`_docs/readme.md`:** Szczegółowe informacje dotyczące implementacji, konfiguracji i zarządzania poszczególnymi komponentami projektu.

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

### **Kontekst i Motywacja**

W erze dynamicznie rozwijającego się Internetu Rzeczy (IoT), roje dronów stają się coraz bardziej istotne w różnych zastosowaniach, takich jak monitorowanie środowiska, inspekcje infrastruktury czy operacje ratunkowe. Zarządzanie taką liczbą autonomicznych urządzeń wymaga zaawansowanych narzędzi i technologii, które umożliwią efektywną komunikację, skalowalność oraz niezawodność systemu.

### **Główne Cele Projektu**

Projekt ma na celu stworzenie skalowalnego i elastycznego systemu do zarządzania rojem dronów, wykorzystując technologię konteneryzacji ([Docker](#2-zaawansowany-kurs-docker)) oraz orkiestrację kontenerów ([Kubernetes](#3-kubernetes---orkiestracja-kontenerow)). Dzięki integracji protokołu MQTT, system umożliwia efektywną wymianę danych pomiędzy dronami a centralnymi komponentami, takimi jak agregator danych i interfejsy API.

### **Architektura Systemu**

Architektura systemu została zaprojektowana w celu zapewnienia modularności, skalowalności i niezawodności. Składa się z następujących kluczowych komponentów:

#### Poziom 1: Fundamenty Komunikacji i Orkiestracji

**MQTT Broker** (`server/mqtt/`)
- *Rola:* Centralny punkt komunikacji w stylu publish-subscribe.
- *Zasoby:*
  - [`mosquitto.conf`](./_docs/broker_mqtt.md#mosquitto-conf) – konfiguracja brokera MQTT (Mosquitto).
  - [`mosquitto-deployment.yaml`](./_docs/broker_mqtt.md#mosquitto-deploymentyaml), [`mosquitto-service.yaml`](./_docs/broker_mqtt.md#mosquitto-serviceyaml) – wdrożenie brokera do klastra Kubernetes.
- *Idea:* Broker MQTT umożliwia luźne powiązanie dronów (publisherów) z agregatorem (subscriberem) i innymi komponentami.

**Kubernetes i Konteneryzacja**
- *Rola:* Orkiestracja wszystkich usług, ich skalowanie, resiliencja, load balancing.
- *Zasoby:* Manifesty YAML (deployment, service, statefulset) dla każdego komponentu.
- *Idea:* Kubernetes zapewnia infrastrukturę do uruchamiania i zarządzania wieloma dronami-kontenerami, brokerem MQTT, agregatorem i API.

#### Poziom 2: Drony i Generowanie Danych

**Drony** (`drones/`)
- *Rola:* Autonomiczne generowanie danych o stanie drona (pozycja, bateria) i publikacja ich do MQTT.
- *Pliki i Konfiguracja:*
  - [`drone_logic.py`](./_docs/drones_component.md#drone_logicpy) – Logika generowania danych i komunikacji z brokerem.
  - [`Dockerfile`](./_docs/drones_component.md#dockerfile), [`requirements.txt`](./_docs/drones_component.md#requirementstxt) – Budowa obrazu kontenera drona.
  - [`drone-deployment.yaml`](./_docs/drones_component.md#drone-deploymentyaml), [`drone-service.yaml`](./_docs/drones_component.md#drone-serviceyaml) – Skrypty wdrażające flotę dronów do Kubernetes.
- *Idea:* Każdy dron jest niezależnym podeinem w Kubernetes, który publikuje dane do brokera MQTT na topiki `drones/{drone_id}/position`. Daje to możliwość łatwego skalowania liczby dronów poprzez modyfikację `replicas`.

#### Poziom 3: Agregacja Danych i API

**Agregator** (`aggregator/`)
- *Rola:* Subskrybent wiadomości MQTT publikowanych przez drony. Zbiera dane, przetwarza je i przygotowuje do udostępnienia przez API.
- *Pliki i Konfiguracja:*
  - [`aggregator.py`](./_docs/aggregator_details.md#aggregatorpy) – Kod logiki subskrypcji i przetwarzania danych z topików `drones/+/position`.
  - [`aggregator-deployment.yaml`](./_docs/aggregator_details.md#aggregator-deploymentyaml), [`aggregator-service.yaml`](./_docs/aggregator_details.md#aggregator-serviceyaml) – Wdrożenie agregatora do klastrów Kubernetes.
  - [`Dockerfile`](./_docs/aggregator_details.md#dockerfile), [`requirements.txt`](./_docs/aggregator_details.md#requirementstxt) – Budowa obrazu.
- *Idea:* Agregator to centralny element logiki biznesowej – odbiera dane z roju i umożliwia ich dalszą analizę i magazynowanie.

**Aggregator API** (`aggregator-api/`)
- *Rola:* Interfejs REST do dostępu do przetworzonych danych dronów. Umożliwia zewnętrznym systemom i użytkownikom pobieranie informacji o stanie dronów, wysyłanie komend i zarządzanie rojem.
- *Pliki i Konfiguracja:*
  - [`aggregator_api.py`](./_docs/aggregator_api_details.md#aggregator_apipy) – Kod implementujący REST endpointy (np. `GET /api/drones/{drone_id}/status`).
  - [`aggregator-api-deployment.yaml`](./_docs/aggregator_api_details.md#aggregator-api-deploymentyaml), [`aggregator-api-service.yaml`](./_docs/aggregator_api_details.md#aggregator-api-serviceyaml) – Wdrożenie API do Kubernetes.
  - [`Dockerfile`](./_docs/aggregator_api_details.md#dockerfile), [`requirements.txt`](./_docs/aggregator_api_details.md#requirementstxt) – Obraz kontenera API.
- *Idea:* API tworzy warstwę integracyjną, dzięki której systemy zewnętrzne mają dostęp do aktualnego stanu roju oraz możliwość sterowania dronami.
- *Szczegółowe Wyjaśnienie:* [Dokumentacja Aggregator API](./_docs/aggregator_api_details.md)

#### Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD

**Monitoring i Wizualizacja**
- *Prometheus, Grafana:* Zbierają metryki z dronów, agregatora, API oraz brokera, wizualizując obciążenie, wykorzystanie zasobów, poziom baterii dronów.
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów systemu, wspierając diagnozę i debugowanie.

**CI/CD**
- *Idea:* Automatyczne pipeline’y (GitLab CI, Jenkins, ArgoCD) kompilują i testują kod, budują obrazy Docker, wdrażają je do Kubernetes.
- *Korzyści:* Szybkie reagowanie na zmiany, zwinność w dostarczaniu nowych funkcji, minimalizacja błędów ręcznej konfiguracji.

**Strategie Wdrożeń (Blue-Green, Canary)**
- *Idea:* Bezpieczne aktualizacje pozwalają wdrażać nowe wersje dronów lub agregatora bez przestojów. Stopniowe przełączanie ruchu (canary) lub równoległe utrzymywanie dwóch wersji (blue-green) minimalizuje ryzyko awarii.

#### Poziom 5: Bezpieczeństwo i Izolacja

**RBAC i Network Policies**
- *Idea:* Kubernetes RBAC kontroluje, którzy użytkownicy mogą czytać, pisać czy wdrażać zasoby w klastrze. Network Policies ograniczają komunikację między podami, zapewniając izolację i minimalizując wektory ataku.

**Secrets Management**
- *Idea:* Dane wrażliwe (klucze API, hasła) przechowywane w Kubernetes Secrets, podłączane do podów w sposób bezpieczny. Szyfrowanie TLS dla komunikacji MQTT i API zwiększa poufność i integralność danych.

---

### Integracja i Przepływ Danych

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

### Korzyści z Implementacji

- **Skalowalność:** Możliwość dynamicznego skalowania roju dronów w zależności od potrzeb operacyjnych.
- **Elastyczność:** Modularna architektura umożliwia łatwe dodawanie nowych funkcjonalności oraz integrację z innymi systemami.
- **Niezawodność:** Redundancja oraz automatyczne przywracanie usług zapewniają ciągłość działania systemu.
- **Bezpieczeństwo:** Implementacja RBAC, Network Policies oraz szyfrowanie komunikacji zapewnia wysoki poziom bezpieczeństwa.
- **Monitorowanie i Analiza:** Integracja z Prometheus, Grafana oraz ELK Stack pozwala na bieżące monitorowanie stanu systemu oraz efektywne rozwiązywanie problemów.

---

### Wyzwania i Rozwiązania

- **Złożoność Systemu:** Zarządzanie dużą liczbą dronów w środowisku Kubernetes wymaga zaawansowanej wiedzy i doświadczenia. Dokumentacja szczegółowa w [readme.md](./_docs/readme.md) oraz inne pliki w katalogu `_docs/` pomagają w pokonaniu tej złożoności.
- **Optymalizacja Zasobów:** Efektywne wykorzystanie zasobów chmurowych jest kluczowe dla minimalizacji kosztów. Kubernetes umożliwia precyzyjne zarządzanie zasobami oraz automatyczne skalowanie.
- **Bezpieczeństwo Danych:** Ochrona danych przesyłanych między dronami a centralnymi komponentami jest kluczowa. Szyfrowanie TLS oraz zarządzanie sekretami w Kubernetes zabezpieczają system przed nieautoryzowanym dostępem.

---

### Przyszłe Rozszerzenia

- **Integracja z Modelami AI:** Wprowadzenie algorytmów uczenia maszynowego do analizy danych z dronów, co umożliwi przewidywanie zachowań roju i optymalizację jego działania.
- **Zaawansowane Funkcje Sterowania:** Implementacja bardziej zaawansowanych mechanizmów sterowania dronami, takich jak śledzenie celów, unikanie przeszkód czy koordynacja z innymi rojami.
- **Rozszerzenie Monitoringu:** Dodanie dodatkowych metryk i logów do systemu monitorowania w celu lepszej analizy wydajności i stanu roju dronów.

Aby dowiedzieć się więcej o konkretnych aspektach implementacji, takich jak zaawansowane zarządzanie kontenerami, budowanie obrazów Docker czy orkiestracja za pomocą Kubernetes, zapraszamy do zapoznania się z [szczegółową dokumentacją](./_docs/readme.md).

---

## 7. Podsumowanie

Dokumentacja ta dostarcza kompleksowego przewodnika po zarządzaniu ekosystemem MQTT oraz rojem dronów w środowisku Docker i Kubernetes. Dzięki integracji konteneryzacji, orkiestracji, komunikacji MQTT, automatyzacji CI/CD oraz zaawansowanemu monitorowaniu, system zapewnia skalowalność, elastyczność i niezawodność niezbędną do efektywnego zarządzania dużą liczbą autonomicznych dronów.

### **Kluczowe Zalety Rozwiązania**

- **Skalowalność i Elastyczność:** Dzięki Kubernetes możliwe jest dynamiczne skalowanie liczby dronów w zależności od potrzeb operacyjnych.
- **Autonomia i Redundancja:** Każdy dron działa autonomicznie, co zapewnia ciągłość działania systemu nawet w przypadku awarii poszczególnych jednostek.
- **Efektywna Komunikacja:** MQTT umożliwia szybką i niezawodną wymianę danych pomiędzy dronami a centralnymi komponentami systemu.
- **Bezpieczeństwo:** Implementacja RBAC, Network Policies oraz szyfrowanie danych zapewnia wysoki poziom bezpieczeństwa całego ekosystemu.
- **Monitorowanie i Analiza:** Integracja z Prometheus, Grafana oraz ELK Stack pozwala na bieżące monitorowanie stanu systemu oraz efektywne rozwiązywanie problemów.

Aby dowiedzieć się więcej o konkretnych aspektach implementacji, takich jak zaawansowane zarządzanie kontenerami, budowanie obrazów Docker czy orkiestracja za pomocą Kubernetes, zapraszamy do zapoznania się z wcześniejszymi sekcjami dokumentacji.

---

## 8. Informacje z Istniejących Plików

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

## 9. Odnośniki

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

