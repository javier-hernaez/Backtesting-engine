import numpy as np

from event import SignalEvent
from strategy import Strategy

class MovingAverageCrossStrategy(Strategy):
    """
    Estrategia fundamental preconfigurada desplegada de manera modular.
    Utiliza una Media Móvil Simple (SMA) a corto plazo para cruzar por 
    el margen de una Media Móvil Simple a largo plazo.
    """

    def __init__(self, bars, events, short_window=10, long_window=30):
        """
        Inicializa la estrategia de cruce de medias MAC.
        
        Args:
            bars: Instancia central de DataHandler.
            events: Instancia de la cola de eventos.
            short_window: Periodos retrospectivos para la media corta.
            long_window: Periodos retrospectivos para la media larga.
        """
        self.bars = bars
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Configurar estado para estar "FUERA" del mercado por defecto
        # Asumiendo una lista pequeña de symbol_list alojada en bars
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Genera el diccionario del estado 'Fuera/Dentro' para cada ticker
        provisto en la inicialización del proveedor de datos.
        """
        bought = {}
        for s in self.bars.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Produce el SignalEvent del tipo LONG, SHORT o EXIT al comparar 
        estrictamente a tiempo real nuestra matemática sobre la barra más actual.
        """
        if event.type == 'MARKET':
            for s in self.bars.symbol_list:
                # 1. Recuperar los datos estrictos necesarios (sin pasarse del buffer)
                bars = self.bars.get_latest_bars(s, N=self.long_window)
                
                # 2. Impedir cálculos sobre "vacío histórico"
                if bars is not None and len(bars) == self.long_window:
                    # Parsear los valores abstractos a Cierre
                    # bars -> lista de [datetime, pandas df_bar]
                    short_closes = np.array([b[1]['close'] for b in bars[-self.short_window:]], dtype=float)
                    long_closes = np.array([b[1]['close'] for b in bars], dtype=float)

                    short_sma = np.mean(short_closes)
                    long_sma = np.mean(long_closes)

                    # Extracción temporal para la firma del evento
                    dt = self.bars.get_latest_bar_datetime(s)

                    # 3. Decisiones de inversión cruzando umbrales lógicos
                    if short_sma > long_sma and self.bought[s] == 'OUT':
                        print(f"[{dt}] CRUCE SUPERIOR ({s}) -> SMA Rápida {short_sma:.2f} > SMA Lenta {long_sma:.2f}")
                        signal = SignalEvent('MAC_STRATEGY', s, dt, 'LONG', 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'

                    elif short_sma < long_sma and self.bought[s] == 'LONG':
                        print(f"[{dt}] CRUCE INFERIOR ({s}) -> SMA Rápida {short_sma:.2f} < SMA Lenta {long_sma:.2f}")
                        signal = SignalEvent('MAC_STRATEGY', s, dt, 'EXIT', 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'
