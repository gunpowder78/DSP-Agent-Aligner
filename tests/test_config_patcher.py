"""Tests for ConfigPatcher - AST-based patching with tmp_path isolation."""

import pytest
import pathlib
from core.config_patcher import ConfigPatcher


class TestConfigPatcherAST:
    """Test suite for ConfigPatcher AST manipulation with isolated temp files."""

    def test_patch_constant_integer(self, tmp_path):
        """Test patching integer constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("TARGET_DEVICE_ID = 10\n", encoding="utf-8")

        result = ConfigPatcher.patch_constant(config_file, "TARGET_DEVICE_ID", 42)

        assert result is True
        content = config_file.read_text(encoding="utf-8")
        assert "42" in content

    def test_patch_constant_float(self, tmp_path):
        """Test patching float constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("SAMPLE_RATE = 44100.0\n", encoding="utf-8")

        result = ConfigPatcher.patch_constant(config_file, "SAMPLE_RATE", 48000.0)

        assert result is True
        content = config_file.read_text(encoding="utf-8")
        assert "48000.0" in content

    def test_patch_constant_string(self, tmp_path):
        """Test patching string constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text('DEVICE_NAME = "Old Name"\n', encoding="utf-8")

        result = ConfigPatcher.patch_constant(config_file, "DEVICE_NAME", "New Name")

        assert result is True
        content = config_file.read_text(encoding="utf-8")
        assert "New Name" in content

    def test_patch_constant_preserves_syntax(self, tmp_path):
        """Test that patching preserves valid Python syntax."""
        config_file = tmp_path / "dummy_config.py"
        original_content = "TARGET_DEVICE_ID = 10\nOTHER_CONST = 20\n"
        config_file.write_text(original_content, encoding="utf-8")

        ConfigPatcher.patch_constant(config_file, "TARGET_DEVICE_ID", 99)

        assert ConfigPatcher.validate_syntax(config_file) is True

    def test_read_constant_integer(self, tmp_path):
        """Test reading integer constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("TARGET_DEVICE_ID = 42\n", encoding="utf-8")

        value = ConfigPatcher.read_constant(config_file, "TARGET_DEVICE_ID")

        assert value == 42

    def test_read_constant_float(self, tmp_path):
        """Test reading float constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("SAMPLE_RATE = 48000.0\n", encoding="utf-8")

        value = ConfigPatcher.read_constant(config_file, "SAMPLE_RATE")

        assert value == 48000.0

    def test_read_constant_string(self, tmp_path):
        """Test reading string constant value."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text('DEVICE_NAME = "Test Device"\n', encoding="utf-8")

        value = ConfigPatcher.read_constant(config_file, "DEVICE_NAME")

        assert value == "Test Device"

    def test_read_nonexistent_constant(self, tmp_path):
        """Test reading a constant that does not exist."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("EXISTING = 10\n", encoding="utf-8")

        value = ConfigPatcher.read_constant(config_file, "NONEXISTENT")

        assert value is None

    def test_validate_syntax_valid_python(self, tmp_path):
        """Test syntax validation with valid Python file."""
        config_file = tmp_path / "valid_config.py"
        config_file.write_text("A = 1\nB = 2\n", encoding="utf-8")

        assert ConfigPatcher.validate_syntax(config_file) is True

    def test_validate_syntax_invalid_python(self, tmp_path):
        """Test syntax validation with invalid Python file."""
        config_file = tmp_path / "invalid_config.py"
        config_file.write_text("A = \n", encoding="utf-8")

        assert ConfigPatcher.validate_syntax(config_file) is False

    def test_patch_nonexistent_constant_returns_false(self, tmp_path):
        """Test that patching nonexistent constant returns False."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("EXISTING = 10\n", encoding="utf-8")

        result = ConfigPatcher.patch_constant(config_file, "NONEXISTENT", 99)

        assert result is False

    def test_patch_preserves_unmodified_constants(self, tmp_path):
        """Test that patching one constant does not affect others."""
        config_file = tmp_path / "dummy_config.py"
        config_file.write_text("A = 1\nB = 2\nC = 3\n", encoding="utf-8")

        ConfigPatcher.patch_constant(config_file, "B", 99)

        content = config_file.read_text(encoding="utf-8")
        assert "A = 1" in content
        assert "B = 99" in content
        assert "C = 3" in content
