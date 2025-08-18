import threading
import subprocess
import time
import csv
import datetime
import re
import os
import locale
from typing import Optional, List

class PingMonitor:
    def __init__(self, targets: dict, ping_interval: int = 5, output_file: str = "ping_results.csv"):
        """
        Initialize the ping monitor
        
        Args:
            targets: Dictionary with target names as keys and IP addresses/hostnames as values
            ping_interval: Time between pings in seconds
            output_file: CSV file to save results
        """
        self.targets = targets
        self.ping_interval = ping_interval
        self.output_file = output_file
        self.running = False
        self.threads = []
        
        # Create CSV file with headers if it doesn't exist
        self.setup_csv_file()
    
    def setup_csv_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'target', 'ip_address', 'ping_time_ms', 'status'])
    
    def ping_target(self, target_name: str, target_ip: str) -> Optional[float]:
        """
        Ping a target and return the response time in milliseconds
        
        Args:
            target_name: Name of the target for logging
            target_ip: IP address or hostname to ping
            
        Returns:
            Ping time in milliseconds or None if ping failed
        """
        try:
            # Try to get system encoding first
            system_encoding = locale.getpreferredencoding()
            
            # Windows ping command with proper encoding handling
            result = subprocess.run(
                ['ping', '-n', '1', target_ip],
                capture_output=True,
                text=True,
                encoding=system_encoding,
                errors='ignore',  # Ignore encoding errors
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse ping time from output
                # Look for various patterns that can appear in ping output
                time_patterns = [
                    r'(?:time|Zeit)=(\d+)ms',           # Standard: time=1ms or Zeit=1ms
                    r'(?:time|Zeit)<(\d+)ms',           # Less than: time<1ms
                    r'(?:time|Zeit)\s*=\s*(\d+)\s*ms', # With spaces: time = 1 ms
                    r'(\d+)\s*ms',                      # Simple: 1ms or 1 ms
                ]
                
                for pattern in time_patterns:
                    matches = re.findall(pattern, result.stdout, re.IGNORECASE)
                    if matches:
                        # Convert to float and validate
                        for match in matches:
                            try:
                                ping_time = float(match)
                                # Only accept reasonable ping times (0-10000ms)
                                if 0 < ping_time < 10000:
                                    return ping_time
                            except ValueError:
                                continue
            
            return None
            
        except Exception as e:
            print(f"Error pinging {target_name} ({target_ip}): {e}")
            return None
    
    def save_ping_result(self, target_name: str, target_ip: str, ping_time: Optional[float]):
        """Save ping result to CSV file"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'success' if ping_time is not None else 'failed'
        ping_time_str = f"{ping_time:.1f}" if ping_time is not None else "N/A"
        
        try:
            with open(self.output_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, target_name, target_ip, ping_time_str, status])
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
    
    def monitor_target(self, target_name: str, target_ip: str):
        """Monitor a single target in a loop"""
        print(f"Starting ping monitoring for {target_name} ({target_ip})")
        
        while self.running:
            ping_time = self.ping_target(target_name, target_ip)
            self.save_ping_result(target_name, target_ip, ping_time)
            
            if ping_time is not None:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {target_name}: {ping_time:.1f}ms")
            else:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {target_name}: FAILED")
            
            time.sleep(self.ping_interval)
    
    def start_monitoring(self):
        """Start monitoring all targets in separate threads"""
        print(f"Starting ping monitoring to {len(self.targets)} targets...")
        print(f"Ping interval: {self.ping_interval} seconds")
        print(f"Output file: {self.output_file}")
        print("-" * 50)
        
        self.running = True
        
        # Create and start a thread for each target
        for target_name, target_ip in self.targets.items():
            thread = threading.Thread(
                target=self.monitor_target,
                args=(target_name, target_ip),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping ping monitoring...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring all targets"""
        self.running = False
        
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join(timeout=2)
        
        print("Ping monitoring stopped.")
    
    def print_recent_stats(self, last_n_minutes: int = 10):
        """Print statistics for the last N minutes"""
        try:
            if not os.path.exists(self.output_file):
                print("No data file found.")
                return
            
            cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=last_n_minutes)
            
            with open(self.output_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                recent_data = {}
                
                for row in reader:
                    try:
                        row_time = datetime.datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                        if row_time >= cutoff_time:
                            target = row['target']
                            if target not in recent_data:
                                recent_data[target] = {'pings': [], 'failures': 0}
                            
                            if row['status'] == 'success' and row['ping_time_ms'] != 'N/A':
                                recent_data[target]['pings'].append(float(row['ping_time_ms']))
                            else:
                                recent_data[target]['failures'] += 1
                    except ValueError:
                        continue
            
            print(f"\n--- Statistics for last {last_n_minutes} minutes ---")
            for target, data in recent_data.items():
                pings = data['pings']
                failures = data['failures']
                total_attempts = len(pings) + failures
                
                if pings:
                    avg_ping = sum(pings) / len(pings)
                    min_ping = min(pings)
                    max_ping = max(pings)
                    success_rate = (len(pings) / total_attempts) * 100 if total_attempts > 0 else 0
                    
                    print(f"{target}:")
                    print(f"  Average: {avg_ping:.1f}ms")
                    print(f"  Min: {min_ping:.1f}ms, Max: {max_ping:.1f}ms")
                    print(f"  Success rate: {success_rate:.1f}% ({len(pings)}/{total_attempts})")
                else:
                    print(f"{target}: No successful pings in the last {last_n_minutes} minutes")
                    
        except Exception as e:
            print(f"Error reading statistics: {e}")

def main():
    # Define targets to ping
    targets = {
        "Fritz_Box": "192.168.1.1",  # Common Fritz Box IP
        "Frankfurt_Server": "8.8.8.8",  # Google DNS as Frankfurt-region server
        # Alternative Frankfurt servers you could use:
        # "Frankfurt_Server": "1.1.1.1",  # Cloudflare DNS
        # "Frankfurt_Server": "185.60.216.35",  # German server example
    }
    
    # Create ping monitor
    monitor = PingMonitor(
        targets=targets,
        ping_interval=1,  # Ping every second
        output_file="ping_results.csv"
    )
    
    try:
        # Start monitoring
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        # Print recent statistics before exit
        monitor.print_recent_stats(last_n_minutes=10)

if __name__ == "__main__":
    main()