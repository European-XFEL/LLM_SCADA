# Karabo Karathon - Image Processing Prompts

## Initial Prompt

I would like you to write me a Karabo middlelayer device implements an image
processor that calculates and exposes the center of mass coordinates of the 
image, alongside their respective standard deviations.

The images are to be received through an input channel from another device, 
and are located at data.beam. The device is then to imprint the center of mass
location as a crosshair which span 1/10s of the image dimension on that axis.
The altered image is then sent out using an output channel.

You can find the Karabo middlelayer documentation here, 
and the links therein: https://howtomiddlelayer.readthedocs.io/en/latest/. 

Use the best practices described therein. Create a single Python file for the
Device, and another file which contains unit tests for the functionality 
you implement. For you test implement a device that produces the test images
using a 2d Gaussian profiel and added noise, and a receiver device that 
receives the altered images. The test should check that the center of mass 
coordinates reasonably match the gaussion parameters, and that the imprinted 
crosshair corresponds to the evaluated center of mass coordinates.

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

Please modify the test to do what I requested, i.e.  actually implement a 
device therein that produces the test images using a 2d Gaussian profiel and 
added noise, and a receiver device therein that receives the altered images.