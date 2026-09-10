import serial_asyncio
import asyncio
import logging
from hardware.base import Device

logger = logging.getLogger("hwapi.arduino")


class DeviceCommError(Exception):
    """Raised when communication with the device fails."""
    pass


class ArduinoDevice(Device):
    def __init__(self, port: str, baud: int = 9600):
        self.port = port
        self.baud = baud
        self._reader = None
        self._writer = None

    async def connect(self):
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port, baudrate=self.baud
            )
            await asyncio.sleep(2)
            logger.info(f"Connected to {self.port} at {self.baud} baud")
        except Exception as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            raise DeviceCommError(f"Could not open port {self.port}: {e}")

    async def measure(self, channel: str) -> float:
        cmd = f"READ {channel}\n".encode()
        try:
            self._writer.write(cmd)
            logger.info(f"Sent: {cmd!r}")
            line = await asyncio.wait_for(self._reader.readline(), timeout=2.0)
            raw = line.decode().strip()
            logger.info(f"Received: {raw!r}")

            if not raw or raw.startswith("ERR"):
                raise DeviceCommError(f"Device returned error: {raw!r}")

            return float(raw)

        except asyncio.TimeoutError:
            logger.error(f"Timeout reading channel {channel}")
            raise DeviceCommError(f"Timeout waiting for response from channel {channel}")
        except ValueError:
            logger.error(f"Could not parse response as float: {raw!r}")
            raise DeviceCommError(f"Invalid response from device: {raw!r}")

    async def close(self):
        if self._writer:
            self._writer.close()
            logger.info(f"Closed connection to {self.port}")