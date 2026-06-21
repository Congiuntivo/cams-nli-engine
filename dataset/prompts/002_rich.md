# Study Protocol

## Data endpoint
- CARP Web Service (`CarpDataEndPoint`, stream upload)
- `deleteWhenUploaded: false` — retain data on device after upload

## Devices
- **Primary**: Smartphone
- **Connected services**: Location Service, Weather Service, Air Quality Service, Health Service

## Background sensing (`ImmediateTrigger` + `BackgroundTask`)

| source device | measures |
|---|---|
| Smartphone | step events, location, battery state, screen events, ambient light, activity, device info |
| Smartphone | connectivity, wifi, bluetooth |

## Periodic sensing (`PeriodicTrigger` + `BackgroundTask`)
- **Weather Service** — period 30 min — measure: `weather`
- **Air Quality Service** — period 30 min — measure: `air quality`
- **Health Service** — period 60 min — types: weight, BMI, birth date, gender, steps, heart rate, HRV RMSSD, HRV SDNN, sleep awake, sleep in bed, sleep asleep, sleep deep, sleep light, sleep REM

## App tasks (`AppTask` image, persistent via `NoUserTaskTrigger`)
- **Best Demo Photo** — user uploads a picture of the best demo they have seen — ~3 min
- **Best Gadget Photo** — user uploads a picture of the best gadget they received — ~3 min
