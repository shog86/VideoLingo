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

def check_nvidia_gpu():
    install_package("pynvml")
    import pynvml
    from translations.translations import translate as t
    initialized = False
    try:
        pynvml.nvmlInit()
        initialized = True
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 0:
            print(t("Detected NVIDIA GPU(s)"))
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                print(f"GPU {i}: {name}")
            return True
        else:
            print(t("No NVIDIA GPU detected"))
            return False
    except pynvml.NVMLError:
        print(t("No NVIDIA GPU detected or NVIDIA drivers not properly installed"))
        return False
    finally:
        if initialized:
            pynvml.nvmlShutdown()

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
        system = platform.system()
        install_cmd = ""
        
        if system == "Windows":
            install_cmd = "choco install ffmpeg"
            extra_note = t("Install Chocolatey first (https://chocolatey.org/)")
        elif system == "Darwin":
            install_cmd = "brew install ffmpeg"
            extra_note = t("Install Homebrew first (https://brew.sh/)")
        elif system == "Linux":
            install_cmd = "sudo apt install ffmpeg  # Ubuntu/Debian\nsudo yum install ffmpeg  # CentOS/RHEL"
            extra_note = t("Use your distribution's package manager")
        
        console.print(Panel.fit(
            t("❌ FFmpeg not found\n\n") +
            f"{t('🛠️ Install using:')}\n[bold cyan]{install_cmd}[/bold cyan]\n\n" +
            f"{t('💡 Note:')}\n{extra_note}\n\n" +
            f"{t('🔄 After installing FFmpeg, please run this installer again:')}\n[bold cyan]python install.py[/bold cyan]",
            style="red"
        ))
        raise SystemExit(t("FFmpeg is required. Please install it and run the installer again."))

