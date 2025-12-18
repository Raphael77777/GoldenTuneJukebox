import time, random, math
import board
import neopixel

# =======================
# CONFIG
# =======================
LED_COUNT = 47
LED_PIN = board.D18
BRIGHTNESS = 1.0

LEFT_LEN  = 18
TOP_LEN   = 11
RIGHT_LEN = 18
assert LEFT_LEN + TOP_LEN + RIGHT_LEN == LED_COUNT, "LEFT+TOP+RIGHT doit = LED_COUNT"

REVERSE_STRIP = False

pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB
)

# =======================
# GLOBAL SHOW GATE (pour preview sans afficher)
# =======================
_SHOW_ENABLED = True

def px_show():
    if _SHOW_ENABLED:
        pixels.show()

# =======================
# HELPERS
# =======================
def tnow(): return time.monotonic()

def clamp8(x): return max(0, min(255, int(x)))

def scale(c, f: float):
    return (clamp8(c[0]*f), clamp8(c[1]*f), clamp8(c[2]*f))

def add(c1, c2):
    return (min(255, c1[0]+c2[0]), min(255, c1[1]+c2[1]), min(255, c1[2]+c2[2]))

def lerp(a, b, t: float):
    return (
        clamp8(a[0] + (b[0]-a[0]) * t),
        clamp8(a[1] + (b[1]-a[1]) * t),
        clamp8(a[2] + (b[2]-a[2]) * t),
    )

def ease_in_out(t: float):
    # smoothstep
    return t*t*(3 - 2*t)

def wheel(pos: int):
    pos = pos & 255
    if pos < 85:   return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85  ; return (0, 255 - pos * 3, pos * 3)
    pos -= 170     ; return (pos * 3, 0, 255 - pos * 3)

def clear(show=True):
    pixels.fill((0,0,0))
    if show: px_show()

def fade_all(f=0.88):
    for i in range(LED_COUNT):
        pixels[i] = scale(pixels[i], f)

def set_px(i, c):
    if REVERSE_STRIP:
        i = LED_COUNT - 1 - i
    if 0 <= i < LED_COUNT:
        pixels[i] = c

def blend_px(i, c):
    if REVERSE_STRIP:
        i = LED_COUNT - 1 - i
    if 0 <= i < LED_COUNT:
        pixels[i] = add(pixels[i], c)

def snapshot_frame():
    return [pixels[i] for i in range(LED_COUNT)]

def apply_frame(frame):
    for i, c in enumerate(frame):
        set_px(i, c)

# ---- "U inversé" helpers (segments)
LEFT_START = 0
TOP_START = LEFT_START + LEFT_LEN
RIGHT_START = TOP_START + TOP_LEN

def left_idx(k):   return LEFT_START + k
def top_idx(k):    return TOP_START + k
def right_idx(k):  return RIGHT_START + k

def u_sym_pair(k):
    li = left_idx(k) if 0 <= k < LEFT_LEN else None
    rk = (RIGHT_LEN - 1 - k)
    ri = right_idx(rk) if 0 <= rk < RIGHT_LEN else None
    return li, ri

# =======================
# TRANSITIONS (FLUIDES)
# =======================
def preview_next_frame(next_fx, preview_time=0.22):
    """
    Lance le prochain FX pendant preview_time SANS affichage,
    puis retourne un snapshot de la frame obtenue.
    """
    global _SHOW_ENABLED
    _SHOW_ENABLED = False
    try:
        # Important: on ne veut pas "polluer" trop longtemps, juste un aperçu
        next_fx(duration=preview_time)
        frame = snapshot_frame()
    finally:
        _SHOW_ENABLED = True
    return frame

def transition_crossfade_to(next_fx, duration=1.2, steps=48, preview_time=0.22):
    """
    Crossfade réel: dernière frame courante -> 1ère frame du prochain FX.
    """
    from_frame = snapshot_frame()
    to_frame = preview_next_frame(next_fx, preview_time=preview_time)

    for s in range(steps):
        t = ease_in_out(s / (steps - 1))
        for i in range(LED_COUNT):
            set_px(i, lerp(from_frame[i], to_frame[i], t))
        px_show()
        time.sleep(duration / steps)

