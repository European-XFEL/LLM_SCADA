import pytest
import numpy as np
from karabo.middlelayer import Hash, ImageData
from karabo.middlelayer.testing import event_loop
from center_of_mass_device import CenterOfMassDevice

_DEVICE_ID = "TestCenterOfMassDevice"
_DEVICE_CONFIG = {"_deviceId_": _DEVICE_ID}

@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_center_of_mass_device(event_loop):
    device = CenterOfMassDevice(_DEVICE_CONFIG)

    # Generate a Gaussian test image with noise
    x0, y0 = 50.5, 60.2
    sigma = 5.0
    size = (100, 120)
    xv, yv = np.meshgrid(np.arange(size[1]), np.arange(size[0]))
    img = np.exp(-((xv - x0) ** 2 + (yv - y0) ** 2) / (2 * sigma ** 2))
    img += np.random.normal(scale=0.01, size=size)

    # Create a Hash with ImageData
    data = Hash('image', ImageData(img))
    # Call the input handler directly
    await device.input(data, None)

    # Check computed center of mass is within tolerance
    x_est = device.centerOfMassX.value
    y_est = device.centerOfMassY.value
    assert abs(x_est - x0) < 1.0
    assert abs(y_est - y0) < 1.0

    # Check crosshair imprint at the estimated COM pixel
    out_img = device.output.schema.image.value
    cx = int(round(x_est))
    cy = int(round(y_est))
    max_val = out_img.max()
    assert out_img[cy, cx] == max_val