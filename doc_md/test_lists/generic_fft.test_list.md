# generic_fft

## Inherit

- [generic_audio.test_list](generic_audio.test_list.md)
- [generic_camera.test_list](generic_camera.test_list.md)
- [generic_display_panel.test_list](generic_display_panel.test_list.md)
- [generic_ec_component_accel.test_list](generic_ec_component_accel.test_list.md)
- [generic_ethernet.test_list](generic_ethernet.test_list.md)
- [generic_touchpad.test_list](generic_touchpad.test_list.md)
- [generic_touchscreen.test_list](generic_touchscreen.test_list.md)
- [generic_wireless.test_list](generic_wireless.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## ChromeboxFFTItems

Test plans for Final Functional Test. The FFT is usually the final stage of FATP, to make sure the system is functional, including most interactive tests.

### Serial subtests

- Probe
- LED
- HWButton
- Wireless
- Bluetooth
- AudioJack
- SpeakerDMic
- CheckRetimerFirmware
- ExternalDisplay
- USBTypeATest
- USBTypeCTest
- SDPerformance
- Ethernet
- Buzzer
- CECHDMI1

## FFT

### Serial subtests

- [FFTStart]()
- Barrier
- [FFTItems]()
- CheckPoint
- [FFTEnd]()

## FFTEnd

### Serial subtests

- StationEnd
- CheckPoint

## FFTItems

Test plans for Final Functional Test. The FFT is usually the final stage of FATP, to make sure the system is functional, including most interactive tests.

### Serial subtests

- Probe
- LidSwitch
- DisplayPoint
- Display
- Backlight
- CameraTests
- LED
- Keyboard
- HWButton
- Wireless
- Bluetooth
- AudioJack
- SpeakerDMic
- ProximitySensor
- Touchpad
- Touchscreen
- StylusAndGarage
- WirelessCharger
- CheckRetimerFirmware
- HPS
- ExternalDisplay
- USBTypeATest
- USBTypeCTest
- SDPerformance
- BaseAccelerometersCalibration
- LidAccelerometersCalibration
- AccelerometersLidAngle
- ScreenRotation
- GyroscopeCalibration
- Gyroscope
- GyroscopeAngle

## FFTStart

### Serial subtests

- StationStart
