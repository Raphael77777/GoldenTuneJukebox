import time
import os
import RPi.GPIO as GPIO

PIN = 13                 # GPIO13 (pin 33)
BOOT_GRACE = 10          # ignore tout pendant 10s après boot
DEBOUNCE = 0.10          # 100ms stable
POLL = 0.02              # 50 Hz

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def stable_for(seconds: float) -> bool:
    """Retourne True si l'état reste identique pendant 'seconds'."""
    state0 = GPIO.input(PIN)
    t0 = time.monotonic()
    while time.monotonic() - t0 < seconds:
        if GPIO.input(PIN) != state0:
            return False
        time.sleep(POLL)
    return True

try:
    # Laisse le système démarrer + évite les glitches
    time.sleep(BOOT_GRACE)

    last = GPIO.input(PIN)

    while True:
        cur = GPIO.input(PIN)

        # Dès que l'utilisateur bascule le switch (dans un sens ou l'autre)
        if cur != last:
            # anti-rebond + stabilité
            if stable_for(DEBOUNCE):
                os.system("shutdown -h now")
                break

        last = cur
        time.sleep(POLL)

finally:
    GPIO.cleanup()
