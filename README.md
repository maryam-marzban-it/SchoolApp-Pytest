# 🏫 School Management System API

Ett API-baserat system för hantering av en skolmiljö, byggt med Python, `psycopg2` och PostgreSQL. Projektet innehåller tabeller för studenter,
kurser, avdelningar, instruktörer och inskrivningar. API:t erbjuder full CRUD-funktionalitet och testas automatiskt med `pytest`.

## 🚀 Funktioner

- Hantera studenter, instruktörer, kurser och avdelningar
- REST API med CRUD-operationer
- PostgreSQL-anslutning via `psycopg2`
- Server körs med `uvicorn`
- Setup-script för att skapa databas och fylla med exempeldata
- Testning med `pytest`

## 📁 Projektstruktur

```bash
.
├── main.py              # API endpoints (körs med uvicorn)
├── setup.py             # Skapar tabeller och lägger in testdata
├── db_config.py         # (om du har en separat DB-anslutningsfil)
├── tests/
│   ├── test_client.py   # Enhetstester
│   └── test_e2e.py      # End-to-end-tester
├── requirements.txt     # Beroenden
└── README.md            # Dokumentation
