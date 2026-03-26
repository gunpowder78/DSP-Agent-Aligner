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
        self.agent_context = AgentContext()
        self.config_patcher = ConfigPatcher()
        self._selected_device_id: int = -1
        self._target_config_path: str = ""

        self.window = MainWindow(
            on_test_triggered=self._on_test_triggered,
            on_scan_requested=self._on_scan_requested,
            on_write_config=self._on_write_config,
            on_copy_context=self._on_copy_context,
            on_target_config_selected=self._on_target_config_selected
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
            device = None
            for dev in self.audio_engine._devices:
                if dev["device_id"] == device_id:
                    device = dev
                    break

            if not device:
                self.window.root.after(0, lambda: self.window.set_status("设备未找到"))
                self.window.root.after(0, lambda: self.window.set_test_button_testing(False))
                return

            self._selected_device_id = device_id

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
        """Generate JSON Schema contract for selected device only and display in UI."""
        if self._selected_device_id < 0:
            self.window.set_status("请先选择设备")
            return

        all_devices = self.audio_engine._devices
        self.agent_context.generate_schema(all_devices, self._selected_device_id)
        schema_json = self.agent_context.get_schema_json()
        self.window.update_schema_display(schema_json)

    def _on_target_config_selected(self, file_path: str):
        """Handle target config file selection."""
        self._target_config_path = file_path
        self.window.set_status(f"已挂载目标配置: {pathlib.Path(file_path).name}")

    def _on_write_config(self):
        """Handle write config request - write selected device to target config.py using top-level constants."""
        if not self._target_config_path:
            self.window.set_status("错误：请先选择目标配置文件")
            return

        if self._selected_device_id < 0:
            self.window.set_status("错误：请先播放测试音选择设备")
            return

        selected_device = self.agent_context.get_selected_device()
        if not selected_device:
            self.window.set_status("设备信息未找到")
            return

        config_path = pathlib.Path(self._target_config_path)

        try:
            self.config_patcher.patch_constant(
                config_path,
                "TARGET_DEVICE_ID",
                selected_device["device_id"]
            )

            self.config_patcher.patch_constant(
                config_path,
                "SAMPLE_RATE",
                selected_device["native_sample_rate"]
            )

            self.window.set_status(f"成功写入 {config_path.name} (ID={selected_device['device_id']}, Rate={selected_device['native_sample_rate']})")
        except ValueError as e:
            self.window.set_status(f"写入错误: {str(e)[:40]}")
        except Exception as e:
            self.window.set_status(f"写入异常: {str(e)[:40]}")

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
