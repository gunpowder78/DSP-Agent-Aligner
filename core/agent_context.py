"""Agent Context Generator - JSON Schema contract for zero-hallucination hardware interaction."""

import json
from typing import Optional


class AgentContext:
    """Context generator that produces deterministic JSON Schema contracts for LLM agents."""

    def __init__(self):
        self._schema: Optional[dict] = None
        self._selected_device: Optional[dict] = None

    def generate_schema(self, all_devices: list, selected_device_id: int) -> dict:
        """Generate strict JSON Schema contract for the selected device only.

        Args:
            all_devices: List of all discovered devices
            selected_device_id: The device ID that user selected and tested

        Returns:
            JSON Schema dict with only the selected endpoint
        """
        selected_device = None
        for dev in all_devices:
            if dev["device_id"] == selected_device_id:
                selected_device = dev
                break

        if selected_device is None:
            raise ValueError(f"Device ID {selected_device_id} not found in device list")

        self._selected_device = selected_device

        self._schema = {
            "version": "1.0",
            "contract_rules": {
                "device_binding": "Agent MUST strictly bind any audio streams to the device_id specified in the selected_endpoint block",
                "sample_rate": "Agent MUST match native_sample_rate exactly in WASAPI mode",
                "duplex_guard": "If is_duplex_supported is False, Agent MUST NOT instantiate full-duplex streams (sd.Stream, sd.playrec)",
                "channel_count": "Agent MUST NOT exceed max_output_channels or max_input_channels when opening streams"
            },
            "selected_endpoint": {
                "device_id": selected_device["device_id"],
                "device_name": selected_device["device_name"],
                "native_sample_rate": selected_device["native_sample_rate"],
                "max_input_channels": selected_device["max_input_channels"],
                "max_output_channels": selected_device["max_output_channels"],
                "is_duplex_supported": selected_device["is_duplex_supported"]
            },
            "constraints": {
                "forbidden_actions": [
                    "Do NOT perform arithmetic on device_id",
                    "Do NOT assume all devices support 44100Hz",
                    "Do NOT create full-duplex streams on half-duplex hardware",
                    "Do NOT use any device_id other than the one in selected_endpoint"
                ]
            }
        }
        return self._schema

    def get_schema_json(self) -> str:
        """Return schema as formatted JSON string."""
        if self._schema is None:
            raise RuntimeError("Schema not generated. Call generate_schema() first.")
        return json.dumps(self._schema, indent=2)

    def get_selected_device(self) -> Optional[dict]:
        """Get the selected device info."""
        return self._selected_device

    def get_device_id(self) -> Optional[int]:
        """Get the selected device ID."""
        if self._selected_device:
            return self._selected_device.get("device_id")
        return None
