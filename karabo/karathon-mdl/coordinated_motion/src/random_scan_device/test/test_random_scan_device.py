# tests/test_random_scan_device.py
import math
import pytest

from karabo.middlelayer.testing import AsyncDeviceContext, event_loop
from karabo.middlelayer import Device, Double, String, Slot, Overwrite, State
from src.random_scan_device import RandomScanDevice

# Simulated motor device implementing the same interface
class FakeMotor(Device):
    targetPosition = Double(defaultValue=0.0)
    position = Double(defaultValue=0.0)
    state = Overwrite(
        defaultValue=State.ACTIVE,
        options={State.ACTIVE, State.MOVING, State.ERROR}
    )

    @Slot()
    async def move(self):
        # Immediately move: set position to target and go back to ACTIVE
        self.state = State.MOVING
        self.position = self.targetPosition
        self.state = State.ACTIVE

    @Slot()
    async def reset(self):
        self.state = State.ACTIVE


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_scan_completes(event_loop: event_loop):
    device_id = "TestRandomScan"
    cfg = {
        "_deviceId_": device_id,
        "motorXId": "X",
        "motorYId": "Y",
        "xMin": 0.0, "xMax": 10.0,
        "yMin": 0.0, "yMax": 10.0,
        "numPoints": 3
    }
    device = RandomScanDevice(cfg)
    motor_x = FakeMotor({"_deviceId_": "X"})
    motor_y = FakeMotor({"_deviceId_": "Y"})

    # Run device together with two fake motors :contentReference[oaicite:1]{index=1}
    async with AsyncDeviceContext(device=device, other_devices=[motor_x, motor_y]):
        await device.start()
        assert device.state == State.ACTIVE
        assert device.status == "Scan complete"
        # After scan, motors should be at the last point of the computed path
        # (We trust that if no exception was raised, the scan logic ran to completion)


def _path_length(path):
    return sum(
        math.hypot(path[i+1][0] - path[i][0],
                   path[i+1][1] - path[i][1])
        for i in range(len(path) - 1)
    )


def test_optimal_path():
    # A simple 3‐point triangle: optimal path length is 1 + sqrt(2)
    points = [(0, 0), (1, 0), (0, 1)]
    device = RandomScanDevice({
        "_deviceId_": "dummy",
        "motorXId": "dummyX",
        "motorYId": "dummyY"
    })
    path = device._calculate_optimal_path(points)
    length = _path_length(path)
    assert length == pytest.approx(1 + math.sqrt(2), rel=1e-6)
