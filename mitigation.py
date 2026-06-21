import subprocess
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def disable_unauthorized_device(serial, is_usbstor=True):
    if not is_admin():
        print("DEBUG: Execution skipped. Requires Administrator privileges.")
        return False
    
    escaped_serial = serial.replace("&", "`&")
    
    cmd = "Get-PnpDevice | Where-Object { $_.InstanceId -like '*" + escaped_serial + "*' } | Disable-PnpDevice -Confirm:$false"
    
    print("DEBUG: Executing mitigation command for serial: " + serial)
    
    try:
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        print("DEBUG: PowerShell Exit Code: " + str(result.returncode))
        if result.returncode == 0:
            return True
        else:
            print("DEBUG: PowerShell Error Output: " + str(result.stderr).strip())
    except Exception as e:
        print("DEBUG: Exception during mitigation execution: " + str(e))
    return False