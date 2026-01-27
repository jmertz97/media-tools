#!/usr/bin/env python3
"""
CRT TV Audio Effect Processor
 
Works on:
  - Windows x64 / ARM64
  - Linux x64 / ARM64
  - macOS (Intel / Apple Silicon)
  - Python 3.9 through 3.14+
 
Dependencies:
  pip install numpy scipy
 
Also requires ffmpeg installed on your system.
"""
 
import math
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
 
import numpy as np
from scipy.io import wavfile
 
 
with open("InputFile.txt", "r") as file:
    InputFile = file.read()

exec(InputFile)
 
 
# =====================================================================
# INTERNAL UTILITIES (no need to edit below this line)
# =====================================================================
 
def get_platform_info() -> dict:
    machine = platform.machine().lower()
    system = platform.system().lower()
 
    is_arm = any(arm_id in machine for arm_id in ("arm", "aarch"))
    is_windows = system == "windows"
    is_linux = system == "linux"
    is_macos = system == "darwin"
 
    arch_friendly = "ARM64" if is_arm else machine.upper()
    if is_windows:
        os_friendly = "Windows"
    elif is_linux:
        os_friendly = "Linux"
    elif is_macos:
        os_friendly = "macOS"
    else:
        os_friendly = system.capitalize()
 
    return {
        "machine": machine,
        "system": system,
        "is_arm": is_arm,
        "is_windows": is_windows,
        "is_linux": is_linux,
        "is_macos": is_macos,
        "arch_friendly": arch_friendly,
        "os_friendly": os_friendly,
        "full_name": f"{os_friendly} {arch_friendly}",
    }
 
 
def get_ffmpeg_path() -> str | None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
 
    if sys.platform == "win32":
        common_paths = [
            Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"),
            Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
            Path.home() / "scoop" / "shims" / "ffmpeg.exe",
        ]
        for p in common_paths:
            if p.exists():
                return str(p)
 
    return None
 
 
def get_ffmpeg_version(ffmpeg_path: str) -> str:
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        first_line = result.stdout.split("\n")[0] if result.stdout else ""
        return first_line
    except Exception:
        return "Unknown"
 
 
def print_system_info() -> tuple[dict, str | None]:
    info = get_platform_info()
    ffmpeg_path = get_ffmpeg_path()
 
    print("=" * 60)
    print(f"Platform: {info['full_name']}")
    print(f"Python:   {platform.python_version()} ({platform.architecture()[0]})")
    print(f"NumPy:    {np.__version__}")
 
    if ffmpeg_path:
        ffmpeg_info = get_ffmpeg_version(ffmpeg_path)
        print(f"FFmpeg:   {ffmpeg_info[:50]}...")
    else:
        print("FFmpeg:   NOT FOUND")
 
    print("=" * 60)
    return info, ffmpeg_path
 
 
def print_ffmpeg_install_guide(plat_info: dict) -> None:
    print("\n" + "=" * 60)
    print("FFMPEG NOT FOUND - INSTALLATION GUIDE")
    print("=" * 60)
 
    if plat_info["is_windows"]:
        if plat_info["is_arm"]:
            print("""
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
""")
        else:
            print("""
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
""")
 
    elif plat_info["is_linux"]:
        print("""
Linux detected. Install using your package manager:
 
  Debian/Ubuntu:  sudo apt update && sudo apt install ffmpeg
  Fedora:         sudo dnf install ffmpeg
  Arch:           sudo pacman -S ffmpeg
 
For ARM64 (Raspberry Pi, etc.), the same commands work.
""")
 
    elif plat_info["is_macos"]:
        print("""
macOS detected. Install using Homebrew:
 
  brew install ffmpeg
 
If you don't have Homebrew:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
""")
 
    else:
        print(f"""
{plat_info['os_friendly']} detected.
Please install ffmpeg using your system's package manager.
""")
 
    print("=" * 60 + "\n")
 
 
def get_script_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).parent.resolve()
 
 
# =====================================================================
# FFMPEG-BASED AUDIO I/O
# =====================================================================
 
