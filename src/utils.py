import numpy as np
from scipy.fft import fft

def detect_signal(sample_rate=1e6, duration=0.1):
    """Detect AV signals (LiDAR/radar) via FFT"""
    samples = np.random.randn(int(sample_rate * duration))  # TODO: Replace with RTL-SDR input
    freqs = fft(samples)
    return np.max(np.abs(freqs[70000:80000])) > 0.5  # Tune for 77GHz radar or LiDAR pulses