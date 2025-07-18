# AI Coding tests for Scientific SCADA Systems

The aim of this repo is to gather experience with the quality of code 
LLMs can output when given the task to write devices/servers for 
scientific SCADA systems, such as Karabo, Tango/Bliss, and EPIC/Ophyd/Bluesky.

## Tests

The tests aim to cover realistic requirements developers might be asked to
implement in such systems. At the same time, they are designed such that
they can be executed on a common Linux system, without the need for specific
hardware. Furthermore, the tests aim to test the capability of the AI to 
produce code for the SCADA system, rather than solve generic coding problems.

Tests consist of performing the scenarios below, using a current LLM model.
Adapt the parts in curly braces to match your SCADA framework.

Results are evaluated by comparing the diff of the the initial AI output,
with respect to a working version. The AI may be asked to revise the
code once with additional human input before the comparison is made.

Creating an appropriate folder structure for the programming language in use
does is not included into the diff in anyway. For Python, this includes
the creation of `__init__.py` files.

Python tests should be run with, unless the SCADA framework requires
otherwise.

```
pytest --cov .
```

The line diff counts should be evaluated by commiting the unaltered
AI-provided code (possibly after a single iteration), and then using
`git diff` on the device, and test file(s):

```
git diff 0b33325 src/random_scan_device/test/test_random_scan_device.py | \
   awk 'BEGIN{a=0;d=0} /^+[^+]/{a++} /^-[^-]/{d++} END{print a, d}'
```


## Scenarios

Each scenario consists of a template prompt, adapted to the framework, and
a follow-up request to produce a setup/installation file for the code that
was created.

One additional iteration may be requested from the model afterwards.

### Scenario 1: Monitoring Device

This is the simplest case. The AI is instructed to write a device/server that
monitors the CPU and memory consumption of its own process.

The template prompt is as follows:

```quote
I would like you to write me a {SCADA FRAMEWORK} {device/server/...} 
that monitors the CPU usage and memory consumption of it's own (linux) process. 

You can find the {SCADA FRAMEWORK} documentation here, and the links therein: 
{... LINKS to relevant DOCUMENTATION ...}

Use the best practices described therein. Create a single {Python/C++/...} file 
for the {device/server/...}, and another file which contains unit tests 
for the functionality you implement. {SCADA FRAMEWORK} {devices/servers/...}  
are generally tested like this:

{Brief outline of testing best practice, such as code snippets.}
```

### Scenario 2: Coordinated Motion and Scanning

Here the AI is asked to implement a scan, coordinating two motion stages in 
the process. This is a common requirement, and tests the capability of the 
AI to produce code that

- executes actions in a distributed system
- coordinates such actions
- is state-aware, i.e. waits on the motors to move (and stop)
- reconfigures and reads back properties, here the motor positions

The output should be tested by implementing simulated motors that implement
a common interface.

The template prompt is as follows:

```quote
I would like you to write me a {SCADA FRAMEWORK} {device/server/...} that 
implements a random scan functionality on motion axes.  When "start" is clicked, 
it creates a user-configurable number of random locations between 
configurable x- and y- limits. It then calculates the optimum path to scan
all points, assuming motion sytems with a constant velocity. Finally, it 
performs the scan, controlling two motors. When idle or started, the 
device state is {ACTIVE}, when it's calculating, the state is {PROCESSING},
and when it's performing the scan, the state is {MOVING}.

The motors are individual devices in the distributed system. 
They have a common interface: a new position is set on the `targetPosition` 
float property, the motor is then issued a `move` command, which transitions 
it to the {MOVING} state, and the motor is done moving when it is not in 
the {MOVING} state anymore. If an error occurs the motor goes into an 
{ERROR} state. If this happens the scan is stopped, the device goes to 
{ERROR}, and it can be reset to {ACTIVE} using a `reset` command.

You can find the {SCADA FRAMEWORK} documentation here, and the links therein: 
{... LINKS to relevant DOCUMENTATION ...}

Use the best practices described therein. Create a single {Python/C++/...} file 
for the {device/server/...}, and another file which contains unit tests 
for the functionality you implement. For your test implement 2 simulated motors
with the above interface, and test that a scan completes, and also that an
optimal path is calculated. 

{SCADA FRAMEWORK} {devices/servers/...}  
are generally tested like this:

{Brief outline of testing best practice, such as code snippets.}
```

