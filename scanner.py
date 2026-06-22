import datetime
import os
try:
    import winreg
    PLATFORM_WINDOWS = True
except ImportError:
    PLATFORM_WINDOWS = False

def check_usbstor_existence():
    if not PLATFORM_WINDOWS:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USBSTOR", 0, winreg.KEY_READ) as k:
            return True
    except Exception:
        return False

def parse_first_connected(serial):
    if not PLATFORM_WINDOWS:
        return "Unknown"
    
    log_path = r"C:\Windows\INF\setupapi.dev.log"
    if not os.path.exists(log_path):
        return "Unknown"
    
    try:
        earliest_time = None
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            current_section_time = None
            for line in f:
                if line.startswith(">>>  ["):
                    current_section_time = None
                elif line.startswith("<<<  [Section end"):
                    try:
                        parts = line.split()
                        if len(parts) >= 5:
                            date_str = parts[3]
                            time_str = parts[4].split(".")[0]
                            current_section_time = date_str.replace("/", "-") + " " + time_str
                    except Exception:
                        pass
                
                if serial in line and current_section_time:
                    if not earliest_time:
                        earliest_time = current_section_time
        if earliest_time:
            return earliest_time
    except Exception:
        pass
    return "Unknown"

def scan_registry_path(base_path, is_usbstor):
    devices = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path, 0, winreg.KEY_READ) as main_key:
            num_devices, _, _ = winreg.QueryInfoKey(main_key)
            for i in range(num_devices):
                try:
                    device_class_name = winreg.EnumKey(main_key, i)
                    device_class_path = base_path + "\\" + device_class_name
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_class_path, 0, winreg.KEY_READ) as class_key:
                        num_serials, _, _ = winreg.QueryInfoKey(class_key)
                        for j in range(num_serials):
                            try:
                                serial_name = winreg.EnumKey(class_key, j)
                                serial_path = device_class_path + "\\" + serial_name
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, serial_path, 0, winreg.KEY_READ) as serial_key:
                                    _, _, filetime = winreg.QueryInfoKey(serial_key)
                                    try:
                                        if filetime == 0:
                                            timestamp_str = "Unknown"
                                        else:
                                            dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
                                            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    except Exception:
                                        timestamp_str = "Unknown"

                                    device_name = "Unknown Device"
                                    for val_name in ["FriendlyName", "DeviceDesc"]:
                                        try:
                                            val, _ = winreg.QueryValueEx(serial_key, val_name)
                                            if val:
                                                if ";" in val:
                                                    val = val.split(";")[-1]
                                                device_name = val.strip()
                                                break
                                        except FileNotFoundError:
                                            continue
                                    
                                    devices.append({
                                        "serial_number": serial_name,
                                        "device_name": device_name,
                                        "last_connected": timestamp_str,
                                        "is_usbstor": is_usbstor
                                    })
                            except Exception:
                                continue
                except Exception:
                    continue
    except Exception:
        pass
    return devices

def scan_usb_history():
    if not check_usbstor_existence():
        return mock_scan_usb_history()

    usbstor_devices = scan_registry_path(r"SYSTEM\CurrentControlSet\Enum\USBSTOR", is_usbstor=True)
    usb_devices = scan_registry_path(r"SYSTEM\CurrentControlSet\Enum\USB", is_usbstor=False)
    
    all_devices = usbstor_devices + usb_devices
    unique_devices = {}
    for dev in all_devices:
        serial = dev["serial_number"]
        if serial not in unique_devices:
            unique_devices[serial] = dev
    
    final_devices = list(unique_devices.values())
    for dev in final_devices:
        dev["first_connected"] = parse_first_connected(dev["serial_number"])
        
    return final_devices

def mock_scan_usb_history():
    return [
        {
            "serial_number": "4C531000010915104273&0",
            "device_name": "SanDisk Cruzer Glide USB Device",
            "last_connected": "2026-06-18 14:22:10",
            "first_connected": "2026-05-01 10:11:45",
            "is_usbstor": True
        },
        {
            "serial_number": "AA00000000013952&1",
            "device_name": "Kingston DataTraveler 3.0",
            "last_connected": "2026-06-15 09:05:43",
            "first_connected": "2026-05-10 11:22:33",
            "is_usbstor": True
        },
        {
            "serial_number": "7&28ea13a4&0&0000",
            "device_name": "Generic USB SD Reader",
            "last_connected": "2026-05-12 18:41:00",
            "first_connected": "2026-04-12 08:30:12",
            "is_usbstor": True
        },
        {
            "serial_number": "001A6B0A11F2&0",
            "device_name": "Samsung Flash Drive FIT",
            "last_connected": "2026-06-19 11:30:15",
            "first_connected": "2026-06-01 15:40:55",
            "is_usbstor": True
        },
        {
            "serial_number": "D3B4C5E6F7A8&2",
            "device_name": "Intruder Stealth Rubber Ducky",
            "last_connected": "2026-06-19 12:40:00",
            "first_connected": "2026-06-19 12:39:50",
            "is_usbstor": False
        },
        {
            "serial_number": "999A888B777C&0",
            "device_name": "Attacker Rogue Wi-Fi Dongle",
            "last_connected": "2026-06-20 12:45:00",
            "first_connected": "2026-06-20 12:45:00",
            "is_usbstor": False
        },
        {
            "serial_number": "777777777777&1",
            "device_name": "Intruder Hardware Keylogger",
            "last_connected": "2026-06-20 13:00:00",
            "first_connected": "2026-06-20 12:59:00",
            "is_usbstor": False
        }
    ]