"""
🧱 MONITOR RENKO EN VIVO - INTERFAZ GRÁFICA
Monitor profesional de reversiones Renko con interfaz moderna
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

        # Ventana principal
        self.root = ctk.CTk()
        self.root.title("🧱 Monitor Renko en Vivo")

        # Obtener tamaño de pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcular tamaño de ventana (70% de la pantalla)
        window_width = min(1100, int(screen_width * 0.7))
        window_height = min(750, int(screen_height * 0.8))

        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)  # Tamaño mínimo

        # Variables del monitor
        self.symbol = "EURUSD"
        self.brick_size_pips = 10
        self.brick_size = self.brick_size_pips / 10000
        self.bricks = []
        self.current_brick_price = None
        self.last_alert_time = None
        self.monitoring = False
        self.monitor_thread = None
        self.mt5_connected = False

        # Variables de UI
        self.info_container = None
        self.trend_frame = None
        self.rec_frame = None
        self.current_layout = "horizontal"

        # Crear interfaz
        self.create_widgets()

        # Configurar evento de redimensionamiento
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""

        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#1a1a1a")
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🧱 MONITOR RENKO EN VIVO",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # ========== BOTONES DE CONTROL ==========
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 15))

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ INICIAR MONITOR",
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
            text="⏸ DETENER",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)

        # ========== PANEL DE CONFIGURACIÓN ==========
        config_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        config_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Título de configuración
        ctk.CTkLabel(
            config_frame,
            text="⚙️ CONFIGURACIÓN",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Frame interno para controles
        controls_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        controls_frame.pack(pady=(5, 15))

        # Selector de Divisa
        ctk.CTkLabel(
            controls_frame,
            text="Par de Divisas:",
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

        # Selector de Tamaño de Ladrillo
        ctk.CTkLabel(
            controls_frame,
            text="Tamaño Ladrillo (pips):",
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

        # ========== SEPARADOR ==========
        separator1 = ctk.CTkFrame(self.root, height=2, fg_color="gray")
        separator1.pack(fill="x", padx=40, pady=5)

        # ========== PANEL DE PRECIOS ==========
        price_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        price_frame.pack(fill="x", padx=20, pady=8)

        # Grid de 3 columnas
        price_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Precio Actual
        price_box1 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box1,
            text="💰 PRECIO ACTUAL",
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

        # Precio Ladrillo
        price_box2 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box2,
            text="🎯 PRECIO LADRILLO",
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

        # Distancia
        price_box3 = ctk.CTkFrame(price_frame, fg_color="#1a1a1a")
        price_box3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            price_box3,
            text="📏 DISTANCIA",
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

        # ========== SEPARADOR ==========
        separator2 = ctk.CTkFrame(self.root, height=2, fg_color="gray")
        separator2.pack(fill="x", padx=40, pady=5)

        # ========== CONTENEDOR PARA TENDENCIA Y RECOMENDACIONES ==========
        self.info_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.info_container.pack(fill="both", expand=False, padx=20, pady=8)
        self.info_container.grid_columnconfigure(0, weight=1, minsize=400)
        self.info_container.grid_columnconfigure(1, weight=1, minsize=400)
        self.info_container.grid_rowconfigure(0, weight=1)

        # ========== PANEL DE TENDENCIA (IZQUIERDA) ==========
        self.trend_frame = ctk.CTkFrame(self.info_container, fg_color="#2b2b2b")
        self.trend_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        ctk.CTkLabel(
            self.trend_frame,
            text="📊 ESTADO DE TENDENCIA",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Frame para emoji y texto
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
            text="NEUTRAL / SIN TENDENCIA",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.trend_label.pack(pady=2)

        self.trend_count_label = ctk.CTkLabel(
            trend_content,
            text="Ladrillos consecutivos: 0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.trend_count_label.pack(pady=(2, 8))

        # ========== PANEL DE RECOMENDACIONES (DERECHA) ==========
        self.rec_frame = ctk.CTkFrame(self.info_container, fg_color="#2b2b2b")
        self.rec_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        ctk.CTkLabel(
            self.rec_frame,
            text="💡 RECOMENDACIONES DE TRADING",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.rec_textbox = ctk.CTkTextbox(
            self.rec_frame,
            height=120,
            font=ctk.CTkFont(size=11),
            fg_color="#1a1a1a"
        )
        self.rec_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        self.rec_textbox.insert("1.0", "   ⚪ Sin tendencia clara - Esperar\n   ⚪ No tomar nuevas posiciones")
        self.rec_textbox.configure(state="disabled")

        # ========== PANEL DE LADRILLOS ==========
        bricks_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        bricks_frame.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            bricks_frame,
            text="📜 ÚLTIMOS 20 LADRILLOS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Textbox para mostrar ladrillos
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

        # ========== PANEL DE ALERTAS (oculto por defecto) ==========
        self.alert_frame = ctk.CTkFrame(self.root, fg_color="#dc3545")
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.alert_label.pack(pady=10)

        # ========== PANEL DE STATUS ==========
        status_container = ctk.CTkFrame(self.root, fg_color="#1a1a1a")
        status_container.pack(fill="x", padx=20, pady=(10, 15))

        status_frame = ctk.CTkFrame(status_container, fg_color="transparent")
        status_frame.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Desconectado",
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
            text="🕐 Última actualización: -",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.time_label.pack(side="left", padx=10)

    def connect_mt5(self):
        """Conectar a MetaTrader 5"""
        if not mt5.initialize():
            messagebox.showerror(
                "Error de Conexión",
                "No se pudo conectar a MT5.\n\nAsegúrate de que MetaTrader 5 esté abierto y ejecutándose."
            )
            return False

        self.mt5_connected = True
        self.status_label.configure(text="🟢 Conectado a MT5", text_color="#28a745")
        return True

    def get_current_price(self):
        """Obtener precio actual del mercado"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return tick.bid

    def initialize_renko(self):
        """Inicializar primer ladrillo desde precio actual"""
        price = self.get_current_price()
        if price is None:
            return False

        self.current_brick_price = round(price / self.brick_size) * self.brick_size

        # Crear primer ladrillo neutral
        self.bricks.append({
            'price': self.current_brick_price,
            'direction': 0,
            'time': datetime.now()
        })

        return True

    def update_renko(self, current_price):
        """Actualizar ladrillos Renko con precio actual"""
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
        """Determinar tendencia actual"""
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
        """Detectar reversión de tendencia"""
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
        """Actualizar todos los elementos visuales"""
        try:
            current_price = self.get_current_price()
            if current_price is None:
                return

            # Actualizar precio actual
            self.current_price_label.configure(text=f"{current_price:.5f}")

            # Actualizar precio del ladrillo
            if self.current_brick_price:
                self.brick_price_label.configure(text=f"{self.current_brick_price:.5f}")

                # Calcular y mostrar distancia
                distance = abs(current_price - self.current_brick_price)
                distance_pips = distance * 10000
                self.distance_label.configure(
                    text=f"{distance_pips:.1f} pips de {self.brick_size_pips} pips"
                )

            # Actualizar tendencia
            trend, count = self.get_trend_status()
            self.update_trend_display(trend, count)

            # Actualizar ladrillos
            self.update_bricks_display()

            # Actualizar recomendaciones
            self.update_recommendations(trend)

            # Actualizar hora
            now = datetime.now().strftime("%H:%M:%S")
            self.time_label.configure(text=f"🕐 Última actualización: {now}")

        except Exception as e:
            print(f"Error en update_display: {e}")

    def update_trend_display(self, trend, count):
        """Actualizar visualización de tendencia"""
        trend_config = {
            'STRONG_UP': ('🚀', 'TENDENCIA ALCISTA FUERTE', '#00ff00'),
            'UP': ('📈', 'TENDENCIA ALCISTA', '#90EE90'),
            'WEAK_UP': ('↗️', 'ALCISTA DÉBIL', '#FFD700'),
            'NEUTRAL': ('⚪', 'NEUTRAL / SIN TENDENCIA', 'white'),
            'WEAK_DOWN': ('↘️', 'BAJISTA DÉBIL', '#FFD700'),
            'DOWN': ('📉', 'TENDENCIA BAJISTA', '#FF6347'),
            'STRONG_DOWN': ('💥', 'TENDENCIA BAJISTA FUERTE', '#ff0000')
        }

        emoji, label, color = trend_config.get(trend, ('⚪', 'NEUTRAL', 'white'))

        self.trend_emoji_label.configure(text=emoji)
        self.trend_label.configure(text=label, text_color=color)
        self.trend_count_label.configure(text=f"📊 Ladrillos consecutivos: {count}")

    def update_bricks_display(self):
        """Actualizar visualización de ladrillos"""
        if not self.bricks:
            return

        # Obtener últimos 20 ladrillos
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
        """Actualizar recomendaciones de trading"""
        rec_text = ""

        if trend in ['STRONG_UP', 'UP']:
            rec_text = "   ✅ Seguro mantener posiciones BUY\n"
            rec_text += "   ✅ Buscar entradas BUY en pullbacks\n"
            rec_text += "   ❌ NO abrir posiciones SELL (contra tendencia)"
        elif trend in ['STRONG_DOWN', 'DOWN']:
            rec_text = "   ✅ Seguro mantener posiciones SELL\n"
            rec_text += "   ✅ Buscar entradas SELL en rebotes\n"
            rec_text += "   ❌ NO abrir posiciones BUY (contra tendencia)"
        elif trend in ['WEAK_UP', 'WEAK_DOWN']:
            rec_text = "   ⚠️ Tendencia débil - Precaución\n"
            rec_text += "   ⚠️ Ajustar trailing stops más cerca\n"
            rec_text += "   ⚠️ Posible consolidación o reversión"
        else:
            rec_text = "   ⚪ Sin tendencia clara - Esperar\n"
            rec_text += "   ⚪ No tomar nuevas posiciones"

        self.rec_textbox.configure(state="normal")
        self.rec_textbox.delete("1.0", "end")
        self.rec_textbox.insert("1.0", rec_text)
        self.rec_textbox.configure(state="disabled")

    def show_alert(self, direction, count):
        """Mostrar alerta de reversión"""
        if direction == 1:
            msg = f"🚨 ¡ALERTA DE REVERSIÓN!\n📈 CAMBIO A ALCISTA - {count} ladrillos verdes\n💡 Considera CERRAR posiciones SELL y buscar BUY"
            color = "#28a745"
        else:
            msg = f"🚨 ¡ALERTA DE REVERSIÓN!\n📉 CAMBIO A BAJISTA - {count} ladrillos rojos\n💡 Considera CERRAR posiciones BUY y buscar SELL"
            color = "#dc3545"

        self.alert_frame.configure(fg_color=color)
        self.alert_label.configure(text=msg)

        # Insertar antes del panel de control
        children = list(self.root.winfo_children())
        control_index = len(children) - 1
        self.alert_frame.pack(fill="x", padx=20, pady=10, before=children[control_index])

        # Reproducir sonido
        try:
            winsound.Beep(1000, 500)
        except:
            pass

        # Ocultar alerta después de 5 segundos
        self.root.after(5000, lambda: self.alert_frame.pack_forget())

    def monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.monitoring:
            try:
                current_price = self.get_current_price()
                if current_price is None:
                    time.sleep(1)
                    continue

                # Actualizar Renko
                new_bricks = self.update_renko(current_price)

                # Verificar reversión
                if new_bricks:
                    is_reversal, direction, count = self.check_reversal()

                    if is_reversal:
                        now = datetime.now()
                        if self.last_alert_time is None or (now - self.last_alert_time).seconds > 30:
                            self.last_alert_time = now
                            self.root.after(0, lambda d=direction, c=count: self.show_alert(d, c))

                # Actualizar display
                self.root.after(0, self.update_display)

                time.sleep(1)

            except Exception as e:
                print(f"Error en monitoring loop: {e}")
                time.sleep(1)

    def start_monitoring(self):
        """Iniciar monitoreo"""
        # Obtener configuración
        self.symbol = self.symbol_var.get()
        self.brick_size_pips = int(self.brick_size_var.get())
        self.brick_size = self.brick_size_pips / 10000

        # Resetear datos
        self.bricks = []
        self.current_brick_price = None
        self.last_alert_time = None

        # Conectar a MT5
        if not self.mt5_connected:
            if not self.connect_mt5():
                return

        # Inicializar Renko
        if not self.initialize_renko():
            messagebox.showerror("Error", f"No se pudo inicializar Renko para {self.symbol}\n\nVerifica que el símbolo exista en tu broker.")
            return

        # Actualizar título
        self.root.title(f"🧱 Monitor Renko en Vivo - {self.symbol}")

        # Actualizar display inmediatamente con los valores iniciales
        self.update_display()

        # Cambiar estado de botones
        self.monitoring = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="🟢 Monitoreando...", text_color="#00ff00")

        # Iniciar thread de monitoreo
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="⏸️ Detenido", text_color="#FFD700")

    def on_window_resize(self, event):
        """Reorganizar layout cuando cambia el tamaño de la ventana"""
        if event.widget != self.root:
            return

        window_width = self.root.winfo_width()

        # Si la ventana es menor a 1000px, cambiar a layout vertical
        if window_width < 1000 and self.current_layout == "horizontal":
            self.current_layout = "vertical"
            self.reorganize_layout()
        # Si la ventana es mayor a 1000px, cambiar a layout horizontal
        elif window_width >= 1000 and self.current_layout == "vertical":
            self.current_layout = "horizontal"
            self.reorganize_layout()

    def reorganize_layout(self):
        """Reorganizar paneles según el layout actual"""
        if not self.trend_frame or not self.rec_frame:
            return

        if self.current_layout == "vertical":
            # Layout vertical: paneles uno arriba del otro
            self.trend_frame.grid_forget()
            self.rec_frame.grid_forget()

            self.trend_frame.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="nsew")
            self.rec_frame.grid(row=1, column=0, padx=0, pady=(5, 0), sticky="nsew")

            self.info_container.grid_rowconfigure(0, weight=1)
            self.info_container.grid_rowconfigure(1, weight=1)
            self.info_container.grid_columnconfigure(0, weight=1)
        else:
            # Layout horizontal: paneles lado a lado
            self.trend_frame.grid_forget()
            self.rec_frame.grid_forget()

            self.trend_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
            self.rec_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

            self.info_container.grid_rowconfigure(0, weight=1)
            self.info_container.grid_columnconfigure(0, weight=1)
            self.info_container.grid_columnconfigure(1, weight=1)

    def on_closing(self):
        """Manejar cierre de ventana"""
        self.monitoring = False
        if self.mt5_connected:
            mt5.shutdown()
        self.root.destroy()

    def run(self):
        """Ejecutar aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = RenkoMonitorGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⏸️ Monitor detenido por el usuario")
        print("✅ Cerrando aplicación...")
        try:
            if app.monitoring:
                app.monitoring = False
            if app.mt5_connected:
                mt5.shutdown()
        except:
            pass
        print("✅ Aplicación cerrada correctamente\n")
