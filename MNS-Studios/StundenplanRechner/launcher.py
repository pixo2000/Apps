#!/usr/bin/env python3
"""
Launcher script for Lanis Stundenplan Rechner
Provides multiple ways to start the application
"""

import os
import sys
import argparse

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'), 
        ('selenium', 'selenium'),
        ('webdriver-manager', 'webdriver_manager'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_env_file():
    """Check if .env file exists and is configured"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("Creating a template .env file...")
        
        with open('.env', 'w') as f:
            f.write("""# Lanis Schulportal Credentials
LANIS_USERNAME=
LANIS_PASSWORD=
LANIS_SCHOOL_ID=""")
        
        print("✅ Template .env file created")
        print("Please edit .env and add your credentials")
        return False
    
    # Check if credentials are filled
    with open('.env', 'r') as f:
        content = f.read()
        
    if 'LANIS_USERNAME=' in content and not 'LANIS_USERNAME=\n' in content:
        print("✅ .env file configured")
        return True
    else:
        print("⚠️  .env file exists but credentials are not filled")
        print("Please edit .env and add your credentials")
        return False

def launch_gui():
    """Launch the GUI application"""
    try:
        from main import StundenplanGUI
        print("🚀 Starting GUI application...")
        app = StundenplanGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return False

def launch_cli():
    """Launch command-line interface"""
    print("📝 Command-line interface not yet implemented")
    print("Use the GUI version with: python launcher.py --gui")

def run_tests():
    """Run application tests"""
    try:
        from test_basic import main as test_main
        test_main()
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def show_example():
    """Show usage example"""
    try:
        from example_usage import example_usage
        example_usage()
    except Exception as e:
        print(f"❌ Error running example: {e}")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Lanis Stundenplan Rechner Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                    # Launch GUI (default)
  python launcher.py --gui              # Launch GUI explicitly
  python launcher.py --test             # Run tests
  python launcher.py --example          # Show usage example
  python launcher.py --check            # Check setup only
        """
    )
    
    parser.add_argument('--gui', action='store_true', 
                       help='Launch GUI application (default)')
    parser.add_argument('--cli', action='store_true',
                       help='Launch command-line interface')
    parser.add_argument('--test', action='store_true',
                       help='Run application tests')
    parser.add_argument('--example', action='store_true',
                       help='Show usage example')
    parser.add_argument('--check', action='store_true',
                       help='Check setup and dependencies only')
    
    args = parser.parse_args()
    
    print("Lanis Stundenplan Rechner Launcher")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Check environment setup
    env_ok = check_env_file()
    
    if args.check:
        print("\n📋 Setup Check Complete")
        return 0 if env_ok else 1
    
    if args.test:
        print("\n🧪 Running Tests...")
        run_tests()
        return 0
    
    if args.example:
        print("\n📖 Running Example...")
        show_example()
        return 0
    
    if args.cli:
        print("\n💻 Starting CLI...")
        launch_cli()
        return 0
    
    # Default: launch GUI
    if not env_ok:
        print("\n⚠️  Warning: Credentials not configured")
        print("You can still use the application and enter credentials in the GUI")
        
        response = input("\nContinue anyway? (y/N): ").lower()
        if response != 'y':
            return 1
    
    print("\n🖥️  Starting GUI...")
    launch_gui()
    return 0

if __name__ == "__main__":
    sys.exit(main())
