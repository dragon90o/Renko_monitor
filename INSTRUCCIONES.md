# 🧱 Renko Monitor - Graphical Interface

## What is this?
A real-time monitor that helps you identify trend reversals in Forex using **Renko bricks**.

### How does it work?
**Renko bricks** ignore time and only form when the price moves a specific amount (e.g., 10 pips):
- 🟢 **Green Brick**: Price went up 10 pips
- 🔴 **Red Brick**: Price went down 10 pips

**Reversal Signal**: When 3+ consecutive bricks of the opposite color appear
- Example: If you had 5 greens 🟢🟢🟢🟢🟢 and 3 reds appear 🔴🔴🔴 → **ALERT! Possible bearish reversal**

## What you'll see on screen

### 💰 Price Information
- **Current Price**: Live market price
- **Brick Price**: Price where the next brick forms
- **Distance**: How many pips until the next brick (e.g., "3.8 pips of 10 pips")

### 📊 Trend Status
Indicates how strong the current trend is:
- 🚀 **STRONG BULLISH** (5+ greens) → Keep buying
- 📈 **BULLISH** (3-4 greens) → Confirmed bullish trend
- 📉 **BEARISH** (3-4 reds) → Confirmed bearish trend
- 💥 **STRONG BEARISH** (5+ reds) → Keep selling
- ⚪ **NEUTRAL** → No clear trend, wait

### 💡 Automatic Recommendations
Tells you what to do based on the trend:
- **Bullish trend**: Hold BUYs, DON'T open SELLs
- **Bearish trend**: Hold SELLs, DON'T open BUYs
- **No trend**: Wait, do nothing

### 🚨 Reversal Alerts
When it detects a reversal (3+ opposite bricks):
- Shows large alert on screen
- Plays a beep sound
- Tells you which positions to consider closing

## How to Use (Step by Step)

### 1️⃣ Prepare the Environment
```bash
# Go to directory
cd C:\Users\dravv\Scripts\Python-files\renko_monitor

# Activate virtual environment
venv\Scripts\activate
```

### 2️⃣ Open MetaTrader 5
- Open MT5 and connect to your account (demo or real)
- Leave it running in the background

### 3️⃣ Start the Monitor
```bash
python renko_monitor_gui.py
```

### 4️⃣ Configure and Monitor
1. **Select the currency pair** (EURUSD, GBPUSD, etc.)
2. **Select the brick size** (10 pips recommended to start)
3. Click **▶ START MONITOR**
4. Done! Watch the bricks and wait for alerts

### 5️⃣ Stop
- **⏸ STOP** button or press **Ctrl+C**

## ⚙️ Brick Size Configuration

Choose according to your trading style:
- **5 pips**: Scalping (quick entries/exits)
- **10 pips**: Intraday (recommended to start)
- **20-30 pips**: Swing trading (positions for hours/days)
- **50 pips**: Position trading (long positions)

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "Could not connect to MT5" | Open MT5 and connect to your account |
| "Could not get price" | Verify the symbol exists with your broker |
| "Symbol not found" | Some brokers use different names (e.g., EURUSD.i) |
| Window looks cut off | Resize the window or use a larger screen |

## 📋 Requirements
- ✅ Windows (MT5 only works on Windows)
- ✅ Python 3.11.7
- ✅ MetaTrader 5 installed
- ✅ MT5 account (demo works perfectly)

## 🎯 Additional Features
- **Responsive Interface**: Adapts to different screen sizes
- **Adaptive Layout**: On small screens, panels stack vertically
- **Real-Time Updates**: Every 1 second
- **Multi-Currency**: 8 currency pairs available
