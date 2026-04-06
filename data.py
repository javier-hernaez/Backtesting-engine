import os
import pandas as pd
from abc import ABC, abstractmethod

from event import MarketEvent


class DataHandler(ABC):
    """
    DataHandler es una Clase Base Abstracta (ABC) proporcionando la interfaz para todas
    las subsiguientes versiones de handlers (tanto históricos en local, simulados o de APIs en vivo).
    
    El objetivo de (una subclase derivada de) un DataHandler es entregar las barras de mercado 
    a las Estrategias (o indicadores) paso a paso para simular que realmente está ocurriendo a 
    tiempo real, por tanto evitando el lookahead bias de observar "futuras" filas de datos.
    """

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Retorna la última barra de datos actualizada para un determinado symbol.
        """
        raise NotImplementedError("Deberá implementar get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Retorna las últimas N barras del archivo listado.
        Utilizado principalmente para cálculos matemáticos en la estratega, ej. (SMA 20)
        """
        raise NotImplementedError("Deberá implementar get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Retorna el timestamp del formato compatible de la última barra.
        """
        raise NotImplementedError("Deberá implementar get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Obtiene uno de los valores OHLCV mediante string en val_type.
        Ejemplo: val_type='Close' recuperará el cierre actual.
        """
        raise NotImplementedError("Deberá implementar get_latest_bar_value()")

    @abstractmethod
    def update_bars(self):
        """
        Avanzará por la cola interna de datos, extrayendo la nueva barra a la lista 
        de "datos disponibles" o latest_bars.
        Esto desencadenará la propagación de un MarketEvent a la cola principal.
        """
        raise NotImplementedError("Deberá implementar update_bars()")


class HistoricalCSVDataHandler(DataHandler):
    """
    DataHandler histórico diseñado para leer archivos CSV de manera local.
    Carga todos los datasets enumerados para cada símbolo a memoria en 
    pandas DataFrame pero devuelve los resultados fila a fila iterativamente 
    como en un entorno live real.
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Inicializa el handler y fuerza la conversión de datos.
        
        Args:
            events: La cola (Queue) principal del Bucle de Eventos.
            csv_dir: Directorio absoluto o relativo donde residen los CSV.
            symbol_list: Lista representativa en forma de strings ["AAPL", "TSLA"].
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True       

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Abre uno por uno los archivos CSV provistos asumiendo un formato similar
        a (Date, Open, High, Low, Close, Adj Close, Volume). 
        Genera un diccionario de generadores mediante .iterrows()
        """
        comb_index = None
        for s in self.symbol_list:
            # Asumimos que los archivos coinciden con el nombre del Symbol
            csv_path = os.path.join(self.csv_dir, f"{s}.csv")
            
            try:
                self.symbol_data[s] = pd.read_csv(
                    csv_path, 
                    header=0, 
                    index_col=0, 
                    parse_dates=True,
                    names=['datetime', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
                )
                self.symbol_data[s].sort_index(inplace=True)

                # Unificamos índices de todos los activos para alinear barras
                if comb_index is None:
                    comb_index = self.symbol_data[s].index
                else:
                    comb_index.union(self.symbol_data[s].index)
                
                # Preparamos una lista vacía nativa para los resultados actuales
                self.latest_symbol_data[s] = []

            except FileNotFoundError:
                print(f"Error Crítico: No se encontró la data para: {s}")
                self.continue_backtest = False

        # Re-indexamos todo usando el calendario global consolidado
        for s in self.symbol_list:
            if s in self.symbol_data:
                self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Tubo interno (generador) por símbolo que arroja las barras en cascada.
        """
        for b in self.symbol_data[symbol]:
            yield b
            
    def get_latest_bar(self, symbol):
        """
        Devuelve estrictamente la última barra de las dispuestas.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("El símbolo proporcionado no opera en el histórico.")
        else:
            if bars_list:
                return bars_list[-1]
            else:
                return None

    def get_latest_bars(self, symbol, N=1):
        """
        Extrae las últimas N barras del símbolo listado.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("El símbolo proporcionado no operaba de base.")
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Extrae el index nativo de la barra provista (datetime).
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("El símbolo proporcionado no operaba de base.")
        else:
            return bars_list[-1][0] if bars_list else None

    def get_latest_bar_value(self, symbol, val_type):
        """
        Permite extracción genérica por String: (ej. OBT[val_type='close'])
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("El símbolo no operaba en las bases.")
        else:
            # bars_list = [(index temporal, serie de pandas pandas.Series), (...)]
            return getattr(bars_list[-1][1], val_type) if bars_list else None

    def update_bars(self):
        """
        Añade la iteración iterrows() a la cola interna visible listada.
        Si alcanza extremo asíncrono finalizará con False flag.
        """
        for s in self.symbol_list:
            try:
                bar = next(self.symbol_data[s])
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
