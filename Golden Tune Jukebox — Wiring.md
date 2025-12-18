# Golden Tune Jukebox — Wiring (ASCII)

```
Recommended
Use AWG18–20 for 5V/GND wire
Use AWG24–26 for GPIO/DATA wire
```

## 1) Power distribution (5V / 8A)
```
[DC 5V 8A]
|
v
[DC Adapter (2 screw)]
|
+------------------------------+
|                              |
v                              v
[GND Terminal]                [+5V Terminal]
```

```
[+5V Terminal (minimum 3 screws)]
| | |
| | |
| | |
| | +------> WS2812B +5V
| +----------> Capacitor (1000µF / 6.3V)
+--------------> USB-C decoy +5V
```
```
[GND Terminal (minimum 4 screws)]
| | | |
| | | |
| | | +--> RPi GND (Pin 39) - (common ground required)
| | +------> WS2812B GND
| +----------> Capacitor (1000µF / 6.3V)
+--------------> USB-C decoy GND
```
---

## 2) Raspberry Pi power (via USB-C decoy)
```
+5V Terminal ----> USB-C Decoy ----> Raspberry Pi USB-C (Power In)
GND Terminal ----> USB-C Decoy ----> Raspberry Pi USB-C (Power In)
```
---

## 3) WS2812B LED strip
### Power (Wire)
```
WS2812B +5V -----------------------> +5V Terminal
WS2812B GND -----------------------> GND Terminal
```

### Data (Pin 12)
```
WS2812B DIN <----------------------- RPi GPIO18 (Pin 12)
```

> Recommended : Add a **220Ω resistor** in series on the DATA line near the first LED. Resistor as close as possible to the first LED.
---

## 4) Rotary encoder (Pin 9-11-13-15-17)
```
GND ------------------> RPi GND (Pin 9)
CLK ------------------> RPi GPIO17 (Pin 11)
DT -------------------> RPi GPIO27 (Pin 13)
SW -------------------> RPi GPIO22 (Pin 15)
+ --------------------> RPi 3.3V (pin 17)
```
---

## 5) Power switch (Pin 33-34)
```
one side --------------------> RPi GPIO13 (Pin 33)
other side ------------------> RPi GND (Pin 34)
```
---

## 6) Speaker (USB)
```
Raspberry Pi USB --------------------> Speaker (USB)
```
---

## 7) Screen (HDMI + USB)
```
Raspberry Pi HDMI -------------------> Screen HDMI (display)
Raspberry Pi USB --------------------> Screen USB (touch + power)
```
---