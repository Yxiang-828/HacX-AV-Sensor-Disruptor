# Dual-Mode AV Disruptor

A non-destructive prototype to stop hostile autonomous vehicles (AVs) by disrupting their sensors (LiDAR, camera, radar) at a 15m range for speeds up to 20 km/h. Built for the HacX hackathon (HTX + Microsoft, Nov 12, 2025). Repository: github.com/Yxiang-828/HacX-AV-Sensor-Disruptor.

## Problem Overview
Hostile AVs (hijacked or malfunctioning) pose public safety risks, acting as "2-ton missiles." Current countermeasures (e.g., EMP, kinetic) are destructive or impractical for first responders. This project fills the gap with a portable, non-destructive device that forces AV emergency stops by disrupting sensor perception. Why included? The problem defines design constraints (15m range, 20 km/h, non-destructive). See docs/problem_brief.md for full 5W1H analysis (WHO: HTX, WHAT: sensor disruption, WHERE: roadside, WHEN: Nov 12, WHY: safety gap, HOW: laser/LED pulses). Logical link: Guides hardware choices in hardware/parts_list.md and tasks in docs/checklists.md.
## Solution

The Dual-Mode AV Disruptor uses a Raspberry Pi Zero/4 to control:

Smoke Bomb Mode: Chaotic IR pulses (1550nm laser, 850nm LEDs) to overwhelm sensors, ensuring a stop in high-threat scenarios.
Smart Obstacle Mode: Detection-triggered pulses (laser 0.15s at 80% duty, LEDs 0.08s at 60%) to spoof obstacles, saving power for prolonged use.
Detection: mmWave radar (RD-03D/MR60FDA2, UART) and photodiode (BPW34, GPIO 22) detect AV signals, with manual trigger (GPIO 26) as fallback.
Safety: DS18B20 temp sensor (GPIO 23), 5V fan (GPIO 24), 10A fuse (GPIO 25).
Specs: ~$342, <500g, 20x10x5 cm, battery-powered (28 min Smoke, 1.2h Smart).

Why included? The solution translates the problem into a tangible system, linking to hardware/schematic.txt (wiring) and src/main.py (control logic).

## System Architecture
The system integrates inputs (toggle switch, detection), processing (RPi GPIO/UART), outputs (laser/LED pulses), and safety checks. The state diagram below shows mode transitions, from boot to mode selection to emission loops, with safety interrupts. Why included? Visualizes runtime behavior—laymen see why dual modes exist (fail-safe vs. efficient), judges see safety integration.

```mermaid
stateDiagram-v2
    [*] --> Idle: Boot RPi, run main.py
    Idle --> ModeCheck: Poll GPIO 21 every 0.1s
    ModeCheck --> SmokeBomb: GPIO 21 HIGH
    ModeCheck --> SmartObstacle: GPIO 21 LOW
    SmokeBomb: Smoke Bomb Mode
    SmokeBomb --> ChaoticEmissions: Check safety/overheat
    ChaoticEmissions: Random pulses (laser/LEDs, 80% duty)
    ChaoticEmissions --> SmokeBomb: Continue loop
    SmokeBomb --> ModeCheck: Switch flipped or overheat
    SmartObstacle: Smart Obstacle Mode
    SmartObstacle --> DetectSignal: Check safety/overheat
    DetectSignal: Poll mmWave/photodiode or GPIO 26 button
    DetectSignal --> TargetedSpoofing: Signal detected
    TargetedSpoofing: Sequence pulses (laser 0.15s 80%, LEDs 0.08s 60%)
    TargetedSpoofing --> SmartObstacle: Continue loop
    DetectSignal --> SmartObstacle: No signal
    SmartObstacle --> ModeCheck: Switch flipped or overheat
    ModeCheck --> Idle: Shutdown (KeyboardInterrupt)
```

## Algo Flow
The algorithm initializes GPIO, polls the toggle switch (GPIO 21), executes mode-specific logic (Smoke: random pulses; Smart: detection-based), and validates safety. The flowchart below details the steps: boot → setup → mode check → emission → safety loop. Why included? Clarifies code logic (src/main.py, src/smoke_mode.py, src/smart_mode.py) for laymen and shows judges how detection (src/utils.py) triggers outputs.

```mermaid
flowchart TD
    A[Boot RPi, Run main.py] --> B[Setup GPIO: 18/19 emitters, 21 toggle, 22 photodiode, 23 temp, 24 fan, 25 fuse, 26 manual trigger]
    B --> C[Idle Loop: Poll GPIO 21 every 0.1s]
    C --> D{Mode?}
    D -->|HIGH| E[Smoke Bomb Mode: Init EmitterDriver for 18/19]
    E --> F[Check safety.py: Temp >40°C → Fan on, >50°C/fuse blown → Stop]
    F --> G[Chaotic Pulses: Random 0.1-0.5s, 80% duty on laser/LEDs]
    G --> E[Loop until switch flipped]
    D -->|LOW| H[Smart Obstacle Mode: Init EmitterDriver for 18/19]
    H --> I[Check safety.py: Temp >40°C → Fan on, >50°C/fuse blown → Stop]
    I --> J[Detect Signal: utils.py mmWave UART/photodiode GPIO 22 or manual GPIO 26]
    J -->|No| H[Loop with 0.4s sleep]
    J -->|Yes| K[Targeted Pulses: Laser 0.15s 80%, LEDs 0.08s 60%]
    K --> H[Loop]
    C --> L[Shutdown: Cleanup GPIO on KeyboardInterrupt]
```

## Hardware Components

