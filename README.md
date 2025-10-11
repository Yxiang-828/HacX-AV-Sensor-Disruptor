# Dual-Mode AV Disruptor

Non-destructive prototype to stop hostile autonomous vehicles (AVs) by disrupting sensors (LiDAR, camera, radar) at 15m range, 20 km/h speed. Built for HacX hackathon (HTX + Microsoft, Nov 12, 2025).

## Features

- **Smoke Bomb Mode**: Chaotic IR/RF emissions to overwhelm sensors.
- **Smart Obstacle Mode**: Targeted pulses to spoof obstacles, energy-efficient.
- Toggle switch for instant mode change.
- **Handheld, ~$342, <500g, battery-powered.**

## Setup

1. Clone repo: `git clone [repo-url]`
2. Install RPi OS Lite on RPi Zero/4.
3. Install dependencies: `pip3 install -r requirements.txt`
4. Wire per `hardware/schematic.txt`.
5. Run: `python3 src/main.py`

## Testing

- **CARLA Sim**: Run `tests/carla_test.py` to simulate AV stop.
- **Hardware**: Test with RC car or sensor puck (LiDAR/camera/radar).
- Demo: Flip toggle, aim at target, verify stop.

## Structure

- `src/`: Python code for RPi control.
- `hardware/`: Schematics, parts list.
- `docs/`: Problem brief, notes, pitch slides.
- `tests/`: CARLA sim scripts.