"""
🧱 LIVE RENKO MONITOR - GRAPHICAL INTERFACE
Professional Renko reversal monitor with modern interface
"""

import customtkinter as ctk
import MetaTrader5 as mt5
from datetime import datetime
import threading
import time
from tkinter import messagebox
import winsound


class RenkoMonitorGUI:
    def __init__(self):
        # Configuración de CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main window
        self.root = ctk.CTk()
        self.root.title("🧱 Live Renko Monitor")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate window size (70% of screen)
        window_width = min(1100, int(screen_width * 0.7))
        window_height = min(750, int(screen_height * 0.8))

        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)  # Minimum size

        # Monitor variables
        self.symbol = "EURUSD"
        self.brick_size_pips = 10
        self.brick_size = self.brick_size_pips / 10000
        self.bricks = []
        self.current_brick_price = None
        self.last_alert_time = None
        self.monitoring = False
        self.monitor_thread = None
        self.mt5_connected = False

        # UI variables
        self.info_container = None
        self.trend_frame = None
        self.rec_frame = None
        self.current_layout = "horizontal"

        # Create interface
        self.create_widgets()

        # Configure resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self):
        """Create all interface widgets"""

        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#1a1a1a")
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🧱 LIVE RENKO MONITOR",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # ========== CONTROL BUTTONS ==========
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 15))

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ START MONITOR",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.start_monitoring
        )
        self.start_button.pack(side="left", padx=10)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏸ STOP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)

        # ========== CONFIGURATION PANEL ==========
        config_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        config_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Configuration title
        ctk.CTkLabel(
            config_frame,
            text="⚙️ CONFIGURATION",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Inner frame for controls
        controls_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        controls_frame.pack(pady=(5, 15))

        # Currency selector
        ctk.CTkLabel(
            controls_frame,
            text="Currency Pair:",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.symbol_var = ctk.StringVar(value="EURUSD")
        symbol_combo = ctk.CTkComboBox(
            controls_frame,
            values=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY", "EURGBP"],
            variable=self.symbol_var,
            width=150,
            state="readonly"
        )
        symbol_combo.grid(row=0, column=1, padx=10, pady=5)

        # Brick size selector
        ctk.CTkLabel(
            controls_frame,
            text="Brick Size (pips):",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.brick_size_var = ctk.StringVar(value="10")
        brick_size_combo = ctk.CTkComboBox(
            controls_frame,
            values=["5", "10", "15", "20", "30", "50"],
            variable=self.brick_size_var,
            width=100,
            state="readonly"
        )
        brick_size_combo.grid(row=0, column=3, padx=10, pady=5)

        # ========== SEPARATOR ==========
        separator1 = ctk.CTkFrame(self.root, height=2, fg_color="gray")
        separator1.pack(fill="x", padx=40, pady=5)

        # ========== PRICE PANEL ==========
        price_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        price_frame.pack(fill="x", padx=20, pady=8)

        # 3-column grid
        price_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Current price
        price_box1 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box1,
            text="💰 CURRENT PRICE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(pady=(10, 2))

        self.current_price_label = ctk.CTkLabel(
            price_box1,
            text="-",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFA500"
        )
        self.current_price_label.pack(pady=(2, 10))

        # Brick price
        price_box2 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box2,
            text="🎯 BRICK PRICE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(pady=(10, 2))

        self.brick_price_label = ctk.CTkLabel(
            price_box2,
            text="-",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00CED1"
        )
        self.brick_price_label.pack(pady=(2, 10))

        # Distance
        price_box3 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box3,
            text="📏 DISTANCE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(pady=(10, 2))

        self.distance_label = ctk.CTkLabel(
            price_box3,
            text="- pips de - pips",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFD700"
        )
        self.distance_label.pack(pady=(2, 10))

        # ========== SEPARATOR ==========
        separator2 = ctk.CTkFrame(self.root, height=2, fg_color="gray")
        separator2.pack(fill="x", padx=40, pady=5)

        # ========== CONTAINER FOR TREND AND RECOMMENDATIONS ==========
        self.info_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.info_container.pack(fill="both", expand=False, padx=20, pady=8)
        self.info_container.grid_columnconfigure(0, weight=1, minsize=400)
        self.info_container.grid_columnconfigure(1, weight=1, minsize=400)
        self.info_container.grid_rowconfigure(0, weight=1)

        # ========== TREND PANEL (LEFT) ==========
        self.trend_frame = ctk.CTkFrame(self.info_container, fg_color="#2b2b2b")
        self.trend_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        ctk.CTkLabel(
            self.trend_frame,
            text="📊 TREND STATUS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Frame for emoji and text
        trend_content = ctk.CTkFrame(self.trend_frame, fg_color="#1a1a1a")
        trend_content.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        self.trend_emoji_label = ctk.CTkLabel(
            trend_content,
            text="⚪",
            font=ctk.CTkFont(size=32)
        )
        self.trend_emoji_label.pack(pady=(8, 3))

        self.trend_label = ctk.CTkLabel(
            trend_content,
            text="NEUTRAL / NO TREND",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.trend_label.pack(pady=2)

        self.trend_count_label = ctk.CTkLabel(
            trend_content,
            text="Consecutive bricks: 0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.trend_count_label.pack(pady=(2, 8))

        # ========== RECOMMENDATIONS PANEL (RIGHT) ==========
        self.rec_frame = ctk.CTkFrame(self.info_container, fg_color="#2b2b2b")
        self.rec_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        ctk.CTkLabel(
            self.rec_frame,
            text="💡 TRADING RECOMMENDATIONS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.rec_textbox = ctk.CTkTextbox(
            self.rec_frame,
            height=120,
            font=ctk.CTkFont(size=11),
            fg_color="#1a1a1a"
        )
        self.rec_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        self.rec_textbox.insert("1.0", "   ⚪ No clear trend - Wait\n   ⚪ Don't take new positions")
        self.rec_textbox.configure(state="disabled")

        # ========== BRICKS PANEL ==========
        bricks_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        bricks_frame.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            bricks_frame,
            text="📜 LAST 20 BRICKS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Textbox to display bricks
        self.bricks_display = ctk.CTkTextbox(
            bricks_frame,
            height=60,
            font=ctk.CTkFont(size=20),
            fg_color="#1a1a1a",
            wrap="none"
        )
        self.bricks_display.pack(fill="x", padx=20, pady=(5, 10))
        self.bricks_display.insert("1.0", "⚪")
        self.bricks_display.configure(state="disabled")

        # ========== ALERT PANEL (hidden by default) ==========
        self.alert_frame = ctk.CTkFrame(self.root, fg_color="#dc3545")
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.alert_label.pack(pady=10)

        # ========== STATUS PANEL ==========
        status_container = ctk.CTkFrame(self.root, fg_color="#1a1a1a")
        status_container.pack(fill="x", padx=20, pady=(10, 15))

        status_frame = ctk.CTkFrame(status_container, fg_color="transparent")
        status_frame.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Disconnected",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10)

        ctk.CTkLabel(
            status_frame,
            text="•",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left")

        self.time_label = ctk.CTkLabel(
            status_frame,
            text="🕐 Last update: -",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.time_label.pack(side="left", padx=10)

    def connect_mt5(self):
        """Connect to MetaTrader 5"""
        if not mt5.initialize():
            messagebox.showerror(
                "Connection Error",
                "Could not connect to MT5.\n\nMake sure MetaTrader 5 is open and running."
            )
            return False

        self.mt5_connected = True
        self.status_label.configure(text="🟢 Connected to MT5", text_color="#28a745")
        return True

    def get_current_price(self):
        """Get current market price"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return tick.bid

    def initialize_renko(self):
        """Initialize first brick from current price"""
        price = self.get_current_price()
        if price is None:
            return False

        self.current_brick_price = round(price / self.brick_size) * self.brick_size

        # Create first neutral brick
        self.bricks.append({
            'price': self.current_brick_price,
            'direction': 0,
            'time': datetime.now()
        })

        return True

    def update_renko(self, current_price):
        """Update Renko bricks with current price"""
        new_bricks = []

        while abs(current_price - self.current_brick_price) >= self.brick_size:
            if current_price > self.current_brick_price:
                direction = 1
                new_price = self.current_brick_price + self.brick_size
                self.current_brick_price = new_price
            else:
                direction = -1
                new_price = self.current_brick_price - self.brick_size
                self.current_brick_price = new_price

            new_brick = {
                'price': new_price,
                'direction': direction,
                'time': datetime.now()
            }

            self.bricks.append(new_brick)
            new_bricks.append(new_brick)

        return new_bricks

    def get_trend_status(self):
        """Determine current trend"""
        if len(self.bricks) < 1:
            return 'NEUTRAL', 0

        count = 0
        last_direction = self.bricks[-1]['direction']

        for brick in reversed(self.bricks):
            if brick['direction'] == last_direction:
                count += 1
            else:
                break

        if last_direction == 1:
            if count >= 5:
                return 'STRONG_UP', count
            elif count >= 3:
                return 'UP', count
            else:
                return 'WEAK_UP', count
        elif last_direction == -1:
            if count >= 5:
                return 'STRONG_DOWN', count
            elif count >= 3:
                return 'DOWN', count
            else:
                return 'WEAK_DOWN', count
        else:
            return 'NEUTRAL', count

    def check_reversal(self):
        """Detect trend reversal"""
        if len(self.bricks) < 4:
            return False, 0, 0

        recent = self.bricks[-4:]
        old_direction = recent[0]['direction']
        new_direction = recent[-1]['direction']

        if old_direction != new_direction and new_direction != 0:
            count = 0
            for brick in reversed(self.bricks):
                if brick['direction'] == new_direction:
                    count += 1
                else:
                    break

            if count >= 3:
                return True, new_direction, count

        return False, 0, 0

    def update_display(self):
        """Update all visual elements"""
        try:
            current_price = self.get_current_price()
            if current_price is None:
                return

            # Update current price
            self.current_price_label.configure(text=f"{current_price:.5f}")

            # Update brick price
            if self.current_brick_price:
                self.brick_price_label.configure(text=f"{self.current_brick_price:.5f}")

                # Calculate and display distance
                distance = abs(current_price - self.current_brick_price)
                distance_pips = distance * 10000
                self.distance_label.configure(
                    text=f"{distance_pips:.1f} pips of {self.brick_size_pips} pips"
                )

            # Update trend
            trend, count = self.get_trend_status()
            self.update_trend_display(trend, count)

            # Update bricks
            self.update_bricks_display()

            # Update recommendations
            self.update_recommendations(trend)

            # Update time
            now = datetime.now().strftime("%H:%M:%S")
            self.time_label.configure(text=f"🕐 Last update: {now}")

        except Exception as e:
            print(f"Error en update_display: {e}")

    def update_trend_display(self, trend, count):
        """Update trend visualization"""
        trend_config = {
            'STRONG_UP': ('🚀', 'STRONG BULLISH TREND', '#00ff00'),
            'UP': ('📈', 'BULLISH TREND', '#90EE90'),
            'WEAK_UP': ('↗️', 'WEAK BULLISH', '#FFD700'),
            'NEUTRAL': ('⚪', 'NEUTRAL / NO TREND', 'white'),
            'WEAK_DOWN': ('↘️', 'WEAK BEARISH', '#FFD700'),
            'DOWN': ('📉', 'BEARISH TREND', '#FF6347'),
            'STRONG_DOWN': ('💥', 'STRONG BEARISH TREND', '#ff0000')
        }

        emoji, label, color = trend_config.get(trend, ('⚪', 'NEUTRAL', 'white'))

        self.trend_emoji_label.configure(text=emoji)
        self.trend_label.configure(text=label, text_color=color)
        self.trend_count_label.configure(text=f"📊 Consecutive bricks: {count}")

    def update_bricks_display(self):
        """Update bricks visualization"""
        if not self.bricks:
            return

        # Get last 20 bricks
        recent_bricks = self.bricks[-20:] if len(self.bricks) > 20 else self.bricks

        brick_str = "   "
        for brick in recent_bricks:
            if brick['direction'] == 1:
                brick_str += "🟢"
            elif brick['direction'] == -1:
                brick_str += "🔴"
            else:
                brick_str += "⚪"

        self.bricks_display.configure(state="normal")
        self.bricks_display.delete("1.0", "end")
        self.bricks_display.insert("1.0", brick_str)
        self.bricks_display.configure(state="disabled")

    def update_recommendations(self, trend):
        """Update trading recommendations"""
        rec_text = ""

        if trend in ['STRONG_UP', 'UP']:
            rec_text = "   ✅ Safe to hold BUY positions\n"
            rec_text += "   ✅ Look for BUY entries on pullbacks\n"
            rec_text += "   ❌ DON'T open SELL positions (against trend)"
        elif trend in ['STRONG_DOWN', 'DOWN']:
            rec_text = "   ✅ Safe to hold SELL positions\n"
            rec_text += "   ✅ Look for SELL entries on bounces\n"
            rec_text += "   ❌ DON'T open BUY positions (against trend)"
        elif trend in ['WEAK_UP', 'WEAK_DOWN']:
            rec_text = "   ⚠️ Weak trend - Caution\n"
            rec_text += "   ⚠️ Adjust trailing stops closer\n"
            rec_text += "   ⚠️ Possible consolidation or reversal"
        else:
            rec_text = "   ⚪ No clear trend - Wait\n"
            rec_text += "   ⚪ Don't take new positions"

        self.rec_textbox.configure(state="normal")
        self.rec_textbox.delete("1.0", "end")
        self.rec_textbox.insert("1.0", rec_text)
        self.rec_textbox.configure(state="disabled")

    def show_alert(self, direction, count):
        """Show reversal alert"""
        if direction == 1:
            msg = f"🚨 REVERSAL ALERT!\n📈 CHANGED TO BULLISH - {count} green bricks\n💡 Consider CLOSING SELL positions and look for BUY"
            color = "#28a745"
        else:
            msg = f"🚨 REVERSAL ALERT!\n📉 CHANGED TO BEARISH - {count} red bricks\n💡 Consider CLOSING BUY positions and look for SELL"
            color = "#dc3545"

        self.alert_frame.configure(fg_color=color)
        self.alert_label.configure(text=msg)

        # Insert before control panel
        children = list(self.root.winfo_children())
        control_index = len(children) - 1
        self.alert_frame.pack(fill="x", padx=20, pady=10, before=children[control_index])

        # Play sound
        try:
            winsound.Beep(1000, 500)
        except:
            pass

        # Hide alert after 5 seconds
        self.root.after(5000, lambda: self.alert_frame.pack_forget())

    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                current_price = self.get_current_price()
                if current_price is None:
                    time.sleep(1)
                    continue

                # Update Renko
                new_bricks = self.update_renko(current_price)

                # Check reversal
                if new_bricks:
                    is_reversal, direction, count = self.check_reversal()

                    if is_reversal:
                        now = datetime.now()
                        if self.last_alert_time is None or (now - self.last_alert_time).seconds > 30:
                            self.last_alert_time = now
                            self.root.after(0, lambda d=direction, c=count: self.show_alert(d, c))

                # Update display
                self.root.after(0, self.update_display)

                time.sleep(1)

            except Exception as e:
                print(f"Error en monitoring loop: {e}")
                time.sleep(1)

    def start_monitoring(self):
        """Start monitoring"""
        # Get configuration
        self.symbol = self.symbol_var.get()
        self.brick_size_pips = int(self.brick_size_var.get())
        self.brick_size = self.brick_size_pips / 10000

        # Reset data
        self.bricks = []
        self.current_brick_price = None
        self.last_alert_time = None

        # Connect to MT5
        if not self.mt5_connected:
            if not self.connect_mt5():
                return

        # Initialize Renko
        if not self.initialize_renko():
            messagebox.showerror("Error", f"Could not initialize Renko for {self.symbol}\n\nVerify that the symbol exists with your broker.")
            return

        # Update title
        self.root.title(f"🧱 Live Renko Monitor - {self.symbol}")

        # Update display immediately with initial values
        self.update_display()

        # Change button states
        self.monitoring = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="🟢 Monitoring...", text_color="#00ff00")

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="⏸️ Stopped", text_color="#FFD700")

    def on_window_resize(self, event):
        """Reorganize layout when window size changes"""
        if event.widget != self.root:
            return

        window_width = self.root.winfo_width()

        # If window is less than 1000px, change to vertical layout
        if window_width < 1000 and self.current_layout == "horizontal":
            self.current_layout = "vertical"
            self.reorganize_layout()
        # If window is greater than 1000px, change to horizontal layout
        elif window_width >= 1000 and self.current_layout == "vertical":
            self.current_layout = "horizontal"
            self.reorganize_layout()

    def reorganize_layout(self):
        """Reorganize panels according to current layout"""
        if not self.trend_frame or not self.rec_frame:
            return

        if self.current_layout == "vertical":
            # Vertical layout: panels stacked on top of each other
            self.trend_frame.grid_forget()
            self.rec_frame.grid_forget()

            self.trend_frame.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="nsew")
            self.rec_frame.grid(row=1, column=0, padx=0, pady=(5, 0), sticky="nsew")

            self.info_container.grid_rowconfigure(0, weight=1)
            self.info_container.grid_rowconfigure(1, weight=1)
            self.info_container.grid_columnconfigure(0, weight=1)
        else:
            # Horizontal layout: panels side by side
            self.trend_frame.grid_forget()
            self.rec_frame.grid_forget()

            self.trend_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
            self.rec_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

            self.info_container.grid_rowconfigure(0, weight=1)
            self.info_container.grid_columnconfigure(0, weight=1)
            self.info_container.grid_columnconfigure(1, weight=1)

    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        if self.mt5_connected:
            mt5.shutdown()
        self.root.destroy()

    def run(self):
        """Run application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = RenkoMonitorGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⏸️ Monitor stopped by user")
        print("✅ Closing application...")
        try:
            if app.monitoring:
                app.monitoring = False
            if app.mt5_connected:
                mt5.shutdown()
        except:
            pass
        print("✅ Application closed successfully\n")
