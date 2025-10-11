# Checklists for Dual-Mode AV Disruptor

Project for HacX hackathon (Nov 12, 2025). Ensures prototype functionality: non-destructive sensor disruption (LiDAR, camera, radar) at 15m range, 20 km/h AV speed, with toggle-switchable Smoke Bomb (chaotic) and Smart Obstacle (targeted) modes.

## Week 1: Initial Setup and Hardware Prep
Goal: Set up RPi, order parts, wire basics, test initial code.

### Project Structure:
- Confirm HacX/ directory has: src/ (main.py, smoke_mode.py, smart_mode.py, utils.py, drivers.py), hardware/ (schematic.txt, parts_list.md, enclosure.stl), docs/ (question.md, prototype_notes.md, pitch_slides.md), tests/ (carla_test.py, hardware_test.py), requirements.txt, .gitignore, setup.sh, README.md.
- Run git add ., git commit -m "Initial setup", git push to repo.

### RPi Setup:
- Flash RPi OS Lite (Zero) or Desktop (4) via Raspberry Pi Imager.
- Connect RPi to WiFi/SSH: sudo raspi-config, enable SSH, set WiFi.
- Run setup.sh: chmod +x setup.sh && ./setup.sh. Verify numpy, scipy, pyserial installed (pip3 list).
- Enable UART: Confirm /dev/ttyAMA0 active (ls /dev/tty*).

### Parts Ordering:
- Order from parts_list.md: RPi Zero ($15), IR laser (1550nm, $50), IR LED (850nm, $15), mmWave module (RD-03D/MR60FDA2, $25), photodiode (BPW34, $2), SPDT toggle ($5), battery (10000mAh, $30), heatsink ($5), lens ($10), filament ($20), misc ($10).
- Expedite shipping (7-10 days, arrive by Oct 18).
- Budget check: ~$330 total.

### Initial Wiring:
- Follow schematic.txt: Wire toggle switch (GPIO 21, 3.3V, GND), laser (GPIO 18 via MOSFET), LED (GPIO 19 via MOSFET), RF (GPIO 20 via MOSFET), mmWave (UART GPIO 14/15), photodiode (GPIO 22 via transistor).
- Use multimeter to verify no shorts (continuity test).
- Add 1kΩ resistors, 1N4001 diodes, 100µF capacitor as per schematic.

### Basic Hardware Test:
- Run tests/hardware_test.py on RPi: python3 tests/hardware_test.py.
- Expect: Emitters blink (1s each), switch state prints (HIGH/LOW), photodiode state prints (HIGH/LOW).
- Test photodiode: Shine laser pointer (any IR) on BPW34, expect LOW on GPIO 22.
- Test mmWave: Wave hand 1-2m away, expect "AV signal detected" (UART data).

### Enclosure Draft:
- Design enclosure (20x10x5 cm) in FreeCAD/Tinkercad: Holes for laser (1cm), LED (2cm), RF antenna (1cm), toggle (0.5cm), battery access (5x3 cm).
- Print draft with PLA filament (local, ~$20). Verify fit for RPi, battery.

## Week 2: Software Integration and Functional Test
Goal: Integrate detection, tune modes, validate in sim or hardware.

### Detection Tuning:
- Update utils.py if mmWave needs specific parser (e.g., RD-03D library from Core Electronics).
- Test detection: Run tests/hardware_test.py, move RC car (or hand) 1-8m from mmWave, expect detection in <0.5s.
- Test photodiode: Flash IR laser (or TV remote) at BPW34, expect detection in <0.1s.
- Adjust threshold in utils.py (e.g., 0.7 to 0.5) if false positives/negatives occur.

### Mode Implementation:
- Update smoke_mode.py/smart_mode.py: Replace GPIO.output with EmitterDriver from drivers.py.
- Smoke mode: Set duty=80% for all emitters, random pulses 0.1-0.5s.
- Smart mode: Set duty=50% (laser), 60% (LED), 70% (RF), pulse durations 0.15s/0.08s/0.2s for spoofing.
- Run main.py: python3 src/main.py. Flip toggle, expect console logs ("Switching to Smoke/Smart").

### Emitter Test:
- Use phone camera to see IR laser/LED output (visible as purple/white).
- Test RF: Use SDR (borrow if needed) to detect noise at 24/60GHz (or check mmWave docs for test signal).
- Verify 15m range: Aim laser at wall, measure beam spread (<10cm at 15m with lens).

### CARLA Sim Test:
- Install CARLA (Ubuntu, ~10GB): pip3 install carla.
- Run tests/carla_test.py: Expect AV (Tesla Model 3) stops in <2s after simulated disruption.
- Mock sensor noise: Edit script to inject LiDAR point-cloud errors, camera dazzle (whiteout), radar echoes.

### Hardware Demo Prep:
- Rent/borrow RC car with sensors (LiDAR/camera, ~$50) or standalone puck (e.g., Velodyne VLP-16, ~$200 rental).
- Test smoke mode: Aim at RC car (5-15m, ~5m/s), expect stop in <2s.
- Test smart mode: Trigger with mmWave/photodiode detection, expect stop in <3s.
- Record video for judges: Show toggle flip, AV stop.

## Things to Note

### Hardware Risks:
- Overheating: Laser/RF may overheat in smoke mode (>5 min). Monitor with finger test