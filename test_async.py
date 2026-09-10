import asyncio
from hardware.arduino import ArduinoDevice

async def main():
    dev = ArduinoDevice("COM3")
    await dev.connect()
    voltage = await dev.measure("0")
    print(f"Voltage: {voltage}")
    await dev.close()

asyncio.run(main())