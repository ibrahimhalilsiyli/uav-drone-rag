# ArduPilot & PX4 Flight Controller Diagnostics

This guide provides troubleshooting steps and diagnostics for common autopilot telemetry errors, compass issues, ESC sync failures, and EKF health anomalies.

## 1. Common Telemetry Status Codes & LED Meanings
Autopilot status LEDs and GCS telemetry alerts communicate real-time health data:
- **Flashing Blue LED**: The flight controller is searching for GPS lock. Do not arm.
- **Flashing Green LED**: GPS lock is acquired, and the system is ready to arm.
- **Solid Green LED**: GPS lock acquired, system is armed and ready for flight.
- **Flashing Red/Yellow LED**: Pre-arm check failure. Check GCS text console for error messages.
- **Telemetry Code `STAT_BOOT_OK`**: Internal boot sequence succeeded.
- **Telemetry Code `ERR_GYRO_OUT_OF_SPEC`**: Accelerometer/gyro initialization failed due to motion during boot. Disconnect battery, place UAV on a stable surface, and power cycle.

## 2. Compass Variance Errors (`Error: Yaw/Compass Variance`)
Compass variance errors occur when the flight controller detects a discrepancy between the multiple onboard magnetometers or between the compass heading and the GPS velocity vector.
- **Root Causes**: Electromagnetic interference (EMI) from high-current power wiring, proximity to ferrous metals (reinforced concrete landing pads), or incorrect orientation parameters.
- **Troubleshooting Steps**:
  1. Move the UAV at least 5 meters away from metallic structures, vehicles, and concrete pads.
  2. Inspect wiring: ensure the GPS/Compass mast is raised and high-current power cables are twisted to cancel magnetic fields.
  3. Perform a **Compass Calibration** (Compass Mot) in an open field away from external interference.
  4. If variance persists, disable the secondary internal compass and rely solely on the external GPS/compass module.

## 3. Electronic Speed Controller (ESC) Sync Failure
An ESC sync failure occurs when the motor and ESC lose synchronization, leading to motor stuttering, excessive heat, or mid-air power loss.
- **Symptoms**: Motor makes a high-pitched chirping sound, hesitates under rapid throttle changes, or spins slowly and heats up rapidly.
- **Troubleshooting & Calibration**:
  1. **ESC Calibration**: Re-calibrate the ESC throttle range. Remove propellers, connect GCS, set throttle to maximum, connect battery, wait for ESC beeps, and drop throttle to minimum.
  2. **Motor Timing**: Adjust motor timing in the ESC firmware (e.g., BLHeli Suite). Set timing to "Medium-High" or "High" for high-pole-count motors.
  3. **Update Rate**: Lower the autopilot servo output frequency (`SERVO_RATE` in ArduPilot) from 400Hz to 200Hz to verify if signal noise is the cause.

## 4. Extended Kalman Filter (EKF) Health Checks
The EKF fuses data from IMU, GPS, and compass sensors to estimate the UAV's position, velocity, and attitude.
- **EKF Status Monitoring**: In the Ground Control Station, monitor the EKF status box. The primary indicators are Velocity, Position, and Altitude variances.
- **Red EKF Status (Variance > 0.8)**: Triggered by high vibration levels (causing sensor clipping), sudden compass offsets, or GPS multipath interference.
- **Action**: Do not switch to GPS-dependent flight modes (Auto, Loiter). Perform an immediate manual landing in AltHold or Stabilize mode. Check vibration dampening on the flight controller board.
