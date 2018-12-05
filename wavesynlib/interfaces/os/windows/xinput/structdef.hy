(require [wavesynlib.languagecenter.hy.cdef [compound]])
(import [ctypes [Structure]])
(import [ctypes.wintypes [BOOL WORD DWORD BYTE SHORT]])



(compound Structure XINPUT-GAMEPAD [
    WORD wButtons
    BYTE bLeftTrigger
    BYTE bRightTrigger
    SHORT sThumbLX
    SHORT sThumbLY
    SHORT sThumbRX
    SHORT sThumbRY])


(compound Structure XINPUT-STATE [
    DWORD dwPacketNumber
    XINPUT-GAMEPAD Gamepad])


(compound Structure XINPUT-VIBRATION [
    WORD wLeftMotorSpeed
    WORD wRightMotorSpeed])


(compound Structure XINPUT-BATTERY-INFORMATION [
    BYTE BatteryType
    BYTE BatteryLevel])

