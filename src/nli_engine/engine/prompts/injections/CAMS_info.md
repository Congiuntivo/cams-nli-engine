## CAMS

### What is CAMS

CAMS (CARP Mobile Sensing) is a framework for building mobile health sensing studies. Authoring a study means defining a `SmartphoneStudyProtocol` that specifies what data to collect, from which devices, and when — without writing application code.

### Study Protocol

A `SmartphoneStudyProtocol` is the root container. At the top level it is composed of:

- **Participant roles**: who takes part in the study. Most studies are individual (one participant per deployment), so the protocol usually has a single role (e.g. `"Participant"`).
- **Expected participant data**: metadata the platform collects about each participant before the study starts — e.g. name, address, informed consent, sex, age. Each entry declares a field name, type, and whether it is required. Declared fields are collected automatically during participant onboarding — they do not require a task, trigger, or task control.
- **Data endpoint**: where the collected data is stored and sent. Specifies the backend (e.g. a CARP server) and connection parameters.
- **Task controls**: the bindings that wire triggers to tasks on specific devices — these are the core of what a study does.

Within those task controls, the protocol also holds the full set of devices, tasks, and triggers that together define a study.

### Devices

A protocol always has at least one primary device and may have any number of connected devices.

- **PrimaryDevice**: the device running CAMS — either a smartphone or a web browser. Always present. Identified by a `roleName` (e.g. `"Smartphone"`).
- **ConnectedDevice**: anything external attached to the primary device. Can be a physical wearable (Polar, Movesense, eSense) or a service (location, weather, air quality). Must reference the primary device via `primaryDeviceRoleName`.

### Services

Some measure types are **not collected on the Smartphone directly** — they are collected through a service device that must be registered as a connected device first. The task that collects from a service must target the **service's role name**, not `"Smartphone"`.

| Measure type                | Required service device | Default role name |
| --------------------------- | ----------------------- | ----------------- |
| `dk.cachet.carp.location`   | LocationService         | `"Location"`      |
| `dk.cachet.carp.weather`    | WeatherService          | `"Weather"`       |
| `dk.cachet.carp.airquality` | AirQualityService       | `"AirQuality"`    |

### Measures

A measure specifies a single type of data to collect. Measure types follow the format `dk.cachet.carp.<type>` (e.g. `dk.cachet.carp.acceleration`).

Two sampling modes:

- **Event-based (EB)**: continuously samples once started; runs until explicitly stopped. Examples: `acceleration`, `polar.hr`, `stepevent`, `screenevent`.
- **One-time (OT)**: produces a single value when triggered. Examples: `weather`, `deviceinformation`, a `location`.

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
