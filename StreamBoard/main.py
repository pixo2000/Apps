import platform
import sys

def list_keyboards():
    """List all connected keyboards based on the current operating system"""
    system = platform.system()
    
    if system == 'Windows':
        return list_windows_keyboards()
    elif system == 'Linux':
        return list_linux_keyboards()
    elif system == 'Darwin':  # macOS
        return list_mac_keyboards()
    else:
        return [f"Unsupported operating system: {system}"]

def list_windows_keyboards():
    """List keyboards on Windows using WMI"""
    try:
        import wmi
    except ImportError:
        return ["Error: wmi module not found. Install with 'pip install wmi'"]
    
    keyboards = []
    try:
        c = wmi.WMI()
        for item in c.Win32_Keyboard():
            description = item.Description or "Unknown keyboard"
            device_id = item.DeviceID or "Unknown ID"
            keyboards.append(f"Keyboard: {description} (ID: {device_id})")
        
        if not keyboards:
            keyboards.append("No keyboards detected.")
    except Exception as e:
        keyboards.append(f"Error detecting keyboards: {e}")
    
    return keyboards

def list_linux_keyboards():
    """List keyboards on Linux by checking input devices"""
    keyboards = []
    try:
        import re
        import subprocess
        
        # Try using xinput if available
        try:
            result = subprocess.check_output(['xinput', 'list'], universal_newlines=True)
            pattern = re.compile(r'↳ (.*keyboard|.*Keyboard).*id=(\d+)')
            for match in pattern.finditer(result):
                name, device_id = match.groups()
                keyboards.append(f"Keyboard: {name} (ID: {device_id})")
        except (subprocess.SubprocessError, FileNotFoundError):
            # Check /dev/input/by-id for keyboards
            import glob
            import os
            
            keyboard_devices = glob.glob('/dev/input/by-id/*kbd*')
            for device in keyboard_devices:
                keyboards.append(f"Keyboard: {os.path.basename(device)}")
        
        if not keyboards:
            keyboards.append("No keyboards detected or insufficient permissions.")
    except Exception as e:
        keyboards.append(f"Error detecting keyboards: {e}")
    
    return keyboards

def list_mac_keyboards():
    """List keyboards on macOS using system_profiler"""
    keyboards = []
    try:
        import subprocess
        import plistlib
        
        cmd = ['system_profiler', 'SPUSBDataType', '-xml']
        result = subprocess.run(cmd, capture_output=True, check=True)
        devices = plistlib.loads(result.stdout)
        
        # Parse the plist output to find keyboards
        if devices and len(devices) > 0:
            usb_items = devices[0].get('_items', [])
            for usb_controller in usb_items:
                for device in usb_controller.get('_items', []):
                    if 'keyboard' in device.get('_name', '').lower():
                        name = device.get('_name', 'Unknown keyboard')
                        vendor = device.get('manufacturer', 'Unknown manufacturer')
                        keyboards.append(f"Keyboard: {name} (Vendor: {vendor})")
        
        if not keyboards:
            # Alternative approach using ioreg
            result = subprocess.run(['ioreg', '-p', 'IOUSB', '-l'], capture_output=True, text=True)
            import re
            keyboard_pattern = re.compile(r'^\s*"(.*keyboard|.*Keyboard).*"', re.IGNORECASE | re.MULTILINE)
            
            for match in keyboard_pattern.finditer(result.stdout):
                keyboards.append(f"Keyboard: {match.group(1)}")
        
        if not keyboards:
            keyboards.append("No keyboards detected.")
    except Exception as e:
        keyboards.append(f"Error detecting keyboards: {e}")
    
    return keyboards

if __name__ == "__main__":
    print("Detecting connected keyboards...")
    keyboards = list_keyboards()
    
    print("\nConnected Keyboards:")
    print("-------------------")
    for keyboard in keyboards:
        print(f"- {keyboard}")
