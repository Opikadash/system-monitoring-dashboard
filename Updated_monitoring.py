import psutil
import time
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import os
from collections import deque
import tkinter as tk
from tkinter import ttk
import webbrowser
import threading

# Configuration
INTERVAL = 5
DURATION = 120
CPU_THRESHOLD = 75
LOG_FILE = "metrics.log"
MAX_DATA_POINTS = 50
OUTPUT_DIR = "dashboard_outputs"
DB_FILE = "system_metrics.db"

# Data storage
cpu_data = deque(maxlen=MAX_DATA_POINTS)
memory_data = deque(maxlen=MAX_DATA_POINTS)
net_sent_data = deque(maxlen=MAX_DATA_POINTS)
net_recv_data = deque(maxlen=MAX_DATA_POINTS)
timestamps = deque(maxlen=MAX_DATA_POINTS)

def setup_database(db_file):
    """Set up SQLite database and create metrics table."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT,
            cpu_percent REAL,
            memory_percent REAL,
            net_sent_kb REAL,
            net_recv_kb REAL
        )
    """)
    conn.commit()
    return conn, cursor

def log_metrics(cpu, memory, net_sent_rate, net_recv_rate, log_file, cursor, conn):
    """Log system metrics to a file and database."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp}, CPU: {cpu:.2f}%, Memory: {memory:.2f}%, "
                f"Net Sent: {net_sent_rate / 1024:.2f} KB, Net Recv: {net_recv_rate / 1024:.2f} KB\n")
    cursor.execute("""
        INSERT INTO metrics (timestamp, cpu_percent, memory_percent, net_sent_kb, net_recv_kb)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, cpu, memory, net_sent_rate / 1024, net_recv_rate / 1024))
    conn.commit()

def check_cpu_alert(cpu, cpu_threshold, text_widget):
    """Check if CPU usage exceeds threshold and display alert."""
    if cpu > cpu_threshold:
        alert = f"ALERT: CPU usage ({cpu:.2f}%) exceeds threshold ({cpu_threshold}%)!"
        print(alert)
        text_widget.insert(tk.END, alert + "\n")
        text_widget.see(tk.END)
        return True
    return False

