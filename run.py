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
        logging.info("Upgrading pip...")
        result = subprocess.run([pip_executable, "install", "--upgrade", "pip"], 
                              capture_output=True, text=True, check=True)
        logging.info("pip upgraded successfully")
        
        # Install dependencies with verbose output
        logging.info("Installing dependencies...")
        result = subprocess.run([pip_executable, "install", "-r", deps_file, "-v"], 
                              capture_output=True, text=True, check=True)
        logging.info("Dependencies installed successfully")
        
        # Verify installation by checking each package
        if verify_dependencies():
            logging.info("All dependencies verified successfully")
            return True
        else:
            logging.error("Dependency verification failed")
            return False
            
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

def verify_dependencies():
    """Verify that all dependencies are properly installed"""
    deps_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "deps.txt")
    python_executable = get_python_executable()
    
    try:
        # Read the dependencies file
        with open(deps_file, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Test each dependency
        for dep in deps:
            # Extract package name (handle cases like "package>=1.0.0")
            package_name = dep.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
            
            logging.info(f"Verifying {package_name}...")
            try:
                result = subprocess.run([python_executable, "-c", f"import {package_name}"], 
                                      capture_output=True, text=True, check=True)
                logging.info(f"✓ {package_name} verified")
            except subprocess.CalledProcessError:
                # Some packages have different import names, try common alternatives
                alt_names = {
                    'python-dotenv': 'dotenv',
                    'paho-mqtt': 'paho.mqtt'
                }
                if package_name in alt_names:
                    try:
                        result = subprocess.run([python_executable, "-c", f"import {alt_names[package_name]}"], 
                                              capture_output=True, text=True, check=True)
                        logging.info(f"✓ {package_name} verified (as {alt_names[package_name]})")
                        continue
                    except:
                        pass
                
                logging.error(f"✗ Failed to verify {package_name}")
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error verifying dependencies: {e}")
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
            logging.info(f"Found virtual environment: {result.stdout.strip()}")
            
            # Check if dependencies are installed
            if verify_dependencies():
                logging.info("All dependencies verified, using existing virtual environment")
                return True
            else:
                logging.warning("Dependencies missing or broken, reinstalling...")
                if not install_dependencies():
                    logging.error("Failed to install dependencies in existing venv")
                    # Try recreating the entire venv
                    logging.info("Recreating virtual environment...")
                    import shutil
                    try:
                        shutil.rmtree(venv_path)
                    except Exception as cleanup_error:
                        logging.error(f"Failed to remove broken venv: {cleanup_error}")
                        return False
                else:
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
    
    # Check for force reinstall flag
    force_reinstall = False
    args = sys.argv[1:]
    if '--force-reinstall' in args:
        force_reinstall = True
        args.remove('--force-reinstall')
        logging.info("Force reinstall requested - will recreate virtual environment")
        
        # Remove existing venv
        venv_path = get_venv_path()
        if os.path.exists(venv_path):
            import shutil
            try:
                shutil.rmtree(venv_path)
                logging.info("Removed existing virtual environment")
            except Exception as e:
                logging.error(f"Failed to remove existing venv: {e}")
                sys.exit(1)
    
    # Setup virtual environment and dependencies
    if not setup_venv():
        logging.error("Failed to setup virtual environment. Exiting.")
        logging.error("You can try running with --force-reinstall to recreate the virtual environment")
        sys.exit(1)
    
    # Determine config file
    if len(args) > 0:
        config_file = args[0]
    else:
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "s2m.conf")
    
    # Validate config file exists
    if not os.path.exists(config_file):
        logging.error(f"Configuration file not found: {config_file}")
        sys.exit(1)
    
    logging.info(f"Using configuration file: {config_file}")
    
    # Start the main application
    start_system2mqtt(config_file)