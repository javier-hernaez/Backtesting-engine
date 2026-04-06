from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    Strategy es un Clase Abstracta Base orientando a interfaces a heredar
    una gestión de cálculo de lógicas comerciales sobre barras de información 
    y cruces matemáticos (ej: Media Móvil, Bollinger, RSI).
    
    Estará diseñada para operar acoplándose ciegamente al framework general. Mantiene
    las reglas de negocio separadas de la ejecución e ignora por completo
    el volumen y el tamaño final con el que operará la cuenta real, solo debe
    "generar un sentimiento".
    """

    @abstractmethod
    def calculate_signals(self, event):
        """
        Proporcionará el mecanismo para calcular el listado potencial 
        de señales (SignalEvent o equivalente) encolándolas a la 
        Queue principal.
        
        Args:
            event: Un MarketEvent que notifica que existe nueva información 
                   en el DataHandler.
        """
        raise NotImplementedError("Deberá implementar calculate_signals()")
