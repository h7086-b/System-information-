import socket
import requests
import uuid
import subprocess
import platform
import os
import json

class SystemInfo:
    def __init__(self):
        self.is_admin = self.check_admin_privileges()
    
    def check_admin_privileges(self):
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            return f"Error: {str(e)}"

    def get_public_ip(self):
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=10)
            data = response.json()
            return data.get('ip', 'Not found')
        except Exception as e:
            return f"Error: {str(e)}"

    def get_mac_address(self):
        try:
            mac_num = hex(uuid.getnode()).replace('0x', '').upper()
            mac = ':'.join(mac_num[i:i+2] for i in range(0, len(mac_num), 2))
            return mac
        except Exception as e:
            return f"Error: {str(e)}"

    def get_wifi_password(self):
        if not self.is_admin:
            return "Administrator rights required"
        
        try:
            if platform.system() != "Windows":
                return "Only available on Windows"
            
            interface_result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if "SSID" not in interface_result.stdout:
                return "No WiFi interface found"
            
            ssid = None
            for line in interface_result.stdout.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        break
            
            if not ssid:
                return "Not connected to WiFi"
            
            password_result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            for line in password_result.stdout.split('\n'):
                if "Key Content" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        password = parts[1].strip()
                        return f"Network: {ssid}\nPassword: {password}"
            
            return f"Password not found for: {ssid}"
            
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    system_info = SystemInfo()
    
    print("\n" + "="*60)
    print("          SYSTEM INFORMATION COLLECTOR")
    print("="*60)
    
    if system_info.is_admin:
        print("\nStatus: ADMIN PRIVILEGES")
    else:
        print("\nStatus: STANDARD USER")
    
    print("\n" + "-"*60 + "\n")
    
    print(f"Local IP Address    : {system_info.get_local_ip()}")
    print(f"Public IP Address   : {system_info.get_public_ip()}")
    print(f"MAC Address         : {system_info.get_mac_address()}")
    print(f"WiFi Password       : {system_info.get_wifi_password()}")
    
    print("\n" + "="*60 + "\n")
