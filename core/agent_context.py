"""Agent Context Generator - JSON Schema contract for zero-hallucination hardware interaction."""

import json
from typing import Optional
from .audio_engine import AudioEngine


class AgentContext:
    """Context generator that produces deterministic JSON Schema contracts for LLM agents."""

    def __init__(self, audio_engine: Optional[AudioEngine] = None):
        self.audio_engine = audio_engine or AudioEngine()
        self._schema: Optional[dict] = None

    def generate_schema(self) -> dict:
        """Scan hardware and generate strict JSON Schema contract."""
        devices = self.audio_engine.scan_devices()

        self._schema = {
            "version": "1.0",
            "contract_rules": {
                "device_selection": "Agent MUST use device_id from this schema directly - no arithmetic or hardcoding",
                "sample_rate": "Agent MUST match native_sample_rate exactly in WASAPI mode",
                "duplex_guard": "If is_duplex_supported is False, Agent MUST NOT instantiate full-duplex streams"
            },
            "devices": devices,
            "constraints": {
                "forbidden_actions": [
                    "Do NOT perform arithmetic on device_id",
                    "Do NOT assume all devices support 44100Hz",
                    "Do NOT create full-duplex streams on half-duplex hardware"
                ]
            }
        }
        return self._schema

    def get_schema_json(self) -> str:
        """Return schema as formatted JSON string."""
        if self._schema is None:
            self.generate_schema()
        return json.dumps(self._schema, indent=2)

    def get_device(self, device_id: int) -> Optional[dict]:
        """Get device info by ID from current schema."""
        if self._schema is None:
            self.generate_schema()
        for dev in self._schema.get("devices", []):
            if dev["device_id"] == device_id:
                return dev
        return None

    def get_duplex_devices(self) -> list:
        """Get list of full-duplex capable devices."""
        if self._schema is None:
            self.generate_schema()
        return [dev for dev in self._schema.get("devices", []) if dev["is_duplex_supported"]]

    def get_output_devices(self) -> list:
        """Get list of output-only devices."""
        if self._schema is None:
            self.generate_schema()
        return [dev for dev in self._schema.get("devices", []) if dev["max_output_channels"] > 0]
