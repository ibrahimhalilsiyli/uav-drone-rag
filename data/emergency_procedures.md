# UAV Emergency Procedures & Safety Regulations

This document defines critical protocols for managing immediate safety threats, physical damage, and battery fire hazards during UAV operations.

## 1. Geofence Breach Mitigation
Geofencing forms a digital boundary around the flight area to prevent flyaways.
- **Geofence Configuration**: Defined by a maximum radius (e.g., **500 meters** from home) and maximum altitude (e.g., **120 meters** AGL).
- **Breach Actions**:
  - **First-level Breach**: When the UAV approaches within 10 meters of the boundary, a warning is sent to the GCS, and speed is automatically capped.
  - **Hard Breach**: If the UAV crosses the geofence boundary, the autopilot enters **RTL (Return-to-Launch)** automatically.
  - **Manual Recovery**: The pilot must toggle the flight mode switch to manual (Stabilize or AltHold) to override the autonomous RTL if it is unsafe to return to takeoff location, but only if they have visual line of sight (VLOS).

## 2. Mid-Air Motor Loss Reaction
Motor loss management depends on the aircraft configuration:
- **Quadcopters (4 motors)**: A single motor failure results in an immediate loss of control. The UAV will yaw rapidly and crash. **Emergency Procedure**: Instantly activate the **Emergency Motor Kill Switch** to stop all spin and prevent battery rupture or motor fire upon ground impact.
- **Hexacopters (6 motors) / Octocopters (8 motors)**: The autopilot (ArduPilot/PX4) can dynamically redistribute thrust to compensate for a single motor failure.
  - **Autonomous Response**: The UAV will automatically yaw to distribute lift. The pilot will lose yaw control but maintain altitude and horizontal control.
  - **Pilot Action**: Immediately transition to a manual hover mode (Loiter or AltHold) and land the aircraft immediately at the nearest clear landing site. Do not attempt to complete the mission.

## 3. Emergency Motor Kill Switch Rules
The motor kill switch is a dedicated switch on the RC transmitter that bypasses normal flight code to cut power to all ESCs and stop the motors instantly.
- **Activation Criteria**: Trigger the kill switch ONLY in the following scenarios:
  1. The UAV is in an uncontrollable flyaway state, heading toward crowds or high-voltage power lines, and normal failsafes (RTL, manual override) have failed.
  2. The UAV has suffered a structural failure (e.g., wing or arm detachment) and is falling.
  3. A quadcopter has lost a motor and is spinning uncontrollably.
  4. Immediately upon landing or crashing to prevent motor burn-out or damage to bystanders.
- **Warning**: Activating the kill switch mid-air will cause the UAV to fall like a stone. Ensure no personnel are directly underneath.

## 4. LiPo Battery Fire Safety Protocols
Lithium Polymer (LiPo) batteries are highly volatile and can experience thermal runaway if damaged, short-circuited, or over-discharged.
- **In-Flight Battery Fire**:
  - Telemetry will show rapid voltage drop (under 3.0V/cell) and temperature exceeding **80°C**.
  - Land the UAV immediately in a clear, non-flammable area.
  - Evacuate all personnel at least 20 meters from the aircraft.
- **Ground Storage & Charging Fire**:
  - **Never use water** to extinguish a LiPo battery fire. Water reacts violently with lithium.
  - Use a **Class D Fire Extinguisher** (for metal fires) or smother the fire with dry sand or a heavy-duty fire blanket.
  - Place burning batteries in a steel containment box or a LiPo-safe charging bag.
  - If a battery begins to swell (puff) or smoke during charging, disconnect power immediately, place it on a concrete surface, and monitor it from a safe distance for at least 30 minutes.
