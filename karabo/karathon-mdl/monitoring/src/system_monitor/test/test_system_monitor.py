# test_system_monitor.py

import pytest

from karabo.middlelayer import connectDevice, waitUntilNew
from karabo.middlelayer.testing import AsyncDeviceContext, create_instanceId, event_loop

from system_monitor import SystemMonitor




@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_device_instantiation(event_loop: event_loop):
    """Basic instantiation and context‐management smoke‐test."""
    _DEVICE_ID = create_instanceId()
    _DEVICE_CONFIG = {"_deviceId_": _DEVICE_ID}
    device = SystemMonitor(_DEVICE_CONFIG)
    async with AsyncDeviceContext(device=device) as ctx:
        # The context should have our device under the key "device"
        assert ctx.instances["device"] is device
        assert device.deviceId == _DEVICE_ID


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_cpu_and_memory_sampling(event_loop: event_loop):
    """
    After the device comes up, it should sample its own CPU% and memory RSS;
    we wait for at least one update on each channel.
    """
    _DEVICE_ID = create_instanceId()
    _DEVICE_CONFIG = {"_deviceId_": _DEVICE_ID}
    device = SystemMonitor(_DEVICE_CONFIG)
    async with AsyncDeviceContext(device=device):
        proxy = await connectDevice(_DEVICE_ID)
        # Wait until we get at least one new cpuUsage and memoryUsage
        await waitUntilNew(proxy.cpuUsage)
        await waitUntilNew(proxy.memoryUsage)

        # Both values should be non‐negative floats
        assert proxy.cpuUsage >= 0.0

        assert proxy.memoryUsage >= 0.0
