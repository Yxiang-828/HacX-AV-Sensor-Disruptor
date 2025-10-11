# Prototype Build and Test Notes

## Build Log
- **Week 1**: Order parts, set up RPi, create project structure, test GPIO with LED blink.
- **Week 2**: Wire emitters, switch, mmWave/photodiode. Test smoke mode (visual IR on phone camera). Start CARLA sim.
- **Week 3**: Implement smart mode detection, tune pulses, validate AV stop in sim or RC car.
- **Week 4**: Finalize enclosure, record demo video, prep pitch.

## Test Plan
1. **Smoke Mode**: Aim at phone camera (IR visible) or RC car with sensors. Expect: Immediate stop or error.
2. **Smart Mode**: Use mmWave/photodiode to detect AV signals. Manual trigger (GPIO 26 button) as fallback. Expect: Pulsed emissions, stop within 2s.
3. **Switching**: Flip toggle 10x, verify mode change in <0.5s (console log).
4. **CARLA Sim**: Simulate AV at 20 km/h, 15m. Inject LiDAR noise (fake points), camera whiteout. Log AV control to verify perception response. Expect: Emergency brake.

## Issues to Monitor
- Heat: Laser/LEDs may overheat in smoke mode (>5 min). Fan on GPIO 24, shutdown at 50°C.
- Range: Test laser focus at 15m (use lens).
- Battery: Verify 1.2h (smart), 28 min (smoke). Math: 37Wh battery, 30W smart, 80W smoke.
- Safety: Fuse (10A) on battery line, GPIO 25 status check.

## Next Steps
- Tune mmWave UART parsing (add RD-03D/MR60FDA2 vendor lib if available).
- Test in rain (simulate with spray bottle).
- Demo: Record AV stop for judges (CARLA + RC car).