def decode_audio_to_wav(
    ffmpeg_path: str,
    input_path: Path,
    output_wav_path: Path,
    target_sample_rate: int,
) -> None:
    cmd = [
        ffmpeg_path,
        "-y",
        "-i", str(input_path),
        "-ac", "1",
        "-ar", str(target_sample_rate),
        "-sample_fmt", "s16",
        str(output_wav_path),
    ]
 
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
 
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg decode failed:\n{result.stderr}")
 
 
def encode_wav_to_output(
    ffmpeg_path: str,
    input_wav_path: Path,
    output_path: Path,
    bitrate: str = "192k",
) -> None:
    output_ext = output_path.suffix.lower()
 
    cmd = [
        ffmpeg_path,
        "-y",
        "-i", str(input_wav_path),
    ]
 
    if output_ext == ".mp3":
        cmd.extend(["-codec:a", "libmp3lame", "-b:a", bitrate])
    elif output_ext == ".ogg":
        cmd.extend(["-codec:a", "libvorbis", "-q:a", "5"])
    elif output_ext == ".flac":
        cmd.extend(["-codec:a", "flac"])
    elif output_ext == ".wav":
        cmd.extend(["-codec:a", "pcm_s16le"])
    else:
        cmd.extend(["-b:a", bitrate])
 
    cmd.append(str(output_path))
 
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
 
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed:\n{result.stderr}")
 
 
def read_wav_to_numpy(wav_path: Path) -> tuple[np.ndarray, int]:
    sample_rate, data = wavfile.read(str(wav_path))
 
    if data.dtype == np.int16:
        samples = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        samples = data.astype(np.float64) / 2147483648.0
    elif data.dtype == np.float32 or data.dtype == np.float64:
        samples = data.astype(np.float64)
    else:
        samples = data.astype(np.float64) / np.max(np.abs(data) + 1e-12)
 
    if samples.ndim > 1:
        samples = np.mean(samples, axis=1)
 
    return samples, sample_rate
 
 
def write_numpy_to_wav(samples: np.ndarray, sample_rate: int, wav_path: Path) -> None:
    samples_clipped = np.clip(samples, -1.0, 1.0)
    int16_samples = (samples_clipped * 32767.0).astype(np.int16)
    wavfile.write(str(wav_path), sample_rate, int16_samples)
 
 
# =====================================================================
# DSP PROCESSING
# =====================================================================
 
def db_to_linear(db_value: float) -> float:
    return 10.0 ** (db_value / 20.0)
 
 
