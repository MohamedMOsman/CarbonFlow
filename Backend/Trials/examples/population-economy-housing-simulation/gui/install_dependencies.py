#!/usr/bin/env python3
"""
Installation script for GUI dependencies.

This script helps install the required dependencies for the spreadsheet-style editor,
multidimensional editor, and other GUI components.
"""

import subprocess
import sys
import importlib.util

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        return False

def main():
    """Main installation function."""
    
    print("=" * 60)
    print("GUI DEPENDENCIES INSTALLATION")
    print("=" * 60)
    
    # Required packages
    required_packages = [
        ("PyQt6", "PyQt6"),
        ("PyYAML", "yaml"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib")
    ]
    
    # Optional packages
    optional_packages = [
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        ("seaborn", "seaborn"),
        ("plotly", "plotly")
    ]
    
    print("Checking required packages...")
    missing_required = []
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            print(f"  ✓ {package_name} is installed")
        else:
            print(f"  ✗ {package_name} is missing")
            missing_required.append(package_name)
    
    print("\nChecking optional packages...")
    missing_optional = []
    
    for package_name, import_name in optional_packages:
        if check_package(package_name, import_name):
            print(f"  ✓ {package_name} is installed")
        else:
            print(f"  - {package_name} is missing (optional)")
            missing_optional.append(package_name)
    
    # Install missing required packages
    if missing_required:
        print(f"\nInstalling {len(missing_required)} required packages...")
        
        for package in missing_required:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"  ✓ {package} installed successfully")
            else:
                print(f"  ✗ Failed to install {package}")
                
    else:
        print("\n✓ All required packages are already installed!")
    
    # Ask about optional packages
    if missing_optional:
        print(f"\nOptional packages missing: {', '.join(missing_optional)}")
        response = input("Install optional packages? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            print("Installing optional packages...")
            for package in missing_optional:
                print(f"Installing {package}...")
                if install_package(package):
                    print(f"  ✓ {package} installed successfully")
                else:
                    print(f"  ✗ Failed to install {package}")
    
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE")
    print("=" * 60)
    
    # Final check
    print("\nFinal verification...")
    all_good = True
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            print(f"  ✓ {package_name}")
        else:
            print(f"  ✗ {package_name} - still missing!")
            all_good = False
    
    if all_good:
        print("\n🎉 All required dependencies are installed!")
        print("\nYou can now:")
        print("1. Run the GUI: python main.py")
        print("2. Test the spreadsheet editor: python test_spreadsheet_editor.py")
        print("3. Try the demo notebook: jupyter notebook Spreadsheet_Editor_Demo.ipynb")
        print("4. Double-click components in the GUI to open the spreadsheet editor")
    else:
        print("\n⚠️  Some required dependencies are still missing.")
        print("You may need to install them manually:")
        print("pip install PyQt6 PyYAML numpy matplotlib")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
