WINDOWS_ARM_HELP = """
Windows ARM64 detected. Choose one option:
 
OPTION 1 - Use x64 FFmpeg via emulation (easiest):
  Open PowerShell and run:
    winget install ffmpeg
 
OPTION 2 - Native ARM64 build (faster):
  1. Download ARM64 build from:
     https://github.com/AnimMouse/ffmpeg-autobuild/releases
     (Look for "ffmpeg-*-win64-arm-gpl.zip")
  2. Extract to C:\\ffmpeg
  3. Add C:\\ffmpeg\\bin to your PATH:
     - Press Win+X, select "System"
     - Click "Advanced system settings"
     - Click "Environment Variables"
     - Edit "Path" and add: C:\\ffmpeg\\bin
  4. Restart your terminal
"""

WINDOWS_NON_ARM_HELP = """
Windows x64 detected. Choose one option:
 
OPTION 1 - Using winget (recommended):
  Open PowerShell and run:
    winget install ffmpeg
 
OPTION 2 - Manual install:
  1. Download from: https://www.gyan.dev/ffmpeg/builds/
     (Get "ffmpeg-release-essentials.zip")
  2. Extract to C:\\ffmpeg
  3. Add C:\\ffmpeg\\bin to your PATH
  4. Restart your terminal
"""

LINUX_HELP = """
Linux detected. Install using your package manager:
 
  Debian/Ubuntu:  sudo apt update && sudo apt install ffmpeg
  Fedora:         sudo dnf install ffmpeg
  Arch:           sudo pacman -S ffmpeg
 
For ARM64 (Raspberry Pi, etc.), the same commands work.
"""

MAC_OS_HELP = """
macOS detected. Install using Homebrew:
 
  brew install ffmpeg
 
If you don't have Homebrew:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
"""

OTHER_OS_HELP = """
{os_name} detected.
Please install ffmpeg using your system's package manager.
"""