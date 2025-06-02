# Weather App – CI/CD Pipeline z Docker i GitHub Actions

## Autor
Hubert Kwiatkowski

## Cel
Celem projektu jest stworzenie pipeline’u CI/CD w usłudze GitHub Actions, który automatyzuje budowę, testowanie i publikację obrazu Docker aplikacji pogodowej z zadania nr 1. Pipeline:
- Wspiera architektury `linux/amd64` i `linux/arm64`.
- Wykorzystuje cache z DockerHub (eksporter: registry, backend: registry, tryb `max`).
- Skanuje obraz pod kątem podatności (CVE) za pomocą Trivy, publikując obraz do GHCR tylko w przypadku braku zagrożeń klasy `CRITICAL` lub `HIGH`.
- Zawiera strategię tagowania obrazów i cache z uzasadnieniem.

## Pipeline – Główne kroki

### 1. Checkout i konfiguracja
- `actions/checkout@v4` – pobiera źródła aplikacji.
- `docker/setup-qemu-action@v3`, `docker/setup-buildx-action@v3` – umożliwia budowanie obrazów dla wielu architektur.

### 2. Autoryzacja
- Logowanie do DockerHub (`DOCKERHUB_USERNAME`, `DOCKERHUB_PASSWORD_TOKEN`) dla cache.
- Logowanie do GitHub Container Registry (GHCR) za pomocą `GITHUB_TOKEN`.
- Konfiguracja SSH (`webfactory/ssh-agent@v0.9.0`) dla potencjalnego dostępu do prywatnych repozytoriów.

### 3. Budowanie i skanowanie obrazu
- Budowa obrazu `local-weather-app:testscan` dla `linux/amd64` z użyciem multi-stage `Dockerfile` (optymalizacja poprzez `python:3.12-slim` i aktualizacje `libc-bin`, `zlib1g`).
- Skanowanie za pomocą Trivy (`aquasecurity/trivy-action@master`), które kończy pipeline błędem w przypadku wykrycia podatności `CRITICAL` lub `HIGH`.
- Trivy wybrano ze względu na otwartoźródłowość, prostotę integracji z GitHub Actions i brak potrzeby subskrypcji, w przeciwieństwie do Docker Scout, który wymaga dodatkowej konfiguracji (źródło: [Trivy Documentation](https://aquasecurity.github.io/trivy/)).

### 4. Publikacja obrazu
- Po pomyślnym skanowaniu obraz jest budowany dla `linux/amd64` i `linux/arm64` i publikowany do `ghcr.io/hubertkwiatkowski/weather-app` z tagami:
  - `:sha-<short-sha>` – dla identyfikowalności wersji.
  - `:vX.Y.Z` – dla wydań semantycznych (np. `v1.0.0`).
  - `:latest` – dla najnowszej wersji.

### 5. Zarządzanie cache
- Cache przechowywany w `${DOCKERHUB_USERNAME}/weather-app:cache` z użyciem eksportera i backendu `registry` w trybie `max`.
- Pojedynczy tag `:cache` upraszcza zarządzanie i minimalizuje ryzyko błędów w pipeline’ie (źródło: [Docker Build Cache](https://docs.docker.com/build/cache/backends/registry/)).

## Tagowanie – Uzasadnienie
- **SHA**: Tag `:sha-<short-sha>` zapewnia jednoznaczną identyfikację wersji obrazu, ułatwiając traceability (źródło: [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)).
- **SemVer**: Tag `:vX.Y.Z` wspiera wersjonowanie produkcyjne, zgodne ze standardami branżowymi.
- **Latest**: Tag `:latest` umożliwia szybkie testowanie najnowszej wersji.
- **Cache**: Stały tag `:cache` upraszcza konfigurację i zapewnia spójność.

## Uruchomienie
```bash
docker pull ghcr.io/hubertkwiatkowski/weather-app:latest
docker run -p 4444:4444 -e API_KEY=YOUR_API_KEY ghcr.io/hubertkwiatkowski/weather-app:latest
