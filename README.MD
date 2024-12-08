# Rój w chmurach - Popatrzmy z laba

## Wprowadzenie

Świadomość roju, percepcja roju, autonomiczność i orkiestracja zbiorów – to obszary łączące wiele dziedzin współczesnej inżynierii systemowej i informatyki. Docker i drony, wbrew pozorom, mają ze sobą więcej wspólnego niż tylko fakt bycia systemami uruchamianymi na fizycznym sprzęcie (np. minikomputerach pokładowych dronów). Analogicznie jak drony w przestrzeni fizycznej, kontenery w świecie wirtualnym mogą być zarządzane, skalowane i orkiestracyjne tworząc „roje” usług, reagujące na zmiany środowiska i wymogi biznesowe.

## Systemy w chmurach i cybernetyka

Budowa systemów informatycznych oraz cybernetyka ściśle wiążą się z pracą w chmurach. Skalowalność, elastyczność i zdolność do natychmiastowego reagowania na obciążenia czy awarie to kluczowe cechy współczesnych środowisk. Podobnie jak rój dronów dostosowuje swoje działanie do warunków w przestrzeni powietrznej, tak systemy w chmurach – oparte na kontenerach i mikrousługach – adaptują się do zmiennych wymagań użytkowników.

W praktyce, podejmowanie decyzji w oparciu o analizę danych i optymalizację wniosków jest fundamentem zarówno dla rozproszonych algorytmów sterujących rojami dronów, jak i dla algorytmów autoskalowania, load balancingu czy failover’u w klastrach kontenerowych.

## Podobieństwo algorytmów i kontenerów

Algorytmy zarządzające rojami dronów są zbliżone do tych wykorzystywanych przy kontroli klastrów kontenerów. Rój dronów może być postrzegany jako zestaw autonomicznych, ale współpracujących jednostek. Podobnie klaster kontenerowy składa się z wielu niezależnych instancji (Podów), które wspólnie tworzą usługę o wysokiej dostępności i skalowalności.

### Przykładowa logika „drona” kontenerowego

```python
# drone_logic.py
import os
import socket
import time
import random

DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{random.randint(1000, 9999)}")
DRONE_PORT = int(os.getenv("DRONE_PORT", "5000"))
DISCOVERY_HOST = "drone-service"
DISCOVERY_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", DRONE_PORT))

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    message = f"{DRONE_NAME} at position {position[0]}, {position[1]}"
    try:
        sock.sendto(message.encode(), (DISCOVERY_HOST, DISCOVERY_PORT))
    except Exception:
        pass

    sock.settimeout(1.0)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"[{DRONE_NAME}] received from {addr}: {data.decode()}")
    except socket.timeout:
        pass

    # Prosta symulacja ruchu
    position[0] += random.randint(-1, 1)
    position[1] += random.randint(-1, 1)
    time.sleep(5)
```

Ten skrypt przedstawia prostą logikę: „dron” komunikuje swoją pozycję, słucha komunikatów zwrotnych i modyfikuje stan na podstawie otrzymanych informacji. W kontekście kontenerów takie jednostki mogą wymieniać dane, reagować na zmiany i podejmować decyzje w sposób rozproszony.

## Percepcja i inteligencja rozproszona

Każda jednostka (dron czy kontener) działa autonomicznie, jednak całościowe zachowanie roju wynika z interakcji pomiędzy tymi jednostkami. Inteligencja roju opiera się na:

- **Świadomości kontekstu**: Każda jednostka wie, jakie jest jej zadanie, i zna swój stan (np. pozycję, obciążenie).
- **Granice percepcji**: Jednostki rozumieją, które informacje są dla nich istotne i potrafią odfiltrować nieistotne dane.
- **Reguły interakcji**: Decyzje wynikają z prostych reguł komunikacji, wymiany informacji i współpracy.

W świecie IT zasady te odpowiadają mechanizmom service discovery, autoskalowaniu, health checkom oraz load balancingowi. 

## Budowanie i uruchamianie kontenerów

Stosowanie dobrych praktyk w zarządzaniu kontenerami obejmuje:

- **Powtarzalność procesu**: Dockerfile i CI/CD zapewniają, że każda instancja jest identyczna, minimalizując problem konfiguracji środowisk.
- **Minimalne obrazy**: Redukowanie rozmiaru obrazów (np. Alpine Linux zamiast Ubuntu) w celu szybszego wdrażania, mniejszej powierzchni ataku i niższych kosztów transferu.
- **Konfiguracja przez zmienne środowiskowe**: Umożliwia uruchamianie tych samych obrazów w różnych środowiskach bez modyfikacji kodu.

### Przykładowy skrypt do automatyzacji budowy i uruchamiania kontenerów

