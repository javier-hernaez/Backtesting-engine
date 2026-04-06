class Event(object):
    """
    Clase base de eventos que provee una interfaz común para todos
    los eventos del sistema subsiguiente, formando el núcleo
    de la arquitectura de backtesting.
    """
    pass


class MarketEvent(Event):
    """
    Maneja el evento de recepción de una nueva actualización de mercado,
    ya sea con información tick por tick u OHLCV. 
    """

    def __init__(self):
        """
        Inicializa el evento de mercado. No requiere datos adicionales 
        porque las características del mercado las conserva el DataHandler.
        """
        self.type = 'MARKET'


class SignalEvent(Event):
    """
    Maneja el evento de emisión de una señal (Long, Short, Exit) tras 
    la evaluación de los datos del mercado por parte de una Estrategia.
    """

    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Inicializa el evento de señal.
        
        Args:
            strategy_id: Identificador de la estrategia que lanza la orden.
            symbol: Identificador de cotización, p.ej. 'AAPL'.
            datetime: Instante de tiempo al generarse la señal.
            signal_type: 'LONG' o 'SHORT'.
            strength: Grado de la señal (utilidad opcional para dimensionamiento).
        """
        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength


class OrderEvent(Event):
    """
    Maneja el evento de envío de una orden al sistema de ejecución
    (bróker virtual o real), determinando el instrumento, cantidad y dirección.
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        Inicializa el evento de Orden.

        Args:
            symbol: El activo a ejecutar.
            order_type: 'MKT' (Market) o 'LMT' (Limit, si procediese).
            quantity: Cantidad no negativa en unidades.
            direction: 'BUY' o 'SELL'.
        """
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Reporta valores clave de la orden emitida.
        """
        print(f"Orden Emitida: Symbol={self.symbol}, Type={self.order_type}, "
              f"Quantity={self.quantity}, Direction={self.direction}")


class FillEvent(Event):
    """
    Evento que encapsula la noción de transacción concretada ("Fill") 
    o parcial proveído por el bróker tras evaluar un OrderEvent. 
    """

    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
        """
        Inicializa el evento de transacción cumplida.
        
        Args:
            timeindex: Momento en el tiempo del fill.
            symbol: El instrumento transado.
            exchange: Donde se cruzó la orden (p.ej. 'ARCA').
            quantity: Cantidad procesada.
            direction: 'BUY' o 'SELL'.
            fill_cost: Costo de ejecución real (precio x cantidad antes de comisiones).
            commission: Una comisión calculada empíricamente de ser necesaria.
        """
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        
        # Calcular comisión por defecto
        if commission is None:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission

    def calculate_commission(self):
        """
        Calcula una comisión estandarizada asumiendo Interactive Brokers, por ejemplo.
        Regla común min ($1.0) aprox en USA. Se adaptará a cada framework.
        Para fases iniciales asume 0 para no arrastrar pérdidas implícitas, 
        pero el marco arquitectónico ya lo soporta.
        """
        return 0.0