Core: RPi Zero/4, IR laser (1550nm, 100mW, GPIO 18), IR LED array (850nm, 10W, GPIO 19), mmWave radar (RD-03D/MR60FDA2, UART GPIO 14/15), photodiode (BPW34, GPIO 22).
Safety/Control: DS18B20 temp sensor (GPIO 23), 5V fan (GPIO 24), 10A fuse (GPIO 25), SPDT toggle (GPIO 21), push button (GPIO 26), 10000mAh battery (3.7V, boost to 5V).
Specs: ~$342 (see hardware/parts_list.md), <500g (RPi ~9g, battery ~200g, laser ~50g, LEDs ~100g, misc ~141g), 20x10x5 cm enclosure (hardware/enclosure.stl).

Why included? Details components for reproducibility, linking to parts_list.md (sourcing) and schematic.txt (wiring).

## Quick Start

### 1. Hardware Setup
```
git clone https://github.com/Yxiang-828/HacX-AV-Sensor-Disruptor
cd HacX-AV-Sensor-Disruptor
chmod +x setup.sh
./setup.sh  # Installs dependencies, enables UART/1-Wire
```

### 2. Wiring
Follow hardware/schematic.txt for GPIO connections (e.g., laser on GPIO 18, mmWave on UART). Why included? Ensures correct assembly, links to checklists.md (wiring tasks) and parts_list.md (components).

### 3. Operation
```
python3 src/main.py
```

GPIO 21 HIGH: Smoke mode (chaotic pulses).
GPIO 21 LOW: Smart mode (detection via mmWave/photodiode or manual trigger on GPIO 26).
Why included? Explains runtime for users, links to src/main.py (code) and checklists.md (operation tests).

## Testing & Validation
### CARLA Simulation
```
cd tests/
python3 carla_test.py  # Injects LiDAR/camera noise, logs vehicle.get_control() for braking
```

Why included? Validates algo in sim, links to prototype_notes.md (results) and checklists.md (Week 2 test plan).

### Hardware Testing
```
python3 tests/hardware_test.py  # Tests GPIO, emitters, detection, temp, fan, fuse
```

RC Car: Disrupt at 5-15m, expect stop in <3s.
Sensor Puck: Direct LiDAR/camera tests.
Why included? Verifies hardware, links to prototype_notes.md (logs) and checklists.md (Week 2).

### Demo Protocol

Power on (LED indicators show status).
Flip toggle (GPIO 21) to select mode.
Aim at AV sensors (15m range).
Verify stop via RC car or CARLA video.
Monitor safety (temp, fuse via src/safety.py).Why included? Outlines judge-facing demo, links to pitch_slides.md (presentation).

## Safety Features

Temperature: DS18B20 (GPIO 23) monitors, fan (GPIO 24) activates at 40°C, shutdown at 50°C.
Overcurrent: 10A fuse (GPIO 25) prevents damage.
Irradiance: LED ~1273 W/m² at 15m, diffuser ready if >1000 W/m².
Legal: Research prototype, requires IMDA waiver for ops.

Why included? Addresses HTX safety concerns, links to safety.py (code) and schematic.txt (wiring).

## Project Structure
```
├── src/                    # Control logic
│   ├── main.py             # Entry point: GPIO setup, mode polling (calls smoke/smart_mode.py).
│   ├── smoke_mode.py       # Chaotic pulses (uses drivers.py, safety.py).
│   ├── smart_mode.py       # Detection-based spoofing (uses utils.py, GPIO 26 trigger).
│   ├── utils.py            # mmWave/photodiode detection (inputs for smart_mode.py).
│   ├── drivers.py          # PWM for emitters (used by modes).
│   ├── temp_monitor.py     # DS18B20 readings (inputs to safety.py).
│   └── safety.py           # Fan/fuse control (called by modes).
├── hardware/               # Physical design
│   ├── schematic.txt       # Wiring diagram (guides setup.sh, hardware_test.py).
│   ├── parts_list.md       # Component sources (inputs for checklists.md).
│   └── enclosure.stl       # 3D model (Tinkercad/FreeCAD, ensures portability).
├── docs/                   # Documentation
│   ├── problem_brief.md    # Challenge analysis (basis for design, pitch_slides.md).
│   ├── checklists.md       # Tasks/risks (tracks progress, links to parts_list.md).
│   ├── prototype_notes.md  # Build/test logs (records checklists.md outcomes).
│   └── pitch_slides.md     # Presentation outline (summarizes tests, notes).
├── tests/                  # Validation
│   ├── carla_test.py       # AV sim with noise (verifies algo flow).
│   └── hardware_test.py    # GPIO/component tests (verifies schematic.txt).
└── requirements.txt        # Dependencies (used by setup.sh).
```

Why included? Maps repo for judges, links files to workflow (problem → build → test → demo).

## HacX Competition Readiness

Innovation (8.5/10): Dual-mode hybrid, portable integration.
Functionality (7.5→9): CARLA/hardware tests, manual trigger.
Practicality (8→9): $342, <500g, safety features (fan, fuse).
Problem Fit (9/10): Meets 15m/20 km/h, defeats sensor redundancy.
Target: 9.5/10 for Top 3 (per judge feedback, addressing untested code, battery math).

Why included? Summarizes strengths for judges, links to pitch_slides.md (demo plan) and prototype_notes.md (test results).

## Immediate Actions (Oct 12, 2025, 12:08 AM +08)

Order Parts: From hardware/parts_list.md (Amazon Prime/AliExpress, ~$342, arrive by Oct 18).
Run CARLA: Install on Ubuntu, test tests/carla_test.py for video by Oct 14.
Start STL: Use Tinkercad (30 min) for hardware/enclosure.stl by Oct 16.
Log Tests: Update docs/prototype_notes.md with initial results (e.g., GPIO tests).

Built for HacX 2025 | Target: Top 3 | Deadline: Nov 12, 2025