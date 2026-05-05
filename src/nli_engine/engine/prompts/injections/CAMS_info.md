## CAMS

### What is CAMS

CAMS (CARP Mobile Sensing) is a framework for building mobile health sensing studies. Authoring a study means defining a `SmartphoneStudyProtocol` that specifies what data to collect, from which devices, and when — without writing application code.

### Study Protocol

A `SmartphoneStudyProtocol` is the root container. It holds the full set of devices, tasks, triggers, and task controls that together define a study.

### Devices

A protocol always has at least one primary device and may have any number of connected devices.

- **PrimaryDevice**: the device running CAMS — either a smartphone or a web browser. Always present. Identified by a `roleName` (e.g. `"Smartphone"`).
- **ConnectedDevice**: anything external attached to the primary device. Can be a physical wearable (Polar, Movesense, eSense) or a service (location, weather, air quality). Must reference the primary device via `primaryDeviceRoleName`.

### Measures

A measure specifies a single type of data to collect. Measure types follow the format `dk.cachet.carp.<type>` (e.g. `dk.cachet.carp.accelerometer`).

Two sampling modes:

- **Event-based (EB)**: continuously samples once started; runs until explicitly stopped. Examples: accelerometer, heart rate, steps, screen events.
- **One-time (OT)**: produces a single value when triggered. Examples: weather data, device info, a location snapshot.

The mode matters when choosing a trigger.

### Tasks

A task groups one or more measures to collect together. Two types:

- **BackgroundTask**: passive background sensing; no user interaction.
- **AppTask**: involves the app or user — surveys, ecological momentary assessments (EMAs), cognitive tests, or any active data collection.

Each task targets a specific device role.

### Triggers

A trigger defines when a task starts or stops. The trigger type must match the measure mode:

- **EB measures**: a one-shot trigger (e.g. `ImmediateTrigger`) is sufficient — the task runs continuously once started.
- **OT measures**: require a recurring trigger (e.g. `PeriodicTrigger`, `CronScheduledTrigger`) so sampling fires repeatedly over time.

Other trigger types: `DelayedTrigger`, `ManualTrigger`, `NoOpTrigger`.

### Task Controls

A `TaskControl` is the binding that connects a trigger to a task on a specific device:

```
trigger → task → device role
```

It also specifies whether the control **starts** or **stops** the task. A protocol typically has one task control per (trigger, task, device) combination.