# =======================
# EFFECTS (inchangés, juste px_show())
# =======================
def fx_rainbow_comet(duration=12.0, speed=0.02, tail=14):
    t0 = tnow()
    hue = 0
    head = 0
    while tnow()-t0 < duration:
        pixels.fill((0,0,0))
        for i in range(tail):
            idx = (head - i) % LED_COUNT
            fade = 1.0 - (i / max(1, tail))
            set_px(idx, scale(wheel((hue + i*10) % 256), fade))
        px_show()
        head = (head + 1) % LED_COUNT
        hue = (hue + 3) % 256
        time.sleep(speed)

def fx_theater_chase_rainbow(duration=12.0, speed=0.06, spacing=3):
    t0 = tnow()
    q, base = 0, 0
    while tnow()-t0 < duration:
        pixels.fill((0,0,0))
        for i in range(LED_COUNT):
            if (i + q) % spacing == 0:
                set_px(i, wheel((base + i*5) % 256))
        px_show()
        q = (q + 1) % spacing
        base = (base + 5) % 256
        time.sleep(speed)

def fx_confetti(duration=12.0, speed=0.02, pop=0.35):
    t0 = tnow()
    clear(show=False)
    hue = random.randrange(256)
    while tnow()-t0 < duration:
        fade_all(0.90)
        if random.random() < pop:
            idx = random.randrange(LED_COUNT)
            hue = (hue + random.randint(5, 45)) % 256
            blend_px(idx, wheel(hue))
            if idx-1 >= 0: blend_px(idx-1, scale(wheel((hue+40)%256), 0.35))
            if idx+1 < LED_COUNT: blend_px(idx+1, scale(wheel((hue+220)%256), 0.35))
        px_show()
        time.sleep(speed)

def fx_galaxy_twinkle(duration=14.0, speed=0.03, density=0.10):
    t0 = tnow()
    buf = [(0,0,0)] * LED_COUNT
    base_h = random.randrange(256)
    while tnow()-t0 < duration:
        buf = [scale(c, 0.88) for c in buf]
        base_h = (base_h + 1) % 256
        for i in range(LED_COUNT):
            neb = scale(wheel((base_h + i*2) % 256), 0.03)
            buf[i] = add(buf[i], neb)
            if random.random() < density:
                buf[i] = add(buf[i], scale(wheel(random.randrange(256)), random.uniform(0.6, 1.0)))
        for i, c in enumerate(buf):
            set_px(i, c)
        px_show()
        time.sleep(speed)

def fx_double_fire_sides(duration=16.0, speed=0.03, cooling=0.10, sparking=0.55):
    t0 = tnow()
    heatL = [0.0]*LEFT_LEN
    heatR = [0.0]*RIGHT_LEN

    def heat_to_color(h):
        h = max(0.0, min(1.0, h))
        if h < 0.33: return (int(255*h/0.33), 0, 0)
        if h < 0.66:
            x=(h-0.33)/0.33
            return (255, int(180*x), 0)
        x=(h-0.66)/0.34
        return (255, 180+int(75*x), int(80*x))

    while tnow()-t0 < duration:
        for i in range(LEFT_LEN):
            heatL[i] = max(0.0, heatL[i] - random.random()*cooling)
        for i in range(RIGHT_LEN):
            heatR[i] = max(0.0, heatR[i] - random.random()*cooling)

        for i in range(LEFT_LEN-1, 1, -1):
            heatL[i] = (heatL[i]+heatL[i-1]+heatL[i-2])/3.0
        for i in range(RIGHT_LEN-1, 1, -1):
            heatR[i] = (heatR[i]+heatR[i-1]+heatR[i-2])/3.0

        if random.random() < sparking:
            j = random.randint(0, min(6, LEFT_LEN-1))
            heatL[j] = min(1.0, heatL[j] + random.uniform(0.5, 1.0))
        if random.random() < sparking:
            j = random.randint(0, min(6, RIGHT_LEN-1))
            heatR[j] = min(1.0, heatR[j] + random.uniform(0.5, 1.0))

        pixels.fill((0,0,0))
        for k in range(LEFT_LEN):
            set_px(left_idx(k), heat_to_color(heatL[k]))
        for k in range(RIGHT_LEN):
            set_px(right_idx(RIGHT_LEN-1-k), heat_to_color(heatR[k]))
        px_show()
        time.sleep(speed)

