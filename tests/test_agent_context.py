"""Tests for AgentContext - JSON Schema contract generation with mocked hardware."""

import pytest
from unittest.mock import patch, MagicMock
from core.agent_context import AgentContext
from core.audio_engine import AudioEngine


MOCK_DEVICE_LIST = [
    {
        "device_id": 0,
        "device_name": "Microsoft Sound Mapper - Input",
        "native_sample_rate": 44100.0,
        "max_input_channels": 2,
        "max_output_channels": 0,
        "is_duplex_supported": False
    },
    {
        "device_id": 1,
        "device_name": "Speakers (Realtek Audio)",
        "native_sample_rate": 48000.0,
        "max_input_channels": 0,
        "max_output_channels": 2,
        "is_duplex_supported": False
    },
    {
        "device_id": 2,
        "device_name": "Microphone Array (Focusrite)",
        "native_sample_rate": 96000.0,
        "max_input_channels": 4,
        "max_output_channels": 0,
        "is_duplex_supported": False
    },
    {
        "device_id": 3,
        "device_name": "Universal Audio Apollo Twin",
        "native_sample_rate": 192000.0,
        "max_input_channels": 18,
        "max_output_channels": 20,
        "is_duplex_supported": True
    }
]


class TestAgentContextSchema:
    """Test suite for AgentContext JSON Schema generation."""

    @patch.object(AudioEngine, "scan_devices")
    def test_generate_schema_returns_valid_structure(self, mock_scan):
        """Test that generate_schema returns properly structured contract."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        schema = context.generate_schema()

        assert "version" in schema
        assert "contract_rules" in schema
        assert "devices" in schema
        assert "constraints" in schema

    @patch.object(AudioEngine, "scan_devices")
    def test_schema_contains_all_mock_devices(self, mock_scan):
        """Test that schema captures all mock devices."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        schema = context.generate_schema()

        assert len(schema["devices"]) == 4

    @patch.object(AudioEngine, "scan_devices")
    def test_schema_contract_rules_present(self, mock_scan):
        """Test that schema contains mandatory contract rules."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        schema = context.generate_schema()

        assert "device_selection" in schema["contract_rules"]
        assert "sample_rate" in schema["contract_rules"]
        assert "duplex_guard" in schema["contract_rules"]

    @patch.object(AudioEngine, "scan_devices")
    def test_schema_forbidden_actions(self, mock_scan):
        """Test that schema lists forbidden actions for agent."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        schema = context.generate_schema()

        forbidden = schema["constraints"]["forbidden_actions"]
        assert "Do NOT perform arithmetic on device_id" in forbidden
        assert "Do NOT assume all devices support 44100Hz" in forbidden
        assert "Do NOT create full-duplex streams on half-duplex hardware" in forbidden

    @patch.object(AudioEngine, "scan_devices")
    def test_get_schema_json_returns_string(self, mock_scan):
        """Test that get_schema_json returns valid JSON string."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        json_str = context.get_schema_json()

        assert isinstance(json_str, str)
        assert '"device_id"' in json_str
        assert '"is_duplex_supported"' in json_str

    @patch.object(AudioEngine, "scan_devices")
    def test_get_device_by_id(self, mock_scan):
        """Test device retrieval by device_id."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        context.generate_schema()

        device = context.get_device(2)
        assert device is not None
        assert device["device_name"] == "Microphone Array (Focusrite)"

    @patch.object(AudioEngine, "scan_devices")
    def test_get_duplex_devices(self, mock_scan):
        """Test filtering of full-duplex devices."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        context.generate_schema()

        duplex_devices = context.get_duplex_devices()
        assert len(duplex_devices) == 1
        assert duplex_devices[0]["device_name"] == "Universal Audio Apollo Twin"

    @patch.object(AudioEngine, "scan_devices")
    def test_get_output_devices(self, mock_scan):
        """Test filtering of output-only devices."""
        mock_scan.return_value = MOCK_DEVICE_LIST

        context = AgentContext()
        context.generate_schema()

        output_devices = context.get_output_devices()
        assert len(output_devices) == 2
        assert all(d["max_output_channels"] > 0 for d in output_devices)
