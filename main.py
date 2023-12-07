import customtkinter
from communication import RobotCommunication
from connection import serial_ports
from leg_frame import LegFrame

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # create connection object
        self.conn = RobotCommunication()

        # configure window
        self.title("Hexapod Control Interface")
        self.geometry(f"{1920}x{1080}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self._configure_sidebar_frame()

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, columnspan=3, rowspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.tabview.add("Leg controls & position")
        self.tabview.add("Inverse kinematics")
        self.tabview.add("Forward kinematics")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.connection_option_menu.set("COM")
        self.baudrate_option_menu.set("Baudrate")

        self._configure_controls_frame()
        self.refresh_serial_port()

    def _configure_sidebar_frame(self):
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140,
                                                    corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 text="Hexapod Control Interface",
                                                 font=customtkinter.CTkFont(
                                                     size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.refresh_button = customtkinter.CTkButton(self.sidebar_frame,
                                                        command=self.refresh_serial_port,
                                                        text="Refresh")
        self.refresh_button.grid(row=3, column=0, padx=20, pady=10)

        self.manage_connection_button = customtkinter.CTkButton(
            self.sidebar_frame,
            command=self.manage_connection,
            text="Connect")
        self.manage_connection_button.grid(row=4, column=0, padx=20, pady=10)

        self.connection_option_menu = customtkinter.CTkOptionMenu(
            self.sidebar_frame, dynamic_resizing=True, values=[])
        self.connection_option_menu.grid(row=1, column=0, padx=20, pady=10)

        baudrates = [str(x) for x in self.conn.get_available_baudrates()]

        self.baudrate_option_menu = customtkinter.CTkOptionMenu(
            self.sidebar_frame, dynamic_resizing=True, values=baudrates)
        self.baudrate_option_menu.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                            text="Appearance Mode:",
                                                            anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame, values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20,
                                              pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                    text="UI Scaling:",
                                                    anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

    def _configure_controls_frame(self):
        self.joints_frame = customtkinter.CTkFrame(self.tabview.tab("Leg controls & position"), width=300, height=100)
        self.joints_frame.grid(row=0, column=0, padx=20, pady=20)

        self.legs = []
        for i in range(1, 7):
            frame = LegFrame(self.joints_frame, self.conn, leg_id=i)
            if i > 3:
                frame.grid(row=i-3, column=1)
            else:
                frame.grid(row=i, column=0)
            self.legs.append(frame)

    def refresh_serial_port(self):
        connections = serial_ports()
        self.connection_option_menu.configure(values=connections)
        self.connection_option_menu.update()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def manage_connection(self):
        if self.conn.conn is None:
            port = self.connection_option_menu.get()
            baudrate = self.baudrate_option_menu.get()

            if port != "COM" and baudrate != "Baudrate":
                baudrate = int(baudrate)
                self.conn.establish_connection(port, baudrate)
                self.manage_connection_button.configure(text="Disconnect")

        else:
            self.conn.disconnect()
            self.manage_connection_button.configure(text="Connect")


if __name__ == "__main__":
    app = App()
    app.mainloop()