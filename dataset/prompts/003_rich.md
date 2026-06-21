# Cardio-wellness Monitoring — Study Protocol

## Data endpoint
- CARP Web Service (`CarpDataEndPoint`)
- Upload method: stream
- Upload interval: **10 minutes**
- `deleteWhenUploaded: true`

## Participant roles
- `Participant` (single role)

## Devices
- **Primary**: Smartphone
- **Connected wearables**:
  - Polar HR Sensor (`PolarDevice`)
  - Movesense (`MovesenseDevice`)
- **Connected services**:
  - Location Service
  - Weather Service
  - Air Quality Service
  - Health Service

## Background sensing (`ImmediateTrigger` + `BackgroundTask`)

| source device | measures |
|---|---|
| Smartphone | timezone, free memory, device info, battery state, screen events, ambient light, step events, activity |
| Smartphone | connectivity, wifi, bluetooth |
| Location Service | location, mobility |
| Polar HR Sensor | HR, ECG |
| Movesense | state, HR, IMU |

## Periodic sensing (`PeriodicTrigger` + `BackgroundTask`)
- **Weather Service** — period 30 min (measure: `weather`)
- **Air Quality Service** — period 30 min (measure: `air quality`)

## App tasks

### One-shot
- **`OneTimeTrigger` → Wearable Setup Photo** (`AppTask`, image, 3 min) — at study start, photograph the wearable setup
- **`ElapsedTimeTrigger(1 h)` → Baseline Voice Recording** (`AppTask`, audio, 1 min) — one hour after study start

### Daily scheduled (`RecurrentScheduledTrigger(daily)`)
- **09:00** → Morning Meal Photo (`AppTask`, image, 3 min)
- **20:00** → Evening Meal Photo (`AppTask`, image, 3 min)

### Persistent (`NoUserTaskTrigger`, always on task list)
- **Voice Diary** (`AppTask`, audio, 2 min)
- **Physical Health Data** (`HealthAppTask`): weight, height, body fat percentage, body temperature
- **Cardiovascular Health Data** (`HealthAppTask`): heart rate, resting heart rate, HRV RMSSD, HRV SDNN, blood pressure systolic, blood pressure diastolic, blood oxygen
- **Activity Health Data** (`HealthAppTask`): steps, exercise time, distance walking/running, distance cycling, active energy burned, basal energy burned, total calories burned, flights climbed, respiratory rate, sleep awake, sleep in bed, sleep asleep, sleep deep, sleep light, sleep REM

### Chained (`UserTaskTrigger`)
- When **Voice Diary** is `done` → **Current Activity Photo** (`AppTask`, image, 3 min)