### Scenario 3: Image Processing

The template prompt is as follows:

```quote
I would like you to write me a {SCADA FRAMEWORK} {device/server/...} that 
implements an image processor that calculates and exposes the center of 
mass coordinates of the image, alongside their respective standard deviations.

The images are to be received through an {input channel} from another device,
and are located at {location}. The device is then to imprint the center of 
mass location as a crosshair which span 1/10s of the image dimension on that 
axis. The altered image is then sent out using an {output channel}.

You can find the {SCADA FRAMEWORK} documentation here, and the links therein: 
{... LINKS to relevant DOCUMENTATION ...}


Use the best practices described therein. Create a single {Python/C++/...} file 
for the {device/server/...}, and another file which contains unit tests 
for the functionality you implement. For your test implement a
{device/server/...} that produces the test images using a 2d Gaussian profile
and added noise, and a receiver device that receives the altered images. 
The test should check that the center of mass coordinates reasonably match 
the gaussion parameters, and that the imprinted crosshair corresponds to the 
evaluated center of mass coordinates.

{SCADA FRAMEWORK} {devices/servers/...}  
are generally tested like this:

{Brief outline of testing best practice, such as code snippets.}
```

## Contributing Results for a new Framework

To contribute results for a new SCADA framework, put up a PR which includes
the results under a top-level folder naming the framework, the API, and then 
code the AI produced within. See the `karabo` folder for an example.

Adapt the prompt to the framework you are testing, but don't add more detail
than in existing examples.

## Results

### Karabo

#### Scenario 1

The functionality was correctly implemented, and the tests cover the relevant
aspects.

The device itself worked out of the box. The test required minor fixes, in
that reusing a device ID within two tests is flaky, and should be avoided.

Commits 9f0d181 vs. 8bce1dc

- **Model used**: OpenAI o4-mini-high
- **Add. Iterations**: 0
- **Chat log**: https://chatgpt.com/share/6878e4e3-1550-8003-bcf5-4f48795dda9e
- **Lines added to get running (device)**: 0
- **Lines removed to get running (device)**: 0
- **Lines added to get running (tests)**: 5
- **Lines removed to get running (tests)**: 5
- **Test coverage:** 81%

#### Scenario 2

The device itself required minor modifications: the `Assignment` 
specification is done through an `enum` and not `string`.
The test required minor modifications on initializing the devices, using 
keywords rather than a list paramter. Also the expected pathlength was 
mis-calculated by the AI, as it assumed the motors returning to the initial
position, while in fact the scan would finish on the last position.

Commits 0b33325 vs. f2b1bef

- **Model used**: OpenAI o4-mini-high
- **Add. Iterations**: 1
- **Chat log**: https://chatgpt.com/share/687a396a-436c-8003-a9e3-28189ff4707c
- **Lines added to get running (device)**: 3
- **Lines removed to get running (device)**: 3
- **Lines added to get running (tests)**: 3
- **Lines removed to get running (tests)**: 3

#### Scenario 3

The device and the test worked with minor modifications: `Image` property 
definitions were incomplete, lacking shape and data type attributes.
Additionally, the AI did not realize that `ImageData` does not automatically
convert to `numpy.ndarray` in all cases. A few delays had to be added for
the test to succeed, and the the model hallucinated a connection establishment
short-cut in testing that doesn't exist. Finally, 

Commits 09a4992 vs. 7783d77

- **Model used**: OpenAI o4-mini-high
- **Add. Iterations**: 1
- **Chat log**: https://chatgpt.com/share/687a3b7d-8408-8003-8585-d0bb5484afc6
- **Lines added to get running (device)**: 13
- **Lines removed to get running (device)**: 5
- **Lines added to get running (tests)**: 18
- **Lines removed to get running (tests)**: 5
- **Test coverage:** 98%