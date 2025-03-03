import wmi
import win32api
import hashlib

def get_hardware_info():
    c = wmi.WMI()
    
    # Get CPU information
    cpu_info = c.Win32_Processor()[0]
    cpu_id = f"{cpu_info.ProcessorId.strip()}"
    
    # Get GPU information
    gpu_info = c.Win32_VideoController()[0]
    gpu_id = f"{gpu_info.Name.strip()}"
    
    # Get motherboard information
    board_info = c.Win32_BaseBoard()[0]
    board_id = f"{board_info.SerialNumber.strip()}"
    
    # Get input devices (mouse and keyboard)
    input_devices = []
    for device in c.Win32_PnPEntity():
        if device.Name:
            if "mouse" in device.Name.lower():
                input_devices.append(("Mouse", device.Name))
            elif "keyboard" in device.Name.lower():
                input_devices.append(("Keyboard", device.Name))
    
    return {
        'cpu': cpu_id,
        'gpu': gpu_id,
        'motherboard': board_id,
        'input_devices': input_devices
    }

def calculate_hwid(hardware_info):
    # Combine all hardware IDs
    combined = (
        hardware_info['cpu'] +
        hardware_info['gpu'] +
        hardware_info['motherboard']
    )
    
    # Create a SHA-256 hash of the combined information
    hwid = hashlib.sha256(combined.encode()).hexdigest()
    return hwid

def main():
    try:
        hardware_info = get_hardware_info()
        hwid = calculate_hwid(hardware_info)
        
        print("Hardware Information:")
        print("-" * 50)
        print(f"CPU ID: {hardware_info['cpu']}")
        print(f"GPU: {hardware_info['gpu']}")
        print(f"Motherboard Serial: {hardware_info['motherboard']}")
        print("\nInput Devices:")
        for device_type, device_name in hardware_info['input_devices']:
            print(f"{device_type}: {device_name}")
        print("-" * 50)
        print(f"Generated HWID: {hwid}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()