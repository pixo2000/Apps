# Ping Monitor

A Python program that monitors ping times to multiple targets using separate threads and saves the results for analysis.

## Features

- **Multi-threaded monitoring**: Pings multiple targets simultaneously using separate threads
- **Continuous monitoring**: Runs indefinitely until stopped with Ctrl+C
- **Data logging**: Saves all ping results to a CSV file with timestamps
- **Real-time feedback**: Shows ping results in the console as they happen
- **Statistics**: Displays recent statistics when the program exits
- **Graph generation**: Includes a separate script to create visualizations from the collected data

## Default Targets

- **Fritz Box**: 192.168.1.1 (common router IP)
- **Frankfurt Server**: 8.8.8.8 (Google DNS - you can change this to a specific Frankfurt server)

## Usage

### Running the Ping Monitor

```bash
python main.py
```

The program will:
- Start pinging both targets every 5 seconds
- Display real-time results in the console
- Save all results to `ping_results.csv`
- Show statistics for the last 10 minutes when you stop it (Ctrl+C)

### Creating Graphs

1. First install the optional dependencies:
```bash
pip install -r requirements.txt
```

2. Run the graph generator:
```bash
python create_graphs.py
```

This will create a comprehensive analysis with:
- Time series plots of ping times
- Box plots comparing distributions
- Success rate over time
- Histograms of ping times

## Configuration

You can modify the targets in `main.py`:

```python
targets = {
    "Fritz_Box": "192.168.1.1",
    "Frankfurt_Server": "your-server-ip-here",
    # Add more targets as needed
}
```

### Other configurable options:
- `ping_interval`: Time between pings (default: 5 seconds)
- `output_file`: CSV filename (default: "ping_results.csv")

## CSV Output Format

The CSV file contains the following columns:
- `timestamp`: When the ping was performed
- `target`: Name of the target (Fritz_Box, Frankfurt_Server, etc.)
- `ip_address`: IP address that was pinged
- `ping_time_ms`: Response time in milliseconds (or "N/A" if failed)
- `status`: "success" or "failed"

## Requirements

- Python 3.6+
- Windows (uses Windows ping command syntax)
- Optional: matplotlib and pandas for graph generation

## Notes

- The program uses the Windows `ping` command internally
- Each target is monitored in its own thread for parallel execution
- Data is continuously saved to prevent loss if the program is interrupted
- The program handles German and English ping command outputs
