# Harmonic Filter – Docker (Part III)

Runs the REST API from Part II as a Docker container using Docker Compose.

---

## Requirements

- Docker Engine
- Docker Compose

---

## How to run

From the `harmonic_filter/` directory:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8001`.  
Interactive docs (Swagger UI) at `http://localhost:8001/docs`.

To run in the background:

```bash
docker compose up --build -d
```

To stop:

```bash
docker compose down
```

---

## Test the API

With the container running, send a request:

```bash
curl -X POST http://localhost:8001/harmonic_filter \
  -H "Content-Type: application/json" \
  -d '{
    "sample_rate": 8000,
    "base_freq": 50.0,
    "num_harmonics": 10,
    "samples": [0.0, 0.0801, 0.1597, 0.2382]
  }'
```

Or run the test script from the `harmonic_filter/` directory:

```bash
python api/test_api.py
```
