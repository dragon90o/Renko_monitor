# Renko Live Monitor

Monitor de gráficos Renko en tiempo real para trading de Forex (EUR/USD).

## Características

- Actualización automática cada segundo
- Alertas sonoras de reversión
- Visualización clara de tendencia actual
- Histórico de últimos 20 ladrillos
- Detección automática de cambios de tendencia

## Requisitos Previos

### 1. MetaTrader 5

Debes tener **MetaTrader 5** instalado y en ejecución:

1. Descarga MetaTrader 5 desde [aquí](https://www.metatrader5.com/es/download)
2. Instala y configura tu cuenta de trading
3. **IMPORTANTE**: Mantén MT5 abierto mientras ejecutas el monitor
4. Asegúrate de que el símbolo EUR/USD esté disponible en tu broker

### 2. Python

Requiere Python 3.8 o superior.

## Instalación

### Paso 1: Instalar dependencias de Python

Abre una terminal en este directorio y ejecuta:

```bash
pip install -r requirements.txt
```

Esto instalará:
- `MetaTrader5`: Librería para conectarse a MT5 y obtener datos en tiempo real
- `pandas`: Procesamiento de datos
- `colorama`: Colores en la terminal
- `playsound`: Alertas sonoras (opcional)

### Paso 2: Verificar instalación

Verifica que MetaTrader 5 esté instalado correctamente:

```python
import MetaTrader5 as mt5
print(mt5.__version__)
```

## Uso

### Ejecutar el monitor:

```bash
python renko_live_monitor.py
```

### Configuración

Puedes ajustar los parámetros en el código:

```python
monitor = RenkoLiveMonitor(
    symbol="EURUSD",        # Par de divisas
    brick_size_pips=10      # Tamaño del ladrillo en pips
)
```

### Detener el monitor

Presiona `Ctrl+C` para detener el monitor de forma segura.

## Notas Importantes

1. **MT5 debe estar abierto**: El monitor no funcionará si MetaTrader 5 no está ejecutándose
2. **Conexión a internet**: Necesitas conexión estable para recibir datos en tiempo real
3. **Cuenta de trading**: Aunque solo lee datos, necesitas una cuenta (demo o real) configurada en MT5

## Solución de Problemas

### Error: "No se pudo conectar a MT5"
- Verifica que MetaTrader 5 esté abierto
- Asegúrate de tener una cuenta configurada (demo o real)
- Reinicia MT5 e intenta de nuevo

### Error: "No se pudo obtener precio"
- Verifica que el símbolo EURUSD esté disponible en tu broker
- Comprueba tu conexión a internet
- Verifica que el mercado esté abierto (Forex está cerrado los fines de semana)

## Contacto

Si tienes problemas o sugerencias, por favor crea un issue.
