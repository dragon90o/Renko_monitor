# 🧱 Monitor Renko - Interfaz Gráfica

## ¿Qué es esto?
Un monitor en tiempo real que te ayuda a identificar reversiones de tendencia en Forex usando **ladrillos Renko**.

### ¿Cómo funciona?
Los **ladrillos Renko** ignoran el tiempo y solo se forman cuando el precio se mueve una cantidad específica (ej: 10 pips):
- 🟢 **Ladrillo Verde**: El precio subió 10 pips
- 🔴 **Ladrillo Rojo**: El precio bajó 10 pips

**Señal de Reversión**: Cuando aparecen 3+ ladrillos del color opuesto consecutivos
- Ejemplo: Si tenías 5 verdes 🟢🟢🟢🟢🟢 y aparecen 3 rojos 🔴🔴🔴 → **¡ALERTA! Posible reversión bajista**

## Lo que verás en la pantalla

### 💰 Información de Precio
- **Precio Actual**: Precio en vivo del mercado
- **Precio Ladrillo**: Precio donde se forma el próximo ladrillo
- **Distancia**: Cuántos pips faltan para el siguiente ladrillo (ej: "3.8 pips de 10 pips")

### 📊 Estado de Tendencia
Indica qué tan fuerte es la tendencia actual:
- 🚀 **ALCISTA FUERTE** (5+ verdes) → Sigue comprando
- 📈 **ALCISTA** (3-4 verdes) → Tendencia alcista confirmada
- 📉 **BAJISTA** (3-4 rojos) → Tendencia bajista confirmada
- 💥 **BAJISTA FUERTE** (5+ rojos) → Sigue vendiendo
- ⚪ **NEUTRAL** → Sin tendencia clara, espera

### 💡 Recomendaciones Automáticas
Te dice qué hacer según la tendencia:
- **Tendencia alcista**: Mantén BUYs, NO abras SELLs
- **Tendencia bajista**: Mantén SELLs, NO abras BUYs
- **Sin tendencia**: Espera, no hagas nada

### 🚨 Alertas de Reversión
Cuando detecta una reversión (3+ ladrillos opuestos):
- Muestra alerta grande en pantalla
- Suena un beep
- Te dice qué posiciones considerar cerrar

## Cómo Usar (Paso a Paso)

### 1️⃣ Preparar el Entorno
```bash
# Ir al directorio
cd C:\Users\dravv\Scripts\Python-files\renko_monitor

# Activar entorno virtual
venv\Scripts\activate
```

### 2️⃣ Abrir MetaTrader 5
- Abre MT5 y conéctate a tu cuenta (demo o real)
- Déjalo abierto en segundo plano

### 3️⃣ Iniciar el Monitor
```bash
python renko_monitor_gui.py
```

### 4️⃣ Configurar y Monitorear
1. **Selecciona el par de divisas** (EURUSD, GBPUSD, etc.)
2. **Selecciona el tamaño de ladrillo** (10 pips recomendado para empezar)
3. Haz clic en **▶ INICIAR MONITOR**
4. ¡Listo! Observa los ladrillos y espera las alertas

### 5️⃣ Detener
- Botón **⏸ DETENER** o presiona **Ctrl+C**

## ⚙️ Configuración de Tamaño de Ladrillo

Elige según tu estilo de trading:
- **5 pips**: Scalping (entradas/salidas rápidas)
- **10 pips**: Intraday (recomendado para empezar)
- **20-30 pips**: Swing trading (posiciones de horas/días)
- **50 pips**: Position trading (posiciones largas)

## 🔧 Solución de Problemas

| Error | Solución |
|-------|----------|
| "No se pudo conectar a MT5" | Abre MT5 y conéctate a tu cuenta |
| "No se pudo obtener precio" | Verifica que el símbolo existe en tu broker |
| "Symbol not found" | Algunos brokers usan nombres diferentes (ej: EURUSD.i) |
| La ventana se ve cortada | Redimensiona la ventana o usa pantalla más grande |

## 📋 Requisitos
- ✅ Windows (MT5 solo funciona en Windows)
- ✅ Python 3.11.7
- ✅ MetaTrader 5 instalado
- ✅ Cuenta MT5 (demo funciona perfectamente)

## 🎯 Características Adicionales
- **Interfaz Responsiva**: Se adapta a diferentes tamaños de pantalla
- **Layout Adaptativo**: En pantallas pequeñas, los paneles se apilan verticalmente
- **Actualización en Tiempo Real**: Cada 1 segundo
- **Multi-Divisa**: 8 pares de divisas disponibles
