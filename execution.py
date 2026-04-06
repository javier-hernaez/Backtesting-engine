from abc import ABC, abstractmethod


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
