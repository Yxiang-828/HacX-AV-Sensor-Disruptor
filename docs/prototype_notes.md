# Prototype Build and Test Notes

## Build Log
- **Week 1**: Order parts, set up RPi, create project structure, test GPIO with LED blink.
- **Week 2**: Wire emitters, switch, and SDR. Test smoke mode (visual IR on phone camera). Start CARLA sim.
- **Week 3**: Implement smart mode detection, tune pulses, validate AV stop in sim or RC car.
- **Week 4**: Finalize enclosure, record demo video, prep pitch.

## Test Plan
1. **Smoke Mode**: Aim at phone camera (IR visible) or RC car with sensors. Expect: Immediate stop or error.
2. **Smart Mode**: Use SDR to detect test signal (e.g., 2.4GHz for simplicity). Expect: Pulsed emissions, stop within 2s.
3. **Switching**: Flip toggle 10x, verify mode change in <0.5s (console log).
4. **CARLA Sim**: Simulate AV at 20 km/h, 15m. Inject noise/spoofed obstacles. Expect: Emergency brake.

## Issues to Monitor
- Heat: Laser/RF may overheat in smoke mode (>5 min). Add fan if needed.
- Range: Test laser focus at 15m (use lens).
- Battery: Verify 20 min (smart), 5-10 min (smoke).

## Next Steps
- Refine SDR detection (tune FFT for 77GHz).
- Test in rain (simulate with spray bottle).
- Demo: Record AV stop for judges.