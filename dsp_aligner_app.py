"""DSP-Agent-Aligner - Main application entry point with MVC thread-safe architecture."""

import sys
import threading
from core.audio_engine import AudioEngine
from core.agent_context import AgentContext
from ui.main_window import MainWindow


class DAAApplication:
    """Main application controller with strict MVC separation and event-driven communication."""

    def __init__(self):
        self.audio_engine = AudioEngine()
        self.agent_context = AgentContext(self.audio_engine)
        self.ui = MainWindow(
            on_test_triggered=self._on_test_triggered,
            on_scan_requested=self._on_scan_requested
        )

    def _on_scan_requested(self):
        """Handle device scan request in background thread - UI thread safe via event_generate."""
        def scan_worker():
            devices = self.audio_engine.scan_devices()
            schema = self.agent_context.generate_schema()
            self.ui.root.event_generate("<<DeviceScanComplete>>", when="tail")

        thread = threading.Thread(target=scan_worker, daemon=True)
        thread.start()

    def _on_test_triggered(self):
        """Handle audio test trigger in background thread - UI thread safe via event_generate."""
        def test_worker():
            devices = self.audio_engine.scan_devices()
            if not devices:
                self.ui.root.event_generate("<<AudioTestComplete>>", when="tail")
                return

            output_devices = self.agent_context.get_output_devices()
            if not output_devices:
                self.ui.root.event_generate("<<AudioTestComplete>>", when="tail")
                return

            target = output_devices[0]
            success = self.audio_engine.play_test_tone(
                device_id=int(target["device_id"]),
                sample_rate=float(target["native_sample_rate"]),
                num_channels=int(target["max_output_channels"]),
                duration=1.0
            )
            self.ui.root.event_generate("<<AudioTestComplete>>", when="tail")

        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()

    def run(self):
        """Start the application main loop."""
        self.ui.run()


def main():
    """Entry point."""
    app = DAAApplication()
    app.run()


if __name__ == "__main__":
    main()
