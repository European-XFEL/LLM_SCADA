# Karabo Karathon - Monitoring Device Prompts

## Initial Prompt

I would like you to write me a Karabo middlelayer device that monitors the CPU 
usage and memory consumption of it's own (linux) process. 

You can find the Karabo middlelayer documentation here, and the links 
therein: https://howtomiddlelayer.readthedocs.io/en/latest/. 

Use the best practices described therein. Create a single Python file for the 
Device, and another file which contains unit tests for the functionality 
you implement. Karabo devices are generally tested like this:

```python
import pytest

from karabo.middlelayer.testing import AsyncDeviceContext, event_loop

from ..__CLASS_NAME__ import __CLASS_NAME__


_DEVICE_ID = "Test__CLASS_NAME__"
_DEVICE_CONFIG = {
    "_deviceId_": _DEVICE_ID,
}


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_device(event_loop: event_loop):
    device = __CLASS_NAME__(_DEVICE_CONFIG)
    async with AsyncDeviceContext(device=device) as ctx:
        assert ctx.instances["device"] is device
        assert ctx.instances["device"].deviceId == _DEVICE_ID
```

## Setup files

Please also output a pyproject.toml that installs the package using the
correct entry points.

## Additional Iteration

Not required