"""Main Window - Pure Tkinter state reflector, NO sounddevice imports allowed."""

import tkinter
import customtkinter
from tkinter import filedialog
from typing import Callable, Optional


class MainWindow:
    """Main GUI window - pure state reflector pattern with Grid layout."""

    def __init__(
        self,
        on_test_triggered: Optional[Callable] = None,
        on_scan_requested: Optional[Callable] = None,
        on_write_config: Optional[Callable] = None,
        on_copy_context: Optional[Callable] = None,
        on_target_config_selected: Optional[Callable] = None
    ):
        self.on_test_triggered = on_test_triggered
        self.on_scan_requested = on_scan_requested
        self.on_write_config = on_write_config
        self.on_copy_context = on_copy_context
        self.on_target_config_selected = on_target_config_selected

        self._selected_device_id: Optional[int] = None
        self._devices: list = []
        self._target_config_path: Optional[str] = None

        self.root = customtkinter.CTk()
        self.root.title("DSP-Agent-Aligner")
        self.root.geometry("900x800")

        self._build_widgets()
        self._bind_events()

    def _build_widgets(self):
        """Build GUI widgets using Grid layout."""
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.title_label = customtkinter.CTkLabel(
            self.root,
            text="DSP Agent Aligner",
            font=("Arial", 28, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        self._build_device_selection_area(row=1, column=0)
        self._build_agent_context_area(row=1, column=1)
        self._build_target_project_area(row=2, column=0, columnspan=2)
        self._build_control_area(row=3, column=0, columnspan=2)

    def _build_device_selection_area(self, row: int, column: int):
        """Build device selection area with CTkOptionMenu."""
        self.device_frame = customtkinter.CTkFrame(self.root)
        self.device_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        self.device_frame.grid_rowconfigure(1, weight=1)
        self.device_frame.grid_columnconfigure(0, weight=1)

        device_header = customtkinter.CTkLabel(
            self.device_frame,
            text="设备选择区",
            font=("Arial", 16, "bold")
        )
        device_header.grid(row=0, column=0, pady=(10, 5))

        self.device_optionmenu = customtkinter.CTkOptionMenu(
            self.device_frame,
            values=["请先扫描设备..."],
            command=self._on_device_selected,
            width=300
        )
        self.device_optionmenu.grid(row=1, column=0, pady=10, padx=10)

        self.device_info_textbox = customtkinter.CTkTextbox(
            self.device_frame,
            height=150,
            state="disabled"
        )
        self.device_info_textbox.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")

        self.test_button = customtkinter.CTkButton(
            self.device_frame,
            text="▶ 播放测试音",
            command=self._on_test_clicked,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            height=40
        )
        self.test_button.grid(row=3, column=0, pady=(5, 15), padx=10)

    def _build_agent_context_area(self, row: int, column: int):
        """Build Agent context display area."""
        self.agent_frame = customtkinter.CTkFrame(self.root)
        self.agent_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        self.agent_frame.grid_rowconfigure(1, weight=1)
        self.agent_frame.grid_columnconfigure(0, weight=1)

        agent_header = customtkinter.CTkLabel(
            self.agent_frame,
            text="Agent 状态对齐区",
            font=("Arial", 16, "bold")
        )
        agent_header.grid(row=0, column=0, pady=(10, 5))

        self.schema_textbox = customtkinter.CTkTextbox(
            self.agent_frame,
            height=200
        )
        self.schema_textbox.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        button_container = customtkinter.CTkFrame(self.agent_frame, fg_color="transparent")
        button_container.grid(row=2, column=0, pady=10)

        self.write_config_button = customtkinter.CTkButton(
            button_container,
            text="写入目标配置",
            command=self._on_write_config_clicked,
            width=140
        )
        self.write_config_button.pack(side="left", padx=5)

        self.copy_context_button = customtkinter.CTkButton(
            button_container,
            text="复制 Context 给 Agent",
            command=self._on_copy_context_clicked,
            width=140
        )
        self.copy_context_button.pack(side="left", padx=5)

    def _build_target_project_area(self, row: int, column: int, columnspan: int):
        """Build target project mount area."""
        self.target_frame = customtkinter.CTkFrame(self.root)
        self.target_frame.grid(row=row, column=column, columnspan=columnspan, pady=10, padx=10, sticky="ew")
        self.target_frame.grid_columnconfigure(1, weight=1)

        target_header = customtkinter.CTkLabel(
            self.target_frame,
            text="目标项目挂载区",
            font=("Arial", 14, "bold")
        )
        target_header.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        self.select_config_button = customtkinter.CTkButton(
            self.target_frame,
            text="📂 选择目标项目 config.py",
            command=self._on_select_target_config,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            width=200
        )
        self.select_config_button.grid(row=1, column=0, pady=10, padx=10)

        self.target_path_label = customtkinter.CTkLabel(
            self.target_frame,
            text="未选择目标配置文件",
            font=("Arial", 12),
            text_color="#7F8C8D"
        )
        self.target_path_label.grid(row=1, column=1, pady=10, padx=10, sticky="w")

    def _build_control_area(self, row: int, column: int, columnspan: int):
        """Build control area with scan button and status."""
        self.control_frame = customtkinter.CTkFrame(self.root)
        self.control_frame.grid(row=row, column=column, columnspan=columnspan, pady=15)

        self.scan_button = customtkinter.CTkButton(
            self.control_frame,
            text="🔄 扫描设备",
            command=self._on_scan_clicked,
            fg_color="#3498DB",
            hover_color="#2980B9",
            height=35
        )
        self.scan_button.pack(side="left", padx=15)

        self.status_label = customtkinter.CTkLabel(
            self.control_frame,
            text="状态: 就绪",
            font=("Arial", 14)
        )
        self.status_label.pack(side="left", padx=15)

    def _bind_events(self):
        """Bind Tkinter virtual events for cross-thread communication."""
        self.root.bind("<<AudioTestComplete>>", self._on_audio_test_complete)
        self.root.bind("<<HardwareStateChanged>>", self._on_hardware_state_changed)
        self.root.bind("<<DeviceScanComplete>>", self._on_device_scan_complete)

    def _on_device_selected(self, selected_value: str):
        """Handle device selection from dropdown."""
        for dev in self._devices:
            display_name = f"{dev['device_id']}: {dev['device_name']}"
            if display_name == selected_value:
                self._selected_device_id = dev["device_id"]
                self._update_device_info(dev)
                break

    def _update_device_info(self, device: dict):
        """Update device info textbox with selected device details."""
        self.device_info_textbox.configure(state="normal")
        self.device_info_textbox.delete("1.0", "end")
        info = f"设备ID: {device['device_id']}\n"
        info += f"设备名称: {device['device_name']}\n"
        info += f"原生采样率: {device['native_sample_rate']} Hz\n"
        info += f"输入通道: {device['max_input_channels']}\n"
        info += f"输出通道: {device['max_output_channels']}\n"
        info += f"全双工支持: {'是' if device['is_duplex_supported'] else '否'}"
        self.device_info_textbox.insert("1.0", info)
        self.device_info_textbox.configure(state="disabled")

    def _on_scan_clicked(self):
        """Handle scan button click."""
        self.set_status("正在扫描设备...")
        self.scan_button.configure(state="disabled", text="扫描中...")
        if self.on_scan_requested:
            self.on_scan_requested()

    def _on_test_clicked(self):
        """Handle test button click."""
        if self._selected_device_id is None:
            self.set_status("请先选择设备！")
            return
        self.set_test_button_testing(True)
        self.set_status("正在播放测试音...")
        if self.on_test_triggered:
            self.on_test_triggered(self._selected_device_id)

    def _on_select_target_config(self):
        """Handle select target config button click."""
        file_path = filedialog.askopenfilename(
            title="选择目标项目配置文件",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self._target_config_path = file_path
            display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
            self.target_path_label.configure(text=display_path, text_color="#2ECC71")
            if self.on_target_config_selected:
                self.on_target_config_selected(file_path)

    def _on_write_config_clicked(self):
        """Handle write config button click."""
        if self.on_write_config:
            self.on_write_config()
        else:
            self.set_status("Config写入功能未连接")

    def _on_copy_context_clicked(self):
        """Handle copy context button click."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.schema_textbox.get("1.0", "end"))
        self.set_status("Context 已复制到剪贴板")
        if self.on_copy_context:
            self.on_copy_context()

    def _on_audio_test_complete(self, event):
        """Handle audio test completion virtual event."""
        self.set_status("测试音播放完成")

    def _on_hardware_state_changed(self, event):
        """Handle hardware state change virtual event."""
        self.set_status("硬件状态已更新")

    def _on_device_scan_complete(self, event):
        """Handle device scan completion virtual event."""
        self.scan_button.configure(state="normal", text="🔄 扫描设备")
        self.set_status("设备扫描完成")

    def set_test_button_testing(self, is_testing: bool):
        """Set test button state during audio test."""
        if is_testing:
            self.test_button.configure(
                state="disabled",
                text="测试中...",
                fg_color="#95A5A6"
            )
        else:
            self.test_button.configure(
                state="normal",
                text="▶ 播放测试音",
                fg_color="#2ECC71"
            )

    def update_device_list(self, devices: list):
        """Update device dropdown with discovered devices."""
        self._devices = devices
        if not devices:
            self.device_optionmenu.configure(values=["未发现设备"])
            return

        display_names = [f"{dev['device_id']}: {dev['device_name']}" for dev in devices]
        self.device_optionmenu.configure(values=display_names)
        self.device_optionmenu.set(display_names[0] if display_names else "请先扫描设备...")
        if devices:
            self._selected_device_id = devices[0]["device_id"]
            self._update_device_info(devices[0])

    def update_schema_display(self, schema_json: str):
        """Update schema textbox with JSON content."""
        self.schema_textbox.delete("1.0", "end")
        self.schema_textbox.insert("1.0", schema_json)

    def get_target_config_path(self) -> Optional[str]:
        """Get the selected target config file path."""
        return self._target_config_path

    def set_status(self, message: str):
        """Update status message."""
        self.status_label.configure(text=f"状态: {message}")

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()

    def destroy(self):
        """Destroy the window."""
        self.root.destroy()
