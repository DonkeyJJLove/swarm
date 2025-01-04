### **Most MQTT?**

Cóż, to jest koncepcja poligonu. My tutaj nie będziemy stawiać klastra z siedmiodniowymi narzędziami bezpieczeństwa klastrów oraz przepływem dla Splunka. To raczej podejście do problematyki klastra, aplikacji w klastrze oraz komunikacji w i z klastrem.

#### **Zrozumienie Roli MQTT w Architekturze Swarm**

Gdy tak na to spojrzymy i zauważymy, że klaster nie obsługuje komunikacji na zewnątrz w UDP, zrozumiemy, że **MQTT** pełni rolę **task brokera** oraz **szyny danych**, a **logi** są przesyłane przez **UDP**. W kontekście naszej aplikacji **MQTT** nie tylko zarządza zadaniami, ale również integruje różne komponenty systemu w specyficznym środowisku **swarm**, które działa jako poligon zabezpieczeń dla chmury.

#### **Komunikacja Dronów: UDP i MQTT**

**Drony** wysyłają informacje zarówno przez **UDP**, jak i **MQTT**. Komunikacja UDP jest używana do przesyłania logów, co pozwala na szybkie i efektywne zbieranie danych telemetrycznych. Z kolei MQTT, dzięki swojej wydajności i niezawodności, służy jako broker do zarządzania zadaniami i przesyłania szyny danych między różnymi komponentami systemu.

**Przykład Przepływu Danych:**
1. **Drony** wysyłają telemetrię do **aggregator-api** za pomocą **MQTT** oraz **UDP**.
2. **Aggregator-api** odbiera te dane i przesyła je do **kolektora danych Splunk** przez **UDP**.
3. **Splunk** analizuje i wizualizuje dane, umożliwiając monitorowanie i podejmowanie decyzji w czasie rzeczywistym.

#### **Backend Serwera jako API dla Frontendu**

Zewnętrzna komunikacja z klastrem odbywa się poprzez **frontend** i **backend**. **Backend** pełni rolę **API serwera**, który umożliwia interakcję z systemem dla usług zewnętrznych. **Frontend** działa jako **pre-processor**, przetwarzając dane przed ich dalszym wykorzystaniem. Warto zauważyć, że **backend** i **frontend** wykonują operacje w kooperacji z dronami, jednak nie mają bezpośredniego dostępu do możliwości sterowania samymi dronami. **Server** działa jako forma **sterowni**, zarządzając komunikacją i przetwarzaniem danych.

#### **Low-Level API: Sterowanie Klastrem przez AI**

Chociaż **low-level API** jeszcze nie istnieje, jego rozwój jest kluczowy dla funkcji sterujących klastrem. **Low-level API** będzie odpowiedzialne za bezpośrednie zarządzanie zasobami klastra, takie jak skalowanie usług, zarządzanie zasobami czy automatyzacja procesów na podstawie wyników analizy danych przez system AI.

**Przykładowe Funkcje Low-Level API:**
- **Skalowanie Usług:** Automatyczne zwiększanie lub zmniejszanie liczby instancji usług w zależności od obciążenia.
- **Zarządzanie Zasobami:** Optymalizacja wykorzystania CPU, pamięci i innych zasobów klastra.
- **Automatyzacja Procesów:** Wdrażanie automatycznych reguł na podstawie danych analitycznych.

#### **Bezpieczeństwo Komunikacji w Swarm**

W środowisku **swarm**, które działa jako poligon zabezpieczeń dla chmury, kluczowe jest zapewnienie bezpiecznej i niezawodnej komunikacji między komponentami. **MQTT** jako broker odgrywa tutaj istotną i niejednoznaczną rolę, umożliwiając zarządzanie zadaniami oraz przesyłanie danych w sposób bezpieczny i efektywny.

**Mechanizmy Zabezpieczeń:**
- **RBAC (Role-Based Access Control):** Kontrola dostępu do zasobów klastra na podstawie ról użytkowników i serwisów.
- **Network Policies:** Ograniczanie przepływu ruchu sieciowego między podami, minimalizując ryzyko nieautoryzowanego dostępu.
- **Encryption:** Szyfrowanie danych przesyłanych przez MQTT oraz UDP, zapewniające poufność i integralność danych.
- **Istio Service Mesh:** Zarządzanie ruchem sieciowym, implementacja mTLS (mutual TLS) oraz monitorowanie komunikacji w klastrze.

#### **Integracja z Monitorowaniem i Tracingiem**

W naszej architekturze, **Prometheus** zbiera metryki z różnych komponentów, **Grafana** wizualizuje te dane, a **Jaeger** śledzi ścieżki przepływu danych w systemie. Dzięki integracji MQTT jako szyny danych, możemy efektywnie monitorować i analizować przepływ informacji oraz wykrywać potencjalne problemy w czasie rzeczywistym.

**Przykładowy Przepływ:**
1. **Drony** wysyłają telemetrię przez **MQTT** i **UDP** do **aggregator-api**.
2. **Aggregator-api** przesyła dane do **Splunk** przez **UDP**.
3. **Splunk** analizuje dane, a wyniki są dostępne poprzez **backend API**.
4. **Prometheus** zbiera metryki z **aggregator-api**, **Splunk**, i innych komponentów.
5. **Grafana** prezentuje te metryki na dashboardach, umożliwiając monitorowanie systemu.
6. **Jaeger** śledzi ścieżki przepływu danych, identyfikując ewentualne opóźnienia lub błędy w komunikacji.
7. **AI System** analizuje dane z **Prometheus** i **Splunk**, sterując klastrem poprzez **low-level API**.

#### **Podsumowanie**

Broker **MQTT** w naszej architekturze pełni kluczową rolę w zarządzaniu zadaniami oraz przesyłaniu danych, jednocześnie integrując się z innymi komponentami systemu w środowisku **swarm**, które działa jako poligon zabezpieczeń dla chmury. Dzięki zastosowaniu **UDP** dla logów oraz starannemu projektowaniu **API**, udało nam się stworzyć system, który jest zarówno efektywny, jak i bezpieczny, bez potrzeby angażowania skomplikowanych narzędzi bezpieczeństwa. Integracja z narzędziami monitorującymi i tracingowymi zapewnia pełną widoczność i kontrolę nad działaniem systemu, co jest niezbędne w dynamicznym środowisku chmurowym.

