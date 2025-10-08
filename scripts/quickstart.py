"""
Quick Start Script for Dremio Connector
This script helps you get started quickly with the Dremio connector.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def run_command(command, description):
    """Run a command and display results."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Main quick start workflow."""
    print_header("Dremio Connector - Quick Start Setup")
    
    project_root = Path(__file__).parent
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return 1
    
    # Step 1: Create virtual environment
    print_header("Step 1: Create Virtual Environment")
    venv_path = project_root / "venv_dremio"
    
    if venv_path.exists():
        print(f"Virtual environment already exists at: {venv_path}")
        response = input("Recreate it? (y/n): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree(venv_path)
            run_command("python -m venv venv_dremio", "Creating virtual environment")
    else:
        run_command("python -m venv venv_dremio", "Creating virtual environment")
    
    # Step 2: Install dependencies
    print_header("Step 2: Install Dependencies")
    
    # Determine pip command based on OS
    if sys.platform == "win32":
        pip_cmd = str(venv_path / "Scripts" / "pip.exe")
        python_cmd = str(venv_path / "Scripts" / "python.exe")
    else:
        pip_cmd = str(venv_path / "bin" / "pip")
        python_cmd = str(venv_path / "bin" / "python")
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Installing dependencies"
    )
    
    # Install package in development mode
    run_command(
        f"{pip_cmd} install -e .",
        "Installing package in development mode"
    )
    
    # Step 3: Configuration
    print_header("Step 3: Configuration Setup")
    
    config_file = project_root / "config" / "ingestion.yaml"
    if config_file.exists():
        print(f"✅ Configuration file found: {config_file}")
        print("\nPlease edit the configuration file with your settings:")
        print("  - Dremio connection details (host, port, credentials)")
        print("  - OpenMetadata server URL and JWT token")
    else:
        print(f"❌ Configuration file not found: {config_file}")
        print("Please create it from the template.")
    
    # Step 4: Test connection
    print_header("Step 4: Test Connection (Optional)")
    
    response = input("\nDo you want to test the connection now? (y/n): ")
    if response.lower() == 'y':
        print("\nMake sure you have edited the configuration file first!")
        input("Press Enter when ready...")
        
        test_cmd = f"{python_cmd} -m dremio_connector.cli --config config/ingestion.yaml --test-connection"
        run_command(test_cmd, "Testing connection")
    
    # Summary
    print_header("Setup Complete!")
    
    print("\n📝 Next Steps:")
    print("1. Edit configuration file: config/ingestion.yaml")
    print("2. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv_dremio\\Scripts\\activate")
    else:
        print("   source venv_dremio/bin/activate")
    print("3. Test connection:")
    print("   dremio-connector --config config/ingestion.yaml --test-connection")
    print("4. Run ingestion:")
    print("   dremio-connector --config config/ingestion.yaml")
    
    print("\n📚 Documentation:")
    print("   - Project Structure: docs/PROJECT_STRUCTURE.md")
    print("   - Examples: examples/basic_ingestion.py")
    print("   - README: README.md")
    
    print("\n✅ Setup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
