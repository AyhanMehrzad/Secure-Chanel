import urllib.request
import urllib.parse
import time
import json
import socket
import threading
import os
import random

# Configuration
TEST_URL = "https://api.telegram.org"
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt"
]
STATUS_FILE = "/dev/shm/tg_proxy_status"
# Target 90ms but allow up to 2 seconds for a working path
LATENCY_TARGET = 0.090 
LATENCY_MAX = 2.0

class ProxyManager:
    def __init__(self):
        self.active_proxy = None
        self.proxies = []
        self.lock = threading.Lock()
        
    def fetch_proxies(self):
        print(f"[{time.ctime()}] Fetching proxy list from {len(PROXY_SOURCES)} sources...")
        new_proxies = set()
        for i, source in enumerate(PROXY_SOURCES):
            try:
                # Use a User-Agent to avoid being blocked by GitHub/ProxyScrape
                req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    found = 0
                    for line in content.splitlines():
                        line = line.strip()
                        if line and ":" in line and not line.startswith("#"):
                            new_proxies.add(line)
                            found += 1
                    print(f"Source {i+1}: Found {found} proxies")
            except Exception as e:
                print(f"Source {i+1} FAILED: {e}")
        
        with self.lock:
            self.proxies = list(new_proxies)
        print(f"Total unique proxies in pool: {len(self.proxies)}")

    def test_proxy(self, proxy_addr):
        proxy_url = f"http://{proxy_addr}"
        try:
            start_time = time.time()
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            # Short timeout to keep the search moving
            with opener.open(TEST_URL, timeout=3) as response:
                latency = time.time() - start_time
                if response.getcode() == 200:
                    return latency
        except:
            pass
        return None

    def find_best_proxy(self):
        print(f"[{time.ctime()}] Scanning for best proxy...")
        with self.lock:
            candidates = self.proxies[:]
            
        if not candidates:
            print("No candidates available. Re-fetching...")
            self.fetch_proxies()
            with self.lock:
                candidates = self.proxies[:]
        
        random.shuffle(candidates)
        
        best_proxy = None
        min_latency = float('inf')
        tested_count = 0
        
        # Test up to 100 proxies per scan
        for proxy_addr in candidates[:100]:
            tested_count += 1
            latency = self.test_proxy(proxy_addr)
            if latency is not None:
                print(f"  FOUND: {proxy_addr} ({latency*1000:.1f}ms)")
                if latency < min_latency:
                    min_latency = latency
                    best_proxy = f"http://{proxy_addr}"
                
                # Stop if we hit the user's high-speed target
                if latency < LATENCY_TARGET:
                    print(f"  Target latency met ({latency*1000:.1f}ms). Stopping search.")
                    break
        
        print(f"Scan complete. Tested {tested_count} proxies.")
        if best_proxy:
            self.set_active_proxy(best_proxy)
        else:
            print("  No working proxies found in this batch.")
            self.set_active_proxy("") 

    def set_active_proxy(self, proxy_url):
        self.active_proxy = proxy_url
        try:
            # Write to file for app.py to read
            with open(STATUS_FILE, "w") as f:
                f.write(proxy_url)
            print(f"ACTIVE PROXY UPDATED: {proxy_url if proxy_url else 'NONE'}")
        except Exception as e:
            print(f"Critical error writing status file: {e}")

    def run(self):
        print("Proxy Manager started.")
        while True:
            try:
                # If no proxy or it fails, find a new one
                needs_new = False
                if not self.active_proxy:
                    needs_new = True
                else:
                    # Test current active proxy
                    latency = self.test_proxy(self.active_proxy.replace("http://", ""))
                    if latency is None:
                        print("Active proxy is dead. Rotating...")
                        needs_new = True
                    elif latency > LATENCY_MAX:
                        print(f"Active proxy is slow ({latency*1000:.1f}ms). Seeking better...")
                        needs_new = True
                
                if needs_new:
                    self.find_best_proxy()
                
                # Sleep between health checks
                time.sleep(30 if self.active_proxy else 5)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(10)

if __name__ == "__main__":
    manager = ProxyManager()
    manager.run()
