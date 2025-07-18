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
Results are evaluated by comparing the diff of the the initial AI output,
with respect to a working version, and then a version into which a human
implemented current best practices. The AI may be asked to revise the
code once with additional human input before the comparison is made.

Creating an appropriate folder structure for the programming language in use
does is not included into the diff in anyway. For Python, this includes
the creation of `__init__.py` files.

## Scenarios

Each scenario consists of a template prompt, adapted to the framework, and
a follow-up request to produce a setup/installation file for the code that
was created.

One additional iteration may be requested from the model afterwards.

### Monitoring Device

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

### Coordinated Motion and Scanning

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
I would like you to write me a {SCADA FRAMEWORK} {device/server/...} implements
a random scan functionality on motion axes.  When "start" is clicked, 
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

The device itself worked out of the box. The test required minor fixes, in
that reusing a device ID within two tests is flaky, and should be avoided.


