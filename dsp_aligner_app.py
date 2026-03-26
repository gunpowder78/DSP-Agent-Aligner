"""DSP-Agent-Aligner - Main application controller with MVC thread-safe architecture."""

import threading
import pathlib
from core.audio_engine import AudioEngine
from core.agent_context import AgentContext
from core.config_patcher import ConfigPatcher
from ui.main_window import MainWindow


class DAAApplication:
    """Main application controller - orchestrates core components and UI with thread-safe communication."""

    def __init__(self):
        self.audio_engine = AudioEngine()
        self.agent_context = AgentContext(self.audio_engine)
        self.config_patcher = ConfigPatcher()
        self._selected_device: dict = {}

        self.window = MainWindow(
            on_test_triggered=self._on_test_triggered,
            on_scan_requested=self._on_scan_requested,
            on_write_config=self._on_write_config,
            on_copy_context=self._on_copy_context
        )

        self._initial_scan()

    def _initial_scan(self):
        """Perform initial device scan on startup."""
        devices = self.audio_engine.scan_devices()
        self.window.update_device_list(devices)

    def _on_scan_requested(self):
        """Handle device scan request from UI - runs in background thread."""
        def scan_worker():
            devices = self.audio_engine.scan_devices()
            self.window.root.after(0, lambda: self.window.update_device_list(devices))
            self.window.root.after(0, lambda: self.window.root.event_generate("<<DeviceScanComplete>>", when="tail"))

        thread = threading.Thread(target=scan_worker, daemon=True)
        thread.start()

    def _on_test_triggered(self, device_id: int):
        """Handle audio test trigger - runs in background thread, safe cross-thread UI update."""
        def test_worker():
            device = self.audio_engine.get_device_by_name("")
            for dev in self.audio_engine._devices:
                if dev["device_id"] == device_id:
                    device = dev
                    break

            if not device:
                self.window.root.after(0, lambda: self.window.set_status("设备未找到"))
                self.window.root.after(0, lambda: self.window.set_test_button_testing(False))
                return

            self._selected_device = device

            success = self.audio_engine.play_test_tone(
                device_id=int(device["device_id"]),
                sample_rate=float(device["native_sample_rate"]),
                num_channels=int(device["max_output_channels"]) if device["max_output_channels"] > 0 else 2,
                duration=1.0
            )

            self.window.root.after(0, self._safe_restore_ui, success)

        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()

    def _safe_restore_ui(self, test_success: bool):
        """Thread-safe UI restoration - MUST be called from main GUI thread via after(0)."""
        self.window.set_test_button_testing(False)

        if test_success:
            self.window.set_status("测试音播放成功")
            self._generate_and_display_schema()
        else:
            self.window.set_status("测试音播放失败")

        self.window.root.event_generate("<<AudioTestComplete>>", when="tail")

    def _generate_and_display_schema(self):
        """Generate JSON Schema contract and display in UI."""
        self.agent_context.generate_schema()
        schema_json = self.agent_context.get_schema_json()
        self.window.update_schema_display(schema_json)

    def _on_write_config(self):
        """Handle write config request - write selected device to config.py."""
        if not self._selected_device:
            self.window.set_status("请先播放测试音选择设备")
            return

        config_path = pathlib.Path("config.py")

        try:
            success = self.config_patcher.patch_constant(
                config_path,
                "TARGET_DEVICE_ID",
                self._selected_device["device_id"]
            )

            if success:
                self.config_patcher.patch_constant(
                    config_path,
                    "SAMPLE_RATE",
                    self._selected_device["native_sample_rate"]
                )
                self.window.set_status(f"已写入 config.py (ID: {self._selected_device['device_id']})")
            else:
                existing_value = self.config_patcher.read_constant(config_path, "TARGET_DEVICE_ID")
                if existing_value is None:
                    with open(config_path, "a", encoding="utf-8") as f:
                        f.write(f"\nTARGET_DEVICE_ID = {self._selected_device['device_id']}\n")
                        f.write(f"SAMPLE_RATE = {self._selected_device['native_sample_rate']}\n")
                    self.window.set_status("已创建 config.py")
                else:
                    self.window.set_status("配置写入失败")
        except Exception as e:
            self.window.set_status(f"写入错误: {str(e)[:30]}")

    def _on_copy_context(self):
        """Handle copy context request - clipboard already handled by UI."""
        self.window.set_status("Context 已复制到剪贴板")

    def run(self):
        """Start the application main loop."""
        self.window.run()


def main():
    """Entry point."""
    app = DAAApplication()
    app.run()


if __name__ == "__main__":
    main()
