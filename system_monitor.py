import psutil
import time
import datetime
import matplotlib.pyplot as plt
import os
from collections import deque

# Configuration
LOG_FILE = "system_metrics.log"
INTERVAL = 10  # seconds
CPU_THRESHOLD = 80  # percentage
DURATION = 60  # seconds (for visualization, adjust as needed)
MAX_DATA_POINTS = 100  # for visualization

# Data storage
cpu_data = deque(maxlen=MAX_DATA_POINTS)
memory_data = deque(maxlen=MAX_DATA_POINTS)
net_sent_data = deque(maxlen=MAX_DATA_POINTS)
net_recv_data = deque(maxlen=MAX_DATA_POINTS)
timestamps = deque(maxlen=MAX_DATA_POINTS)

def log_metrics(cpu, memory, net_sent, net_recv):
    """Log system metrics to a file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp}, CPU: {cpu:.2f}%, Memory: {memory:.2f}%, "
                f"Net Sent: {net_sent / 1024:.2f} KB, Net Recv: {net_recv / 1024:.2f} KB\n")

def check_cpu_alert(cpu):
    """Check if CPU usage exceeds threshold and print alert."""
    if cpu > CPU_THRESHOLD:
        print(f"ALERT: CPU usage ({cpu:.2f}%) exceeds threshold ({CPU_THRESHOLD}%)!")

def collect_metrics():
    """Collect system metrics."""
    # CPU usage
    cpu = psutil.cpu_percent(interval=1)
    
    # Memory usage
    memory = psutil.virtual_memory().percent
    
    # Network I/O
    net_io = psutil.net_io_counters()
    net_sent = net_io.bytes_sent
    net_recv = net_io.bytes_recv
    
    return cpu, memory, net_sent, net_recv

def plot_metrics():
    """Plot collected metrics."""
    plt.figure(figsize=(12, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(timestamps, cpu_data, label="CPU Usage (%)", color="blue")
    plt.axhline(y=CPU_THRESHOLD, color="red", linestyle="--", label="CPU Threshold")
    plt.title("CPU Usage Over Time")
    plt.xlabel("Time")
    plt.ylabel("Usage (%)")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 1, 2)
    plt.plot(timestamps, memory_data, label="Memory Usage (%)", color="green")
    plt.title("Memory Usage Over Time")
    plt.xlabel("Time")
    plt.ylabel("Usage (%)")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 1, 3)
    plt.plot(timestamps, net_sent_data, label="Network Sent (KB)", color="orange")
    plt.plot(timestamps, net_recv_data, label="Network Received (KB)", color="purple")
    plt.title("Network I/O Over Time")
    plt.xlabel("Time")
    plt.ylabel("Data (KB)")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()

def main():
    """Main function to run the monitoring loop."""
    print("Starting system monitoring... Press Ctrl+C to stop.")
    
    try:
        start_time = time.time()
        prev_net_sent = psutil.net_io_counters().bytes_sent
        prev_net_recv = psutil.net_io_counters().bytes_recv
        
        while time.time() - start_time < DURATION:
            # Collect metrics
            cpu, memory, net_sent, net_recv = collect_metrics()
            
            # Calculate network I/O rates (bytes per interval)
            net_sent_rate = (net_sent - prev_net_sent) / INTERVAL
            net_recv_rate = (net_recv - prev_net_recv) / INTERVAL
            prev_net_sent = net_sent
            prev_net_recv = net_recv
            
            # Log metrics
            log_metrics(cpu, memory, net_sent_rate, net_recv_rate)
            
            # Store for visualization
            cpu_data.append(cpu)
            memory_data.append(memory)
            net_sent_data.append(net_sent_rate / 1024)  # Convert to KB
            net_recv_data.append(net_recv_rate / 1024)  # Convert to KB
            timestamps.append(datetime.datetime.now().strftime("%H:%M:%S"))
            
            # Check for CPU alert
            check_cpu_alert(cpu)
            
            # Wait for the next interval
            time.sleep(INTERVAL)
            
        # Plot metrics after collection
        plot_metrics()
        
    except KeyboardInterrupt:
        print("\nStopped monitoring.")
        plot_metrics()

if __name__ == "__main__":
    # Clear log file at start
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    main()
