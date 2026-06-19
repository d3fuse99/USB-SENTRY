import datetime
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

def mock_scan_usb_history():
    return [
        {
            "serial_number": "4C531000010915104273&0",
            "device_name": "SanDisk Cruzer Glide USB Device",
            "last_connected": "2026-06-18 14:22:10"
        },
        {
            "serial_number": "AA00000000013952&1",
            "device_name": "Kingston DataTraveler 3.0",
            "last_connected": "2026-06-15 09:05:43"
        },
        {
            "serial_number": "7&28ea13a4&0&0000",
            "device_name": "Generic USB SD Reader",
            "last_connected": "2026-05-12 18:41:00"
        },
        {
            "serial_number": "001A6B0A11F2&0",
            "device_name": "Samsung Flash Drive FIT",
            "last_connected": "2026-06-19 11:30:15"
        },
        {
            "serial_number": "D3B4C5E6F7A8&2",
            "device_name": "Intruder Stealth Rubber Ducky",
            "last_connected": "2026-06-19 12:40:00"
        }
    ]

def scan_usb_history():
    if not check_usbstor_existence():
        return mock_scan_usb_history()

    devices = []
    usbstor_path = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, usbstor_path, 0, winreg.KEY_READ) as usbstor_key:
            num_devices, _, _ = winreg.QueryInfoKey(usbstor_key)
            for i in range(num_devices):
                try:
                    device_class_name = winreg.EnumKey(usbstor_key, i)
                    device_class_path = usbstor_path + "\\" + device_class_name
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_class_path, 0, winreg.KEY_READ) as device_class_key:
                        num_serials, _, _ = winreg.QueryInfoKey(device_class_key)
                        for j in range(num_serials):
                            try:
                                serial_name = winreg.EnumKey(device_class_key, j)
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
                                        "last_connected": timestamp_str
                                    })
                            except Exception:
                                continue
                except Exception:
                    continue
    except Exception:
        pass
    return devices