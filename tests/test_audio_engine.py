"""Tests for AudioEngine - TDD with deep mock of sounddevice.query_devices()."""

import pytest
import numpy
from unittest.mock import patch, MagicMock
from core.audio_engine import SafeAudioTester, AudioEngine


MOCK_DEVICE_LIST = [
    {
        "name": "Microsoft Sound Mapper - Input",
        "hostapi": 0,
        "max_input_channels": 2,
        "max_output_channels": 0,
        "default_samplerate": 44100.0
    },
    {
        "name": "Speakers (Realtek Audio)",
        "hostapi": 1,
        "max_input_channels": 0,
        "max_output_channels": 2,
        "default_samplerate": 48000.0
    },
    {
        "name": "Microphone Array (Focusrite)",
        "hostapi": 2,
        "max_input_channels": 4,
        "max_output_channels": 0,
        "default_samplerate": 96000.0
    },
    {
        "name": "Universal Audio Apollo Twin",
        "hostapi": 2,
        "max_input_channels": 18,
        "max_output_channels": 20,
        "default_samplerate": 192000.0
    }
]


class TestAudioEngineDeviceScanning:

    @patch("sounddevice.query_devices")
    def test_scan_devices_returns_structured_list(self, mock_query):
        mock_query.return_value = MOCK_DEVICE_LIST

        engine = AudioEngine()
        devices = engine.scan_devices()

        assert len(devices) == 4
        assert devices[0]["device_id"] == 0
        assert devices[0]["device_name"] == "Microsoft Sound Mapper - Input"
        assert devices[0]["is_duplex_supported"] is False

    @patch("sounddevice.query_devices")
    def test_wasapi_half_duplex_detection(self, mock_query):
        mock_query.return_value = MOCK_DEVICE_LIST

        engine = AudioEngine()
        devices = engine.scan_devices()

        speaker_device = devices[1]
        assert speaker_device["max_input_channels"] == 0
        assert speaker_device["max_output_channels"] == 2
        assert speaker_device["is_duplex_supported"] is False

    @patch("sounddevice.query_devices")
    def test_full_duplex_professional_device(self, mock_query):
        mock_query.return_value = MOCK_DEVICE_LIST

        engine = AudioEngine()
        devices = engine.scan_devices()

        apollo_device = devices[3]
        assert apollo_device["max_input_channels"] == 18
        assert apollo_device["max_output_channels"] == 20
        assert apollo_device["is_duplex_supported"] is True

    @patch("sounddevice.query_devices")
    def test_get_device_by_name_pattern(self, mock_query):
        mock_query.return_value = MOCK_DEVICE_LIST

        engine = AudioEngine()
        engine.scan_devices()

        result = engine.get_device_by_name("realtek")
        assert result is not None
        assert "Realtek" in result["device_name"]

    @patch("sounddevice.query_devices")
    def test_get_device_by_name_case_insensitive(self, mock_query):
        mock_query.return_value = MOCK_DEVICE_LIST

        engine = AudioEngine()
        engine.scan_devices()

        result = engine.get_device_by_name("APOLLO")
        assert result is not None
        assert "Apollo" in result["device_name"]


class TestSafeAudioTesterCallback:

    def test_callback_zero_padding_at_boundary(self):
        waveform = numpy.zeros(512, dtype=numpy.float32)
        tester = SafeAudioTester(
            device_id=0,
            sample_rate=44100.0,
            num_channels=1,
            waveform=waveform
        )

        outdata = numpy.zeros((256, 1), dtype=numpy.float32)
        tester.audio_callback(outdata, 256, None, None)

        assert numpy.all(outdata == 0)

    def test_callback_raises_callback_stop_when_exhausted(self):
        import sounddevice

        waveform = numpy.zeros(256, dtype=numpy.float32)
        tester = SafeAudioTester(
            device_id=0,
            sample_rate=44100.0,
            num_channels=1,
            waveform=waveform
        )

        outdata = numpy.zeros((256, 1), dtype=numpy.float32)

        tester.audio_callback(outdata, 256, None, None)

        with pytest.raises(sounddevice.CallbackStop):
            tester.audio_callback(outdata, 256, None, None)

    def test_callback_partial_consumption(self):
        t = numpy.linspace(0, 1, 1024, False)
        waveform = (numpy.sin(2 * numpy.pi * 440 * t)).astype(numpy.float32)

        tester = SafeAudioTester(
            device_id=0,
            sample_rate=44100.0,
            num_channels=1,
            waveform=waveform
        )

        outdata = numpy.zeros((256, 1), dtype=numpy.float32)
        tester.audio_callback(outdata, 256, None, None)

        assert tester.current_frame_index == 256
        assert numpy.array_equal(outdata.flatten(), waveform[:256])

    def test_callback_stereo_expansion(self):
        mono_waveform = numpy.ones(512, dtype=numpy.float32)

        tester = SafeAudioTester(
            device_id=0,
            sample_rate=44100.0,
            num_channels=2,
            waveform=mono_waveform
        )

        outdata = numpy.zeros((256, 2), dtype=numpy.float32)
        tester.audio_callback(outdata, 256, None, None)

        assert outdata.shape == (256, 2)
