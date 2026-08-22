# UAV Pre-Flight Checklist & Maintenance Guide

This document details the standard pre-flight inspection procedures, battery voltage thresholds, structural torque specifications, and IMU calibration guidelines for commercial UAV operations.

## 1. Visual Inspection Routine
Perform a comprehensive walk-around of the UAV before powering on the avionics:
- **Chassis Inspection**: Check carbon fiber arms for hairline cracks or fatigue. Verify that motor mounts are rigid and free of play.
- **Wiring & Connectors**: Ensure XT90/AS150 battery connectors are clean and show no signs of electrical arcing. Verify routing of telemetry and GPS cables away from high-current power leads.
- **Camera & Payload**: Clean payload lenses. Ensure the gimbal dampening balls are intact and the gimbal moves freely on all three axes without binding.

## 2. Propeller Torque Specifications
Pervane (propeller) tork ve sıkılık değerleri motor şaftı stabilitesi için kritiktir:
- **Direct-Mount Props**: Standard M3 screws on carbon propellers must be torqued to **1.2 Nm (Newton-meters)** using a calibrated torque driver. Apply a drop of medium-strength blue threadlocker (Loctite 243) to secure threads.
- **Quick-Release Adaptors**: Inspect adaptor pins for wear. Ensure the locking mechanism clicks securely into place.
- **Caution**: Over-tightening causes microscopic fracturing in carbon fiber props, while under-tightening leads to mid-air propeller detachment.

## 3. Battery Voltage Thresholds
LiPo battery management is crucial for preventing critical in-flight failures:
- **Maximum Cell Voltage**: A fully charged standard LiPo cell must register **4.20V per cell**. Do not exceed 4.25V under any circumstances.
- **Nominal Cell Voltage**: **3.70V per cell**.
- **Minimum Safe Flight Voltage**: **3.50V per cell** under load. Land immediately if voltage drops below this point.
- **Storage Voltage**: If batteries are to be stored for more than 48 hours, discharge or charge them to **3.80V - 3.85V per cell** to prevent swelling and capacity degradation.

## 4. Inertial Measurement Unit (IMU) Calibration Steps
IMU calibration must be performed after any major hardware modification, firmware update, or when telemetry warns of compass/accelerometer inconsistency.
1. Place the UAV on a perfectly level, vibration-free surface.
2. Connect to the Ground Control Station (GCS) via telemetry or USB.
3. Select "IMU Calibration" / "3D Accel Calibration".
4. Follow the GCS prompts to place the UAV on each of its six sides:
   - Level (flat on landing gear)
   - Left side
   - Right side
   - Nose down
   - Nose up
   - Back side (inverted)
5. Hold the vehicle completely still for 5 seconds on each side until the GCS confirms capture.
6. Reboot the flight controller (Pixhawk / Cube) to apply new calibration parameters.
