# System Monitoring Dashboard

A Python-based dashboard for monitoring system metrics (CPU, memory, network I/O) using `psutil`, designed to mimic Power BI’s interactivity and insights. The project includes two scripts: `system_monitor.py` (fixed settings) and `Updated_monitoring.py` (command-line configurable). Both support real-time GUI visualization, SQLite storage, interactive `plotly` plots, and duration-based monitoring, ideal for infrastructure testing and automation.

## Features
- Collects CPU usage (%), memory usage (%), and network I/O (sent/received in KB/s) at regular intervals.
- Stores metrics in a SQLite database (`system_metrics.db` by default) for historical analysis.
- Displays real-time interactive plots using `plotly`, with zoom, pan, and hover capabilities.
- Provides a `tkinter` GUI for alerts and plot display (opens in browser).
- Saves plots (HTML) and insights reports (TXT) to a configurable output directory.
- Generates actionable insights (e.g., high CPU/memory warnings).
- Alerts when CPU usage exceeds a threshold (default: 80%).
- Supports configurable monitoring duration (unlimited by default).
- Code versioned with Git and hosted on GitHub.

## Scripts Overview

### 1. `system_monitor.py` (Original)
- **Description**: A simple script with hardcoded settings for monitoring system metrics.
- **Key Characteristics**:
  - Fixed settings: 5-second interval, 120-second duration, 75% CPU threshold, 50 max data points, outputs to `dashboard_outputs`, database in `system_metrics.db`, logs to `metrics.log`.
  - Ideal for quick setup or fixed requirements.
- **Contents**:
  - **Metric Collection**: Uses `psutil` for CPU, memory, and network I/O.
  - **Database Storage**: Stores metrics in a SQLite database, thread-safe.
  - **Logging**: Writes metrics to `metrics.log`.
  - **Visualization**: Real-time interactive `plotly` subplots (CPU, memory, network) with annotations, saved as HTML.
  - **GUI**: `tkinter` interface showing alerts and triggering plots in browser.
  - **Insights**: Generates average/max metrics and warnings in `dashboard_outputs/insights_<timestamp>.txt`.
  - **Alerts**: Displays CPU usage alerts (>75%) in GUI and console.
  - **Error Handling**: Handles `KeyboardInterrupt` and ensures database/plot saving.
- **Usage**:
  ```bash
  python system_monitor.py
  ```
  - No command-line arguments; edit the script to change settings.
- **Strengths**:
  - Simple and quick to deploy for fixed use cases.
  - Minimal code complexity for beginners.
- **Limitations**:
  - Requires code modification to change settings.
  - Less flexible for testing or automation.

### 2. `Updated_monitoring.py` (Argparse Version)
- **Description**: An enhanced script with command-line configurability for flexible monitoring.
- **Key Characteristics**:
  - Configurable settings: interval, duration, CPU threshold, log file, max data points, output directory, database file.
  - Suitable for testing, automation, and varied use cases.
- **Contents**:
  - **Metric Collection**: Identical to the original, using `psutil`.
  - **Database Storage**: Stores metrics in a user-specified SQLite database, thread-safe.
  - **Logging**: Writes to a user-specified log file.
  - **Visualization**: Same real-time `plotly` subplots, saved as HTML.
  - **GUI**: Same `tkinter` interface as the original.
  - **Insights**: Same insights report, saved to the specified output directory.
  - **Alerts**: Alerts for CPU usage above a user-defined threshold.
  - **Error Handling**: Validates command-line inputs and handles `KeyboardInterrupt`.
- **Usage**:
  Run with default settings:
  ```bash
  python Updated_monitoring.py
  ```
  Or with custom settings:
  ```bash
  python Updated_monitoring.py --interval 5 --duration 120 --cpu-threshold 75 --log-file metrics.log --max-data-points 50 --output-dir dashboard_outputs --db-file system_metrics.db
  ```
  - **Arguments**:
    - `--interval`: Interval between collections (seconds, default: 10).
    - `--duration`: Monitoring duration (seconds, default: 0 for unlimited).
    - `--cpu-threshold`: CPU usage alert threshold (%, default: 80).
    - `--log-file`: Log file path (default: `system_metrics.log`).
    - `--max-data-points`: Max data points for visualization (default: 100).
    - `--output-dir`: Directory for plots and reports (default: `dashboard_outputs`).
    - `--db-file`: SQLite database file (default: `system_metrics.db`).
- **Strengths**:
  - Highly configurable for testing and automation.
  - Supports programmatic integration (e.g., CI/CD pipelines).
  - Ideal for collaborative or production environments.
- **Limitations**:
  - Slightly more complex due to `argparse` logic.
  - Requires understanding of command-line syntax.
- **Recommendation**:
  - `Updated_monitoring.py` is better for infrastructure testing and automation due to its support for varied use cases and flexibility, with configuration without modifying code.
  - `system_monitoring` is better for fixed scenarios or quick setups.

## Requirements
- Python 3.x
- Libraries: `psutil`, `plotly`, `pandas`, `sqlite3` (included in Python).
  ```bash
  pip install psutil plotly pandas
  ```

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd system_monitoring-system dashboard
   ```

3. Install dependencies:
   ```bash
   pip install psutil plotly pandas
   ```

## Implementation Details
- **Metrics**:
  - CPU usage (%).
  - Memory usage (%).
  - Network I/O (sent/received in KB/s).
- **Database**:
  - SQLite table (`metrics`) storing timestamped data).
- **Visualization**:
  - Real-time `plotly` plots with interactivity, saved as HTML.
- **GUI**:
  - `tkinter` interface for alerts and plot triggering (opens in browser).
- **Insights**:
  - Summary statistics (avg/max) and actionable warnings saved as TXT.
- **Output**:
  - Logs to a file.
  - Plots to `dashboard_outputs/dashboard_<timestamp>.html`.
  - Insights to `dashboard_outputs/insights_<timestamp>.txt`.

## Testing and Debugging
- **Reliability**:
  - Ensured consistent metric collection, storage, and reporting.
- **Debugging**:
  - Handles `KeyboardInterrupt`, file I/O, database errors, and threading issues.
  - Validates command-line inputs in `Updated_monitoring.py`.
- **Bottleneck Detection**:
  - Insights highlight high CPU (>threshold), memory (>90%), or network (>1 MB/s) usage).

## Future Improvements
- Add email or desktop notifications for alerts.
- Implement a web-based dashboard (e.g., with `dash`) for full Power BI-like interactivity).
- Add a database query interface for historical analysis.
- Support additional metrics (e.g., disk usage).

## Repository structure

```
system_monitoring.py
Updated_monitoring.py
metrics.log
system_metrics.db
dashboard_outputs/
├── dashboard_<timestamp>.html
├── insights_<timestamp>.txt
.gitignore
README.md
```