```python
# build_and_run.py
import docker
import os

client = docker.from_env()
dockerfile_path = os.path.abspath("../drones")

image_name = "drone_image"
image_tag = "latest"

print("Budowanie obrazu Docker...")
image, build_logs = client.images.build(
    path=dockerfile_path,
    tag=f"{image_name}:{image_tag}",
    rm=True
)

for log_line in build_logs:
    if 'stream' in log_line:
        print(log_line['stream'], end='')

print("Obraz zbudowany:", image.id)

container_name = "my_drone_container"
environment_variables = {
    "DRONE_NAME": "drone_1",
    "DDS_TOPIC_POSITION": "drone_positions",
    "DDS_TOPIC_SENSOR": "drone_sensors",
    "PUBLISH_INTERVAL": "2"
}

print("Uruchamianie kontenera...")
container = client.containers.run(
    image=f"{image_name}:{image_tag}",
    name=container_name,
    environment=environment_variables,
    detach=True
)

print("Kontener uruchomiony:", container.name)
```

W praktyce, zgodnie z najlepszymi praktykami branżowymi, powyższy skrypt warto zintegrować z systemem CI/CD (np. GitLab CI, GitHub Actions), aby każdy kod po zatwierdzeniu w repozytorium był automatycznie budowany, testowany i wdrażany.

## Kubernetes jako rój

Kubernetes to domyślny standard w orkiestracji kontenerów. Zapewnia:

- **Deklaratywne wdrożenia**: Opis stanu pożądanego (np. liczby replik) w plikach YAML.
- **Autoskalowanie**: HPA (Horizontal Pod Autoscaler) umożliwia automatyczne dostosowanie liczby Podów.
- **Service Discovery** i **Load Balancing**: Za pomocą Services i Ingress można z łatwością wykrywać i równoważyć obciążenie pomiędzy Podami.
- **Konfiguracja i sekrety**: ConfigMap i Secret umożliwiają zewnętrzne zarządzanie konfiguracjami i danymi wrażliwymi, dzięki czemu obrazy są uniwersalne i neutralne środowiskowo.
- **Bezpieczeństwo**: RBAC (Role-Based Access Control), Network Policies i Pod Security Admission zapewniają kontrolę dostępu, segmentację sieci oraz wysoki poziom bezpieczeństwa.

### Przykładowa definicja wdrożenia w Kubernetes

```yaml
# drone-deployment.yaml
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
        image: drone_image:latest
        env:
        - name: DRONE_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

Powyższa konfiguracja uruchamia trzy repliki Podów zawierających kontener z dronem. Dzięki **Headless Service** i **StatefulSet** można zapewnić identyfikowalne nazwy i adresy, co ułatwia tworzenie zaawansowanych komunikacyjnie rojów, w których poszczególne jednostki są odkrywane i adresowane bezpośrednio.

## Dobre praktyki w zarządzaniu kontenerami i klastrami

1. **Infrastruktura jako kod (IaC)**: Wykorzystywanie narzędzi takich jak Terraform, Ansible lub Helm Chartów do zarządzania całym środowiskiem ułatwia powtarzalność i testowalność.
2. **Obserwowalność**: Monitoring (Prometheus, Grafana), logowanie (ELK, Loki) i tracing (Jaeger) są niezbędne dla zrozumienia zachowania rozproszonego systemu i szybkiego reagowania na problemy.
3. **Ciągłe testowanie i walidacja**: Testy integracyjne, testy bezpieczeństwa, skanowanie obrazów pod kątem luk (np. Trivy, Anchore) oraz analiza wydajności (np. K6) pozwalają na utrzymanie wysokiej jakości i bezpieczeństwa.
4. **Cykl życia aplikacji**: Wykorzystywanie strategii blue-green deployment lub canary release do płynnego wdrażania nowych wersji bez przestoju
[[strategie wdrażania: Blue-Green Deployment i Canary Release](_docs/strategia_blue_green_canary.md)].
## Podsumowanie

Technologie kontenerowe (Docker, Podman) oraz ich orkiestracja (Kubernetes) stanowią solidną platformę do tworzenia systemów wzorowanych na koncepcjach rojów dronów. Rozproszone podejmowanie decyzji, autonomiczność jednostek i emergentne zachowania to cechy, które sprawiają, że rój w chmurach może być efektywnie modelowany przy użyciu praktyk branżowych oraz dobrych praktyk DevOps i SRE (Site Reliability Engineering).

**Rój to nie tylko zbiór autonomicznych jednostek – to złożony ekosystem, w którym odpowiednia orkiestracja, standaryzacja i niezawodność infrastruktury są kluczowe do osiągnięcia spójnej, skalowalnej i efektywnej całości.**
```