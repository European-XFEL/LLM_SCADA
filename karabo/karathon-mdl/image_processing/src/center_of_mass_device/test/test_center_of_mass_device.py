import asyncio
import pytest
import numpy as np
from karabo.middlelayer import (
    Hash,
    ImageData,
    Device,
    Configurable,
    Image,
    DaqDataType,
    InputChannel,
    OutputChannel
)
from karabo.middlelayer.testing import AsyncDeviceContext, event_loop

from center_of_mass_device import CenterOfMassDevice

# Processor device configuration
_DEVICE_ID_PROC = "ProcessDevice"
_DEVICE_CONFIG_PROC = {"_deviceId_": _DEVICE_ID_PROC}

class GaussianSourceDevice(Device):
    """Device that emits a 2D Gaussian image with noise."""
    __version__ = "1.0"

    class OutputSchema(Configurable):
        daqDataType = DaqDataType.TRAIN
        image = Image(displayedName="Gaussian Image")

    output = OutputChannel(OutputSchema, displayedName="Output")

    async def send_image(self, data: Hash):
        self.output.schema.image = data.image
        await self.output.writeData()

class ReceiverDevice(Device):
    """Device that receives an image and stores it for inspection."""
    __version__ = "1.0"
    last_image = None

    class InputSchema(Configurable):
        daqDataType = DaqDataType.TRAIN
        image = Image(displayedName="Received Image")

    input = InputChannel(InputSchema, displayedName="Input")

    @InputChannel(raw=False)
    async def input(self, data, meta):
        self.last_image = data.image

@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_center_of_mass_pipeline(event_loop):
    # Instantiate devices
    source = GaussianSourceDevice({"_deviceId_": "SourceDevice"})
    processor = CenterOfMassDevice(_DEVICE_CONFIG_PROC)
    receiver = ReceiverDevice({"_deviceId_": "ReceiverDevice"})

    # Set up a device context with all three
    devices = {
        "source": source,
        "processor": processor,
        "receiver": receiver,
    }

    async with AsyncDeviceContext(devices=devices) as ctx:
        # Wire the channels: source -> processor -> receiver
        await ctx.connect("source.output", "processor.input")
        await ctx.connect("processor.output", "receiver.input")

        # Create a noisy 2D Gaussian test image
        x0, y0 = 50.5, 60.2
        sigma = 5.0
        size = (100, 120)
        xv, yv = np.meshgrid(np.arange(size[1]), np.arange(size[0]))
        img = np.exp(-((xv - x0) ** 2 + (yv - y0) ** 2) / (2 * sigma ** 2))
        img += np.random.normal(scale=0.01, size=size)

        # Wrap the image in a Hash and ImageData
        data = Hash("image", ImageData(img))

        # Send the image into the pipeline
        await source.send_image(data)
        # Allow the async pipeline to process
        await asyncio.sleep(0.1)

        # Validate that the processor computed the COM correctly
        x_est = processor.centerOfMassX
        y_est = processor.centerOfMassY
        assert abs(x_est - x0) < 1.0, f"X COM off by {abs(x_est-x0)}"
        assert abs(y_est - y0) < 1.0, f"Y COM off by {abs(y_est-y0)}"

        # Validate that the receiver got the altered image with the crosshair
        out_img = receiver.last_image
        cx = int(round(x_est))
        cy = int(round(y_est))
        max_val = out_img.max()

        # Crosshair span lengths
        half_len_x = int(size[1] * 0.1 / 2)
        half_len_y = int(size[0] * 0.1 / 2)

        # Check horizontal segment
        x_start = max(cx - half_len_x, 0)
        x_end = min(cx + half_len_x, size[1] - 1)
        assert np.all(out_img[cy, x_start:x_end] == max_val), \
            "Horizontal crosshair not found at COM"

        # Check vertical segment
        y_start = max(cy - half_len_y, 0)
        y_end = min(cy + half_len_y, size[0] - 1)
        assert np.all(out_img[y_start:y_end, cx] == max_val), \
            "Vertical crosshair not found at COM"