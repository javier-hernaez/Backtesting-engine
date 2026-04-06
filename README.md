# Motor de Backtesting Orientado a Eventos (En Desarrollo)

Un robusto sistema de backtesting algorítmico desarrollado íntegramente en Python utilizando una **arquitectura puramente orientada a eventos**. Este motor ha sido diseñado específicamente para emular de manera fidedigna la latencia e interacciones del trading algorítmico en tiempo real e impedir el "look-ahead bias" (sesgo retrospectivo).

## 📌 Características Principales

- **Gestión Asíncrona:** Toda interacción dentro del software se agrupa en un Event Loop infinito alimentado por eventos aislados (`MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`).
- **Resiliencia al Look-Ahead Bias:** Imposibilidad arquitectónica de que la estrategia pueda conocer el futuro, debido a la inyección tick-a-tick o barra-a-barra simulando un reloj en vivo.
- **Desacoplamiento Estricto:** La Lógica de Estrategia (`Strategy`) y la Lógica de Gestión Monetaria (`Portfolio`) están 100% aisladas. La estrategia es "ciega" a las matemáticas de la cuenta real.
- **Cero Dependencias Circulares:** El bucle central es agnóstico a quién produce la señal. Permite migrar código fácilmente a ejecución en vivo (*Live Trading*) conectando el handler a un WebSocket de mercado en la fase de producción.

## ⚙️ Arquitectura del Sistema

El flujo de información se estructura en torno a una única tubería central (*Event Queue*), logrando el siguiente ciclo inmutable:

1. **`DataHandler`**: Inyecta continuamente al sistema los datos de mercado disponibles hasta el instante presente. Dispara `MarketEvent`.
2. **`Strategy`**: Escucha el marcador del mercado, computa sus indicadores e inyecta órdenes sin medir volumen. Dispara `SignalEvent`.
3. **`Portfolio`**: Evalúa el riesgo disponible en la billetera y dicta si se puede asumir o no la señal, cuantificando la entrada. Dispara `OrderEvent`.
4. **`ExecutionHandler`**: Emula la transacción con el bróker final (con comisiones y *slippage* reales). Retorna un `FillEvent` para el cuadre contable final de la cartera.

## 🛠 Instalación y Configuración

*(Instrucciones en construcción. Actualmente el proyecto se encuentra en Fase 1: Despliegue de estructura y componentes lógicos)*

### Dependencias Base
Se recomienda la instanciación de un entorno virtual:
```bash
python -m venv venv
# Activar (.venv/Scripts/activate en Windows)
pip install pandas numpy
```

## 📜 Estructura del Repositorio
* `event.py` - Jerarquía y estructura central de eventos.
* `data.py` - Interfaz abstracta para inyección de matrices CSV.
* `strategy.py` - Interfaz abstracta para la toma de decisiones matemáticas.
* `portfolio.py` - Manejador físico del P&L y contabilidad interna.
* `execution.py` - Interfaz final de enrutamiento sintético al bróker.

*(Nota: La documentación interna y planes arquitectónicos de trabajo personal están registrados en un repositorio privado asilado de este entorno).*
