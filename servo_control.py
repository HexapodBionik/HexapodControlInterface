from typing import Tuple
from enum import Enum


class FrameType(Enum):
    ALL_SERVO = 0
    ONE_LEG = 1
    ONE_SERVO = 2
    READ_ADC = 3
    OTHER = 4


class ServoOpCodes(Enum):
    START = 1
    STOP = 2
    SET = 3


# TODO READ_ADC frame length to be defined
frame_lengths = {
    FrameType.ALL_SERVO: 37,
    FrameType.ONE_LEG: 8,
    FrameType.ONE_SERVO: 6,
    FrameType.READ_ADC: 0
}


def entry_angle_to_transmit_data(entry: str) -> Tuple[int, int]:
    entry_filtered = entry.replace('\r', '').replace('\n', '')
    try:
        entry_number = float(entry_filtered)
        integer_part = int(entry_number)
        float_part = int((entry_number-integer_part)*100)

        if integer_part > 255 or float_part > 99:
            raise Exception("Incorrect angle value")

        return integer_part, float_part
    except Exception as e:
        print(e)


def one_servo_frame(servo_id: int, servo_op_code: int,
                             angle_int_part: int, angle_float_part: int):
    one_servo_list = [
        frame_lengths[FrameType.ONE_SERVO], FrameType.ONE_SERVO.value,
        servo_id, servo_op_code, angle_int_part, angle_float_part
    ]
    return one_servo_list
