# **SWARM**
## **Spis Treści**

1. [Wprowadzenie](#1-wprowadzenie)
2. [Zaawansowany Kurs Docker](#2-zaawansowany-kurs-docker)
    - [2.1 Podstawowe Komendy Docker (Szybkie Przypomnienie)](#21-podstawowe-komendy-docker-szybkie-przypomnienie)
    - [2.2 Zarządzanie Kontenerami](#22-zarz%C4%85dzanie-kontenerami)
    - [2.3 Budowanie i Optymalizacja Obrazów](#23-budowanie-i-optymalizacja-obra%C5%BC%C3%B3w)
        - [2.3.1 Przykładowy `Dockerfile`](#231-przyk%C5%82adowy-dockerfile)
        - [2.3.2 Budowanie Obrazu](#232-budowanie-obrazu)
        - [2.3.3 Optymalizacja Obrazów](#233-optymalizacja-obra%C5%BC%C3%B3w)
    - [2.4 Docker Compose](#24-docker-compose)
        - [2.4.1 `docker-compose.yml` – Przykład](#241-docker-composeyml-przyk%C5%82ad)
        - [2.4.2 Uruchamianie Docker Compose](#242-uruchamianie-docker-compose)
    - [2.5 Woluminy i Sieci](#25-woluminy-i-sieci)
        - [2.5.1 Woluminy](#251-woluminy)
        - [2.5.2 Sieci](#252-sieci)
    - [2.6 Docker w Produkcji i Best Practices](#26-docker-w-produkcji-i-best-practices)
    - [Podsumowanie](#2-podsumowanie)
3. [Kubernetes – Orkiestracja Kontenerów](#3-kubernetes---orkiestracja-kontenerow)
    - [3.1 Wprowadzenie do Kubernetes](#31-wprowadzenie-do-kubernetes)
    - [3.2 Podstawowe Komponenty Kubernetes](#32-podstawowe-komponenty-kubernetes)
    - [3.3 Deployment i Service](#33-deployment-i-service)
        - [3.3.1 Przykład Deployment](#331-przyk%C5%82ad-deployment)
        - [3.3.2 Przykład Service](#332-przyk%C5%82ad-service)
    - [3.4 Skalowanie Aplikacji](#34-skalowanie-aplikacji)
        - [3.4.1 Skalowanie ręczne](#341-skalowanie-r%C4%99czne)
        - [3.4.2 Autoskalowanie (Horizontal Pod Autoscaler)](#342-autoskalowanie-horizontal-pod-autoscaler)
    - [3.5 Monitoring i Logowanie](#35-monitorowanie-i-logowanie)
    - [3.6 Best Practices w Kubernetes](#36-best-practices-w-kubernetes)
    - [Podsumowanie Kubernetes](#3-podsumowanie-kubernetes)
    - [3.7 Zarządzanie Deploymentami w Kubernetes](#37-zarz%C4%85dzanie-deploymentami-w-kubernetes)
4. [Docker w Chmurach Hybrydowych](#4-docker-w-chmurach-hybrydowych)
    - [4.1 Co to jest Chmura Hybrydowa?](#41-co-to-jest-chmura-hybrydowa)
    - [4.2 Zalety Docker w Chmurach Hybrydowych](#42-zalety-docker-w-chmurach-hybrydowych)
    - [4.3 Przykłady Zastosowań](#43-przyk%C5%82ady-zastosowa%C5%84)
    - [4.4 Integracja Docker z Platformami Chmurowymi](#44-integracja-docker-z-platformami-chmurowymi)
    - [Podsumowanie Docker w Chmurach Hybrydowych](#4-podsumowanie-docker-w-chmurach-hybrydowych)
5. [Zarządzanie Rojem Dronów w Kubernetes](#5-zarz%C4%85dzanie-rojem-dron%C3%B3w-w-kubernetes)
    - [5.1 Wprowadzenie](#51-wprowadzenie)
    - [5.2 Konfiguracja Headless Service dla Rojów Dronów](#52-konfiguracja-headless-service-dla-roj%C3%B3w-dron%C3%B3w)
        - [5.2.1 Definicja Headless Service](#521-definicja-headless-service)
        - [5.2.2 Ograniczenia Headless Service w Komunikacji UDP](#522-ograniczenia-headless-service-w-komunikacji-udp)
    - [5.3 Implementacja Centralnego Agregatora Danych](#53-implementacja-centralnego-agregatora-danych)
        - [5.3.1 Tworzenie Skryptu Agregatora](#531-tworzenie-skryptu-agregatora)
        - [5.3.2 Dockerfile dla Agregatora](#532-dockerfile-dla-agregatora)
        - [5.3.3 Deployment i Service dla Agregatora](#533-deployment-i-service-dla-agregatora)
        - [5.3.4 Modyfikacja Logiki Drona](#534-modyfikacja-logiki-drona)
        - [5.3.5 Aktualizacja Deployment dla Dronów](#535-aktualizacja-deployment-dla-dron%C3%B3w)
        - [5.3.6 Wdrożenie Konfiguracji w Kubernetes](#536-wdro%C5%BCenie-konfiguracji-w-kubernetes)
        - [5.3.7 Weryfikacja Działania Agregatora](#537-weryfikacja-dzia%C5%82ania-agregatora)
    - [5.4 Usuwanie Usługi Mosquitto](#54-usuwanie-us%C5%82ugi-mosquitto)
        - [5.4.1 Sprawdzenie Istniejących Zasobów Mosquitto](#541-sprawdzenie-istniej%C4%85cych-zasob%C3%B3w-mosquitto)
        - [5.4.2 Usunięcie Deployment i Service dla Mosquitto](#542-usuni%C4%99cie-deployment-i-service-dla-mosquitto)
        - [5.4.3 Weryfikacja Usunięcia Zasobów](#543-weryfikacja-usuni%C4%99cia-zasob%C3%B3w)
    - [5.5 Alternatywne Podejścia do Agregacji Danych](#55-alternatywne-podej%C4%85cia-do-agregacji-danych)
        - [5.5.1 Użycie Message Broker (MQTT)](#551-u%C5%BCycie-message-broker-mqtt)
        - [5.5.2 Użycie HTTP REST API](#552-u%C5%BCycie-http-rest-api)
    - [5.6 Rozwiązywanie Problemów w PowerShell](#56-rozwiazywanie-problem%C3%B3w-w-powershell)
        - [5.6.1 Zastąpienie `grep` w PowerShell](#561-zast%C4%85pienie-grep-w-powershell)
    - [5.7 Integracja Ingress Gateway i Egress Gateway](#57-integracja-ingress-gateway-i-egress-gateway)
    - [5.8 Podsumowanie](#58-podsumowanie)
6. [Opis Projektu](#6-opis-projektu)
    - [6.1 Idea i Koncepcja](#61-idea-i-koncepcja)
    - [6.2 Poziomy Architektoniczne i Komponenty](#62-poziomy-architektoniczne-i-komponenty)
        - [Poziom 1: Fundamenty Komunikacji i Orkiestracji](#poziom-1-fundamenty-komunikacji-i-orkiestracji)
        - [Poziom 2: Drony i Generowanie Danych](#poziom-2-drony-i-generowanie-danych)
        - [Poziom 3: Agregacja Danych i API](#poziom-3-agregacja-danych-i-api)
        - [Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD](#poziom-4-narz%C4%99dzia-wspomagaj%C4%85ce-monitoring-cicd)
        - [Poziom 5: Bezpieczeństwo i Izolacja](#poziom-5-bezpiecze%C5%84stwo-i-izolacja)
    - [6.3 Integracja i Przepływ](#63-integracja-i-przep%C5%82yw)
    - [6.4 Rola dla Modeli AI](#64-rola-dla-modeli-ai)
7. [Podsumowanie](#7-podsumowanie)
8. [Informacje z Istniejących Plików](#8-informacje-z-istniej%C4%85cych-plik%C3%B3w)
9. [Odnośniki](#9-odno%C5%9Bniki)

---

## 5.7 Integracja Ingress Gateway i Egress Gateway

Aby zwiększyć bezpieczeństwo oraz kontrolę nad ruchem sieciowym w projekcie MQTT (Broker & Aggregator) działającym w Kubernetes, zastosujemy **Ingress Gateway** i **Egress Gateway** za pomocą **Istio Service Mesh**. Poniżej przedstawiamy kroki konfiguracji oraz przykłady manifestów YAML.

### **5.7.1 Wprowadzenie do Ingress Gateway i Egress Gateway**

- **Ingress Gateway**: Służy jako punkt wejścia dla ruchu przychodzącego z zewnątrz do klastra Kubernetes. Umożliwia kontrolę dostępu, routowanie oraz zabezpieczanie połączeń przy użyciu mTLS oraz autoryzacji JWT.

- **Egress Gateway**: Kontroluje ruch wychodzący z klastra do zewnętrznych usług. Zapewnia centralny punkt kontroli, audytu oraz zabezpieczenia dla wszystkich połączeń zewnętrznych.

### **5.7.2 Instalacja Istio**

Przed rozpoczęciem konfiguracji Ingress i Egress Gateway upewnij się, że Istio jest zainstalowane w Twoim klastrze Kubernetes. Możesz to zrobić za pomocą Istioctl:

```bash
istioctl install --set profile=demo -y
```

Po zakończeniu instalacji zweryfikuj status komponentów Istio:

```bash
kubectl get pods -n istio-system
```

### **5.7.3 Konfiguracja Ingress Gateway**

#### **Tworzenie Ingress Gateway dla Aggregator API**

1. **Utworzenie Secret z Certyfikatem TLS**

Ingress Gateway wymaga certyfikatu TLS do zabezpieczenia połączeń. Możesz utworzyć Secret Kubernetes zawierający certyfikat i klucz prywatny:

```bash
kubectl create -n istio-system secret tls aggregator-ingress-credential \
  --key /path/to/tls.key \
  --cert /path/to/tls.crt
```

2. **Definicja Gateway**

Utwórz zasób `Gateway`, który definiuje konfigurację dla Ingress Gateway:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: aggregator-ingress-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway # Używa domyślnego Ingress Gateway Istio
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: aggregator-ingress-credential # Secret z certyfikatem TLS
      minProtocolVersion: TLSV1_2
    hosts:
    - "aggregator.example.com"
```

Zastosuj konfigurację:

```bash
kubectl apply -f aggregator-ingress-gateway.yaml
```

3. **Definicja VirtualService dla Aggregator API**

VirtualService definiuje, jak ruch przychodzący przez Gateway ma być routowany do odpowiednich usług wewnętrznych.

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

Zastosuj konfigurację:

```bash
kubectl apply -f aggregator-virtualservice.yaml
```

#### **Konfiguracja mTLS i Autoryzacji JWT dla Ingress Gateway**

1. **Włączenie mTLS**

Aby zabezpieczyć komunikację między klientami a Ingress Gateway, włączamy mutual TLS (mTLS):

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

Zastosuj konfigurację:

```bash
kubectl apply -f peer-authentication.yaml
```

2. **Tworzenie Policy JWT**

Utwórz `RequestAuthentication` i `AuthorizationPolicy` dla Aggregator API:

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: aggregator-jwt
  namespace: default
spec:
  selector:
    matchLabels:
      app: aggregator-api
  jwtRules:
  - issuer: "https://identity.provider.com/"
    jwksUri: "https://identity.provider.com/.well-known/jwks.json"
```

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: aggregator-authorize
  namespace: default
spec:
  selector:
    matchLabels:
      app: aggregator-api
  rules:
  - from:
    - source:
        requestPrincipals: ["https://identity.provider.com/*"]
```

Zastosuj konfigurację:

```bash
kubectl apply -f request-authentication.yaml
kubectl apply -f authorization-policy.yaml
```

#### **Konfiguracja Rate Limiting i Blokowania IP**

1. **Rate Limiting**

Skonfiguruj Envoy Rate Limiter za pomocą `EnvoyFilter`:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit
  namespace: istio-system
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: GATEWAY
      listener:
        portNumber: 443
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
          domain: ingress_ratelimit
          timeout: 0.25s
          failure_mode_deny: true
          rate_limit_service:
            grpc_service:
              envoy_grpc:
                cluster_name: rate_limit_cluster
              timeout: 0.25s
```

**Uwagi:**
- Wymaga implementacji zewnętrznego serwisu rate limiting.
- Można również wykorzystać Istio’s built-in `Quota` system.

Zastosuj konfigurację:

```bash
kubectl apply -f envoyfilter-rate-limit.yaml
```

2. **Blokowanie IP**

Użyj `AuthorizationPolicy` do blokowania podejrzanych adresów IP:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: block-suspicious-ips
  namespace: default
spec:
  selector:
    matchLabels:
      app: aggregator-api
  action: DENY
  rules:
  - from:
    - source:
        ipBlocks: ["192.168.1.100/32", "10.0.0.0/24"]
```

Zastosuj konfigurację:

```bash
kubectl apply -f authorization-policy-block-ips.yaml
```

### **5.7.4 Podsumowanie Konfiguracji Ingress Gateway**

Dzięki zastosowaniu Ingress Gateway, ruch przychodzący do Aggregator API jest zabezpieczony za pomocą mTLS oraz autoryzacji JWT. Dodatkowo, implementacja rate limiting oraz blokowanie podejrzanych adresów IP zwiększa ochronę przed atakami typu DDoS oraz nadużyciami.

### **5.7.5 Konfiguracja Egress Gateway**

Egress Gateway umożliwia kontrolę ruchu wychodzącego z klastra Kubernetes do zewnętrznych usług, takich jak zewnętrzne API dostawców czy usługi chmurowe.

#### **Tworzenie ServiceEntry dla Zewnętrznych API**

Definiujemy zaufane domeny, do których klaster może się łączyć, poprzez `ServiceEntry`:

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

Zastosuj konfigurację:

```bash
kubectl apply -f serviceentry-external-api.yaml
```

#### **Routing Ruchu przez Egress Gateway**

1. **Definicja VirtualService dla Egress Gateway**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: external-api-route
  namespace: default
spec:
  hosts:
  - "api.external-payments.com"
  gateways:
  - istio-egressgateway
  - mesh
  tls:
  - match:
    - port: 443
      sniHosts:
      - "api.external-payments.com"
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        port:
          number: 443
  - match:
    - port: 443
      sniHosts:
      - "api.external-payments.com"
    route:
    - destination:
        host: api.external-payments.com
        port:
          number: 443
```

Zastosuj konfigurację:

```bash
kubectl apply -f virtualservice-egress.yaml
```

2. **Definicja DestinationRule dla Egress Gateway**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: external-api-mtls
  namespace: default
spec:
  host: istio-egressgateway.istio-system.svc.cluster.local
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
      credentialName: egressgateway-certs
      sni: api.external-payments.com
```

Zastosuj konfigurację:

```bash
kubectl apply -f destinationrule-egress-mtls.yaml
```

3. **Utworzenie Secret z Certyfikatami dla Egress Gateway**

```bash
kubectl create -n istio-system secret tls egressgateway-certs \
  --key /path/to/egressgateway.key \
  --cert /path/to/egressgateway.crt
```

#### **Polityki Blokujące dla Egress Gateway**

Aby zapewnić, że tylko `aggregator` ma dostęp do zewnętrznego API, zastosuj `AuthorizationPolicy`:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-aggregator-egress
  namespace: default
spec:
  selector:
    matchLabels:
      app: aggregator
  rules:
  - to:
    - operation:
        hosts: ["api.external-payments.com"]
```

Zastosuj konfigurację:

```bash
kubectl apply -f authorization-policy-egress.yaml
```

#### **Podsumowanie Konfiguracji Egress Gateway**

Egress Gateway umożliwia kontrolę i zabezpieczenie wszystkich połączeń wychodzących z klastra Kubernetes do zewnętrznych API. Dzięki `ServiceEntry`, `VirtualService` oraz `DestinationRule`, ruch do `api.external-payments.com` jest routowany przez Egress Gateway, gdzie jest zabezpieczony za pomocą mTLS. Polityki blokujące gwarantują, że tylko wybrane usługi (w tym przypadku `aggregator`) mają dostęp do określonych zewnętrznych zasobów.

### **5.7.6 Integracja Ingress i Egress Gateway z Projektem MQTT**

Integracja Ingress i Egress Gateway w projekcie MQTT (Broker & Aggregator) pozwala na:

- **Bezpieczne Wystawienie Aggregator API**: Dzięki Ingress Gateway, API jest dostępne z zewnątrz klastra Kubernetes w sposób zabezpieczony, umożliwiając autoryzowany dostęp użytkownikom i systemom zewnętrznym.

- **Kontrolowany Dostęp do Zewnętrznych API**: Egress Gateway zapewnia, że `aggregator` może komunikować się tylko z zaufanymi zewnętrznymi usługami, takimi jak API dostawcy płatności, co minimalizuje ryzyko nieautoryzowanego dostępu.

- **Monitorowanie i Audyt Ruchu**: Oba Gateway zapewniają centralne punkty do monitorowania i logowania ruchu, co ułatwia identyfikację potencjalnych zagrożeń i analizę incydentów.

### **5.7.7 Przykładowa Architektura Systemu po Integracji**

```
[Internet]
     |
[Ingress Gateway]
     |
[mTLS + JWT]
     |
[Aggregator API Service]
     |
[Aggregator Pod]
     |
[Egress Gateway]
     |
[External API: api.external-payments.com]
```

- **Ingress Gateway**: Przyjmuje ruch przychodzący z internetu, zabezpiecza go za pomocą mTLS i JWT, oraz kieruje go do `Aggregator API`.
- **Aggregator API**: Odbiera żądania od zewnętrznych użytkowników i przekazuje je do `Aggregator`.
- **Egress Gateway**: Kontroluje ruch wychodzący z `Aggregator` do zewnętrznego API.
- **External API**: Zewnętrzny dostawca usług, z którym `Aggregator` komunikuje się w sposób bezpieczny i kontrolowany.

### **5.7.8 Testowanie Konfiguracji**

1. **Sprawdzenie Dostępności Aggregator API**

Upewnij się, że Aggregator API jest dostępne poprzez Ingress Gateway:

```bash
curl -k https://aggregator.example.com/api/drones
```

**Uwagi:**
- Użyj odpowiednich nagłówków `Authorization` z ważnym tokenem JWT.
- Sprawdź, czy odpowiedź jest poprawna i czy dane są zwracane zgodnie z oczekiwaniami.

2. **Sprawdzenie Ruchu Wychodzącego przez Egress Gateway**

Monitoruj ruch wychodzący z `Aggregator` do `api.external-payments.com`:

```bash
kubectl logs deployment/istio-egressgateway -n istio-system
```

Upewnij się, że połączenia są nawiązywane poprawnie i że dane są przesyłane bez błędów.

3. **Monitorowanie i Logowanie**

Skorzystaj z narzędzi monitorujących takich jak **Prometheus** i **Grafana** oraz systemów logowania **ELK Stack**, aby śledzić ruch sieciowy, metryki wydajności oraz logi z Ingress i Egress Gateway.

---

## 5.8 Podsumowanie

Integracja **Ingress Gateway** i **Egress Gateway** w projekcie MQTT (Broker & Aggregator) znacząco zwiększa bezpieczeństwo oraz kontrolę nad ruchem sieciowym w klastrze Kubernetes. Dzięki zastosowaniu Istio Service Mesh, możliwe jest:

- **Bezpieczne wystawienie usług na zewnątrz** poprzez Ingress Gateway, zabezpieczając połączenia za pomocą mTLS i JWT.
- **Kontrolowane zarządzanie ruchem wychodzącym** za pomocą Egress Gateway, ograniczając dostęp do zaufanych zewnętrznych API.
- **Zaawansowane monitorowanie i logowanie**, co umożliwia szybką detekcję i reakcję na potencjalne zagrożenia oraz zapewnia pełną widoczność ruchu sieciowego.

Implementacja tych rozwiązań wspiera **zasadę najmniejszych uprawnień**, **spójność architektoniczną** oraz **najlepsze praktyki bezpieczeństwa**, co przekłada się na stabilność, skalowalność i bezpieczeństwo całego systemu zarządzania rojem dronów.

---

## 6. Opis Projektu

### 6.1 Idea i Koncepcja

W centrum projektu znajduje się symulacja roju dronów działających w środowisku chmurowym i kontenerowym. Każdy dron funkcjonuje jako autonomiczny kontener, komunikujący się z pozostałymi elementami systemu za pomocą protokołu MQTT. Wspólna komunikacja oparta o model publikacja-subskrypcja (publish-subscribe) zapewnia luźne powiązanie komponentów, elastyczność i skalowalność.

**Główne założenia:**

1. **Autonomiczne Kontenery/Drony** – Każdy dron jest kontenerem, generującym dane o swojej pozycji, stanie baterii i innych parametrach.
2. **Komunikacja MQTT** – Drony publikują dane do brokera MQTT, a inne komponenty, takie jak agregator, subskrybują te informacje.
3. **Architektura Kontenerowa w Kubernetes** – Całość wdrożenia opiera się na orkiestracji Kubernetes, zapewniając skalowalność, niezawodność, elastyczność i prostotę zarządzania.
4. **Agregacja i Dostęp do Danych** – Agregator zbiera dane z dronów, przetwarza je i udostępnia zewnętrznemu światu poprzez REST API (aggregator-api), co umożliwia zarządzanie rojem i analizę danych.
5. **Monitorowanie, CI/CD, Bezpieczeństwo** – Projekt uwzględnia pipeline’y CI/CD, monitoring (Prometheus, Grafana), logowanie (ELK), strategie wdrożeń (Blue-Green, Canary), bezpieczeństwo (RBAC, Network Policies, szyfrowanie).

### 6.2 Poziomy Architektoniczne i Komponenty

#### Poziom 1: Fundamenty Komunikacji i Orkiestracji

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

#### Poziom 2: Drony i Generowanie Danych

**Drony** (`drones/`)
- *Rola:* Autonomiczne generowanie danych o stanie drona (pozycja, bateria) i publikacja ich do MQTT.
- *Pliki i Konfiguracja:*
  - `drone_logic.py` – Logika generowania danych i komunikacji z brokerem.
  - `Dockerfile`, `requirements.txt` – Budowa obrazu kontenera drona.
  - `drone-deployment.yaml`, `drone-service.yaml` – Skrypty wdrażające flotę dronów do Kubernetes.
- *Idea:* Każdy dron jest niezależnym Podem w Kubernetes, który publikuje dane do brokera MQTT na topiki `drones/{drone_id}/position`. Daje to możliwość łatwego skalowania liczby dronów poprzez modyfikację `replicas`.

---

#### Poziom 3: Agregacja Danych i API

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

#### Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD

**Monitoring i Wizualizacja**
- *Prometheus, Grafana:* Zbierają metryki z dronów, agregatora, API oraz brokera, wizualizując obciążenie, wykorzystanie zasobów, poziom baterii dronów.
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów systemu, wspierając diagnozę i debugowanie.

**CI/CD**
- *Idea:* Automatyczne pipeline’y (GitLab CI, Jenkins, ArgoCD) kompilują i testują kod, budują obrazy Docker, wdrażają je do Kubernetes.
- *Korzyści:* Szybkie reagowanie na zmiany, zwinność w dostarczaniu nowych funkcji, minimalizacja błędów ręcznej konfiguracji.

**Strategie Wdrożeń (Blue-Green, Canary)**
- *Idea:* Bezpieczne aktualizacje pozwalają wdrażać nowe wersje dronów lub agregatora bez przestojów. Stopniowe przełączanie ruchu (canary) lub równoległe utrzymywanie dwóch wersji (blue-green) minimalizuje ryzyko awarii.

---

#### Poziom 5: Bezpieczeństwo i Izolacja

**RBAC i Network Policies**
- *Idea:* Kubernetes RBAC kontroluje, którzy użytkownicy mogą czytać, pisać czy wdrażać zasoby w klastrze. Network Policies ograniczają komunikację między Podami, zapewniając izolację i minimalizując wektory ataku.

**Secrets Management**
- *Idea:* Dane wrażliwe (klucze API, hasła) przechowywane w Kubernetes Secrets, podłączane do Podów w sposób bezpieczny. Szyfrowanie TLS dla komunikacji MQTT i API zwiększa poufność i integralność danych.

**Ingress Gateway i Egress Gateway (Integracja w Poziomie 5)**
- *Role:* Zapewniają zaawansowane mechanizmy bezpieczeństwa i kontroli ruchu sieciowego, zgodne z zasadami najlepszych praktyk chmurowych.
- *Konfiguracja:* Opisana w sekcji [5.7 Integracja Ingress Gateway i Egress Gateway](#57-integracja-ingress-gateway-i-egress-gateway).

---

## 5.8 Podsumowanie

W tej sekcji omówiliśmy integrację **Ingress Gateway** i **Egress Gateway** w projekcie MQTT (Broker & Aggregator) w środowisku Kubernetes z wykorzystaniem Istio Service Mesh. Implementacja tych komponentów zapewnia:

1. **Bezpieczne Wystawienie API**: Dzięki Ingress Gateway, Aggregator API jest dostępne z zewnątrz klastra w sposób zabezpieczony przez mTLS i JWT.
2. **Kontrolowany Dostęp do Zewnętrznych Usług**: Egress Gateway umożliwia bezpieczne i kontrolowane połączenia z zewnętrznymi API, zapewniając integralność i poufność danych.
3. **Zaawansowane Monitorowanie i Logowanie**: Centralizacja logów i metryk ruchu sieciowego pozwala na skuteczne monitorowanie oraz szybkie reagowanie na incydenty bezpieczeństwa.
4. **Zgodność z Najlepszymi Praktykami**: Implementacja zgodna z zasadami najmniejszych uprawnień, segmentacją sieci oraz automatyzacją zarządzania certyfikatami i politykami bezpieczeństwa.

Dzięki zastosowaniu Ingress i Egress Gateway, projekt zyskuje na elastyczności, bezpieczeństwie oraz możliwości skalowania, co jest niezbędne w dynamicznym środowisku zarządzania rojem dronów.

---

## 6. Opis Projektu

### 6.1 Idea i Koncepcja

W centrum projektu znajduje się symulacja roju dronów działających w środowisku chmurowym i kontenerowym. Każdy dron funkcjonuje jako autonomiczny kontener, komunikujący się z pozostałymi elementami systemu za pomocą protokołu MQTT. Wspólna komunikacja oparta o model publikacja-subskrypcja (publish-subscribe) zapewnia luźne powiązanie komponentów, elastyczność i skalowalność.

**Główne założenia:**

1. **Autonomiczne Kontenery/Drony** – Każdy dron jest kontenerem, generującym dane o swojej pozycji, stanie baterii i innych parametrach.
2. **Komunikacja MQTT** – Drony publikują dane do brokera MQTT, a inne komponenty, takie jak agregator, subskrybują te informacje.
3. **Architektura Kontenerowa w Kubernetes** – Całość wdrożenia opiera się na orkiestracji Kubernetes, zapewniając skalowalność, niezawodność, elastyczność i prostotę zarządzania.
4. **Agregacja i Dostęp do Danych** – Agregator zbiera dane z dronów, przetwarza je i udostępnia zewnętrznemu światu poprzez REST API (aggregator-api), co umożliwia zarządzanie rojem i analizę danych.
5. **Monitorowanie, CI/CD, Bezpieczeństwo** – Projekt uwzględnia pipeline’y CI/CD, monitoring (Prometheus, Grafana), logowanie (ELK), strategie wdrożeń (Blue-Green, Canary), bezpieczeństwo (RBAC, Network Policies, szyfrowanie).

### 6.2 Poziomy Architektoniczne i Komponenty

#### Poziom 1: Fundamenty Komunikacji i Orkiestracji

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

#### Poziom 2: Drony i Generowanie Danych

**Drony** (`drones/`)
- *Rola:* Autonomiczne generowanie danych o stanie drona (pozycja, bateria) i publikacja ich do MQTT.
- *Pliki i Konfiguracja:*
  - `drone_logic.py` – Logika generowania danych i komunikacji z brokerem.
  - `Dockerfile`, `requirements.txt` – Budowa obrazu kontenera drona.
  - `drone-deployment.yaml`, `drone-service.yaml` – Skrypty wdrażające flotę dronów do Kubernetes.
- *Idea:* Każdy dron jest niezależnym Podem w Kubernetes, który publikuje dane do brokera MQTT na topiki `drones/{drone_id}/position`. Daje to możliwość łatwego skalowania liczby dronów poprzez modyfikację `replicas`.

---

#### Poziom 3: Agregacja Danych i API

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

#### Poziom 4: Narzędzia Wspomagające, Monitoring, CI/CD

**Monitoring i Wizualizacja**
- *Prometheus, Grafana:* Zbierają metryki z dronów, agregatora, API oraz brokera, wizualizując obciążenie, wykorzystanie zasobów, poziom baterii dronów.
- *ELK (Elasticsearch, Logstash, Kibana):* Agregują i analizują logi wszystkich komponentów systemu, wspierając diagnozę i debugowanie.

**CI/CD**
- *Idea:* Automatyczne pipeline’y (GitLab CI, Jenkins, ArgoCD) kompilują i testują kod, budują obrazy Docker, wdrażają je do Kubernetes.
- *Korzyści:* Szybkie reagowanie na zmiany, zwinność w dostarczaniu nowych funkcji, minimalizacja błędów ręcznej konfiguracji.

**Strategie Wdrożeń (Blue-Green, Canary)**
- *Idea:* Bezpieczne aktualizacje pozwalają wdrażać nowe wersje dronów lub agregatora bez przestojów. Stopniowe przełączanie ruchu (canary) lub równoległe utrzymywanie dwóch wersji (blue-green) minimalizuje ryzyko awarii.

---

#### Poziom 5: Bezpieczeństwo i Izolacja

**RBAC i Network Policies**
- *Idea:* Kubernetes RBAC kontroluje, którzy użytkownicy mogą czytać, pisać czy wdrażać zasoby w klastrze. Network Policies ograniczają komunikację między Podami, zapewniając izolację i minimalizując wektory ataku.

**Secrets Management**
- *Idea:* Dane wrażliwe (klucze API, hasła) przechowywane w Kubernetes Secrets, podłączane do Podów w sposób bezpieczny. Szyfrowanie TLS dla komunikacji MQTT i API zwiększa poufność i integralność danych.

**Ingress Gateway i Egress Gateway**
- *Idea:* Zastosowanie Ingress i Egress Gateway w Istio zapewnia zaawansowane mechanizmy bezpieczeństwa, kontrolę dostępu oraz monitorowanie ruchu sieciowego, zgodne z zasadami najlepszych praktyk chmurowych.
- *Konfiguracja:* Opisana w sekcji [5.7 Integracja Ingress Gateway i Egress Gateway](#57-integracja-ingress-gateway-i-egress-gateway).

---

## 6. Integracja i Przepływ

1. **Drony** publikują dane o swojej pozycji i stanie przez MQTT:
   - **MQTT Broker** (Mosquitto) odbiera i przechowuje te informacje tymczasowo.

2. **Agregator** subskrybuje temat `drones/+/position`:
   - Przetwarza dane i agreguje je, tworząc jednolitą bazę informacji o stanie całego roju.
   - Agregator może również zapisywać dane do bazy danych oraz przekazywać je dalej do Aggregator API.

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
   - Ingress i Egress Gateway zapewniają kontrolę ruchu przychodzącego i wychodzącego, zgodnie z najlepszymi praktykami.

---

## 7. Rola dla Modeli AI

Ten opis służy jako główny punkt odniesienia dla modeli AI, które mają operować na kodzie i logice projektu. Dzięki niemu:

- **Modele językowe** mogą łatwiej zrozumieć kontekst, rolę i powiązania między elementami kodu.
- **Generatory kodu** opierają się na wspólnych założeniach architektonicznych, mając mapę połączeń i zrozumienie, gdzie wdrożyć nowe funkcjonalności.
- **Analityczne modele AI** łatwiej identyfikują punkty wejścia do optymalizacji (np. poprawa wydajności MQTT, zwiększenie bezpieczeństwa) i wiedzą, gdzie ingerować w kod lub konfigurację.

---

## 8. Informacje z Istniejących Plików

Poniżej znajduje się tabela zawierająca odnośniki do istniejących dokumentów w katalogu `_docs/` oraz ich opisy:

| **Dokument**                                       | **Link**                                                                                   | **Opis**                                                         |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Strategie wdrożeń Blue-Green i Canary             | [strategia_blue_green_canary.md](./strategia_blue_green_canary.md)                        | Strategie wdrożeń Blue-Green i Canary.                          |
| Ogólny opis projektu                               | [readme.md](./readme.md)                                                                  | Ogólny opis projektu: symulacja roju, komunikacja MQTT, wdrożenie, monitoring, CI/CD. |
| Dokumentacja Brokera MQTT                          | [broker_mqtt.md](./broker_mqtt.md)                                                        | Szczegółowa Dokumentacja Brokera MQTT.                           |
| Szczegółowy opis agregatora                        | [aggregator_details.md](./aggregator_details.md)                                          | Szczegółowy opis agregatora.                                     |
| Szczegółowy opis Aggregator API                    | [aggregator_api_details.md](./aggregator_api_details.md)                                  | Szczegółowy opis Aggregator API.                                 |
| Dokumentacja Bazy Danych                           | [database.md](./database.md)                                                                | Dokumentacja Bazy Danych.                                        |
| Dokumentacja Frontend                               | [frontend.md](./frontend.md)                                                                | Dokumentacja Frontend.                                            |

---

## 9. Odnośniki

- [Wprowadzenie do Docker i Kubernetes - Chmury Hybrydowe](./readme.md)
- [Kubernetes – Orkiestracja Kontenerów](./readme.md#3-kubernetes---orkiestracja-kontenerow)
- [Docker w Chmurach Hybrydowych](./readme.md#4-docker-w-chmurach-hybrydowych)
- [Strategia Blue-Green i Canary](./strategia_blue_green_canary.md)
- [Ogólny Opis Projektu](./readme.md#6-opis-projektu)
- [Dokumentacja Brokera MQTT](./broker_mqtt.md)
- [Szczegółowy opis agregatora](./aggregator_details.md)
- [Szczegółowy opis Aggregator API](./aggregator_api_details.md)
- [Dokumentacja Bazy Danych](./database.md)
- [Dokumentacja Frontend](./frontend.md)

---

**Uwagi Końcowe:**

Integracja **Ingress Gateway** i **Egress Gateway** w projekcie MQTT (Broker & Aggregator) znacząco podnosi poziom bezpieczeństwa oraz kontroli nad ruchem sieciowym w klastrze Kubernetes. Dzięki zastosowaniu Istio Service Mesh, możliwe jest implementowanie zaawansowanych mechanizmów bezpieczeństwa, które są zgodne z najlepszymi praktykami w branży. Pamiętaj, aby regularnie aktualizować konfiguracje, monitorować system oraz dostosowywać polityki bezpieczeństwa do zmieniających się wymagań i zagrożeń.

**Pamiętaj**, że bezpieczeństwo to proces ciągły. Regularnie aktualizuj komponenty, monitoruj system oraz dostosowuj polityki do zmieniających się wymagań i zagrożeń.