def fx_u_edge_wipe(duration=12.0, speed=0.02):
    t0 = tnow()
    hue = random.randrange(256)
    pos = 0
    while tnow()-t0 < duration:
        fade_all(0.86)
        set_px(pos, wheel(hue))
        px_show()
        pos = (pos + 1) % LED_COUNT
        hue = (hue + 2) % 256
        time.sleep(speed)

def fx_u_sym_wave(duration=14.0, speed=0.02):
    t0 = tnow()
    phase = 0.0
    while tnow()-t0 < duration:
        pixels.fill((0,0,0))
        for k in range(min(LEFT_LEN, RIGHT_LEN)):
            amp = (math.sin(phase + k*0.35) + 1.0)/2.0
            c = scale(wheel(int((k*12 + phase*30) % 256)), 0.15 + 0.85*amp)
            li, ri = u_sym_pair(k)
            if li is not None: set_px(li, c)
            if ri is not None: set_px(ri, c)
        for k in range(TOP_LEN):
            set_px(top_idx(k), scale(wheel(int((phase*40 + k*8) % 256)), 0.15))
        px_show()
        phase += 0.18
        time.sleep(speed)

def fx_strobe_soft(duration=8.0, bpm=120, hue=None):
    t0 = tnow()
    hue = random.randrange(256) if hue is None else hue
    period = 60.0 / bpm
    while tnow()-t0 < duration:
        c = scale(wheel(hue), 1.0)
        pixels.fill(c); px_show()
        time.sleep(period*0.08)
        for _ in range(12):
            fade_all(0.65)
            px_show()
            time.sleep(period*0.03)
        hue = (hue + 10) % 256

def fx_meteor_storm(duration=14.0, speed=0.02, spawn=0.30, max_m=4, tail=12):
    t0 = tnow()
    meteors = []
    while tnow()-t0 < duration:
        fade_all(0.86)
        if random.random() < spawn and len(meteors) < max_m:
            d = random.choice([-1, 1])
            pos = 0 if d == 1 else LED_COUNT-1
            meteors.append([pos, d, random.randrange(256)])
        alive = []
        for m in meteors:
            pos, d, hue = m
            for i in range(tail):
                idx = int(pos - i*d)
                if 0 <= idx < LED_COUNT:
                    blend_px(idx, scale(wheel((hue+i*6) % 256), 1.0 - i/max(1,tail)))
            m[0] = pos + d*1.2
            m[2] = (hue + 3) % 256
            if -tail < m[0] < LED_COUNT+tail:
                alive.append(m)
        meteors = alive
        px_show()
        time.sleep(speed)

def fx_rainbow_cycle(duration=14.0, speed=0.02):
    t0 = tnow()
    hue = 0
    while tnow()-t0 < duration:
        for i in range(LED_COUNT):
            set_px(i, wheel((hue + int(i*256/LED_COUNT)) % 256))
        px_show()
        hue = (hue + 2) % 256
        time.sleep(speed)

def fx_scanner_rainbow(duration=14.0, speed=0.015, tail=10):
    t0 = tnow()
    pos, d, hue = 0, 1, 0
    while tnow()-t0 < duration:
        pixels.fill((0,0,0))
        for i in range(tail):
            idx = pos - i*d
            if 0 <= idx < LED_COUNT:
                set_px(idx, scale(wheel((hue + i*12) % 256), 1.0 - i/max(1,tail)))
        px_show()
        pos += d
        if pos >= LED_COUNT-1: d = -1
        if pos <= 0: d = 1
        hue = (hue + 3) % 256
        time.sleep(speed)

