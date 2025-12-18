# Golden Tune Jukebox — Script

### Update the Raspberry Pi:
```
sudo apt update
sudo apt upgrade
```

### Install prerequisites :
```
sudo apt install -y python3-full python3-venv pipewire-audio-client-libraries python3-gpiozero python3-lgpio curl libasound2t64 chromium unclutter
sudo apt install -y equivs
sudo apt install -y pulseaudio-utils
```

### Create the libasound2 compatibility package :
```
cat > /tmp/libasound2-compat <<'EOF'
Section: misc
Priority: optional
Standards-Version: 3.9.2

Package: libasound2
Version: 1.2.14-1+rpt1+compat1
Maintainer: local <local@localhost>
Architecture: all
Depends: libasound2t64
Description: Compatibility package for libasound2 (t64 transition)
EOF
equivs-build /tmp/libasound2-compat
sudo dpkg -i ./libasound2_1.2.14-1+rpt1+compat1_all.deb
```

### Install raspotify :
```
curl -sSL https://dtcooper.github.io/raspotify/install.sh | sh
```

### Create configuration directory :
```
cd /home/user/
mkdir -p ~/.config/systemd/user
```

### Create a venv in directory /jukebox :
```
cd /home/user/
mkdir -p ~/jukebox
cd ~/jukebox
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install rpi_ws281x adafruit-circuitpython-neopixel RPi.GPIO gpiozero
deactivate
```

### Create a venv in directory /nowplaying :
```
cd /home/user/
mkdir -p ~/nowplaying
cd ~/nowplaying
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install flask requests python-dotenv
deactivate
```

## > 1.0 LED

```
sudo reboot
cd /home/user/jukebox/
```

### Create the LED script :
```
sudo nano led_fullshow.py
```

### Make it executable :
```
sudo chmod +x /home/user/jukebox/led_fullshow.py
```

### Run the LED script : 
```
sudo ~/jukebox/.venv/bin/python led_fullshow.py
```

### Create the service :
```
sudo nano /etc/systemd/system/led_fullshow.service
```

### Run the service : 
```
sudo systemctl daemon-reload
sudo systemctl enable led_fullshow.service
sudo systemctl restart led_fullshow.service
sudo systemctl status led_fullshow.service --no-pager
```

## > 2.0 VOLUME

```
sudo reboot
cd /home/user/jukebox/
```

### Create the VOLUME script : 
```
sudo nano volume_decoder.py
```

### Make it executable :
```
sudo chmod +x /home/user/jukebox/volume_decoder.py
```

### Run the VOLUME script : 
```
python3 volume_decoder.py
```

### Create the service :
```
sudo nano ~/.config/systemd/user/volume_decoder.service
```

### Run the service : 
```
systemctl --user daemon-reload
systemctl --user enable --now volume_decoder.service
```

### Create the boot service :
```
sudo nano ~/.config/systemd/user/volume_boot.service
```

### Run the boot service : 
```
systemctl --user daemon-reload
systemctl --user enable --now volume_boot.service
```

### Enable boot service :
```
systemctl --user daemon-reload
sudo loginctl enable-linger user
```

## > 3.0 SOUND 

### List speakers :
```
pactl list short sinks
```

### Copy the name of the speaker (the one that start with usb-...) and use it below instead of 'USB_SINK_NAME' :
```
pactl set-default-sink USB_SINK_NAME
```

### Test it :
```
paplay /usr/share/sounds/alsa/Front_Center.wav
```

## > 4.0 SHUTDOWN

```
sudo reboot
cd /home/user/jukebox/
```

### Create the SHUTDOWN script : 
```
sudo nano power_switch.py
```

### Make it executable :
```
sudo chmod +x /home/user/jukebox/power_switch.py
```

### Enable shutdown without password :
```
sudo visudo
```

### Add at the very bottom (replace user by the actual user) :
```
user ALL=(ALL) NOPASSWD: /sbin/shutdown
```

### Create the service :
```
sudo nano /etc/systemd/system/power_switch.service
```

### Run the service : 
```
sudo systemctl daemon-reload
sudo systemctl enable power_switch.service
sudo systemctl restart power_switch.service
sudo systemctl status power_switch.service --no-pager
```

## > 5.0 SPOTIFY 

```
sudo reboot
```

### Identify USB DAC :
```
aplay -l
```

### Create an ALSA device with resampling for the USB DAC : 
```
sudo nano /etc/asound.conf
```

### Disable PipeWire / PulseAudio (trixie) :
```
systemctl --user stop pipewire pipewire-pulse wireplumber pulseaudio 2>/dev/null || true
systemctl --user disable pipewire pipewire-pulse wireplumber pulseaudio 2>/dev/null || true
sudo systemctl mask pipewire pipewire-pulse wireplumber pulseaudio 2>/dev/null || true
```

### Force the raspotify configuration via systemd :
```
sudo systemctl edit raspotify
```

### Reload systemd and run the service :
```
sudo systemctl daemon-reload
sudo systemctl restart raspotify
```

## > 6.0 SCREEN 

```
sudo reboot
cd /home/user/nowplaying/
```

### Create web ressources : 
```
mkdir /home/user/nowplaying/static/
cd /home/user/nowplaying/static/
sudo nano index.html
sudo nano style.css
```

---

```
cd /home/user/nowplaying/
```

### Create Spotify secrets : 
```
sudo nano ~/.env
```

### Create the APP script :
```
sudo nano app.py
```

### Make it executable :
```
sudo chmod +x ~/nowplaying/app.py
```

### Create the service :
```
sudo nano /etc/systemd/system/jukebox_api.service
```

### Run the service : 
```
sudo systemctl daemon-reload
sudo systemctl enable jukebox_api.service
sudo systemctl restart jukebox_api.service
sudo systemctl status jukebox_api.service --no-pager
```

---

```
cd /home/user/nowplaying/
```

### Configure Chromium :
```
mkdir -p /home/user/.config/chromium-kiosk
sudo chown -R user:user /home/user/.config/chromium-kiosk
```

### Manage browser preferences : 
```
sudo rm -f /home/user/.config/chromium-kiosk/Default/Preferences
sudo mkdir /home/user/.config/chromium-kiosk/Default/
sudo nano /home/user/.config/chromium-kiosk/Default/Preferences
```

### Create the KIOSK script :
```
sudo nano kiosk.sh
```

### Make it executable :
```
sudo chmod +x ~/nowplaying/kiosk.sh
```

### Create the service :
```
sudo nano /etc/systemd/system/jukebox_kiosk.service
```

### Run the service : 
```
sudo systemctl daemon-reload
sudo systemctl enable jukebox_kiosk.service
sudo systemctl restart jukebox_kiosk.service
sudo systemctl status jukebox_kiosk.service --no-pager
```

## > 7.0 LAUNCH

```
sudo reboot
```

### Verify services :
```
systemctl status led_fullshow.service --no-pager
systemctl status power_switch.service --no-pager
systemctl --user status volume_decoder.service --no-pager
systemctl status raspotify.service --no-pager
systemctl status jukebox_kiosk.service --no-pager
systemctl status jukebox_api.service --no-pager
```

### Quick Logs
```
journalctl -u raspotify -n 100 --no-pager
journalctl -u jukebox_kiosk -n 100 --no-pager
journalctl -u jukebox_api -n 100 --no-pager
```