from abc import ABC, abstractmethod
from event import FillEvent


class ExecutionHandler(ABC):
    """
    La clase abstracta base ExecutionHandler manejará de forma aislada
    la interacción real o emulada mediante las órdenes comerciales frente
    al "mundo exterior".
    
    Toma un OrderEvent e "ingresa" esa instrucción en la base del bróker. 
    Una vez respondido, creará instancias FillEvent dictaminando realmente 
    cuánto volumen y a qué precio procesó para que la contabilidad del sistema
    esté estrictamente cuadrada con la ejecución.
    """

    @abstractmethod
    def execute_order(self, event):
        """
        Toma una instrucción puramente proveniente de Portfolio y simula o lleva 
        a cabo el reenvio con una conexión.
        
        Args:
            event: Es un objeto OrderEvent subscrito a la cola general.
        """
        raise NotImplementedError("Deberá implementar execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):
    """
    El handler de simulación se limita a tomar cualquier OrderEvent proveniente
    del gestor de flujo (Portfolio) y emite un ticket Fill de cumplimiento automático
    dictando que las acciones se consumieron a su precio exacto de cierre 
    (ignorando spread, market depths ni delays temporales).
    """

    def __init__(self, events):
        """
        Inicializa el handler.
        """
        self.events = events

    def execute_order(self, event):
        """
        Convierte de manera cruda las órdenes OrderEvents directas en 
        comprobantes estáticos retronables como FillEvents sin denegaciones.
        """
        if event.type == 'ORDER':
            import datetime
            # Utilizamos precio 0 por el momento asumiendo que Portfolio 
            # recalcula a costo presente de cierre (o predefinirlo en Fill cost parameter)
            fill_event = FillEvent(
                datetime.datetime.now(), 
                event.symbol,
                'ARCA', 
                event.quantity, 
                event.direction, 
                fill_cost=None, 
                commission=None
            )
            self.events.put(fill_event)
