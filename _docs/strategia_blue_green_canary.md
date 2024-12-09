# Strategie Wdrażania: Blue-Green Deployment i Canary Release

Aby zapewnić płynne wdrażanie nowych wersji aplikacji bez przestojów, warto zastosować zaawansowane strategie wdrażania, takie jak **blue-green deployment** oraz **canary release**. Poniżej omówimy te strategie w kontekście projektowanego rozwiązania.

---

## Blue-Green Deployment

**Blue-Green Deployment** polega na utrzymaniu dwóch identycznych środowisk produkcyjnych: `blue` (aktualnie aktywne) i `green` (nowa wersja). Proces wdrażania wygląda następująco:

### 1. Przygotowanie Nowej Wersji

Nowa wersja aplikacji jest wdrażana w środowisku `green`. Wszystkie testy są przeprowadzane w środowisku `green`, aby upewnić się, że działa poprawnie.

### 2. Przełączenie Ruchu

Po zweryfikowaniu stabilności środowiska `green`, ruch użytkowników jest przekierowywany z `blue` do `green`. Może to być zrealizowane poprzez aktualizację konfiguracji `Service` w Kubernetes.

### 3. Monitorowanie

Śledzenie działania nowej wersji w środowisku `green`. Jeśli wystąpią problemy, można szybko przywrócić ruch do środowiska `blue`.

### 4. Czyszczenie

Po potwierdzeniu stabilności nowej wersji, stare środowisko `blue` może zostać usunięte lub przygotowane do kolejnych aktualizacji.

### Przykład Implementacji w Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: blue
  template:
    metadata:
      labels:
        app: my-app
        version: blue
    spec:
      containers:
      - name: my-app
        image: my-app:blue

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: green
  template:
    metadata:
      labels:
        app: my-app
        version: green
    spec:
      containers:
      - name: my-app
        image: my-app:green

---
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
    version: green  # Przełącz na 'blue' w razie potrzeby
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

---

## Canary Release

**Canary Release** polega na stopniowym wdrażaniu nowej wersji aplikacji do części użytkowników, monitorowaniu jej działania, a następnie pełnym wdrożeniu, jeśli wszystko przebiegnie pomyślnie.

### Proces Wdrażania

1. **Wdrażanie Małej Liczby Replik**  
   Nowa wersja aplikacji jest wdrażana jako niewielka liczba Podów (np. 5% całej infrastruktury).

2. **Monitorowanie**  
   Ścisłe monitorowanie działania nowej wersji pod kątem błędów i wydajności.

3. **Stopniowe Skalowanie**  
   Jeśli nowa wersja działa poprawnie, zwiększa się liczbę Podów z nową wersją, zmniejszając jednocześnie liczbę Podów ze starą wersją.

4. **Pełne Wdrożenie**  
   Po pełnym przetestowaniu nowej wersji wszystkie ruchy są przekierowywane do nowych Podów.

### Przykład Implementacji w Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 10
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  template:
    metadata:
      labels:
        app: my-app
        version: canary  # Użyj 'stable' dla głównej wersji
    spec:
      containers:
      - name: my-app
        image: my-app:canary
```

### Wdrażanie Canariego

```bash
kubectl set image deployment/my-app my-app=my-app:canary --record
```

### Stopniowe Zwiększanie Replik

```bash
kubectl scale deployment my-app --replicas=15
```

### Pełne Wdrożenie

```bash
kubectl set image deployment/my-app my-app=my-app:stable --record
```

---

## Korzyści z Wykorzystania Strategii Blue-Green i Canary Release

- **Minimalizacja Ryzyka**: Nowe wersje są wdrażane na małą skalę, co ogranicza potencjalne problemy.
- **Brak Przestojów**: Użytkownicy nie doświadczają przestojów podczas wdrażania nowych wersji.
- **Szybkie Przywracanie**: W razie problemów można szybko wrócić do poprzedniej stabilnej wersji.
- **Lepsze Monitorowanie**: Możliwość dokładnego monitorowania wpływu nowej wersji na środowisko produkcyjne.

---

## Podsumowanie Strategii Wdrażania

Stosowanie strategii **blue-green deployment** i **canary release** w Kubernetes pozwala na płynne i bezpieczne wdrażanie nowych wersji aplikacji bez przestojów. Dzięki nim można zminimalizować ryzyko związane z aktualizacjami, zapewniając ciągłość działania usług dla użytkowników końcowych.

---

**Plik:** `_docs/rstrategia_blue_green_canary.md`

[Powrót do głównej dokumentacji](../README.MD)
