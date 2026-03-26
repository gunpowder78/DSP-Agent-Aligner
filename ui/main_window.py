"""Main Window - Pure Tkinter state reflector, NO sounddevice imports allowed."""

import tkinter
import customtkinter
from typing import Callable, Optional


class MainWindow:
    """Main GUI window - pure state reflector pattern, no hardware calls permitted."""

    def __init__(self, on_test_triggered: Optional[Callable] = None, on_scan_requested: Optional[Callable] = None):
        self.on_test_triggered = on_test_triggered
        self.on_scan_requested = on_scan_requested

        self.root = customtkinter.CTk()
        self.root.title("DSP-Agent-Aligner")
        self.root.geometry("800x600")

        self._build_widgets()
        self._bind_events()

    def _build_widgets(self):
        """Build GUI widgets."""
        self.title_label = customtkinter.CTkLabel(self.root, text="DSP Agent Aligner", font=("Arial", 24))
        self.title_label.pack(pady=20)

        self.device_frame = customtkinter.CTkFrame(self.root)
        self.device_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.device_label = customtkinter.CTkLabel(self.device_frame, text="Audio Devices", font=("Arial", 16))
        self.device_label.pack(pady=10)

        self.device_listbox = customtkinter.CTkTextbox(self.device_frame, height=200)
        self.device_listbox.pack(pady=10, padx=10, fill="both", expand=True)

        self.button_frame = customtkinter.CTkFrame(self.root)
        self.button_frame.pack(pady=20)

        self.scan_button = customtkinter.CTkButton(
            self.button_frame,
            text="Scan Devices",
            command=self._on_scan_clicked
        )
        self.scan_button.pack(side="left", padx=10)

        self.test_button = customtkinter.CTkButton(
            self.button_frame,
            text="Run Audio Test",
            command=self._on_test_clicked
        )
        self.test_button.pack(side="left", padx=10)

        self.status_label = customtkinter.CTkLabel(self.root, text="Status: Ready", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def _bind_events(self):
        """Bind Tkinter virtual events for cross-thread communication."""
        self.root.bind("<<AudioTestComplete>>", self._on_audio_test_complete)
        self.root.bind("<<HardwareStateChanged>>", self._on_hardware_state_changed)
        self.root.bind("<<DeviceScanComplete>>", self._on_device_scan_complete)

    def _on_scan_clicked(self):
        """Handle scan button click - delegates to core via callback."""
        self.status_label.configure(text="Status: Scanning...")
        if self.on_scan_requested:
            self.on_scan_requested()

    def _on_test_clicked(self):
        """Handle test button click - delegates to core via callback."""
        self.status_label.configure(text="Status: Running audio test...")
        if self.on_test_triggered:
            self.on_test_triggered()

    def _on_audio_test_complete(self, event):
        """Handle audio test completion virtual event."""
        self.status_label.configure(text="Status: Audio test complete")

    def _on_hardware_state_changed(self, event):
        """Handle hardware state change virtual event."""
        self.status_label.configure(text="Status: Hardware state changed")

    def _on_device_scan_complete(self, event):
        """Handle device scan completion virtual event."""
        self.status_label.configure(text="Status: Device scan complete")

    def update_device_list(self, devices: list):
        """Update the device list display with formatted device information."""
        self.device_listbox.delete("1.0", "end")
        for dev in devices:
            line = f"[{dev['device_id']}] {dev['device_name']} | "
            line += f"IN: {dev['max_input_channels']} | OUT: {dev['max_output_channels']} | "
            line += f"Rate: {dev['native_sample_rate']} | Duplex: {dev['is_duplex_supported']}\n"
            self.device_listbox.insert("end", line)

    def set_status(self, message: str):
        """Update status message."""
        self.status_label.configure(text=f"Status: {message}")

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()

    def destroy(self):
        """Destroy the window."""
        self.root.destroy()
