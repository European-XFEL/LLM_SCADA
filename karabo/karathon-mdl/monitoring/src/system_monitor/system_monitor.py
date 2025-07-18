# system_monitor.py

import os
import psutil

from karabo.middlelayer import (
    Device,
    AccessMode,
    Assignment,
    DaqPolicy,
    Double,
    AsyncTimer,
)


class SystemMonitor(Device):
    """
    A Karabo middlelayer device that monitors its own CPU usage (percent)
    and memory RSS (MB), sampling once per second.
    """

    __version__ = "2.0"

    cpuUsage = Double(
        displayedName="CPU Usage (%)",
        description="CPU usage percentage of this process",
        accessMode=AccessMode.READONLY,
        assignment=Assignment.INTERNAL,
        daqPolicy=DaqPolicy.SAVE,
    )

    memoryUsage = Double(
        displayedName="Memory Usage (MB)",
        description="Resident memory usage of this process in MB",
        accessMode=AccessMode.READONLY,
        assignment=Assignment.INTERNAL,
        daqPolicy=DaqPolicy.SAVE,
    )

    def __init__(self, config):
        super().__init__(config)
        # psutil Process for the current PID
        self._process = psutil.Process(os.getpid())
        self._timer: AsyncTimer | None = None

    async def onInitialization(self):
        # Initialize properties
        self.cpuUsage = 0.0
        self.memoryUsage = float(self._process.memory_info().rss) / (1024 * 1024)
        # Set up a repeating timer (every 1 s) to resample
        self._timer = AsyncTimer(self._sample, timeout=1.0)
        self._timer.start()

    async def _sample(self):
        # Sample CPU and memory, then publish
        cpu = self._process.cpu_percent(interval=None)
        mem = float(self._process.memory_info().rss) / (1024 * 1024)
        self.cpuUsage = cpu
        self.memoryUsage = mem
        # Trigger the update of both properties
        self.update()

    async def onDestruction(self):
        # Cleanly stop the timer
        if self._timer is not None:
            self._timer.stop()
