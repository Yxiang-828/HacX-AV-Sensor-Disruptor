# Checklists for Dual-Mode AV Disruptor

Prototype for HacX hackathon (Nov 12, 2025). Non-destructive disruption of hostile AV sensors (LiDAR, camera, radar) at 15m range, 20 km/h speed. Toggle-switchable modes: Smoke Bomb (chaotic emissions) and Smart Obstacle (targeted spoofing). Hardware: RPi Zero/4, IR laser (1550nm), IR LEDs (850nm), mmWave (24GHz detection), photodiode, DS18B20 temp sensor, MOSFET drivers, battery. Software: Python GPIO/PWM/UART, CARLA sim.

## Week 1: Setup and Hardware Prep (Oct 11-18, 2025)
**Goal**: Initialize repo, order parts, wire basics, test code.

- [ ] **Project Structure**:
  - Confirm `HacX/` has: `src/` (`main.py`, `smoke_mode.py`, `smart_mode.py`, `utils.py`, `drivers.py`, `temp_monitor.py`), `hardware/` (`schematic.txt`, `parts_list.md`, `enclosure.stl`), `docs/` (`question.md`, `prototype_notes.md`, `pitch_slides.md`, `checklists.md`), `tests/` (`carla_test.py`, `hardware_test.py`), `requirements.txt`, `.gitignore`, `setup.sh`, `README.md`.
  - Run `git add .`, `git commit -m "Week 1 setup"`, `git push`.

- [ ] **RPi Setup**:
  - Flash RPi OS Lite (Zero) or Desktop (4) via Raspberry Pi Imager.
  - Enable SSH/WiFi: `sudo raspi-config`.
  - Run `setup.sh`: `chmod +x setup.sh && ./setup.sh`. Verify `numpy`, `scipy`, `pyserial`, `RPi.GPIO` (`pip3 list`, `dpkg -l | grep python3-rpi.gpio`).
  - Confirm UART: `ls /dev/tty*` shows `/dev/ttyAMA0` (Zero) or `/dev/ttyS0` (4).

- [ ] **Parts Ordering**:
  - Order from `parts_list.md`: RPi Zero ($15), IR laser (1550nm, $50), IR LEDs (850nm, $15), mmWave (RD-03D/MR60FDA2, $25), photodiode (BPW34, $2), SPDT toggle ($5), battery (10000mAh, $30), heatsink ($5), lens ($10), filament ($20), DS18B20 temp sensor ($5), MOSFET (IRLZ44N, $2), diode (1N4001, $1), capacitor (100µF, $1), misc ($5).
  - Expedite shipping (arrive by Oct 18).   - Budget: ~$342.
  - Backup: Local electronics store for resistors, diodes.

- [ ] **Initial Wiring**:
  - Follow `schematic.txt`: Toggle (GPIO 21, 3.3V, GND), laser (GPIO 18 via MOSFET), LEDs (GPIO 19 via MOSFET), mmWave (UART GPIO 14/15), photodiode (GPIO 22 via transistor), DS18B20 (GPIO 23, 1-Wire).
  - Verify no shorts with multimeter (continuity test).
  - Add 1kΩ resistors, 1N4001 diodes, 100µF capacitor.

- [ ] **Basic Hardware Test**:
  - Run `tests/hardware_test.py`: `python3 tests/hardware_test.py`.
  - Expect: Laser/LEDs blink (1s, 100% duty), switch prints HIGH/LOW, photodiode prints HIGH/LOW, mmWave detects motion, temp sensor reads ~20-30°C.
  - Test photodiode: Shine IR laser/TV remote, expect LOW on GPIO 22.
  - Test mmWave: Wave hand 1-8m, expect "AV signal detected."
  - Test temp: Run `temp_monitor.py`, expect room temp.

- [ ] **Enclosure Draft**:
  - Design in FreeCAD/Tinkercad: 20x10x5 cm, holes for laser (1cm), LEDs (2cm), mmWave antenna (1cm), toggle (0.5cm), battery access (5x3 cm).
  - Export `enclosure.stl`, print with PLA (~$20). Verify RPi, battery fit.

## Week 2: Software Integration and Functional Test (Oct 19-25, 2025)
**Goal**: Tune detection, finalize modes, validate in sim/hardware.

