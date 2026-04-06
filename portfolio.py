from abc import ABC, abstractmethod


class Portfolio(ABC):
    """
    La clase Portfolio actuará como contable interno manteniendo y gestionando 
    el valor y volumen del conjunto de posiciones que tenemos, el capital 
    restante y el dimensionamiento del riesgo. Módulo estrictamente enfocado a 
    la gestión del capital ("Money Management").
    
    Deberá saber actualizarse desde un SignalEvent y convertir la señal 
    en un OrderEvent tras validar con qué capital cuenta. Luego de la orden de un
    bróker procesará el FillEvent final.
    """

    @abstractmethod
    def update_signal(self, event):
        """
        Actuará sobre un SignalEvent enviado por un objeto Strategy. 
        Manejará el componente de dimensionamiento y lo despachará 
        al order_queue o como OrderEvent normal.
        """
        raise NotImplementedError("Deberá implementar update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Actualizará el valor actual del holding (cartera física) y el cajón libre 
        mediante la notificación del FillEvent provisto por ExecutionHandler.
        """
        raise NotImplementedError("Deberá implementar update_fill()")
