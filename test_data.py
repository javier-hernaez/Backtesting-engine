import queue
from data import HistoricalCSVDataHandler

def test_data_handler():
    events = queue.Queue()
    # Cargamos AAPL desde carpeta data usando la estructura preparada
    data_handler = HistoricalCSVDataHandler(events, 'data', ['AAPL'])
    
    print("Iniciando inyección de 3 barras manuales:")
    for i in range(3):
        data_handler.update_bars()
        
        # Verificar qué hay en la cola de variables
        evento = events.get(False)
        print(f"Evento recogido en cola: {evento.type}")
        
        # Consultar la historia conocida hasta ese latido
        print(f"Index de la barra actual (AAPL): {data_handler.get_latest_bar_datetime('AAPL')}")
        print(f"Precio de Cierre (AAPL): {data_handler.get_latest_bar_value('AAPL', 'close')}")
        print("-" * 30)

if __name__ == "__main__":
    test_data_handler()
