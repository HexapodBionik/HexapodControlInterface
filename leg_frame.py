import tkinter
import tkinter.messagebox
import customtkinter
from connection import serial_ports
from tkinter import filedialog
from servo_control import entry_angle_to_transmit_data, one_servo_frame, ServoOpCodes


class LegFrame(customtkinter.CTkFrame):
    def __init__(self, master, connection, leg_id: int):
        super().__init__(master)

        # General variables
        self._leg_id = leg_id
        self._connection = connection

        self.header_label = customtkinter.CTkLabel(self,
                                                   text=f"Leg {self._leg_id}",
                                                   anchor="w")

        self.servo_frames = []

        # Add three ServoFrames under each LegFrame
        for i in range(1, 4):
            servo_id = self._leg_id * 10 + i
            servo_frame = ServoFrame(self, self._connection, servo_id)
            servo_frame.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.servo_frames.append(servo_frame)

        # Place LegFrame widgets using grid
        self.header_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def disable_leg(self):
        for servo_frame in self.servo_frames:
            servo_frame.disable_servo()


class ServoFrame(customtkinter.CTkFrame):
    def __init__(self, master, connection, servo_id: int):
        super().__init__(master)

        self._connection = connection
        self._servo_id = servo_id
        self._servo_active = False
        self._servo_angle = None
        self._default_angle = 0

        self._slider_label = customtkinter.CTkLabel(self, text="Angle:", anchor="w")
        self._slider = customtkinter.CTkSlider(self, from_=0, to=180, orientation="horizontal", command=self.update_slider)

        self._joint1_label = customtkinter.CTkLabel(self, text=f"Servo {servo_id}", anchor="w")
        self._value_entry = customtkinter.CTkEntry(self, placeholder_text="0.0", font=customtkinter.CTkFont(size=14), width=60, validate='key', validatecommand=(self.register(self.validate_entry), '%P'))
        self._value_entry.bind("<KeyRelease>", command=self.update_entry)

        self._dynamic_control_var = customtkinter.BooleanVar()
        self._dynamic_control_checkbox = customtkinter.CTkCheckBox(self, text="Dynamic control", variable=self._dynamic_control_var)

        self._start_servo = customtkinter.CTkButton(self, text="Start", width=6, command=self.start_servo)
        self._stop_servo = customtkinter.CTkButton(self, text="Stop", width=6, command=self.disable_servo)
        self._set_servo_angle = customtkinter.CTkButton(self, text="Set Angle", width=8, command=self.set_servo_angle)

        # Status indicator using Canvas
        self._status_canvas = customtkinter.CTkCanvas(self, width=20, height=20, bg="white", bd=0, highlightthickness=0)

        # Set initial status to red (not working)
        self.set_status_icon("red")

        # Use the grid manager to arrange widgets side by side
        self._joint1_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._dynamic_control_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self._slider_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self._slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self._value_entry.grid(row=1, column=2, padx=5, pady=5, sticky="ew", ipadx=5)
        self._start_servo.grid(row=1, column=3, padx=5, pady=5)
        self._stop_servo.grid(row=1, column=4, padx=5, pady=5)
        self._set_servo_angle.grid(row=1, column=5, padx=5, pady=5)
        self._status_canvas.grid(row=1, column=6, padx=5, pady=5, sticky="e")

        # Update widgets
        self.update_slider(self._default_angle)
        self.update_entry(self._default_angle)

    def validate_entry(self, new_value):
        if new_value == "":
            return True

        if new_value.count('.') == 1:
            if new_value.replace('.', '', 1).isdigit() and len(new_value) <= 6:
                return True
        else:
            if new_value.isdigit() and len(new_value) <= 3:
                return True

        return False

    def update_slider(self, value):
        self._value_entry.delete(0, tkinter.END)
        self._value_entry.insert(0, round(value, 4))

        if self._dynamic_control_var.get():
            self.set_servo_angle()

    def update_entry(self, value):
        try:
            self._slider.set(float(self._value_entry.get()))
        except:
            pass

    def start_servo(self):
        if self._connection.conn is not None:
            angle = self._value_entry.get()
            integer_part, float_part = entry_angle_to_transmit_data(angle)
            spi_frame = one_servo_frame(self._servo_id, ServoOpCodes.START.value,
                                    integer_part, float_part)

            print(spi_frame)
            values = bytearray(spi_frame)
            self._connection.conn.write(values)
            self.set_status_icon("green")
            self._servo_active = True

    def disable_servo(self):
        if self._connection.conn is not None:
            spi_frame = one_servo_frame(self._servo_id, ServoOpCodes.STOP.value, 10, 10)

            print(spi_frame)
            values = bytearray(spi_frame)
            self._connection.conn.write(values)
            self.set_status_icon("red")
            self._servo_active = False

    def set_servo_angle(self):
        if self._servo_active and self._connection.conn is not None:
            angle = self._value_entry.get()
            integer_part, float_part = entry_angle_to_transmit_data(angle)
            spi_frame = one_servo_frame(self._servo_id,
                                        ServoOpCodes.SET.value,
                                        integer_part, float_part)

            values = bytearray(spi_frame)
            print(spi_frame)
            self._connection.conn.write(values)

    def set_status_icon(self, color):
        # Update the status icon based on the specified color
        if color == "green":
            self._status_canvas.configure(bg="green")
        elif color == "red":
            self._status_canvas.configure(bg="red")
