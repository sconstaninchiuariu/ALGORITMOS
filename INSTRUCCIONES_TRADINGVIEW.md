# EUR/USD SMC Strategy — Guía de Configuración TradingView

## 🧠 Estrategia Detectada del Backtest

Basado en el análisis de 400+ trades en FXReplay, tu estrategia sigue la metodología **Smart Money Concepts (SMC / ICT)**:

| Parámetro | Valor |
|-----------|-------|
| Par | EUR/USD |
| Riesgo por trade | 1% del capital |
| RR objetivo | 2:1 (ganar 2R, perder 1R) |
| Sesiones | Londres (03:00–07:00 UTC) + NY (08:00–12:00 UTC) |
| SL típico | 3–15 pips |
| Entradas | FVG 1H, FVG 4H, FVG Daily, PDH/PDL, Asia Range, Swing H/L |
| Resultado global | +139% en ~400 trades |

### Distribución de resultados observada:
- **Ganador (+2R)**: ~55% de trades
- **Perdedor (−1R)**: ~35% de trades
- **Breakeven (0R)**: ~10% de trades
- **Win rate aproximado**: ~60%

---

## 📥 Instalación en TradingView

### Paso 1 — Abrir Pine Editor
1. Entra en TradingView con tu cuenta
2. Abre un gráfico de **EUR/USD**
3. Cambia el timeframe a **15M** o **1H** (recomendado para ver FVGs)
4. En la barra inferior, haz clic en **"Pine Editor"**

### Paso 2 — Pegar el código
1. Borra todo el contenido del editor
2. Copia y pega el contenido de `eurusd_smc_strategy.pine`
3. Haz clic en **"Add to chart"**

### Paso 3 — Configuración recomendada

Ve a **Settings** del indicador (⚙️ en el gráfico):

**Session Filters:**
- London Start Hour: `3`
- London End Hour: `12`
- NY Start Hour: `13`
- NY End Hour: `20`
- Trade London Session: ✅
- Trade NY Session: ✅

**Fair Value Gaps:**
- Show 1H FVG Zones: ✅
- Show 4H FVG Zones: ✅
- Show Daily FVG Zones: ✅
- Min FVG Size: `0.0003` (3 pips mínimo)
- Max FVG Age: `50` barras

**Key Levels:**
- Show Previous Day H/L: ✅
- Show Asia Range: ✅
- Show Swing Highs/Lows: ✅
- Swing Lookback: `10`

**Risk Management:**
- Risk per Trade: `1.0` (%)
- Risk:Reward Ratio: `2.0`
- SL Buffer: `0.0002` (2 pips extra sobre el FVG)
- Max SL Size: `0.0020` (20 pips máximo)
- Min SL Size: `0.0003` (3 pips mínimo)

**Entry Filters:**
- Require candle to close inside FVG: ✅
- Max Trades per Day: `3`

---

## 📊 Cómo usar el script manualmente

El script genera **señales automáticas** cuando:

### SHORT (Venta):
1. Precio sube hacia una zona FVG bajista (zona roja)
2. La vela **cierra dentro del FVG**
3. Estamos en sesión London o NY
4. El SL está entre 3–20 pips
5. TP = SL × 2 (ratio 2:1)

### LONG (Compra):
1. Precio baja hacia una zona FVG alcista (zona verde)
2. La vela **cierra dentro del FVG**
3. Estamos en sesión London o NY
4. El SL está entre 3–20 pips
5. TP = SL × 2 (ratio 2:1)

---

## 🔔 Configurar Alertas

Para recibir notificaciones en tiempo real:
1. Clic derecho en el gráfico → **"Add Alert"**
2. Condition: **"SMC-EURUSD"**
3. Selecciona **"SMC SHORT Signal - EURUSD"** o **"SMC LONG Signal - EURUSD"**
4. Notificación: Email + App TradingView

---

## 🎨 Colores del gráfico

| Color | Significado |
|-------|-------------|
| 🔴 Rojo (zona) | FVG bajista (Supply Zone) — zona para vender |
| 🟢 Verde (zona) | FVG alcista (Demand Zone) — zona para comprar |
| 🟠 Naranja (línea punteada) | Previous Day High/Low |
| 🟣 Morado (línea punteada) | Asia Session High/Low |
| 🔵 Fondo azul | Sesión Londres activa |
| 🟡 Fondo amarillo | Sesión NY activa |
| ▼ Triángulo rojo | Swing High detectado |
| ▲ Triángulo verde | Swing Low detectado |

---

## ⚠️ Notas importantes

1. **Timeframe óptimo**: Usa el script en **1H o 15M**. Los FVGs se detectan en el timeframe actual.
2. **Contexto mayor**: Antes de entrar, revisa el gráfico **4H y Daily** para confirmar la dirección macro.
3. **Noticias**: Evita operar 30 minutos antes y después de noticias de alto impacto (NFP, FOMC, BCE).
4. **Backtesting**: Usa la pestaña "Strategy Tester" de TradingView para ver los resultados del script en histórico.
5. **No es financiero**: Este script automatiza patrones observados en tu backtest. El rendimiento pasado no garantiza resultados futuros.

---

## 🚀 Próximos pasos — MetaTrader 5 (EA)

Una vez validado el script en TradingView, migraremos la estrategia a un **Expert Advisor (EA) para MT5** que ejecutará las órdenes automáticamente con:
- Conexión directa al broker
- Ejecución automática sin necesidad de estar en el ordenador
- Gestión de riesgo dinámica
- Log de trades para análisis continuo

---

## 📈 Tags de estrategia detectados en tu backtest

| Tag FXReplay | Concepto SMC |
|-------------|--------------|
| `IMBALANCE-1H` | Fair Value Gap en gráfico 1H |
| `IMBALANCE-4H` | Fair Value Gap en gráfico 4H |
| `IMBALANCE-DAILY` | Fair Value Gap en gráfico Daily |
| `MAXIMOS/MINIMOS` | Swing Highs / Swing Lows |
| `PDL` | Previous Day Low |
| `ASIA` | Niveles del rango asiático |
