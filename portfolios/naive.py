from event import OrderEvent
from portfolio import Portfolio

class NaivePortfolio(Portfolio):
    """
    Portfolio predeterminado de simulación enviará órdenes puramente asiladas
    ajustadas a un volumen estático ciego (ej. 100 participaciones cada vez)
    sin dimensionador de riesgo heurístico.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Inicia el porfolio sobre la cola y los datos del mercado en uso.
        
        Args:
            bars: Proveedor DataHandler con la historia de todos los symbol_list actuales.
            events: El motor global Event Queue.
            start_date: Fecha de inicio de indexado temporal (bar.datetime).
            initial_capital: Float representando balance inicial de simulación.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, int(0)) for k in self.symbol_list)

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        """Preconstruye la estructura local de número de acciones por activo histórico."""
        d = dict((k, int(0)) for k in self.symbol_list)
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """Preconstruye la lista maestra del balance valor-dinero histórico."""
        d = dict((k, 0.0) for k in self.symbol_list)
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """Preconstruye el diccionario fotográfico del balance actual dictaminante."""
        d = dict((k, 0.0) for k in self.symbol_list)
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        """
        Sincroniza el marcador de paso del reloj capturando el valor en vivo
        de cada ticket para repuntar la gráfica del Equidad Total para este datetime.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        dp = dict((k, int(v)) for k, v in self.current_positions.items())
        dp['datetime'] = latest_datetime
        self.all_positions.append(dp)

        dh = dict((k, float(v)) for k, v in self.current_holdings.items())
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            market_value = self.current_positions[s] * self.bars.get_latest_bar_value(s, "close")
            dh[s] = market_value
            dh['total'] += market_value

        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        """Aplica a la base de cálculo físico del stock un cruce realizado por el Broker."""
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        elif fill.direction == 'SELL':
            fill_dir = -1

        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """Aplica la modificación aritmética a los fondos (Cash y Equidad) tras ejecución."""
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        elif fill.direction == 'SELL':
            fill_dir = -1

        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "close")
        cost = fill_dir * fill_cost * fill.quantity

        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """Wrapper final que recibe FillEvents y unifica las dos variables arquitectónicas."""
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """Dimensionamiento ciego de posiciones de señal -> Instrucción de Mercado (Order)."""
        order_type = 'MKT'
        mkt_quantity = 100
        cur_quantity = self.current_positions[signal.symbol]

        if signal.signal_type == 'LONG' and cur_quantity == 0:
            return OrderEvent(signal.symbol, order_type, mkt_quantity, 'BUY')
        elif signal.signal_type == 'SHORT' and cur_quantity == 0:
            return OrderEvent(signal.symbol, order_type, mkt_quantity, 'SELL')
        
        elif signal.signal_type == 'EXIT' and cur_quantity > 0:
            return OrderEvent(signal.symbol, order_type, abs(cur_quantity), 'SELL')
        elif signal.signal_type == 'EXIT' and cur_quantity < 0:
            return OrderEvent(signal.symbol, order_type, abs(cur_quantity), 'BUY')
        
        return None

    def update_signal(self, event):
        """Receptáculo global y ejecutor de conversiones."""
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            if order_event is not None:
                self.events.put(order_event)
