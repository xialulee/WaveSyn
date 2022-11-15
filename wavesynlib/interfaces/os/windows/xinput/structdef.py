from ctypes import Structure
from ctypes.wintypes import BOOL, WORD, DWORD, BYTE, SHORT


class XINPUT_GAMEPAD(Structure):
    _fields_ = [
        ("wButtons", WORD), 
        ("bLeftTrigger", BYTE), 
        ("bRightTrigger", BYTE), 
        ("sThumbLX", SHORT), 
        ("sThumbLY", SHORT), 
        ("sThumbRX", SHORT), 
        ("sThumbRY", SHORT)
    ]


class XINPUT_STATE(Structure):
    _fields_ = [
        ("dwPacketNumber", DWORD), 
        ("Gamepad", XINPUT_GAMEPAD)
    ]


class XINPUT_VIBRATION(Structure):
    _fields_ = [
        ("wLeftMotorSpeed", WORD), 
        ("wRightMotorSpeed", WORD)
    ]


class XINPUT_BATTERY_INFORMATION(Structure):
    _fields_ = [
        ("BatteryType", BYTE), 
        ("BatteryLevel", BYTE)
    ]