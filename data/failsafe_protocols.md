# UAV Failsafe Protocols & Autonomous Fallbacks

This document outlines the standard failsafe routines configured on the autopilot (ArduPilot/PX4) to preserve aircraft integrity during signal, power, or component failures.

## 1. Low-Battery Return-to-Launch (RTL) Failsafe
The low-battery failsafe is triggered based on remaining voltage or estimated capacity:
- **Failsafe Threshold**: Set to trigger when battery voltage drops below **3.60V per cell** for more than 5 consecutive seconds, or when remaining capacity reaches **25%**.
- **Action Sequence (RTL)**:
  1. The autopilot sounds an audible alarm and flashes telemetry warnings.
  2. The UAV halts its current mission and climbs to the pre-configured safe RTL altitude (default: **30 meters** above home, or current altitude if higher).
  3. The UAV flies directly back to the takeoff (Home) coordinates at a speed of **8 m/s**.
  4. Upon reaching the home position, the UAV hovers for 5 seconds, then performs a controlled vertical landing at **0.5 m/s** and disarms its motors automatically.
- **Critical Override**: If the battery drops to **3.40V per cell** (Critical Battery Failsafe), the UAV bypasses RTL and performs an immediate landing (Land Mode) at its current location to prevent catastrophic battery exhaustion.

## 2. GPS Signal Loss Fallback (AltHold Mode)
When the GPS/GNSS receiver loses signal lock (HDOP > 2.0 or satellite count < 6) during autonomous flight:
- **Automatic Fallback to AltHold**: The autopilot can no longer maintain horizontal position hold. It immediately transitions from Auto or Loiter mode into **Altitude Hold (AltHold) Mode**.
- **Flight Behavior under AltHold**:
  - The autopilot controls the barometer to maintain the current altitude automatically.
  - The pilot must immediately take manual control of the roll and pitch axes using the RC transmitter to navigate the aircraft back safely.
  - **Caution**: The drone will drift horizontally with the wind in AltHold mode. The pilot must actively counteract drift.
- **Auto-Recovery**: If GPS lock is restored for 3 consecutive seconds, the drone will hover in place and await pilot mode selection or resume its previous path if in an autonomous mission.

## 3. RC Transmitter Link Loss Procedures (Failsafe)
If the connection between the ground station RC transmitter (radio controller) and the onboard RC receiver is lost for more than **1.5 seconds** (e.g., due to interference, range limits, or transmitter battery failure):
- **Receiver Behavior**: The receiver outputs a pre-programmed channel 3 (Throttle) pulse-width modulation (PWM) value below **975 µs** (standard throttle range is 1000 µs - 2000 µs), signaling a loss of signal to the autopilot.
- **Autopilot Response Options**:
  - **In Mission (Auto Mode)**: If the drone is executing an autonomous waypoint mission, it is configured to continue the mission to completion if GPS is active, or trigger RTL depending on regional aviation authority requirements.
  - **In Manual/Loiter Mode**: The autopilot immediately executes a **Return-to-Launch (RTL)** sequence.
  - **Re-establishment**: If the RC link is re-established during the RTL sequence, the pilot can reclaim manual control by toggling the flight mode switch on the transmitter.
