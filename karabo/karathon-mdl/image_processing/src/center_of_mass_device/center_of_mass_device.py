from karabo.middlelayer import (
    Device,
    InputChannel,
    OutputChannel,
    Image,
    Configurable,
    Node,
    DaqDataType,
    Double
)
import numpy as np

class CenterOfMassDevice(Device):
    __version__ = "1.0"
    
    # Exposed properties for center of mass and standard deviations
    centerOfMassX = Double(
        displayedName="Center X",
        description="Center of mass X coordinate"
    )
    centerOfMassY = Double(
        displayedName="Center Y",
        description="Center of mass Y coordinate"
    )
    sigmaX = Double(
        displayedName="Sigma X",
        description="Standard deviation X"
    )
    sigmaY = Double(
        displayedName="Sigma Y",
        description="Standard deviation Y"
    )

    # Define the schema for incoming images
    class InputSchema(Configurable):
        daqDataType = DaqDataType.TRAIN
        image = Image(displayedName="Input Image")

    # Define the schema for outgoing images
    class OutputSchema(Configurable):
        daqDataType = DaqDataType.TRAIN
        image = Image(displayedName="Output Image")

    # Input and output channels
    input = InputChannel(InputSchema, displayedName="Input")  # ([rtd.xfel.eu](https://rtd.xfel.eu/docs/howtomiddlelayer/en/latest/chap4/intro_advanced.html?utm_source=chatgpt.com))
    output = OutputChannel(OutputSchema, displayedName="Output")  # ([rtd.xfel.eu](https://rtd.xfel.eu/downloads/howtomiddlelayer/latest/pdf/))

    @InputChannel(raw=False, displayedName="Input")
    async def input(self, data, meta):
        """Handle incoming image, compute COM and imprint crosshair."""
        img = data.image  # numpy ndarray

        # Compute center of mass and standard deviations
        y_idx, x_idx = np.indices(img.shape)
        total = img.sum()
        if total == 0:
            x_com = y_com = sigma_x = sigma_y = 0.0
        else:
            x_com = (img * x_idx).sum() / total
            y_com = (img * y_idx).sum() / total
            sigma_x = np.sqrt((img * (x_idx - x_com) ** 2).sum() / total)
            sigma_y = np.sqrt((img * (y_idx - y_com) ** 2).sum() / total)

        # Expose metrics
        self.centerOfMassX = x_com
        self.centerOfMassY = y_com
        self.sigmaX = sigma_x
        self.sigmaY = sigma_y

        # Imprint a crosshair spanning 1/10 of each axis at the COM
        out_img = img.copy()
        h, w = img.shape
        half_len_x = int(w * 0.1 / 2)
        half_len_y = int(h * 0.1 / 2)
        cx = int(round(x_com))
        cy = int(round(y_com))
        x_start = max(cx - half_len_x, 0)
        x_end = min(cx + half_len_x, w - 1)
        y_start = max(cy - half_len_y, 0)
        y_end = min(cy + half_len_y, h - 1)
        max_val = out_img.max()
        out_img[cy, x_start:x_end] = max_val
        out_img[y_start:y_end, cx] = max_val

        # Send out altered image
        self.output.schema.image = out_img
        await self.output.writeData()