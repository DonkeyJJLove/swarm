# **Manual: Bezpieczna i Zintegrowana Komunikacja z Zewnętrznym API w Klastrze Kubernetes z Service Mesh (Istio)**

## **Spis Treści**

1. [Wprowadzenie](#wprowadzenie)
2. [Architektura Systemu](#architektura-systemu)
3. [Konfiguracja Ingress Gateway](#konfiguracja-ingress-gateway)
    - [Tworzenie Ingress Gateway](#tworzenie-ingress-gateway)
    - [Konfiguracja mTLS](#konfiguracja-mtls)
    - [Autoryzacja JWT](#autoryzacja-jwt)
    - [Rate Limiting i Blokowanie IP](#rate-limiting-i-blokowanie-ip)
4. [Konfiguracja Egress Gateway](#konfiguracja-egress-gateway)
    - [Tworzenie ServiceEntry](#tworzenie-serviceentry)
    - [Konfiguracja mTLS dla Ruchu Wychodzącego](#konfiguracja-mtls-dla-ruchu-wychodzącego)
    - [Polityki Blokujące](#polityki-blokujące)
5. [Monitorowanie i Obserwowalność](#monitorowanie-i-obserwowalność)
    - [Integracja z Prometheus i Grafana](#integracja-z-prometheus-i-grafana)
    - [Centralne Logowanie](#centralne-logowanie)
6. [Najlepsze Praktyki Bezpieczeństwa](#najlepsze-praktyki-bezpieczeństwa)
7. [Przykłady Konfiguracji](#przykłady-konfiguracji)
    - [Przykład Ingress Gateway z mTLS i JWT](#przykład-ingress-gateway-z-mtls-i-jwt)
    - [Przykład Egress Gateway z ServiceEntry](#przykład-egress-gateway-z-serviceentry)
8. [Podsumowanie](#podsumowanie)

---

## **Wprowadzenie**

Współczesne aplikacje często składają się z wielu mikroserwisów działających w rozproszonych środowiskach. Kubernetes, jako popularna platforma orkiestracji kontenerów, umożliwia zarządzanie tymi mikroserwisami w sposób skalowalny i elastyczny. Jednakże, wraz z korzyściami pojawiają się wyzwania związane z bezpieczeństwem, kontrolą ruchu oraz monitorowaniem komunikacji między serwisami a zewnętrznymi API.

Service mesh, taki jak Istio, oferuje zaawansowane mechanizmy zarządzania ruchem, bezpieczeństwem i obserwowalnością, które integrują się z Kubernetes, umożliwiając tworzenie bezpiecznych i monitorowanych połączeń zarówno wewnątrz klastra, jak i na zewnątrz.

Celem tego manuala jest przedstawienie kompleksowego podejścia do zabezpieczenia komunikacji z zewnętrznym API w środowisku klastrowym opartym o Kubernetes i Istio. Przeanalizujemy konfigurację Ingress i Egress Gateway, implementację mTLS, autoryzację JWT, rate limiting, blokowanie IP oraz monitorowanie ruchu sieciowego.

---

## **Architektura Systemu**

Załóżmy, że posiadamy klaster Kubernetes, który zawiera wiele mikroserwisów, w tym serwis `payment-service`. `Payment-service` musi komunikować się z zewnętrznym API dostawcy płatności, np. `api.external-payments.com`. Chcemy zapewnić, że:

- Tylko `payment-service` ma dostęp do zewnętrznego API.
- Wszystkie połączenia są zabezpieczone, monitorowane i logowane.
- Architektura jest spójna z najlepszymi praktykami chmurowymi.

Poniższa architektura ilustruje kluczowe komponenty:

```
[Internet]
     |
[Ingress Gateway]
     |
[mTLS]
     |
[Payment-Service]
     |
[Egress Gateway]
     |
[External API: api.external-payments.com]
```

- **Ingress Gateway**: Kontroluje ruch przychodzący do klastra.
- **Payment-Service**: Mikroserwis odpowiedzialny za obsługę płatności.
- **Egress Gateway**: Kontroluje ruch wychodzący z klastra do zewnętrznych API.
- **External API**: Zewnętrzny dostawca płatności.

---

## **Konfiguracja Ingress Gateway**

Ingress Gateway w Istio działa jako punkt wejścia dla ruchu przychodzącego do klastra. Odpowiada za kontrolę dostępu, zabezpieczenie połączeń oraz kierowanie ruchu do odpowiednich usług wewnętrznych.

### **Tworzenie Ingress Gateway**

1. **Instalacja Istio**

   Przed rozpoczęciem konfiguracji upewnij się, że Istio jest zainstalowane w Twoim klastrze Kubernetes. Możesz to zrobić za pomocą Istioctl:

   ```bash
   istioctl install --set profile=demo -y
   ```

2. **Konfiguracja Gateway**

   Utwórz zasób `Gateway`, który definiuje konfigurację dla Ingress Gateway:

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: Gateway
   metadata:
     name: payment-ingress-gateway
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
         credentialName: payment-ingress-credential # Secret zawierający certyfikat TLS
         minProtocolVersion: TLSV1_2
       hosts:
       - "payment.example.com"
   ```

3. **Utworzenie Secret z Certyfikatem TLS**

   Ingress Gateway wymaga certyfikatu TLS do zabezpieczenia połączeń. Możesz utworzyć Secret Kubernetes zawierający certyfikat i klucz prywatny:

   ```bash
   kubectl create -n istio-system secret tls payment-ingress-credential \
     --key /path/to/tls.key \
     --cert /path/to/tls.crt
   ```

### **Konfiguracja mTLS**

Mutual TLS (mTLS) zapewnia szyfrowanie oraz wzajemne uwierzytelnianie między klientem a serwerem. W Istio można skonfigurować mTLS na poziomie klastra lub dla konkretnych usług.

1. **Włączenie mTLS Globalnie**

   Aby włączyć mTLS dla całego klastra:

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

2. **Konfiguracja mTLS dla Ingress Gateway**

   Aby skonfigurować mTLS specyficznie dla Ingress Gateway, można użyć `DestinationRule`:

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: DestinationRule
   metadata:
     name: ingressgateway-mtls
     namespace: istio-system
   spec:
     host: istio-ingressgateway.istio-system.svc.cluster.local
     trafficPolicy:
       tls:
         mode: MUTUAL
         clientCertificate: /etc/certs/cert-chain.pem
         privateKey: /etc/certs/key.pem
         caCertificates: /etc/certs/root-cert.pem
         sni: payment.example.com
   ```

   Zastosuj konfigurację:

   ```bash
   kubectl apply -f destination-rule-mtls.yaml
   ```

### **Autoryzacja JWT**

JWT (JSON Web Token) umożliwia autoryzację użytkowników na podstawie tokenów. W Istio można skonfigurować polityki autoryzacji oparte na JWT.

1. **Tworzenie Policy JWT**

   Utwórz `RequestAuthentication` i `AuthorizationPolicy`:

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: RequestAuthentication
   metadata:
     name: payment-jwt
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
     jwtRules:
     - issuer: "https://identity.provider.com/"
       jwksUri: "https://identity.provider.com/.well-known/jwks.json"
   ```

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: AuthorizationPolicy
   metadata:
     name: payment-authorize
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
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

2. **Dodanie Tokena JWT do Klienta**

   Upewnij się, że każdy klient wysyłający żądanie do `payment-service` posiada ważny token JWT. Token powinien być dołączony w nagłówku `Authorization`:

   ```
   Authorization: Bearer <JWT_TOKEN>
   ```

### **Rate Limiting i Blokowanie IP**

Ochrona przed atakami typu DDoS oraz nadużyciami jest kluczowa dla stabilności systemu. Istio oferuje mechanizmy ograniczania liczby żądań oraz filtrowania ruchu na podstawie adresów IP.

1. **Konfiguracja Rate Limiting**

   Istio wykorzystuje Envoy Rate Limiter. Poniżej przedstawiamy przykładową konfigurację:

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
         app: payment-service
     action: DENY
     rules:
     - from:
       - source:
           ipBlocks: ["192.168.1.100/32", "10.0.0.0/24"]
   ```

   Zastosuj konfigurację:

   ```bash
   kubectl apply -f block-suspicious-ips.yaml
   ```

---

## **Konfiguracja Egress Gateway**

Egress Gateway kontroluje ruch wychodzący z klastra Kubernetes do zewnętrznych API. Zapewnia centralny punkt kontroli, audytu oraz zabezpieczenia.

### **Tworzenie ServiceEntry**

`ServiceEntry` definiuje zewnętrzne usługi, do których klaster może się łączyć. Pozwala na kontrolę dozwolonych domen, portów i protokołów.

1. **Definiowanie ServiceEntry**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: ServiceEntry
   metadata:
     name: external-payments-api
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
   kubectl apply -f serviceentry-external-payments.yaml
   ```

2. **Routing Ruchu przez Egress Gateway**

   Utwórz `VirtualService`, który kieruje ruch do Egress Gateway:

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: VirtualService
   metadata:
     name: external-payments-route
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

### **Konfiguracja mTLS dla Ruchu Wychodzącego**

Aby zapewnić bezpieczeństwo ruchu wychodzącego, skonfiguruj mTLS na Egress Gateway.

1. **Tworzenie DestinationRule dla External API**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: DestinationRule
   metadata:
     name: external-payments-mtls
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

2. **Konfiguracja Secret z Certyfikatami dla Egress Gateway**

   Utwórz Secret zawierający certyfikaty dla Egress Gateway:

   ```bash
   kubectl create -n istio-system secret tls egressgateway-certs \
     --key /path/to/egressgateway.key \
     --cert /path/to/egressgateway.crt
   ```

### **Polityki Blokujące**

Aby zapewnić, że tylko `payment-service` ma dostęp do zewnętrznego API, zastosuj `AuthorizationPolicy`.

1. **Utworzenie AuthorizationPolicy**

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: AuthorizationPolicy
   metadata:
     name: allow-payment-service
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
     rules:
     - to:
       - operation:
           hosts: ["api.external-payments.com"]
   ```

   Zastosuj konfigurację:

   ```bash
   kubectl apply -f authorization-policy-egress.yaml
   ```

2. **Blokowanie Dostępu dla Innych Serwisów**

   Domyślnie, jeśli nie zdefiniujesz polityki zezwalającej, dostęp będzie zablokowany. Upewnij się, że nie istnieją inne polityki zezwalające na dostęp do `api.external-payments.com` dla innych serwisów.

---

## **Monitorowanie i Obserwowalność**

Monitorowanie ruchu sieciowego oraz stanu bezpieczeństwa jest kluczowe dla szybkiego wykrywania i reagowania na incydenty.

### **Integracja z Prometheus i Grafana**

Istio integruje się z Prometheus do zbierania metryk oraz Grafana do wizualizacji danych.

1. **Instalacja Prometheus i Grafana**

   Istio w trybie demo instaluje Prometheus i Grafana automatycznie. Możesz uzyskać dostęp do dashboardów:

   ```bash
   kubectl port-forward svc/prometheus 9090:9090 -n istio-system
   kubectl port-forward svc/grafana 3000:3000 -n istio-system
   ```

   Następnie odwiedź `http://localhost:3000` w przeglądarce, aby uzyskać dostęp do Grafana.

2. **Konfiguracja Dashboardów**

   W Grafana możesz wykorzystać wbudowane dashboardy Istio do monitorowania ruchu, opóźnień, błędów itp.

### **Centralne Logowanie**

Istio umożliwia centralne logowanie ruchu przez Ingress i Egress Gateway, co jest niezbędne dla audytu i analizy bezpieczeństwa.

1. **Konfiguracja Logowania w Istio**

   Użyj Fluentd lub innego narzędzia do zbierania logów z podów Istio:

   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: fluentd-config
     namespace: kube-system
   data:
     fluent.conf: |
       <source>
         @type tail
         path /var/log/containers/*.log
         pos_file /var/log/fluentd-containers.log.pos
         tag kubernetes.*
         format json
       </source>
       <filter kubernetes.**>
         @type kubernetes_metadata
       </filter>
       <match istio.ingressgateway.**>
         @type elasticsearch
         host elasticsearch.kube-system.svc.cluster.local
         port 9200
         logstash_format true
         flush_interval 5s
       </match>
       <match istio.egressgateway.**>
         @type elasticsearch
         host elasticsearch.kube-system.svc.cluster.local
         port 9200
         logstash_format true
         flush_interval 5s
       </match>
   ```

   Zastosuj konfigurację:

   ```bash
   kubectl apply -f fluentd-configmap.yaml
   ```

2. **Integracja z Systemami SIEM**

   Skonfiguruj Elasticsearch, Kibana lub inne narzędzia SIEM do analizy logów zebranych przez Fluentd. Pozwoli to na detekcję incydentów oraz analizę po fakcie.

---

## **Najlepsze Praktyki Bezpieczeństwa**

1. **Zasada Najmniejszych Uprawnień (Least Privilege)**

   Upewnij się, że każdy serwis ma dostęp tylko do tych zasobów, które są mu niezbędne do działania. Wykorzystuj `AuthorizationPolicy` do kontrolowania dostępu.

2. **Regularna Rotacja Certyfikatów**

   Automatyzuj odnawianie certyfikatów TLS za pomocą narzędzi takich jak `cert-manager`.

3. **Monitorowanie i Audyt**

   Stałe monitorowanie ruchu oraz centralne logowanie umożliwiają szybkie wykrywanie anomalii i reagowanie na potencjalne zagrożenia.

4. **Segmentacja Sieci**

   Wykorzystaj Network Policies oraz Service Mesh do segmentacji sieci, co ogranicza możliwość lateralnego ruchu w przypadku kompromitacji serwisu.

5. **Automatyzacja i Infrastruktura jako Kod (IaC)**

   Wszystkie konfiguracje powinny być definiowane jako kod, co umożliwia wersjonowanie, audyt oraz łatwe wdrażanie zmian.

---

## **Przykłady Konfiguracji**

Poniżej przedstawiamy konkretne przykłady konfiguracji dla kluczowych komponentów opisanych powyżej.

### **Przykład Ingress Gateway z mTLS i JWT**

1. **Gateway**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: Gateway
   metadata:
     name: payment-ingress-gateway
     namespace: istio-system
   spec:
     selector:
       istio: ingressgateway
     servers:
     - port:
         number: 443
         name: https
         protocol: HTTPS
       tls:
         mode: SIMPLE
         credentialName: payment-ingress-credential
         minProtocolVersion: TLSV1_2
       hosts:
       - "payment.example.com"
   ```

2. **VirtualService**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: VirtualService
   metadata:
     name: payment-virtualservice
     namespace: default
   spec:
     hosts:
     - "payment.example.com"
     gateways:
     - istio-system/payment-ingress-gateway
     http:
     - match:
       - uri:
           prefix: /payment
       route:
       - destination:
           host: payment-service.default.svc.cluster.local
           port:
             number: 80
   ```

3. **RequestAuthentication i AuthorizationPolicy**

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: RequestAuthentication
   metadata:
     name: payment-jwt
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
     jwtRules:
     - issuer: "https://identity.provider.com/"
       jwksUri: "https://identity.provider.com/.well-known/jwks.json"
   ```

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: AuthorizationPolicy
   metadata:
     name: payment-authorize
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
     rules:
     - from:
       - source:
           requestPrincipals: ["https://identity.provider.com/*"]
   ```

### **Przykład Egress Gateway z ServiceEntry**

1. **ServiceEntry**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: ServiceEntry
   metadata:
     name: external-payments-api
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

2. **VirtualService kierujący ruch przez Egress Gateway**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: VirtualService
   metadata:
     name: external-payments-route
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

3. **DestinationRule dla mTLS**

   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: DestinationRule
   metadata:
     name: external-payments-mtls
     namespace: default
   spec:
     host: istio-egressgateway.istio-system.svc.cluster.local
     trafficPolicy:
       tls:
         mode: ISTIO_MUTUAL
         credentialName: egressgateway-certs
         sni: api.external-payments.com
   ```

4. **AuthorizationPolicy dla Egress Gateway**

   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: AuthorizationPolicy
   metadata:
     name: allow-payment-service
     namespace: default
   spec:
     selector:
       matchLabels:
         app: payment-service
     rules:
     - to:
       - operation:
           hosts: ["api.external-payments.com"]
   ```

---

## **Podsumowanie**

Zabezpieczenie komunikacji z zewnętrznym API w środowisku Kubernetes wymaga zastosowania wielowarstwowego podejścia obejmującego kontrolę ruchu, zabezpieczenia komunikacji, autoryzację oraz monitorowanie. Wykorzystanie service mesh, takiego jak Istio, wraz z Ingress i Egress Gateway, umożliwia stworzenie skalowalnej i bezpiecznej architektury, która spełnia wymagania nowoczesnych aplikacji chmurowych.

Kluczowe korzyści z zastosowania tego podejścia to:

- **Centralna Kontrola Ruchu**: Umożliwia spójne zarządzanie ruchem przychodzącym i wychodzącym.
- **Zaawansowane Polityki Bezpieczeństwa**: Implementacja mTLS, autoryzacji JWT, rate limiting oraz blokowania IP w jednym miejscu.
- **Granularność Polityk Sieciowych**: Precyzyjna kontrola dostępu na poziomie poszczególnych serwisów czy domen.
- **Rozbudowane Monitorowanie i Audyt**: Pełna obserwowalność ruchu sieciowego oraz możliwość integracji z systemami SIEM.

Implementując opisane rozwiązania, `payment-service` może bezpiecznie integrować się z zewnętrznym API, a cały system zyskuje na elastyczności, bezpieczeństwie i możliwości szybkiego reagowania na zmiany czy incydenty.

**Pamiętaj**, że bezpieczeństwo to proces ciągły. Regularnie aktualizuj komponenty, monitoruj system oraz dostosowuj polityki do zmieniających się wymagań i zagrożeń.