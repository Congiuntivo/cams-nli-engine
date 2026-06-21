# Case 003 — "Cardio-wellness monitoring" (hard)

Plan for the third dataset case. Goal: a protocol-complexity step above 002, exercising API surface not used by 001/002. Inspired by `carp_study_app_configurations/app_store/test/app_store_protocol.dart` and `demo/test/carp_demo_protocol.dart`.

## Constraints

- No surveys / research package (not implemented in engine).
- No multi-participant protocols (not implemented in engine).
- No `CronScheduledTrigger` (deliberately excluded by user, even though supported).

## Devices & services

- **Primary:** Smartphone
- **Connected wearables:** Polar HR Sensor, Movesense
- **Connected services:** LocationService, WeatherService, AirQualityService, HealthService

## Background sensing — `ImmediateTrigger`

| On                   | Measures                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| Phone                | timezone, free memory, device info, battery, screen events, ambient light, step events, activity |
| Phone (connectivity) | connectivity, wifi, bluetooth                                                                    |
| Location service     | location, mobility                                                                               |
| Polar                | HR, ECG                                                                                          |
| Movesense            | STATE, HR, IMU                                                                                   |

## Periodic sensing — `PeriodicTrigger`

- Weather **every 30 min** (weather service)
- Air quality **every 30 min** (air quality service)

## Scheduled — `RecurrentScheduledTrigger`

- **09:00 daily** — image app task "morning meal photo" (3 min)
- **20:00 daily** — image app task "evening meal photo" (3 min)

## One-time — `OneTimeTrigger`

- At start — image app task "photograph your wearable setup" (3 min)

## Elapsed time — `ElapsedTimeTrigger`

- **1 h after study start** — audio app task "baseline voice recording" (1 min)

## Persistent `HealthAppTask`s — `NoUserTaskTrigger`

| Task title                 | Types                                                                                                                                                                                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Physical Health Data       | weight, height, body fat %, body temperature                                                                                                                                                                                                       |
| Cardiovascular Health Data | heart rate, resting heart rate, HRV RMSSD, HRV SDNN, blood pressure systolic, blood pressure diastolic, blood oxygen                                                                                                                               |
| Activity Health Data       | steps, exercise time, distance walking/running, distance cycling, active energy burned, basal energy burned, total calories burned, flights climbed, respiratory rate, sleep awake, sleep in bed, sleep asleep, sleep deep, sleep light, sleep REM |

## Persistent audio task — `NoUserTaskTrigger`

- Audio app task "voice diary" (2 min)

## Chained task — `UserTaskTrigger`

- **When voice diary is `done`** → trigger image app task "photograph your current activity" (3 min)

## Data endpoint

- CARP Web Service, stream upload, **upload interval 10 min**, **`deleteWhenUploaded: true`**

## Complexity vector

Descriptive complexity per case (no composite score — see eval plan discussion).

| dimension                             | 001     | 002   | 003                                                                                     |
| ------------------------------------- | ------- | ----- | --------------------------------------------------------------------------------------- |
| #measures (background + periodic)     | ~2      | ~15   | ~20                                                                                     |
| #app tasks                            | 0       | 2     | 8                                                                                       |
| #trigger declarations (task controls) | 2       | ~5    | ~15                                                                                     |
| distinct trigger types                | 1–2     | 2     | 6 (Immediate, Periodic, RecurrentScheduled, OneTime, ElapsedTime, UserTask, NoUserTask) |
| connected devices/services            | 1       | 4     | 6                                                                                       |
| inter-task dependencies               | 0       | 0     | 1 (voice diary → follow-up image)                                                       |
| `deleteWhenUploaded`                  | default | false | true                                                                                    |

## Open items

- Point (b): design the three richness levels of the prompt for case 003 (rich / medium / poor) and back-fill the missing richness levels for 001 and 002 to complete the 3x3 grid.
- Eval method: F1 against canonical `expected.json`. Number of runs per cell still TBD (affects whether variance claims have statistical teeth).