def check_environment():
    """Check if running in correct Python and conda environment"""
    import sys

    # Check Python version
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor != 10:
        print(f"❌ Error: Python 3.10 is required, but you are using Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        print("\n📝 Please follow these steps:")
        print("1. Create conda environment: conda create -n videolingo python=3.10.0 -y")
        print("2. Activate environment: conda activate videolingo")
        print("3. Run installer again: python install.py")
        sys.exit(1)

    # Check if in conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix:
        print("⚠️  Warning: Not running in a conda environment")
        print("\n📝 Recommended steps:")
        print("1. Install Miniconda or Anaconda")
        print("2. Create environment: conda create -n videolingo python=3.10.0 -y")
        print("3. Activate environment: conda activate videolingo")
        print("4. Run installer again: python install.py")

        # Ask user if they want to continue anyway
        response = input("\nDo you want to continue anyway? (not recommended) [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        # Check if in videolingo environment
        env_name = os.path.basename(conda_prefix)
        if env_name != 'videolingo':
            print(f"⚠️  Warning: You are in conda environment '{env_name}', not 'videolingo'")
            print("\n📝 Recommended steps:")
            print("1. Create videolingo environment: conda create -n videolingo python=3.10.0 -y")
            print("2. Activate environment: conda activate videolingo")
            print("3. Run installer again: python install.py")

            response = input("\nDo you want to continue anyway? (not recommended) [y/N]: ")
            if response.lower() != 'y':
                sys.exit(1)

def main():
    # Check environment before proceeding
    check_environment()

    install_package("requests", "rich", "ruamel.yaml", "InquirerPy")
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
    has_gpu = platform.system() != 'Darwin' and check_nvidia_gpu()
    if has_gpu:
        console.print(Panel(t("🎮 NVIDIA GPU detected, installing CUDA version of PyTorch..."), style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.0.0", "torchaudio==2.0.0", "--index-url", "https://download.pytorch.org/whl/cu118"])
    else:
        system_name = "🍎 MacOS" if platform.system() == 'Darwin' else "💻 No NVIDIA GPU"
        console.print(Panel(t(f"{system_name} detected, installing CPU version of PyTorch... Note: it might be slow during whisperX transcription."), style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.1.2", "torchaudio==2.1.2"])

    # macOS-specific: Install av and moviepy via conda to avoid FFmpeg compatibility issues
    if platform.system() == 'Darwin':
        console.print(Panel(t("🍎 Installing pkg-config, av, and moviepy via conda (required for macOS)..."), style="cyan"))
        try:
            # Check if running in conda environment
            conda_prefix = os.environ.get('CONDA_PREFIX')
            if conda_prefix:
                # Check if av and moviepy are already installed with correct version
                av_installed = False
                moviepy_installed = False
                av_needs_reinstall = False

                try:
                    import av
                    # Check if av version is 11.x (required by faster-whisper 1.0.0)
                    if av.__version__.startswith('11.'):
                        av_installed = True
                        console.print(Panel(t(f"✅ av {av.__version__} already installed"), style="green"))
                    else:
                        av_needs_reinstall = True
                        console.print(Panel(t(f"⚠️ av {av.__version__} is incompatible, need to reinstall av 11.0.0"), style="yellow"))
                        # Remove the incompatible version first
                        console.print(Panel(t(f"🗑️ Removing av {av.__version__}..."), style="yellow"))
                        subprocess.check_call(["conda", "remove", "av", "-y"])
                except ImportError:
                    pass

                try:
                    import moviepy
                    moviepy_installed = True
                    console.print(Panel(t(f"✅ moviepy already installed"), style="green"))
                except ImportError:
                    pass

                # Install or reinstall packages via conda
                packages_to_install = []
                if not av_installed or av_needs_reinstall:
                    # Force reinstall with specific versions to ensure compatibility
                    packages_to_install.extend(["pkg-config", "av=11.0.0", "ffmpeg>=6.0.0,<7.0"])
                if not moviepy_installed:
                    packages_to_install.append("moviepy")

                if packages_to_install:
                    console.print(Panel(t(f"📦 Installing via conda: {', '.join(packages_to_install)}"), style="cyan"))
                    # Use --force-reinstall to ensure clean installation
                    subprocess.check_call(["conda", "install", "-c", "conda-forge", "--force-reinstall"] + packages_to_install + ["-y"])
                    console.print(Panel(t("✅ Successfully installed packages via conda"), style="green"))

                    # Verify installation
                    try:
                        import importlib
                        if 'av' in sys.modules:
                            importlib.reload(sys.modules['av'])
                        import av
                        console.print(Panel(t(f"✅ Verified: av {av.__version__} is now installed"), style="green"))
                    except Exception as e:
                        console.print(Panel(t(f"⚠️ Warning: Could not verify av installation: {e}"), style="yellow"))
                else:
                    console.print(Panel(t("✅ All required packages already installed"), style="green"))
            else:
                console.print(Panel(t("⚠️ Warning: Not running in conda environment. PyAV may fail to install."), style="yellow"))
        except Exception as e:
            console.print(Panel(t(f"⚠️ Warning: Failed to install via conda: {e}"), style="yellow"))

    @except_handler("Failed to install project")
    def install_requirements():
        console.print(Panel(t("Installing project in editable mode using `pip install -e .`"), style="cyan"))

        # Prepare environment variables
        env = {**os.environ, "PIP_NO_CACHE_DIR": "0", "PYTHONIOENCODING": "utf-8"}

        # On macOS with conda, tell pip to skip av if already installed
        constraint_file = None
        if platform.system() == 'Darwin':
            try:
                import av
                # Verify av version is 11.x (required by faster-whisper 1.0.0)
                if not av.__version__.startswith('11.'):
                    console.print(Panel(t(f"⚠️ Warning: av {av.__version__} may be incompatible with faster-whisper"), style="yellow"))

                # Create a constraint file to prevent pip from reinstalling av
                constraint_file = os.path.join(os.path.dirname(__file__), '.pip-constraints.txt')
                with open(constraint_file, 'w') as f:
                    # Use av 11.* wildcard to satisfy faster-whisper's av==11.* requirement
                    f.write(f"av=={av.__version__}\n")
                # Use both PIP_CONSTRAINT and PIP_BUILD_CONSTRAINT for compatibility
                env['PIP_CONSTRAINT'] = constraint_file
                env['PIP_BUILD_CONSTRAINT'] = constraint_file
                console.print(Panel(t(f"🔧 Configured pip to use existing av {av.__version__} from conda"), style="cyan"))
            except ImportError:
                pass

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], env=env)
        finally:
            # Clean up constraint file
            if constraint_file and os.path.exists(constraint_file):
                os.remove(constraint_file)

    @except_handler("Failed to install Noto fonts")
    def install_noto_font():
        # Detect Linux distribution type
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu systems
            cmd = ['sudo', 'apt-get', 'install', '-y', 'fonts-noto']
            pkg_manager = "apt-get"
        elif os.path.exists('/etc/redhat-release'):
            # RHEL/CentOS/Fedora systems
            cmd = ['sudo', 'yum', 'install', '-y', 'google-noto*']
            pkg_manager = "yum"
        else:
            console.print("Warning: Unrecognized Linux distribution, please install Noto fonts manually", style="yellow")
            return

        subprocess.run(cmd, check=True)
        console.print(f"✅ Successfully installed Noto fonts using {pkg_manager}", style="green")

    if platform.system() == 'Linux':
        install_noto_font()
    
    install_requirements()
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
        "2. " + t("Re-run the installer: [bold]python install.py[/bold]")
    )
    console.print(Panel(panel2_text, style="yellow"))

    # start the application
    subprocess.Popen(["streamlit", "run", "st.py"])

if __name__ == "__main__":
    main()
