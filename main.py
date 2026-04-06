import os
import queue
import time
import pandas as pd

from data import HistoricalCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolios.naive import NaivePortfolio
from strategies.mac import MovingAverageCrossStrategy
import performance

def main():
    """Tubería asíncrona fundamental"""
    print("Iniciando el Motor de Backtesting Orientado a Eventos...")
    
    # 1. Ajustes y Declaraciones
    csv_dir = "data"
    symbol_list = ['AAPL']
    initial_capital = 100000.0
    heartbeat = 0.0 # Segundos entre ticks (0 por ser backtest veloz ideal)

    # 2. Cola compartida global
    events = queue.Queue()

    # 3. Modelado Arquitectónico (Patrón Observer inverso)
    print("Pre-cargando histórico y componentes abstractos...")
    bars = HistoricalCSVDataHandler(events, csv_dir, symbol_list)
    strategy = MovingAverageCrossStrategy(bars, events, short_window=10, long_window=30)
    # Ventanas de medias móviles clásicas (ej. corta 10 dias, larga 30 dias)
    # tiene únicamente 4 dias en la carpeta para garantizar triggers del evento
    
    # Asegurar el primer tick de tiempo dinámico provisto por la base
    start_date = bars.get_latest_bar_datetime(symbol_list[0]) if bars.latest_symbol_data[symbol_list[0]] else "START"
    
    port = NaivePortfolio(bars, events, start_date, initial_capital)
    broker = SimulatedExecutionHandler(events)

    # 4. EVENT LOOP 
    print("---------------------------------")
    print("Arrancando el Bucle Asíncrono...")
    print("---------------------------------")
    
    while True:
        # A) Recuperación continua del DataHandler para bombear un MarketEvent
        if bars.continue_backtest:
            bars.update_bars()
        else:
            break
        
        # B) Bucle interno vaciando toda tarea pendiente dictada a la cola
        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    # Direccionamiento estructural ciego
                    if event.type == 'MARKET':
                        strategy.calculate_signals(event)
                        port.update_timeindex(event)

                    elif event.type == 'SIGNAL':
                        port.update_signal(event)

                    elif event.type == 'ORDER':
                        broker.execute_order(event)

                    elif event.type == 'FILL':
                        port.update_fill(event)

        time.sleep(heartbeat)

    print("---------------------------------")
    print("Backtest Finalizado. Realizando cómputos financieros...")
    
    # 5. Volcado en memoria de Analíticas a final de bucle
    equity_curve = pd.DataFrame(port.all_holdings)
    equity_curve.set_index('datetime', inplace=True)
    equity_curve['returns'] = equity_curve['total'].pct_change()
    
    returns = equity_curve['returns'].dropna()
    total_return = round((equity_curve['total'].iloc[-1] / initial_capital - 1.0) * 100.0, 2)
    
    sharpe = round(performance.create_sharpe_ratio(returns, periods=252), 4)
    drawdowns, max_dd, dd_duration = performance.create_drawdowns(equity_curve['total'])
    
    print("\n[RESULTADOS OBTENIDOS AL CIERRE]")
    print(f"Retorno Total:          {total_return}%")
    print(f"Capital Final Restante: ${round(equity_curve['total'].iloc[-1], 2)}")
    print(f"Sharpe Ratio Total:     {sharpe}")
    print(f"Máximo Drawdown (USD):  ${round(max_dd, 2)} (Duras: {dd_duration} ticks temporales)")
    
    # Desplegar informe visual de cruces operativos de la cartera
    print("Transacciones efectivas detectadas en posiciones:")
    for symb in symbol_list:
        print(f"{symb} unidades actuales al final del backtest: {port.current_positions[symb]}")

if __name__ == "__main__":
    main()
