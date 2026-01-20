import os, sys
import platform
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ascii_logo = r"""
__     ___     _            _     _
\ \   / (_) __| | ___  ___ | |   (_)_ __   __ _  ___
 \ \ / /| |/ _` |/ _ \/ _ \| |   | | '_ \ / _` |/ _ \
  \ V / | | (_| |  __/ (_) | |___| | | | | (_| | (_) |
   \_/  |_|\__,_|\___|\___/|_____|_|_| |_|\__, |\___/
                                          |___/
"""

def install_package(*packages):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

# Removed check_nvidia_gpu for Mac-only version

def check_ffmpeg():
    from rich.console import Console
    from rich.panel import Panel
    from translations.translations import translate as t
    console = Console()

    try:
        # Check if ffmpeg is installed
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        console.print(Panel(t("✅ FFmpeg is already installed"), style="green"))
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        install_cmd = "brew install ffmpeg"
        extra_note = t("Install Homebrew first (https://brew.sh/)")
        
        console.print(Panel.fit(
            t("❌ FFmpeg not found\n\n") +
            f"{t('🛠️ Install using:')}\n[bold cyan]{install_cmd}[/bold cyan]\n\n" +
            f"{t('💡 Note:')}\n{extra_note}\n\n" +
            f"{t('🔄 After installing FFmpeg, please run this installer again:')}\n[bold cyan]bash run_installer.sh[/bold cyan]",
            style="red"
        ))
        raise SystemExit(t("FFmpeg is required. Please install it and run the installer again."))

def check_environment():
    """Check if running in correct Python and conda environment"""
    import sys

    # Check Python version
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 10:
        from translations.translations import translate as t
        print(f"❌ {t('Error: Python >= 3.10 is required, but you are using Python')} {python_version.major}.{python_version.minor}.{python_version.micro}")
        print(f"\n📝 {t('Please run [bold cyan]bash run_installer.sh[/bold cyan] to setup the correct environment.')}")
        sys.exit(1)

    # Check if in conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix or os.path.basename(conda_prefix) != 'videolingo':
        from translations.translations import translate as t
        print(f"⚠️  {t('Warning: Not running in videolingo conda environment')}")
        print(f"\n📝 {t('Please run [bold cyan]bash run_installer.sh[/bold cyan] to activate the environment.')}")
        sys.exit(1)

