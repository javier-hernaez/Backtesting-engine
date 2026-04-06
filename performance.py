import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods=252):
    """
    Crea el ratio de Sharpe modelando la métrica estándar.
    
    Args:
        returns: Serie de Pandas con retornos porcentuales de cada periodo.
        periods: 252 (Diario), 252*6.5 (Horario), 252*6.5*60 (Minuto).
    """
    if len(returns) == 0:
        return 0.0
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(pnl):
    """
    Calcula el pico más alto a pozo (Maximum Drawdown) local de la curva.
    
    Args:
        pnl: Serie de Pandas que representa el P&L acumulativo.
        
    Returns:
        drawdown: Serie de Drawdowns en el tiempo.
        max_dd: Valor máximo de caida y duración histórica.
        duration: Duración temporal que tomó dicho Drawdown.
    """
    # Calculando los High Water Marks de forma incremental (el pico actual)
    hwm = [0]
    
    # Creamos las series temporales
    eq_idx = pnl.index
    drawdown = pd.Series(index=eq_idx, data=np.zeros(len(eq_idx)))
    duration = pd.Series(index=eq_idx, data=np.zeros(len(eq_idx)))
    
    # Bucle por la gráfica de rendimientos para asentar picos y simas
    for t in range(1, len(eq_idx)):
        hwm.append(max(hwm[t-1], pnl.iloc[t]))
        drawdown.iloc[t] = (hwm[t] - pnl.iloc[t])
        duration.iloc[t] = (0 if drawdown.iloc[t] == 0 else duration.iloc[t-1] + 1)
        
    return drawdown, drawdown.max(), duration.max()
