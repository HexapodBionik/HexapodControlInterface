import serial
import numpy as np


class RobotCommunication:
    def __init__(self):
        self.conn = None
        self.available_baudrates = [115200, 9600]

    def get_available_baudrates(self):
        return sorted(self.available_baudrates)

    def establish_connection(self, port: str, baudrate):
        self.conn = serial.Serial(port, baudrate)
        self.conn.write_timeout = 50

    def disconnect(self):
        self.conn.close()
        self.conn = None

    def send_bytes(self, bytes: np.array):
        if self.conn:
            self.conn.write(bytes)

    def send_data_terminal(self, command: str) -> None:
        if self.conn:
            i = 0
            for letter in command:
                self.conn.write(letter.encode("utf-8"))
                if i < len(command) - 1:
                    data = self.receive_data_terminal()
                i += 1

    def receive_data_terminal(self) -> bytes | None:
        if self.conn:
            return self.conn.readline()

    def execute_programme(self, programme: list):
        if self.conn:
            for command in programme:
                print(f"Sent command: {command}")
                command += "\r"
                self.send_data_terminal(command)

                data = self.receive_data_terminal()

                if int(data.decode().strip('\r').strip('\n')) == 0:
                    print("Success")
                else:
                    print("Failure")
                    return 1
            return 0