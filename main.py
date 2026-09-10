from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging
from hardware.arduino import ArduinoDevice, DeviceCommError
from db import init_db, save_measurement, get_measurements
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("hwapi.log"), logging.StreamHandler()],

)
logger = logging.getLogger("hwapi")

app = FastAPI()
devices: dict[str, ArduinoDevice] = {}


@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")


class DeviceRegister(BaseModel):
    device_id: str
    port: str
    baud: int = 9600


class MeasureRequest(BaseModel):
    channel: str


class Measurement(BaseModel):
    voltage: float
    timestamp: str


@app.post("/devices")
async def register_device(req: DeviceRegister):

    if req.device_id in devices:
        raise HTTPException(400, f"Device {req.device_id} already registered")
    dev = ArduinoDevice(req.port, req.baud)

    try:
        await dev.connect()
    except DeviceCommError as e:
        logger.error(f"Registration failed for {req.device_id}: {e}")
        raise HTTPException(502, str(e))
    devices[req.device_id] = dev
    logger.info(f"Registered device {req.device_id} on {req.port}")
    return {"status": "connected", "device_id": req.device_id}


@app.get("/devices")
async def list_devices():
    return {"devices": list(devices.keys())}


@app.post("/devices/{device_id}/measure", response_model=Measurement)
async def measure(device_id: str, req: MeasureRequest):

    dev = devices.get(device_id)
    if not dev:
        raise HTTPException(404, f"Device {device_id} not found")
    try:
        voltage = await dev.measure(req.channel)
    except DeviceCommError as e:
        logger.error(f"Measurement failed on {device_id}, channel {req.channel}: {e}")
        raise HTTPException(502, str(e))

    timestamp = datetime.utcnow().isoformat()
    await save_measurement(device_id, req.channel, voltage, timestamp)
    return Measurement(voltage=voltage, timestamp=timestamp)


@app.get("/measurements")
async def query_measurements(device_id: str | None = None, since: str | None = None):
    return await get_measurements(device_id, since)



@app.delete("/devices/{device_id}")
async def unregister_device(device_id: str):
    dev = devices.get(device_id)
    if not dev:
        raise HTTPException(404, f"Device {device_id} not found")
    await dev.close()
    del devices[device_id]
    logger.info(f"Unregistered device {device_id}")
    return {"status": "disconnected", "device_id": device_id}



@app.websocket("/devices/{device_id}/stream")
async def stream_measurements(websocket: WebSocket, device_id: str, channel: str = "0", interval: float = 1.0):
    await websocket.accept()
    dev = devices.get(device_id)
    if not dev:
        await websocket.send_json({"error": f"Device {device_id} not found"})
        await websocket.close()
        return

    try:
        while True:
            try:
                voltage = await dev.measure(channel)
                timestamp = datetime.utcnow().isoformat()
                await save_measurement(device_id, channel, voltage, timestamp)
                await websocket.send_json({"voltage": voltage, "timestamp": timestamp})
            except DeviceCommError as e:
                await websocket.send_json({"error": str(e)})
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from {device_id} stream")