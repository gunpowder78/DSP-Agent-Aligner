"""Tests for AgentContext - JSON Schema contract generation with precise alignment."""

import pytest
import json
from core.agent_context import AgentContext


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
    """Test suite for AgentContext JSON Schema generation with precise alignment."""

    def test_generate_schema_returns_valid_structure(self):
        """Test that generate_schema returns properly structured contract."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=1)

        assert "version" in schema
        assert "contract_rules" in schema
        assert "selected_endpoint" in schema
        assert "constraints" in schema

    def test_schema_contains_only_selected_device(self):
        """Test that schema contains ONLY the selected device, not all devices."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=1)

        assert "selected_endpoint" in schema
        assert "devices" not in schema

        endpoint = schema["selected_endpoint"]
        assert endpoint["device_id"] == 1
        assert endpoint["device_name"] == "Speakers (Realtek Audio)"

    def test_schema_contract_rules_present(self):
        """Test that schema contains mandatory contract rules."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=3)

        assert "device_binding" in schema["contract_rules"]
        assert "sample_rate" in schema["contract_rules"]
        assert "duplex_guard" in schema["contract_rules"]

    def test_schema_forbidden_actions(self):
        """Test that schema lists forbidden actions for agent."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=0)

        forbidden = schema["constraints"]["forbidden_actions"]
        assert "Do NOT perform arithmetic on device_id" in forbidden
        assert "Do NOT use any device_id other than the one in selected_endpoint" in forbidden

    def test_get_schema_json_returns_valid_json(self):
        """Test that get_schema_json returns valid JSON string."""
        context = AgentContext()
        context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=2)

        json_str = context.get_schema_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["selected_endpoint"]["device_id"] == 2

    def test_get_selected_device(self):
        """Test get_selected_device returns the correct device."""
        context = AgentContext()
        context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=3)

        device = context.get_selected_device()

        assert device is not None
        assert device["device_id"] == 3
        assert device["device_name"] == "Universal Audio Apollo Twin"

    def test_get_device_id(self):
        """Test get_device_id returns correct ID."""
        context = AgentContext()
        context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=1)

        assert context.get_device_id() == 1

    def test_invalid_device_id_raises_error(self):
        """Test that invalid device_id raises ValueError."""
        context = AgentContext()

        with pytest.raises(ValueError, match="Device ID 999 not found"):
            context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=999)

    def test_get_schema_json_before_generate_raises_error(self):
        """Test that get_schema_json raises error if generate_schema not called."""
        context = AgentContext()

        with pytest.raises(RuntimeError, match="Schema not generated"):
            context.get_schema_json()

    def test_duplex_device_correctly_identified(self):
        """Test that full-duplex device is correctly identified in schema."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=3)

        assert schema["selected_endpoint"]["is_duplex_supported"] is True
        assert schema["selected_endpoint"]["max_input_channels"] == 18
        assert schema["selected_endpoint"]["max_output_channels"] == 20

    def test_half_duplex_device_correctly_identified(self):
        """Test that half-duplex device is correctly identified in schema."""
        context = AgentContext()
        schema = context.generate_schema(MOCK_DEVICE_LIST, selected_device_id=1)

        assert schema["selected_endpoint"]["is_duplex_supported"] is False
        assert schema["selected_endpoint"]["max_output_channels"] == 2
        assert schema["selected_endpoint"]["max_input_channels"] == 0