def collect_metrics():
    """Collect system metrics."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    net_io = psutil.net_io_counters()
    net_sent = net_io.bytes_sent
    net_recv = net_io.bytes_recv
    return cpu, memory, net_sent, net_recv

def generate_insights(cpu_data, memory_data, net_sent_data, net_recv_data, cpu_threshold, output_dir):
    """Generate and save insights based on collected metrics."""
    insights = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"insights_{timestamp}.txt")

    cpu_avg = sum(cpu_data) / len(cpu_data) if cpu_data else 0
    cpu_max = max(cpu_data) if cpu_data else 0
    memory_avg = sum(memory_data) / len(memory_data) if memory_data else 0
    memory_max = max(memory_data) if memory_data else 0
    net_sent_avg = sum(net_sent_data) / len(net_sent_data) if net_sent_data else 0
    net_recv_avg = sum(net_recv_data) / len(net_recv_data) if net_recv_data else 0

    insights.append("System Monitoring Insights")
    insights.append("=" * 25)
    insights.append(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    insights.append(f"CPU Usage - Avg: {cpu_avg:.2f}%, Max: {cpu_max:.2f}%")
    insights.append(f"Memory Usage - Avg: {memory_avg:.2f}%, Max: {memory_max:.2f}%")
    insights.append(f"Network Sent - Avg: {net_sent_avg:.2f} KB/s")
    insights.append(f"Network Received - Avg: {net_recv_avg:.2f} KB/s")

    if cpu_max > cpu_threshold:
        insights.append(f"\nWARNING: High CPU usage detected (Max: {cpu_max:.2f}%). Consider closing heavy applications.")
    if memory_max > 90:
        insights.append(f"WARNING: High memory usage detected (Max: {memory_max:.2f}%). Free up memory or add more RAM.")
    if net_sent_avg > 1024 or net_recv_avg > 1024:
        insights.append("NOTICE: High network activity detected. Check for large data transfers.")

    os.makedirs(output_dir, exist_ok=True)
    with open(report_file, "w") as f:
        f.write("\n".join(insights))
    print(f"Insights saved to {report_file}")
    return insights

def plot_metrics(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, cpu_threshold, output_dir):
    """Create interactive Plotly plots and save as HTML."""
    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=("CPU Usage Over Time", "Memory Usage Over Time", "Network I/O Over Time"),
                        vertical_spacing=0.15)

    fig.add_trace(go.Scatter(x=list(timestamps), y=list(cpu_data), name="CPU Usage (%)", line=dict(color="blue")), row=1, col=1)
    fig.add_hline(y=cpu_threshold, line_dash="dash", line_color="red", annotation_text=f"Threshold ({cpu_threshold}%)",
                  row=1, col=1)
    if cpu_data:
        max_cpu = max(cpu_data)
        max_idx = cpu_data.index(max_cpu)
        fig.add_annotation(x=timestamps[max_idx], y=max_cpu, text=f"Max: {max_cpu:.1f}%", showarrow=True,
                           arrowhead=2, ax=20, ay=-30, row=1, col=1)

    fig.add_trace(go.Scatter(x=list(timestamps), y=list(memory_data), name="Memory Usage (%)", line=dict(color="green")),
                  row=2, col=1)
    if memory_data:
        max_memory = max(memory_data)
        max_idx = memory_data.index(max_memory)
        fig.add_annotation(x=timestamps[max_idx], y=max_memory, text=f"Max: {max_memory:.1f}%", showarrow=True,
                           arrowhead=2, ax=20, ay=-30, row=2, col=1)

    fig.add_trace(go.Scatter(x=list(timestamps), y=list(net_sent_data), name="Network Sent (KB/s)", line=dict(color="orange")),
                  row=3, col=1)
    fig.add_trace(go.Scatter(x=list(timestamps), y=list(net_recv_data), name="Network Received (KB/s)", line=dict(color="purple")),
                  row=3, col=1)

    fig.update_layout(height=900, width=1200, title_text="System Monitoring Dashboard", showlegend=True)
    fig.update_xaxes(title_text="Time", tickangle=45)
    fig.update_yaxes(title_text="Usage (%)", row=1, col=1)
    fig.update_yaxes(title_text="Usage (%)", row=2, col=1)
    fig.update_yaxes(title_text="Data (KB/s)", row=3, col=1)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_file = os.path.join(output_dir, f"dashboard_{timestamp}.html")
    fig.write_html(plot_file)
    print(f"Plot saved to {plot_file}")
    return plot_file

def create_gui(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, cpu_threshold, output_dir, text_widget, root):
    """Update GUI with latest plot."""
    plot_file = plot_metrics(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, cpu_threshold, output_dir)
    webbrowser.open(f"file://{os.path.abspath(plot_file)}")

def main():
    """Main function to run the monitoring loop with GUI."""
    root = tk.Tk()
    root.title("System Monitoring Dashboard")
    root.geometry("400x300")

    label = ttk.Label(root, text="System Monitoring Dashboard", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    text_widget = tk.Text(root, height=10, width=50)
    text_widget.pack(pady=10)
    text_widget.insert(tk.END, "Starting system monitoring... Press Ctrl+C or Stop button to stop.\n")

    stop_button = ttk.Button(root, text="Stop Monitoring", command=root.quit)
    stop_button.pack(pady=10)

    def monitoring_loop():
        conn, cursor = setup_database(DB_FILE)
        try:
            start_time = time.time()
            prev_net_sent = psutil.net_io_counters().bytes_sent
            prev_net_recv = psutil.net_io_counters().bytes_recv

            while DURATION == 0 or time.time() - start_time < DURATION:
                cpu, memory, net_sent, net_recv = collect_metrics()

                net_sent_rate = (net_sent - prev_net_sent) / INTERVAL
                net_recv_rate = (net_recv - prev_net_recv) / INTERVAL
                prev_net_sent = net_sent
                prev_net_recv = net_recv

                log_metrics(cpu, memory, net_sent_rate, net_recv_rate, LOG_FILE, cursor, conn)

                cpu_data.append(cpu)
                memory_data.append(memory)
                net_sent_data.append(net_sent_rate / 1024)
                net_recv_data.append(net_recv_rate / 1024)
                timestamps.append(datetime.datetime.now().strftime("%H:%M:%S"))

                check_cpu_alert(cpu, CPU_THRESHOLD, text_widget)

                create_gui(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, CPU_THRESHOLD,
                          OUTPUT_DIR, text_widget, root)

                root.update()
                time.sleep(INTERVAL)

            text_widget.insert(tk.END, "Monitoring duration reached.\n")
            text_widget.see(tk.END)
            generate_insights(cpu_data, memory_data, net_sent_data, net_recv_data, CPU_THRESHOLD, OUTPUT_DIR)
            create_gui(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, CPU_THRESHOLD,
                      OUTPUT_DIR, text_widget, root)
            conn.close()
            root.quit()

        except KeyboardInterrupt:
            print("\nStopped monitoring.")
            text_widget.insert(tk.END, "Monitoring stopped.\n")
            text_widget.see(tk.END)
            generate_insights(cpu_data, memory_data, net_sent_data, net_recv_data, CPU_THRESHOLD, OUTPUT_DIR)
            create_gui(cpu_data, memory_data, net_sent_data, net_recv_data, timestamps, CPU_THRESHOLD,
                      OUTPUT_DIR, text_widget, root)
            conn.close()

    monitoring_thread = threading.Thread(target=monitoring_loop)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    root.mainloop()

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    main()
