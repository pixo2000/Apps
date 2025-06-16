import psutil
import threading
import time
from datetime import datetime
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, Label, MultiColumnListBox
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.event import KeyboardEvent

class ProcessFrame(Frame):
    def __init__(self, screen):
        super(ProcessFrame, self).__init__(screen,
                                         screen.height,
                                         screen.width,
                                         hover_focus=True,
                                         title="Task Manager - Processes",
                                         reduce_cpu=True)
        
        # Create layout
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        
        # Header info
        self._cpu_label = Label("CPU: 0%")
        self._memory_label = Label("Memory: 0%")
        self._processes_label = Label("Processes: 0")
        
        layout.add_widget(self._cpu_label)
        layout.add_widget(self._memory_label)
        layout.add_widget(self._processes_label)
        layout.add_widget(Divider())
        
        # Process list
        self._process_list = MultiColumnListBox(
            height=screen.height - 10,
            columns=["<15", "<30", ">8", ">10", ">8"],
            options=[],
            titles=["PID", "Name", "CPU%", "Memory MB", "Status"]
        )
        layout.add_widget(self._process_list)
        
        # Buttons
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("End Task", self._kill_process), 0)
        layout2.add_widget(Button("Refresh", self._refresh), 1)
        layout2.add_widget(Button("Performance", self._show_performance), 2)
        layout2.add_widget(Button("Exit", self._exit), 3)
        
        self.fix()
        
        # Start background thread for updates
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _update_loop(self):
        """Background thread to update process information"""
        while self._running:
            try:
                self._update_data()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                # Handle any errors gracefully
                pass
    
    def _update_data(self):
        """Update process and system information"""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Update labels
            self._cpu_label.text = f"CPU: {cpu_percent:.1f}%"
            self._memory_label.text = f"Memory: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)"
            
            # Get processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    info = proc.info
                    memory_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                    
                    processes.append([
                        str(info['pid']),
                        info['name'][:25] if info['name'] else "N/A",
                        f"{info['cpu_percent']:.1f}" if info['cpu_percent'] is not None else "0.0",
                        f"{memory_mb:.1f}",
                        info['status'][:7] if info['status'] else "unknown"
                    ])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage (descending)
            processes.sort(key=lambda x: float(x[2]), reverse=True)
            
            self._processes_label.text = f"Processes: {len(processes)}"
            
            # Update process list
            self._process_list.options = [(proc, i) for i, proc in enumerate(processes)]
            
        except Exception as e:
            # Handle errors gracefully
            pass
    
    def _kill_process(self):
        """Kill selected process"""
        if self._process_list.value is not None:
            try:
                selected_process = self._process_list.options[self._process_list.value][0]
                pid = int(selected_process[0])
                
                # Confirm kill
                proc = psutil.Process(pid)
                proc_name = proc.name()
                
                # Create confirmation frame
                self._scene.add_effect(
                    ConfirmFrame(self._screen, 
                               f"End process '{proc_name}' (PID: {pid})?",
                               self._confirm_kill, pid)
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                pass
    
    def _confirm_kill(self, pid):
        """Actually kill the process"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            # If it doesn't terminate gracefully, force kill
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _refresh(self):
        """Force refresh of data"""
        self._update_data()
    
    def _show_performance(self):
        """Switch to performance view"""
        self._scene.add_effect(PerformanceFrame(self._screen))
    
    def _exit(self):
        """Exit application"""
        self._running = False
        raise StopApplication("User pressed exit")
    
    def process_event(self, event):
        # Handle keyboard shortcuts
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q')]:
                self._exit()
            elif event.key_code == ord('r'):
                self._refresh()
            elif event.key_code == ord('k'):
                self._kill_process()
        
        return super(ProcessFrame, self).process_event(event)

class PerformanceFrame(Frame):
    def __init__(self, screen):
        super(PerformanceFrame, self).__init__(screen,
                                             screen.height,
                                             screen.width,
                                             hover_focus=True,
                                             title="Task Manager - Performance",
                                             reduce_cpu=True)
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        
        # Performance metrics
        self._cpu_label = Label("CPU Usage: 0%")
        self._cpu_cores = Label("CPU Cores: 0")
        self._memory_label = Label("Memory Usage: 0%")
        self._memory_available = Label("Available Memory: 0 GB")
        self._disk_label = Label("Disk Usage: 0%")
        self._network_sent = Label("Network Sent: 0 MB")
        self._network_recv = Label("Network Received: 0 MB")
        self._uptime_label = Label("System Uptime: 0")
        
        layout.add_widget(Label("=== SYSTEM PERFORMANCE ==="))
        layout.add_widget(Divider())
        layout.add_widget(self._cpu_label)
        layout.add_widget(self._cpu_cores)
        layout.add_widget(Divider())
        layout.add_widget(self._memory_label)
        layout.add_widget(self._memory_available)
        layout.add_widget(Divider())
        layout.add_widget(self._disk_label)
        layout.add_widget(Divider())
        layout.add_widget(self._network_sent)
        layout.add_widget(self._network_recv)
        layout.add_widget(Divider())
        layout.add_widget(self._uptime_label)
        
        # CPU usage per core
        self._core_labels = []
        cpu_count = psutil.cpu_count()
        for i in range(min(cpu_count, 8)):  # Show max 8 cores to fit screen
            label = Label(f"Core {i}: 0%")
            self._core_labels.append(label)
            layout.add_widget(label)
        
        # Buttons
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Back to Processes", self._back_to_processes), 0)
        layout2.add_widget(Button("Exit", self._exit), 1)
        
        self.fix()
        
        # Start update thread
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        
        # Store network stats for delta calculation
        self._last_network = psutil.net_io_counters()
    
    def _update_loop(self):
        """Background thread to update performance data"""
        while self._running:
            try:
                self._update_performance()
                time.sleep(1)  # Update every second for performance
            except Exception:
                pass
    
    def _update_performance(self):
        """Update performance metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            
            self._cpu_label.text = f"CPU Usage: {cpu_percent:.1f}%"
            self._cpu_cores.text = f"CPU Cores: {cpu_count}"
            
            # Update per-core usage
            for i, (label, usage) in enumerate(zip(self._core_labels, cpu_per_core)):
                label.text = f"Core {i}: {usage:.1f}%"
            
            # Memory
            memory = psutil.virtual_memory()
            self._memory_label.text = f"Memory Usage: {memory.percent:.1f}%"
            self._memory_available.text = f"Available Memory: {memory.available / (1024**3):.1f} GB"
            
            # Disk
            disk = psutil.disk_usage('/')
            self._disk_label.text = f"Disk Usage: {disk.percent:.1f}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)"
            
            # Network
            current_network = psutil.net_io_counters()
            sent_mb = (current_network.bytes_sent - self._last_network.bytes_sent) / (1024 * 1024)
            recv_mb = (current_network.bytes_recv - self._last_network.bytes_recv) / (1024 * 1024)
            
            self._network_sent.text = f"Network Sent: {current_network.bytes_sent / (1024**2):.1f} MB total"
            self._network_recv.text = f"Network Received: {current_network.bytes_recv / (1024**2):.1f} MB total"
            
            self._last_network = current_network
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            self._uptime_label.text = f"System Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
            
        except Exception:
            pass
    
    def _back_to_processes(self):
        """Go back to process view"""
        self._running = False
        self._scene.add_effect(ProcessFrame(self._screen))
    
    def _exit(self):
        """Exit application"""
        self._running = False
        raise StopApplication("User pressed exit")

class ConfirmFrame(Frame):
    def __init__(self, screen, message, callback, *args):
        super(ConfirmFrame, self).__init__(screen,
                                         7, 50,
                                         hover_focus=True,
                                         title="Confirm Action")
        self._callback = callback
        self._args = args
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        
        layout.add_widget(Label(message))
        layout.add_widget(Divider())
        
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Yes", self._yes), 0)
        layout2.add_widget(Button("No", self._no), 1)
        
        self.fix()
    
    def _yes(self):
        self._callback(*self._args)
        self._scene.remove_effect(self)
    
    def _no(self):
        self._scene.remove_effect(self)

def demo(screen, scene):
    screen.play([Scene([ProcessFrame(screen)], 500)], stop_on_resize=True, start_scene=scene)

def main():
    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
            break
        except ResizeScreenError as e:
            last_scene = e.scene

if __name__ == "__main__":
    # Install required packages if not present
    try:
        import psutil
        from asciimatics.widgets import Frame
    except ImportError:
        print("Installing required packages...")
        import os
        os.system("pip install psutil asciimatics")
        import psutil
        from asciimatics.widgets import Frame
    
    print("Starting Task Manager...")
    print("Controls:")
    print("- Arrow keys: Navigate")
    print("- Enter: Select")
    print("- Q: Quit")
    print("- R: Refresh")
    print("- K: Kill process")
    print("\nPress any key to continue...")
    input()
    
    main()
