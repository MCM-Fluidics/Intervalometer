# Night Intervalometer

A compact Python/Kivy intervalometer overlay for interval photography and night-time camera work. The phone layout is portrait-oriented and keeps the camera view visible behind a translucent control box and red aiming cross.

## Current controls

The default sequence is:

| Control | Default | Meaning |
| --- | ---: | --- |
| `DELAY` | 3 sec | One-time wait before the first press |
| `LONG` | 1 sec | How long the shutter button is held |
| `INTERVAL` | 2 sec | Wait after one press is released before the next press |
| `NUMBER` | 5 | Number of presses |
| `TOTAL` | 00:16 | Calculated duration for the complete sequence |

The total updates while values are being edited. Empty, invalid, or too-small values are replaced with safe minimums when the sequence is started.

During a sequence, the active field pulses softly in red: `DELAY` while waiting to start, `LONG` while the shutter target is held, and `INTERVAL` while waiting for the next press. During the complete `LONG` hold, the red crosshair shows a continuous, gently breathing translucent ring. It fades when the simulated press is released.

## Run on a PC

Use Python 3.12 or 3.13. The current tested setup is Python 3.13 with Kivy 2.3.1.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Drag the box from any non-interactive area, including its instruction text or empty space. Text fields and buttons remain interactive. Drag the red target directly. These gestures work with both a mouse in the desktop preview and touch on Android.

In the desktop preview, the scheduler represents a camera push through the status text and animations. It does not control another desktop application.

To preview a smartphone-sized portrait window on the PC:

```powershell
C:/Users/Manuel/AppData/Local/Programs/Python/Python313/python.exe main.py --phone
```

The `--phone` option opens a 412 x 915 portrait window. Omit it for the normal desktop-sized window.

## Android build

### Easiest method: GitHub Actions

This project includes [`.github/workflows/build-apk.yml`](.github/workflows/build-apk.yml). After uploading the project to a GitHub repository:

1. Open the repository on GitHub and select **Actions**.
2. Select **Build Android APK**.
3. Select **Run workflow** and confirm.
4. When it finishes, open the workflow run and download `night-intervalometer-debug-apk` under **Artifacts**.
5. Copy the downloaded APK to the phone and open it to install.

The workflow pins its build Python to 3.11 and pip to 24.3.1, avoiding known Python/pip compatibility problems in the Python-for-Android build chain. It builds the APK on GitHub and avoids installing Android build tools on the PC.

For click-by-click beginner instructions, see [GITHUB_BEGINNER_GUIDE.md](GITHUB_BEGINNER_GUIDE.md).

### 1. Install WSL2

In an administrator PowerShell, install Ubuntu and restart Windows if requested:

```powershell
wsl --install -d Ubuntu
```

Open Ubuntu from the Start menu, create its Linux user, then install the Android build dependencies:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
	autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
	cmake libffi-dev libssl-dev
```

### 2. Build the debug APK

Build from the project folder mounted into WSL. The first build downloads the Android toolchain and can take a while:

```bash
cd /mnt/e/OneDrive/Desktop/Intervalometer
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install --upgrade pip
pip install buildozer cython==0.29.34
buildozer android debug deploy run
```

The APK is written to `bin/`. If USB deployment is not configured, build with `buildozer android debug`, then copy the APK from `bin/` to the phone and open it there.

### 3. Test on the Galaxy S21 FE

On the phone, enable **Developer options** and **USB debugging**, connect the USB cable, and accept the computer authorization prompt. For manual APK installation, allow the file manager to install unknown apps when Android asks.

The first APK verifies the portrait UI, movable box and crosshair, scheduler, live total, and animations. The native overlay service is included in `android_src/`; enable both Android permissions described below before testing Samsung Camera.

## Android overlay limitation

The APK now includes a native Android overlay service in `android_src/`. On first launch it opens the overlay permission screen; allow **Display over other apps**, then enable the app's accessibility service in **Settings -> Accessibility -> Installed apps**. After that, the Kivy host window hides and the compact native panel and crosshair remain on top of Samsung Camera. The accessibility service performs the held gesture at the crosshair position. The Python/Kivy desktop preview remains a simulation because desktop applications do not provide the same overlay/accessibility APIs.
