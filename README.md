# Minitel Fortune Teller

Interactive fortune-telling machine for a French Minitel. The active
`fortune80qr.py` application collects birth data, creates individual or partner
analyses with OpenAI and Kerykeion, and presents the result on the Minitel, on a
thermal receipt, and as an uploadable PDF with a QR code.

## Active files

- `fortune80qr.py`: current main application
- `pynitel.py`: Minitel communication
- `settings.ini`: runtime configuration
- `WM/lang.csv`: interface text in French, English, German, and Spanish
- `WM/CC.csv`: country and language mapping
- `fortunestart.service`: systemd service for DietPi/Raspberry Pi
- `tests/`: hardware-independent automated tests
- `archive/`: old program versions, assets, and historical utility scripts that
  are not used by the active application

## Hardware

- Minitel connected to the `/dev/ttyUSB0` serial port
- Arduino coin counter, detected automatically through a port description
  containing `Arduino`
- Optional ESC/POS thermal printer
- Optional HID USB relay

The Minitel runs at 1200 or 4800 baud according to `[prefs] speed`. The Arduino
coin counter uses 19200 baud.

## Installation on DietPi

```bash
git clone https://github.com/flapfrance/Minitel-Fortune-Teller.git
cd Minitel-Fortune-Teller
APP_USER="$(id -un)"
APP_DIR="$(pwd -P)"
sudo apt update
sudo apt install python3-venv python3-dev build-essential pkg-config libcairo2-dev libusb-1.0-0
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
sudo usermod -aG dialout "$APP_USER"
```

If the repository is already available locally, start with `cd` into that
checkout and set `APP_USER` and `APP_DIR` as shown above. Log in again or
restart the system after changing the group membership.

Do not store the OpenAI key in `settings.ini`. It is loaded from
`/etc/minitel-fortune.env`:

```text
OPENAI_API_KEY=...
```

The file should only be readable by root:

```bash
sudo chmod 600 /etc/minitel-fortune.env
```

## Configuration

### `[prefs]`

- `speed`: Minitel baud rate, normally `4800`
- `timer`: timeout and screensaver interval in seconds
- `lang_code`: initial language (`FR`, `EN`, `DE`, or `ES`)
- `ip_adr`: displayed local address

### `[printer]`

- `auto_print = yes/no`: print the completed analysis automatically
- `print_special_code = yes/no`: print a detachable special code after the QR
  code; when set to `no`, the receipt is cut completely immediately after the
  QR code
- `p_idvend`, `p_idprod`: printer USB identifiers
- `p_timer`, `p_3`, `p_4`: reserved legacy fields

The same option is available as `Spec. Code` on the Minitel settings page.

### `[IA]`

- `ia_model`: OpenAI model
- `max_tok`: requested visible response length
- `max_completion_tok`: complete output limit, including reasoning tokens
- `reasoning_effort`: model reasoning setting
- `partner_extra_question = yes/no`: enable an additional question for partner
  analyses

### `[astrology]` and `[pdf]`

These sections control the astrology charts for the thermal receipt and PDF.
The charts can be enabled independently with `print_chart` and `include_chart`.
`chart_width`, `chart_render_scale`, `chart_threshold`, and `chart_line_boost`
control the quality of the black-and-white thermal print.

### `[coin_counter]`

- `enabled = yes`: payment is required; input remains locked when no Arduino is
  detected
- `enabled = no`: operate without a coin counter

The coin counter authorizes a session with `CMD:WAIT`, `WAIT`, or `WAIT_FOR_OK`.
After completing the prediction, the Pi sends `OK` and locks the next session.
A stale `WAIT` generated immediately after the reset is ignored.

## Minitel settings

Enter `98` on the welcome page to open the settings page. Options including
`Auto Print` and `Coin Count` can be changed with `YES` or `NO`. Press `ENVOI`
to save the values. Coin-counter changes take effect after restarting the
service.

To reboot or shut down the system, enter `YES` in the corresponding field and
confirm with `ENVOI`. The service user only needs these specific sudo rights:

```bash
APP_USER="$(id -un)"
printf '%s ALL=(root) NOPASSWD: /usr/bin/systemctl reboot, /usr/bin/systemctl poweroff, /usr/bin/systemctl --no-block restart fortunestart.service\n' "$APP_USER" \
  | sudo tee /etc/sudoers.d/minitel-fortune >/dev/null
sudo chmod 440 /etc/sudoers.d/minitel-fortune
sudo visudo -cf /etc/sudoers.d/minitel-fortune
```

## systemd service

`fortunestart.service` is a portable template. Install it from the repository
directory after replacing `@APP_USER@` and `@APP_DIR@` with the current user and
the absolute checkout path:

```bash
APP_USER="$(id -un)"
APP_DIR="$(pwd -P)"
sed -e "s|@APP_USER@|$APP_USER|g" -e "s|@APP_DIR@|$APP_DIR|g" fortunestart.service \
  | sudo tee /etc/systemd/system/fortunestart.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now fortunestart.service
```

Run these commands from a path that does not contain `|` or `&`, because those
characters have a special meaning in the `sed` replacement expression.

Check the status and follow the live log with:

```bash
sudo systemctl status fortunestart.service
sudo journalctl -fu fortunestart.service
```

## Updating from the development computer

```bash
REMOTE="user@hostname"
REMOTE_DIR="projects/minitel/Fortune2"
scp fortune80qr.py pynitel.py settings.ini "$REMOTE:$REMOTE_DIR/"
ssh "$REMOTE" 'sudo systemctl restart fortunestart.service'
```

Always transfer `pynitel.py` when keyboard handling or Minitel communication
has been changed.

After changing `fortunestart.service`, also run:

```bash
APP_USER="$(id -un)"
APP_DIR="$(pwd -P)"
sed -e "s|@APP_USER@|$APP_USER|g" -e "s|@APP_DIR@|$APP_DIR|g" fortunestart.service \
  | sudo tee /etc/systemd/system/fortunestart.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl restart fortunestart.service
```

## Tests

The hardware-independent test suite covers the configuration, language data,
coin-counter protocol, reset guard, printer parameters, PDF upload, Minitel
keyboard handling, and reboot/shutdown commands:

```bash
python3 -m py_compile fortune80qr.py pynitel.py
python3 -m unittest discover -s tests -v
```

## Troubleshooting

- Payment not detected: look for `Read from coin counter` in the journal.
- Free session after a reset: the journal should contain
  `Ignoring coin signal generated during counter reset`.
- No printout: check USB permissions and look for `USB printer unavailable` in
  the journal.
- Reboot or shutdown denied: validate the sudoers file with
  `sudo visudo -c -f /etc/sudoers.d/minitel-fortune`.
- No AI response: check `OPENAI_API_KEY` and look for `Chatbot error` in the
  journal.
