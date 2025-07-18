Karabo Karathon - Coordinated Motion Prompts

## Initial Prompt

I would like you to write me a Karabo middlelayer device implements a 
random scan functionality on motion axes.  When "start" is clicked, 
it creates a user-configurable number of random locations between 
configurable x- and y- limits. It then calculates the optimum path to scan 
all points, assuming motion sytems with a constant velocity. Finally, 
it performs the scan, controlling two motors. When idle or started, 
the device state is ACTIVE, when it's calculating, the state is PROCESSING, 
and when it's performing the scan, the state is MOVING.

The motors are individual devices in the distributed system. They have a 
common interface: a new position is set on the `targetPosition` float property,
the motor is then issued a `move` command, which transitions it to the 
MOVING state, and the motor is done moving when it is not in the `MOVING` 
state anymore. If an error occurs the motor goes into an ERROR state. If 
this happens the scan is stopped, the device goes to ERROR, and it can be 
reset to ACTIVE using a `reset` command.

You can find the Karabo middlelayer documentation here, 
and the links therein: https://howtomiddlelayer.readthedocs.io/en/latest/. 

Use the best practices described therein. Create a single Python file for 
the Device, and another file which contains unit tests for the functionality 
you implement. For you test implement 2 simulated motors with the above 
interface, and test that a scan completes, and also that an optimal path is 
calculated. 

Karabo devices are generally tested like this:

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
Thanks, please adapt the device and the test to not use device nodes. 
Rather the motor device ids are given as Strings, and you then use 
connectDevice to control then. This also means you should implement actual 
devices for the simulated motors.