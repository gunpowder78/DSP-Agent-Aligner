"""Audio Engine Module - SafeAudioTester implementation with non-blocking async callbacks."""

import sounddevice
import numpy
from typing import Optional, Callable


class SafeAudioTester:
    """Embodied test loop for hardware audio testing with WASAPI exclusive lock safety."""

    def __init__(
        self,
        device_id: int,
        sample_rate: float,
        num_channels: int,
        waveform: numpy.ndarray
    ):
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.waveform = waveform
        self.current_frame_index = 0
        self._stream: Optional[sounddevice.OutputStream] = None

    def audio_callback(self, outdata, frames, time_info, status):
        """Non-blocking audio callback - preallocated waveform slices only."""
        if status:
            raise sounddevice.CallbackAbort(str(status))

        remaining_frames = len(self.waveform) - self.current_frame_index

        if remaining_frames <= 0:
            raise sounddevice.CallbackStop()

        frames_to_copy = min(frames, remaining_frames)
        chunk = self.waveform[self.current_frame_index:self.current_frame_index + frames_to_copy]

        if self.num_channels == 1:
            outdata[:frames_to_copy, 0] = chunk
        else:
            if chunk.ndim == 1:
                outdata[:frames_to_copy, 0] = chunk
                outdata[:frames_to_copy, 1] = chunk
            else:
                outdata[:frames_to_copy] = chunk

        if frames_to_copy < frames:
            outdata[frames_to_copy:] = 0
            raise sounddevice.CallbackStop()

        self.current_frame_index += frames_to_copy

    def run(self, duration_frames: int) -> bool:
        """Execute the audio test sequence."""
        try:
            self._stream = sounddevice.OutputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.num_channels,
                callback=self.audio_callback,
                blocksize=256
            )
            with self._stream:
                while self.current_frame_index < duration_frames:
                    pass
            return True
        except Exception:
            return False
        finally:
            self._stream = None


class AudioEngine:
    """Core audio engine managing device scanning and test sequences."""

    def __init__(self):
        self._devices = []
        self._current_device = None

    def scan_devices(self) -> list:
        """Scan available audio devices and return their topology."""
        self._devices = []
        try:
            devices = sounddevice.query_devices()
            if isinstance(devices, dict):
                devices = [devices]
            for idx, dev in enumerate(devices):
                self._devices.append({
                    "device_id": idx,
                    "device_name": dev.get("name", "Unknown"),
                    "native_sample_rate": dev.get("default_samplerate", 44100.0),
                    "max_input_channels": dev.get("max_input_channels", 0),
                    "max_output_channels": dev.get("max_output_channels", 0),
                    "is_duplex_supported": dev.get("max_input_channels", 0) > 0 and dev.get("max_output_channels", 0) > 0
                })
        except Exception:
            pass
        return self._devices

    def get_device_by_name(self, name_pattern: str) -> Optional[dict]:
        """Find device by name pattern."""
        for dev in self._devices:
            if name_pattern.lower() in dev["device_name"].lower():
                return dev
        return None

    def play_test_tone(self, device_id: int, sample_rate: float, num_channels: int, duration: float) -> bool:
        """Play a test tone on the specified device."""
        frequency = 440.0
        t = numpy.linspace(0, duration, int(sample_rate * duration), False)
        waveform = (numpy.sin(2 * numpy.pi * frequency * t) * 0.5).astype(numpy.float32)

        if num_channels == 2:
            waveform = numpy.column_stack([waveform, waveform])

        tester = SafeAudioTester(
            device_id=device_id,
            sample_rate=sample_rate,
            num_channels=num_channels,
            waveform=waveform
        )
        return tester.run(len(waveform))

    def stop(self):
        """Stop any ongoing audio operations."""
        pass
