from abc import ABC, abstractmethod


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