def apply_tv_eq(
    x: np.ndarray,
    sample_rate: int,
    band_low_hz: float,
    band_high_hz: float,
    low_mid_split_hz: float,
    mid_high_split_hz: float,
    low_gain_db: float,
    mid_gain_db: float,
    high_gain_db: float,
) -> np.ndarray:
    n = len(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    X = np.fft.rfft(x)
 
    low_gain = db_to_linear(low_gain_db)
    mid_gain = db_to_linear(mid_gain_db)
    high_gain = db_to_linear(high_gain_db)
 
    out_of_band_gain = db_to_linear(-24.0)
 
    gains = np.full_like(freqs, out_of_band_gain, dtype=np.float64)
 
    in_band = (freqs >= band_low_hz) & (freqs <= band_high_hz)
    low_band = (freqs < low_mid_split_hz) & in_band
    mid_band = (freqs >= low_mid_split_hz) & (freqs < mid_high_split_hz) & in_band
    high_band = (freqs >= mid_high_split_hz) & in_band
 
    gains[low_band] = low_gain
    gains[mid_band] = mid_gain
    gains[high_band] = high_gain
 
    X_processed = X * gains
    y = np.fft.irfft(X_processed, n=n)
    return y.astype(np.float64)
 
 
def add_hiss(x: np.ndarray, level_db_rel: float | None) -> np.ndarray:
    if level_db_rel is None:
        return x
 
    rms_signal = np.sqrt(np.mean(x ** 2) + 1e-12)
    if rms_signal == 0:
        return x
 
    target_rms_noise = rms_signal * db_to_linear(level_db_rel)
    if target_rms_noise <= 0:
        return x
 
    rng = np.random.default_rng()
    noise = rng.standard_normal(len(x)).astype(np.float64)
    rms_noise = np.sqrt(np.mean(noise ** 2) + 1e-12)
    noise *= (target_rms_noise / rms_noise)
 
    return x + noise
 
 
def add_hum(
    x: np.ndarray,
    sample_rate: int,
    level_db_rel: float | None,
    base_freq_hz: float,
    harmonics: int,
) -> np.ndarray:
    if level_db_rel is None:
        return x
 
    rms_signal = np.sqrt(np.mean(x ** 2) + 1e-12)
    if rms_signal == 0:
        return x
 
    target_rms_hum = rms_signal * db_to_linear(level_db_rel)
    if target_rms_hum <= 0:
        return x
 
    t = np.arange(len(x), dtype=np.float64) / float(sample_rate)
    hum = np.zeros(len(x), dtype=np.float64)
 
    for k in range(1, harmonics + 1):
        freq = base_freq_hz * k
        hum += (1.0 / k) * np.sin(2.0 * math.pi * freq * t)
 
    rms_hum = np.sqrt(np.mean(hum ** 2) + 1e-12)
    hum *= (target_rms_hum / rms_hum)
 
    return x + hum
 
 
def apply_soft_clip_distortion(
    x: np.ndarray, drive_db: float, mix: float
) -> np.ndarray:
    if drive_db <= 0.0 or mix <= 0.0:
        return x
 
    mix = float(np.clip(mix, 0.0, 1.0))
    drive = db_to_linear(drive_db)
 
    driven = x * drive
    y = np.tanh(driven)
    max_abs = np.max(np.abs(y)) + 1e-12
    y = y / max_abs
 
    return (1.0 - mix) * x + mix * y
 
 
def normalize_peak(x: np.ndarray, target_peak_db: float) -> np.ndarray:
    current_peak = np.max(np.abs(x)) + 1e-12
    if current_peak == 0:
        return x
 
    target_peak_lin = db_to_linear(target_peak_db)
    return x * (target_peak_lin / current_peak)
 
 
# =====================================================================
# MAIN PROCESSING PIPELINE
# =====================================================================
 
def process_file(
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    target_sample_rate: int,
    tv_sound: dict,
    noise: dict,
    distortion: dict,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_input_wav = temp_dir_path / "input_temp.wav"
        temp_output_wav = temp_dir_path / "output_temp.wav"
 
        print(f"Decoding: {input_path}")
        decode_audio_to_wav(ffmpeg_path, input_path, temp_input_wav, target_sample_rate)
 
        print("Reading audio data...")
        x, sr = read_wav_to_numpy(temp_input_wav)
 
        print("Applying TV EQ...")
        x = apply_tv_eq(
            x,
            sample_rate=sr,
            band_low_hz=tv_sound["band_low_hz"],
            band_high_hz=tv_sound["band_high_hz"],
            low_mid_split_hz=tv_sound["low_mid_split_hz"],
            mid_high_split_hz=tv_sound["mid_high_split_hz"],
            low_gain_db=tv_sound["low_gain_db"],
            mid_gain_db=tv_sound["mid_gain_db"],
            high_gain_db=tv_sound["high_gain_db"],
        )
 
        print("Applying distortion...")
        x = apply_soft_clip_distortion(
            x,
            drive_db=distortion["drive_db"],
            mix=distortion["mix"],
        )
 
        print("Adding hiss...")
        x = add_hiss(x, level_db_rel=noise["hiss_level_db_rel"])
 
        print("Adding hum...")
        x = add_hum(
            x,
            sample_rate=sr,
            level_db_rel=noise["hum_level_db_rel"],
            base_freq_hz=noise["hum_frequency_hz"],
            harmonics=noise["hum_harmonics"],
        )
 
        print("Normalizing...")
        x = normalize_peak(x, tv_sound["output_gain_db"])
 
        print("Writing processed audio...")
        write_numpy_to_wav(x, sr, temp_output_wav)
 
        print(f"Encoding: {output_path}")
        encode_wav_to_output(ffmpeg_path, temp_output_wav, output_path)
 
 
def main() -> None:
    plat_info, ffmpeg_path = print_system_info()
 
    if not ffmpeg_path:
        print_ffmpeg_install_guide(plat_info)
        print("ERROR: ffmpeg is required but was not found.")
        sys.exit(1)
 
    script_dir = get_script_directory()
 
    input_path = script_dir / INPUT_FILENAME
    output_path = script_dir / OUTPUT_FILENAME
 
    if not input_path.exists():
        print(f"\nERROR: Input file not found: {input_path}")
        print(f"Place your audio file in: {script_dir}")
        sys.exit(1)
 
    print()
    process_file(
        ffmpeg_path,
        input_path,
        output_path,
        TARGET_SAMPLE_RATE,
        TV_SOUND,
        NOISE,
        DISTORTION,
    )
 
    print("\nDone!")
 
 
if __name__ == "__main__":
    main()
