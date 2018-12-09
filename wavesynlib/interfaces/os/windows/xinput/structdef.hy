(require [wavesynlib.languagecenter.hy.cdef [struct]])
(import [ctypes.wintypes [BOOL WORD DWORD BYTE SHORT]])



(struct XINPUT-GAMEPAD [
    WORD wButtons
    BYTE bLeftTrigger
    BYTE bRightTrigger
    SHORT sThumbLX
    SHORT sThumbLY
    SHORT sThumbRX
    SHORT sThumbRY])


(struct XINPUT-STATE [
    DWORD dwPacketNumber
    XINPUT-GAMEPAD Gamepad])


(struct XINPUT-VIBRATION [
    WORD wLeftMotorSpeed
    WORD wRightMotorSpeed])


(struct XINPUT-BATTERY-INFORMATION [
    BYTE BatteryType
    BYTE BatteryLevel])

