# Renko Live Monitor

Real-time Renko chart monitor for Forex trading (EUR/USD).

## Features

- Automatic updates every second
- Reversal sound alerts
- Clear visualization of current trend
- History of last 20 bricks
- Automatic trend change detection

## Prerequisites

### 1. MetaTrader 5

You must have **MetaTrader 5** installed and running:

1. Download MetaTrader 5 from [here](https://www.metatrader5.com/en/download)
2. Install and configure your trading account
3. **IMPORTANT**: Keep MT5 open while running the monitor
4. Make sure the EUR/USD symbol is available with your broker

### 2. Python

Requires Python 3.8 or higher.

## Installation

### Step 1: Install Python dependencies

Open a terminal in this directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `MetaTrader5`: Library to connect to MT5 and get real-time data
- `pandas`: Data processing
- `colorama`: Terminal colors
- `playsound`: Sound alerts (optional)

### Step 2: Verify installation

Verify that MetaTrader 5 is installed correctly:

```python
import MetaTrader5 as mt5
print(mt5.__version__)
```

## Usage

### Run the monitor:

```bash
python renko_monitor_gui.py
```

### Configuration

You can adjust the parameters in the code:

```python
monitor = RenkoLiveMonitor(
    symbol="EURUSD",        # Currency pair
    brick_size_pips=10      # Brick size in pips
)
```

### Stop the monitor

Press `Ctrl+C` to stop the monitor safely.

## Important Notes

1. **MT5 must be open**: The monitor will not work if MetaTrader 5 is not running
2. **Internet connection**: You need a stable connection to receive real-time data
3. **Trading account**: Although it only reads data, you need a configured account (demo or real) in MT5

## Troubleshooting

### Error: "Could not connect to MT5"
- Verify that MetaTrader 5 is open
- Make sure you have a configured account (demo or real)
- Restart MT5 and try again

### Error: "Could not get price"
- Verify that the EURUSD symbol is available with your broker
- Check your internet connection
- Verify that the market is open (Forex is closed on weekends)

## Contact

If you have problems or suggestions, please create an issue.
