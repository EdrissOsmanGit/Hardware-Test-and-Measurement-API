# Hardware Test & Measurement API

A REST + WebSocket API for controlling and collecting measurements from lab hardware over serial, built with FastAPI and Python's `asyncio`. Demonstrates the core patterns used in real test/measurement automation systems: an async hardware abstraction layer, structured error handling, persistence, live streaming, and a test suite that doesn't depend on physical hardware. Built as hands-on prep for hardware automation / test engineering roles — the kind of work where software has to reliably talk to physical instruments (multimeters, oscilloscopes, custom test fixtures) over serial or SCPI, not just other web services.

## Architecture

```
                    REST / WebSocket
                          ↓
                    FastAPI Server
                          ↓
                  Hardware Controller
                   (async Device ABC)
                          ↓
                  pyserial-asyncio
                          ↓
                   Arduino (USB Serial)
                          ↓
                    Analog Sensors
```

The `Device` abstract base class decouples the API layer from any specific hardware. The current implementation (`ArduinoDevice`) talks to an Arduino over a simple line-based serial protocol, but the same interface could back a SCPI instrument (multimeter, oscilloscope) without changing the API layer at all. A `FakeDevice` implementation backs the automated test suite.

## Features

- **REST endpoints** to register, list, and unregister devices, and take one-off measurements
- **WebSocket streaming** for continuous live readings at a configurable interval
- **Async serial I/O** via `pyserial-asyncio`, so the API stays responsive under concurrent requests
- **Structured error handling** — device communication failures (timeouts, invalid responses, invalid channels) surface as clean `502` responses instead of crashes
- **Firmware-level input validation** — the Arduino itself rejects out-of-range channel requests
- **Persistent measurement history** in SQLite, queryable by device and time range
- **Structured logging** of every command sent and response received, to both console and file
- **Automated tests** using `pytest` and a mock hardware device, so the suite runs without any hardware attached

## API Reference

| Method   | Endpoint                       | Description                                                 |
| -------- | ------------------------------ | ----------------------------------------------------------- |
| `POST`   | `/devices`                     | Register and connect a device (`device_id`, `port`, `baud`) |
| `GET`    | `/devices`                     | List currently connected devices                            |
| `DELETE` | `/devices/{device_id}`         | Disconnect and remove a device                              |
| `POST`   | `/devices/{device_id}/measure` | Take a single measurement on a channel                      |
| `GET`    | `/measurements`                | Query measurement history (`device_id`, `since` filters)    |
| `WS`     | `/devices/{device_id}/stream`  | Stream live readings (`channel`, `interval` query params)   |

### Example

```bash
curl -X POST http://127.0.0.1:8000/devices \
  -H "Content-Type: application/json" \
  -d '{"device_id": "arduino1", "port": "COM3", "baud": 9600}'

curl -X POST http://127.0.0.1:8000/devices/arduino1/measure \
  -H "Content-Type: application/json" \
  -d '{"channel": "0"}'
```

```json
{ "voltage": 3.27, "timestamp": "2026-09-10T14:25:53.438484" }
```

## Setup

**Arduino side:**

1. Flash `arduino/firmware.ino` to your board
2. Note the COM port it enumerates on (Device Manager, or Arduino IDE → Tools → Port)

**Server side:**

```bash
pip install fastapi uvicorn pyserial-asyncio aiosqlite pytest httpx websockets
uvicorn main:app --reload
```

Interactive API docs available at `http://127.0.0.1:8000/docs`.

**Run tests:**

```bash
pytest -v
```

## Serial Protocol

A minimal ASCII, newline-delimited command set — intentionally similar in spirit to SCPI:

| Command           | Response                      |
| ----------------- | ----------------------------- |
| `READ <channel>`  | Voltage reading, e.g. `3.270` |
| `*IDN?`           | Device identification string  |
| (invalid channel) | `ERR invalid channel`         |

## What This Demonstrates

Python · FastAPI · REST API design · async/await · serial communication · hardware/software integration · Pydantic validation · structured error handling · logging · SQLite persistence · WebSocket streaming · automated testing with mocked I/O

## Possible Extensions

- Real SCPI instrument support (multimeter/oscilloscope) via `pyvisa`
- Multi-device concurrent polling
- Docker Compose deployment
- Web dashboard for live measurement visualization








https://github.com/user-attachments/assets/f2de4bbd-742b-4d61-b1a7-c52110e9a757



