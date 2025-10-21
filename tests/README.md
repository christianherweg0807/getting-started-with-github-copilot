# Tests für Mergington High School Activities API

Dieses Verzeichnis enthält umfassende Tests für die FastAPI-Anwendung des Mergington High School Activity Management Systems.

## Test-Struktur

- `conftest.py`: Pytest-Konfiguration mit Fixtures und Setup
- `test_activities.py`: Haupttestdatei mit allen API-Endpoint-Tests

## Test-Kategorien

### 1. **API-Endpoint-Tests (`TestActivitiesAPI`)**
- ✅ Abrufen aller Aktivitäten
- ✅ Datentyp-Validierung
- ✅ Struktur-Validierung

### 2. **Anmeldungs-Tests (`TestSignupEndpoint`)**
- ✅ Erfolgreiche Anmeldung
- ✅ Nicht existierende Aktivität (404)
- ✅ Doppelte Anmeldung (400)
- ✅ Volle Aktivität (400)
- ✅ Verschiedene E-Mail-Formate

### 3. **Abmeldungs-Tests (`TestUnregisterEndpoint`)**
- ✅ Erfolgreiche Abmeldung
- ✅ Nicht existierende Aktivität (404)
- ✅ Nicht angemeldeter Student (400)

### 4. **Root-Endpoint-Tests (`TestRootEndpoint`)**
- ✅ Weiterleitung zu static/index.html

### 5. **Integrations-Tests (`TestIntegrationScenarios`)**
- ✅ Kompletter Workflow (Anmelden → Überprüfen → Abmelden)
- ✅ Mehrere Studenten, eine Aktivität
- ✅ Ein Student, mehrere Aktivitäten

## Tests ausführen

### Alle Tests ausführen
```bash
pytest tests/ -v
```

### Mit Coverage-Report
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Einzelne Testklasse ausführen
```bash
pytest tests/test_activities.py::TestSignupEndpoint -v
```

### Einzelnen Test ausführen
```bash
pytest tests/test_activities.py::TestSignupEndpoint::test_signup_success -v
```

## Test-Coverage

Die aktuelle Test-Coverage beträgt **100%** für den `src/app.py` Code.

## Test-Features

- **Isolation**: Jeder Test wird mit zurückgesetzten Aktivitätsdaten ausgeführt
- **Fixtures**: Wiederverwendbare Test-Komponenten (Client, Sample-Daten)
- **Comprehensive**: Tests decken Success-Cases, Error-Cases und Edge-Cases ab
- **Integration**: End-to-End Workflow-Tests
- **Fast**: Alle Tests laufen in unter 1 Sekunde

## Hinweise

- Tests verwenden das FastAPI TestClient für HTTP-Requests
- Aktivitätsdaten werden vor jedem Test zurückgesetzt (Test-Isolation)
- Alle HTTP-Status-Codes und Response-Formate werden validiert
- Tests sind deterministisch und können in beliebiger Reihenfolge ausgeführt werden