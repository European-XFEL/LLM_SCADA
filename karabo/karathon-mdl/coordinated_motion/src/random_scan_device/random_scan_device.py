# src/random_scan_device.py
import math
import random
import itertools

from karabo.middlelayer import (
    Device, Slot, String, Int32, Double, Overwrite, State,
    connectDevice
)

__version__ = "1.0"


class RandomScanDevice(Device):
    """
    A Karabo middlelayer device that performs a random scan on two motion axes.
    Motors are connected by ID strings using connectDevice().
    """

    motorXId = String(
        assignment="MANDATORY",
        description="Device ID of X motor")
    motorYId = String(
        assignment="MANDATORY",
        description="Device ID of Y motor")

    numPoints = Int32(
        defaultValue=5,
        description="Number of random scan points")

    xMin = Double(
        defaultValue=0.0,
        description="Minimum X limit (inclusive)")
    xMax = Double(
        defaultValue=1.0,
        description="Maximum X limit (inclusive)")
    yMin = Double(
        defaultValue=0.0,
        description="Minimum Y limit (inclusive)")
    yMax = Double(
        defaultValue=1.0,
        description="Maximum Y limit (inclusive)")

    # Our own state machine
    state = Overwrite(
        defaultValue=State.ACTIVE,
        options={State.ACTIVE, State.PROCESSING, State.MOVING, State.ERROR})
    status = String(
        defaultValue="",
        description="Human‐readable status message")

    async def onInitialization(self):
        # Connect to the two motor devices by their IDs :contentReference[oaicite:0]{index=0}
        self.motorX = await connectDevice(self.motorXId)
        self.motorY = await connectDevice(self.motorYId)
        self.status = "Connected to motors"
        self.state = State.ACTIVE

    @Slot(displayedName="Start Scan", allowedStates={State.ACTIVE})
    async def start(self):
        """Generate random points, compute optimal path, and move both motors."""
        self.state = State.PROCESSING
        try:
            # 1) Generate random locations
            points = [
                (random.uniform(self.xMin, self.xMax),
                 random.uniform(self.yMin, self.yMax))
                for _ in range(self.numPoints)
            ]

            # 2) Compute the shortest path (TSP by brute force for small N)
            path = self._calculate_optimal_path(points)

            # 3) Perform the scan
            self.status = "Starting scan"
            self.state = State.MOVING
            for x, y in path:
                self.motorX.targetPosition = x
                await self.motorX.move()
                self.motorY.targetPosition = y
                await self.motorY.move()

            self.status = "Scan complete"
            self.state = State.ACTIVE

        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            self.status = "Error during scan"
            self.state = State.ERROR

    @Slot(displayedName="Reset", allowedStates={State.ERROR})
    async def reset(self):
        """Reset the device from ERROR back to ACTIVE."""
        self.state = State.ACTIVE
        self.status = ""
        try:
            await self.motorX.reset()
            await self.motorY.reset()
        except Exception:
            pass

    def _calculate_optimal_path(self, points):
        """Brute‐force TSP solver: find the permutation of points with minimal total distance."""
        best = None
        shortest = float("inf")
        for perm in itertools.permutations(points):
            dist = sum(
                math.hypot(perm[i+1][0] - perm[i][0],
                           perm[i+1][1] - perm[i][1])
                for i in range(len(perm) - 1)
            )
            if dist < shortest:
                shortest = dist
                best = perm
        return list(best)
