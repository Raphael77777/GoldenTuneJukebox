import time
import subprocess
from gpiozero import Button

CLK = 17
DT  = 27
SW  = 22

STEP = 5
vol = 50

clk = Button(CLK, pull_up=False)
dt  = Button(DT,  pull_up=False)
sw  = Button(SW,  pull_up=True)

def set_volume(v):
    v = max(0, min(100, v))
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{v}%"],
        check=False
    )
    print(f"Volume: {v}%")
    return v

def toggle_mute():
    subprocess.run(
        ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
        check=False
    )
    print("Mute toggle")

vol = set_volume(vol)
last_clk = clk.value
last_press = 0

try:
    while True:
        cur_clk = clk.value
        if last_clk == 1 and cur_clk == 0:
            # Direction via DT
            if dt.value == 1:
                vol = set_volume(vol + STEP)
            else:
                vol = set_volume(vol - STEP)
        last_clk = cur_clk

        if sw.is_pressed and time.time() - last_press > 0.3:
            toggle_mute()
            last_press = time.time()

        time.sleep(0.001)

except KeyboardInterrupt:
    pass
