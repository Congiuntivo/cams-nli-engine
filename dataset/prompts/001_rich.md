# Diary Study — Study Protocol

## Devices
- **Primary**: Smartphone
- **Connected service**: Location Service

## Background sensing (`ImmediateTrigger` + `BackgroundTask`)
- Smartphone — `step events`

## Periodic sensing (`PeriodicTrigger` + `BackgroundTask`)
- Location Service — measure `location`, period **1 hour**

## Expected participant data
- `full_name`, assigned to the `Participant` role, requested at study start

## Data endpoint
- CARP Web Service (`CarpDataEndPoint`, stream upload)
