from hardware.base import Device

class FakeDevice(Device):
    """Mock device for testing without real hardware."""
    def __init__(self, canned_values: dict[str, float] = None):
        self.canned_values = canned_values or {"0": 3.30, "1": 1.65}
        self.connected = False

    async def connect(self):
        self.connected = True

    async def measure(self, channel: str) -> float:
        if channel not in self.canned_values:
            from hardware.arduino import DeviceCommError
            raise DeviceCommError(f"Device returned error: 'ERR invalid channel'")
        return self.canned_values[channel]

    async def close(self):
        self.connected = False