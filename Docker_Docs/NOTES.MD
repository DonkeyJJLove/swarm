### Budowanie i Zarządzanie Obrazami Dockerowymi

#### Krok 1: Pobieranie obrazu bazowego
Przy budowaniu obrazów z użyciem Dockera używa się obrazów bazowych. W tym przypadku używamy `python:3.11-slim`.

**Przykład:**
```bash
docker pull python:3.11-slim
```

#### Krok 2: Struktura projektu
Przygotuj strukturę projektu z następującymi plikami i katalogami:

```
dockerBotnet/
│-- aggregator/
│   └── aggregator.py
│-- drones/
│   └── drone_logic.py
│-- server/
│   └── mqtt/
│       └── mqtt_aggregator.py
│-- aggregator/Dockerfile
│-- drones/Dockerfile
│-- server/mqtt/Dockerfile
```

#### Krok 3: Plik `.dockerignore`
Utwórz plik `.dockerignore`, aby wykluczyć niepotrzebne pliki z budowania obrazu.

**Przykład zawartości `.dockerignore`:**
```
__pycache__/
*.pyc
*.pyo
*.pyd
```

#### Krok 4: Tworzenie Dockerfile

**Przykładowy `Dockerfile` dla agregatora:**

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY aggregator/aggregator.py /app/aggregator.py
```

#### Krok 5: Budowanie obrazów Dockerowych

**Budowanie obrazu `data-aggregator`:**

```bash
docker build -t data-aggregator:1.0 -f aggregator/Dockerfile .
```

**Budowanie obrazu `drones`:**

```bash
docker build -t drones:1.0 -f drones/Dockerfile .
```

**Budowanie obrazu `mqtt-broker`:**

```bash
docker build -t mqtt-broker:1.0 -f server/mqtt/Dockerfile .
```

#### Krok 6: Sprawdzanie dostępnych obrazów

```bash
docker images
```

**Przykładowy wynik:**

```
REPOSITORY        TAG     IMAGE ID       CREATED         SIZE
data-aggregator   1.0     2f794fd50176   13 minutes ago  194MB
drones            1.0     eae909d517a4   2 hours ago     194MB
mqtt-broker       1.0     48fc7ef99f73   3 hours ago     212MB
```

#### Krok 7: Uruchamianie kontenerów

**Uruchamianie `data-aggregator`:**

```bash
docker run -d --name data-aggregator-container data-aggregator:1.0
```

**Uruchamianie `drones`:**

```bash
docker run -d --name drones-container drones:1.0
```

**Uruchamianie `mqtt-broker`:**

```bash
docker run -d --name mqtt-broker-container mqtt-broker:1.0
```

#### Krok 8: Sprawdzanie uruchomionych kontenerów

```bash
docker ps
```

#### Krok 9: Usuwanie kontenerów i obrazów

**Usuwanie kontenera:**

```bash
docker rm -f data-aggregator-container
```

**Usuwanie obrazu:**

```bash
docker rmi data-aggregator:1.0
```