def fx_top_marquee(duration=12.0, speed=0.06):
    t0 = tnow()
    phase = 0
    while tnow()-t0 < duration:
        pixels.fill((0,0,0))
        for k in range(LEFT_LEN):
            set_px(left_idx(k), scale((255, 60, 0), 0.08))
        for k in range(RIGHT_LEN):
            set_px(right_idx(k), scale((255, 60, 0), 0.08))
        for k in range(TOP_LEN):
            if (k + phase) % 3 == 0:
                set_px(top_idx(k), (255, 180, 60))
        px_show()
        phase = (phase + 1) % 3
        time.sleep(speed)

def fx_sparkle_white(duration=10.0, speed=0.02, density=0.20):
    t0 = tnow()
    clear(show=False)
    while tnow()-t0 < duration:
        fade_all(0.80)
        for _ in range(int(LED_COUNT * density)):
            idx = random.randrange(LED_COUNT)
            blend_px(idx, (255,255,255))
        px_show()
        time.sleep(speed)

def fx_center_burst(duration=12.0, speed=0.02):
    t0 = tnow()
    mid_top = TOP_LEN // 2
    radius = 0
    hue = random.randrange(256)
    while tnow()-t0 < duration:
        fade_all(0.84)
        c = wheel(hue)
        for k in range(TOP_LEN):
            dist = abs(k - mid_top)
            if dist == radius:
                blend_px(top_idx(k), c)
        lvl = max(0, (LEFT_LEN-1) - radius)
        li, ri = u_sym_pair(lvl)
        if li is not None: blend_px(li, scale(c, 0.8))
        if ri is not None: blend_px(ri, scale(c, 0.8))

        px_show()
        radius = (radius + 1) % max(LEFT_LEN, TOP_LEN)
        hue = (hue + 8) % 256
        time.sleep(speed)

def fx_noise_rainbow(duration=14.0, speed=0.03):
    t0 = tnow()
    base = random.randrange(256)
    while tnow()-t0 < duration:
        for i in range(LED_COUNT):
            n = random.random()
            set_px(i, scale(wheel((base + i*3) % 256), 0.15 + 0.85*n))
        px_show()
        base = (base + 2) % 256
        time.sleep(speed)

# =======================
# SHOW (durées plus longues + transitions crossfade)
# =======================
SHOW = [
    lambda duration=12.0: fx_top_marquee(duration=duration),
    lambda duration=14.0: fx_rainbow_comet(duration=duration),
    lambda duration=14.0: fx_u_sym_wave(duration=duration),
    lambda duration=16.0: fx_double_fire_sides(duration=duration),
    lambda duration=14.0: fx_meteor_storm(duration=duration),
    lambda duration=12.0: fx_confetti(duration=duration),
    lambda duration=14.0: fx_galaxy_twinkle(duration=duration),
    lambda duration=14.0: fx_scanner_rainbow(duration=duration),
    lambda duration=10.0: fx_sparkle_white(duration=duration),
    lambda duration=14.0: fx_rainbow_cycle(duration=duration),
    lambda duration=12.0: fx_u_edge_wipe(duration=duration),
    lambda duration=12.0: fx_center_burst(duration=duration),
    lambda duration=14.0: fx_noise_rainbow(duration=duration),
    lambda duration=8.0:  fx_strobe_soft(duration=duration, bpm=128),
    lambda duration=12.0: fx_theater_chase_rainbow(duration=duration),
]

def main():
    clear()
    i = 0
    while True:
        cur_fx = SHOW[i % len(SHOW)]
        next_fx = SHOW[(i + 1) % len(SHOW)]

        # run current
        cur_fx()  # duration gérée par le lambda

        # smooth transition vers le prochain
        transition_crossfade_to(next_fx, duration=1.2, steps=50, preview_time=0.22)

        i += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