def main():
    # Check environment before proceeding
    check_environment()

    install_package("requests", "rich", "ruamel.yaml", "InquirerPy", "python-dotenv")
    from rich.console import Console
    from rich.panel import Panel
    from rich.box import DOUBLE
    from InquirerPy import inquirer
    from translations.translations import translate as t
    from translations.translations import DISPLAY_LANGUAGES
    from core.utils.config_utils import load_key, update_key
    from core.utils.decorator import except_handler

    console = Console()
    
    width = max(len(line) for line in ascii_logo.splitlines()) + 4
    welcome_panel = Panel(
        ascii_logo,
        width=width,
        box=DOUBLE,
        title="[bold green]🌏[/bold green]",
        border_style="bright_blue"
    )
    console.print(welcome_panel)
    # Language selection
    current_language = load_key("display_language")
    # Find the display name for current language code
    current_display = next((k for k, v in DISPLAY_LANGUAGES.items() if v == current_language), "🇬🇧 English")
    selected_language = DISPLAY_LANGUAGES[inquirer.select(
        message="Select language / 选择语言 / 選擇語言 / 言語を選択 / Seleccionar idioma / Sélectionner la langue / Выберите язык:",
        choices=list(DISPLAY_LANGUAGES.keys()),
        default=current_display
    ).execute()]
    update_key("display_language", selected_language)

    console.print(Panel.fit(t("🚀 Starting Installation"), style="bold magenta"))

    # Configure mirrors
    # add a check to ask user if they want to configure mirrors
    if inquirer.confirm(
        message=t("Do you need to auto-configure PyPI mirrors? (Recommended if you have difficulty accessing pypi.org)"),
        default=True
    ).execute():
        from core.utils.pypi_autochoose import main as choose_mirror
        choose_mirror()

    # Detect system and GPU
    # MacOS optimized installation
    console.print(Panel(t("🍎 Installing MacOS optimized dependencies..."), style="cyan"))
    try:
        subprocess.check_call(["conda", "install", "-c", "conda-forge", "pkg-config", "ffmpeg>=6.0.0", "-y"])
        console.print(Panel(t("✅ Successfully installed base packages via conda"), style="green"))
        console.print(Panel(t("🍎 Installing PyTorch for MacOS..."), style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchaudio"])
    except Exception as e:
        console.print(Panel(t("⚠️ Warning: Failed to install via conda or pip: {e}").format(e=e), style="yellow"))

    @except_handler("Failed to install project")
    def install_requirements():
        console.print(Panel(t("Installing project requirements..."), style="cyan"))
        env = {**os.environ, "PIP_NO_CACHE_DIR": "0", "PYTHONIOENCODING": "utf-8"}
        
        # 1. Install project in editable mode
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], env=env)
        
        # 2. Re-install demucs from git with --no-deps to fix missing demucs.api and avoid version conflicts
        console.print(Panel(t("Fixing Demucs API..."), style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "git+https://github.com/adefossez/demucs"], env=env)
        
        # 3. Update spacy models to match installed spacy version
        console.print(Panel(t("Updating Spacy models..."), style="cyan"))
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"], env=env)
        
        # 4. Ensure torchaudio consistency (last step)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torchaudio", "--no-deps"], env=env)

    
    install_requirements()
    
    def pre_download_models():
        """Optional step to pre-download models if HF token is provided"""
        from rich.console import Console
        from rich.panel import Panel
        from translations.translations import translate as t
        from core.utils.config_utils import load_key
        console = Console()
        
        token = load_key("api.huggingface_token")
        if not token or token == 'YOUR_HF_TOKEN' or len(token) < 10:
            console.print(Panel(t("💡 Tip: Set your Hugging Face token in config.yaml to pre-download AI models during installation."), style="yellow"))
            return

        console.print(Panel(t("📥 Pre-downloading AI Models..."), style="cyan"))
        
        import subprocess
        import sys
        
        download_script = """
import os, sys
import numpy as np
import mlx_whisper
import torch
from pyannote.audio import Pipeline
from core.utils.config_utils import load_key

# Set HF_HOME to match backend
MODEL_DIR = os.path.join(os.getcwd(), load_key("model_dir"))
os.environ["HF_HOME"] = MODEL_DIR

whisper_model = load_key("whisper.model")
token = load_key("api.huggingface_token")

print(f"Checking MLX-Whisper model: {whisper_model}")
try:
    # Trigger download with a tiny silent segment
    mlx_whisper.transcribe(np.zeros(16000), path_or_hf_repo=whisper_model)
    print("✅ MLX-Whisper model ready.")
except Exception as e:
    print(f"⚠️ MLX-Whisper download note: {e}")

print("Checking Pyannote models...")
try:
    Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    Pipeline.from_pretrained("pyannote/segmentation-3.0", use_auth_token=token)
    print("✅ Pyannote models ready.")
except Exception as e:
    print(f"⚠️ Pyannote download failed: {e}")
    print("Make sure you have accepted the terms on Hugging Face (see README).")
"""
        try:
            tmp_file = "_tmp_download.py"
            with open(tmp_file, "w") as f:
                f.write(download_script)
            subprocess.run([sys.executable, tmp_file], check=False)
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception as e:
            console.print(t("⚠️ Note: Manual model download failed: {e}").format(e=e), style="yellow")

    pre_download_models()
    check_ffmpeg()
    
    # First panel with installation complete and startup command
    panel1_text = (
        t("Installation completed") + "\n\n" +
        t("Now I will run this command to start the application:") + "\n" +
        "[bold]streamlit run st.py[/bold]\n" +
        t("Note: First startup may take up to 1 minute")
    )
    console.print(Panel(panel1_text, style="bold green"))

    # Second panel with troubleshooting tips
    panel2_text = (
        t("If the application fails to start:") + "\n" +
        "1. " + t("Check your network connection") + "\n" +
        "2. " + t("Re-run the installer: [bold]bash run_installer.sh[/bold]")
    )
    console.print(Panel(panel2_text, style="yellow"))

    # start the application
    subprocess.Popen(["streamlit", "run", "st.py"])

if __name__ == "__main__":
    main()