- [ ] **Detection Tuning**:
  - Check mmWave parser in `utils.py` (RD-03D/MR60FDA2 UART protocol, e.g., from Core Electronics/Seeed). Add library if needed (download from vendor).
  - Test: Move RC car/hand 1-8m from mmWave, expect detection in <0.5s.
  - Test photodiode: Flash IR laser at BPW34, expect detection in <0.1s.
  - Adjust `utils.py` threshold (e.g., 0.7 to 0.5) for false positives/negatives.

- [ ] **Mode Implementation**:
  - Confirm `smoke_mode.py`/`smart_mode.py` use `EmitterDriver` (80% duty smoke, 50-60% smart).
  - Smoke: Random pulses (0.1-0.5s, laser/LEDs). Smart: Sequence (laser 0.15s 80%, LEDs 0.08s 60%).
  - Run `main.py`: `python3 src/main.py`. Flip toggle, expect logs ("Switching to Smoke/Smart").
  - Check temp: Run modes 5 min, expect `temp_monitor.py` reads <50°C.

- [ ] **Emitter Test**:
  - Verify laser/LEDs with phone camera (IR as purple/white).
  - Confirm 15m range: Laser beam <10cm spread at 15m (use lens).
  - Check mmWave detection (no RF emitter; detection-only).

- [ ] **CARLA Sim Test**:
  - Install CARLA (Ubuntu, ~10GB): `pip3 install carla`.
  - Run `tests/carla_test.py`: Expect AV stop in <2s with injected noise (LiDAR: fake points, camera: whiteout).
  - Log results in `prototype_notes.md`.

- [ ] **Hardware Demo Prep**:
  - Rent RC car with IR camera/LiDAR ($50, Amazon/local) or standalone puck ($200 rental).
  - Test smoke: Aim at RC car (5-15m, ~5m/s), expect stop in <2s.
  - Test smart: Trigger with mmWave/photodiode, expect stop in <3s.
  - Record video: Toggle flip, AV stop.

## Things to Note
- **Hardware Risks**:
  - **Overheating**: Laser/LEDs hot in smoke mode (>5 min). Use `temp_monitor.py`; shutdown if >50°C. Add fan ($5) if persistent.
  - **Battery**: Smoke (~80W, 28 min); smart (~30W, 1.2h). Recharge between demos. Math: 10000mAh × 3.7V = 37Wh; 37Wh/80W = 0.46h, 37Wh/30W = 1.23h.
  - **Wiring**: Check MOSFET polarity (IRLZ44N: Gate to GPIO via 1kΩ). Test with `hardware_test.py` to avoid shorts.
  - **Range**: Rain/fog cuts laser ~20-30%. Test indoors; note for v2.

- **Software Risks**:
  - **Detection**: mmWave may misfire on non-AV motion. Tune threshold or filter range (5-15m). Photodiode needs IR source (test with remote).
  - **UART**: Buffer overflow at 256000 baud. Check `dmesg` for errors; try 115200 if fails.
  - **Crashes**: Add logs in `main.py` (`print(f"GPIO {pin}: {state}")`). Handle serial/GPIO exceptions.

- **Demo Notes**:
  - **Legality**: Jamming FCC-restricted. Frame as "research prototype" for hackathon.
  - **Safety**: 1550nm laser eye-safe, but avoid direct aim. LEDs may dazzle—use narrow beam (lens).
  - **Judges**: Show toggle (practicality), dual modes (innovation), video/live stop (functionality). Use `pitch_slides.md`.

- **Testing Notes**:
  - **CARLA**: Needs GPU. Inject LiDAR points (15m obstacle), camera whiteout. Log stop time in `prototype_notes.md`.
  - **RC Car**: Budget option ($20 toy with IR camera). Stop on dazzle = success.
  - **Metrics**: >80% stop rate at 15m, <3s response. Log failures.

- **Timeline**:
  - Oct 12: Order parts (expedite for Oct 18).
  - Week 2: If detection fails, use manual trigger (GPIO 26 button). Still meets brief.
  - Week 3-4: Polish enclosure, record demo.

- **Budget**: ~$335. If over ($350 max), skip fan, use cheaper filament ($15).