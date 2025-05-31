#!/usr/bin/env python3

# s2m watchdog with virtual environment management

import subprocess
from subprocess import call, check_call, PIPE, STDOUT
from time import sleep
import logging, os, sys
import venv

def setup_logging():
    """Setup basic logging for the watchdog"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def get_venv_path():
    """Get the path to the virtual environment directory"""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "venv")

def get_python_executable():
    """Get the Python executable path for the virtual environment"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        return os.path.join(venv_path, "bin", "python")

def get_pip_executable():
    """Get the pip executable path for the virtual environment"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "pip")
    else:  # Unix/Linux/macOS
        return os.path.join(venv_path, "bin", "pip")

def create_venv():
    """Create a virtual environment"""
    venv_path = get_venv_path()
    logging.info(f"Creating virtual environment at: {venv_path}")
    
    try:
        # Create the virtual environment
        venv.create(venv_path, with_pip=True)
        logging.info("Virtual environment created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install dependencies in the virtual environment"""
    deps_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "deps.txt")
    pip_executable = get_pip_executable()
    
    if not os.path.exists(deps_file):
        logging.error(f"Dependencies file not found: {deps_file}")
        return False
    
    logging.info(f"Installing dependencies from: {deps_file}")
    
    try:
        # Upgrade pip first
        result = subprocess.run([pip_executable, "install", "--upgrade", "pip"], 
                              capture_output=True, text=True, check=True)
        logging.info("pip upgraded successfully")
        
        # Install dependencies
        result = subprocess.run([pip_executable, "install", "-r", deps_file], 
                              capture_output=True, text=True, check=True)
        logging.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        if e.stdout:
            logging.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logging.error(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during dependency installation: {e}")
        return False

def setup_venv():
    """Setup virtual environment and install dependencies"""
    venv_path = get_venv_path()
    python_executable = get_python_executable()
    
    # Check if virtual environment already exists and is valid
    if os.path.exists(venv_path) and os.path.exists(python_executable):
        logging.info("Virtual environment already exists")
        
        # Verify it's working by trying to run python
        try:
            result = subprocess.run([python_executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            logging.info(f"Using existing virtual environment: {result.stdout.strip()}")
            return True
        except Exception as e:
            logging.warning(f"Existing virtual environment appears broken: {e}")
            logging.info("Recreating virtual environment...")
            
            # Remove broken venv
            import shutil
            try:
                shutil.rmtree(venv_path)
            except Exception as cleanup_error:
                logging.error(f"Failed to remove broken venv: {cleanup_error}")
                return False
    
    # Create new virtual environment
    if not create_venv():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    logging.info("Virtual environment setup completed successfully")
    return True

def get_hostname():
    """Get hostname for logging purposes"""
    try:
        # Import the function from the libs module if available
        from libs.system_info import get_hostname
        return get_hostname()
    except ImportError:
        # Fallback to socket.gethostname if libs not available
        import socket
        return socket.gethostname()

def start_system2mqtt(envfile):
    """Start the main s2m.py script in the virtual environment"""
    python_executable = get_python_executable()
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "s2m.py")
    
    try:
        hostname = get_hostname()
        logging.info(f"Starting '{hostname}' script: '{script_path}' with config: '{envfile}'")
        
        # Run the script in the virtual environment
        if envfile:
            result = subprocess.call([python_executable, script_path, envfile])
        else:
            result = subprocess.call([python_executable, script_path])
            
        logging.info(f"Watchdog PID: {os.getpid()}")
        
        # If script exits normally, don't restart
        if result == 0:
            logging.info("Script exited normally")
            return
        else:
            logging.warning(f"Script exited with code: {result}")
            
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
        return
    except Exception as e:
        logging.error(f"Error running script: {e}")
    
    # Script crashed or exited abnormally, restart it
    logging.error(f"Script crashed! Restarting in {restart_timer} seconds")
    handle_crash(envfile)

def handle_crash(envfile):
    """Handle script crashes by restarting after a delay"""
    sleep(restart_timer)
    start_system2mqtt(envfile)

# Global variables
restart_timer = 2

if __name__ == '__main__':
    # Setup logging first
    setup_logging()
    
    # Setup virtual environment and dependencies
    if not setup_venv():
        logging.error("Failed to setup virtual environment. Exiting.")
        sys.exit(1)
    
    # Determine config file
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "s2m.conf")
    
    # Validate config file exists
    if not os.path.exists(config_file):
        logging.error(f"Configuration file not found: {config_file}")
        sys.exit(1)
    
    logging.info(f"Using configuration file: {config_file}")
    
    # Start the main application
    start_system2mqtt(config_file)