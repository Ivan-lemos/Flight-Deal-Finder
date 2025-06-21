class FlightData:
    """Representa os dados de um voo específico, incluindo preço, aeroportos de origem e destino, datas e número de escalas.

    Atributos:
        price (float): O custo do voo.
        origin_airport (str): O código IATA do aeroporto de origem do voo.
        destination_airport (str): O código IATA do aeroporto de destino do voo.
        out_date (str): A data de partida do voo (formato YYYY-MM-DD).
        return_date (str): A data de retorno do voo (formato YYYY-MM-DD).
        stops (int): O número de escalas do voo (0 para voos diretos).
    """

    def __init__(self, price: float, origin_airport: str, destination_airport: str, out_date: str, return_date: str, stops: int):
        """Inicializa uma nova instância de FlightData.

        Args:
            price (float): O custo do voo.
            origin_airport (str): O código IATA do aeroporto de origem do voo.
            destination_airport (str): O código IATA do aeroporto de destino do voo.
            out_date (str): A data de partida do voo.
            return_date (str): A data de retorno do voo.
            stops (int): O número de escalas do voo.
        """
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.stops = stops

    @classmethod
    def from_amadeus_data(cls, flight_json: dict):
        """Cria uma instância de FlightData a partir de um dicionário de dados da API Amadeus.

        Args:
            flight_json (dict): Um dicionário contendo os dados de um voo da API Amadeus.

        Returns:
            FlightData: Uma nova instância de FlightData preenchida com os dados do voo.
        """
        # Extrai o número de escalas (um voo com 2 segmentos tem 1 escala)
        nr_stops = len(flight_json["itineraries"][0]["segments"]) - 1

        # Extrai os códigos IATA de origem e destino
        origin = flight_json["itineraries"][0]["segments"][0]["departure"]["iataCode"]
        # O destino final é encontrado no último segmento do voo
        destination = flight_json["itineraries"][0]["segments"][nr_stops]["arrival"]["iataCode"]

        # Extrai as datas de partida e retorno
        out_date = flight_json["itineraries"][0]["segments"][0]["departure"]["at"].split("T")[0]
        # A data de retorno é o primeiro segmento do segundo itinerário
        return_date = flight_json["itineraries"][1]["segments"][0]["departure"]["at"].split("T")[0]

        # Extrai o preço total
        price = float(flight_json["price"]["grandTotal"])

        return cls(price, origin, destination, out_date, return_date, nr_stops)


def find_cheapest_flight(data: dict) -> FlightData:
    """Analisa os dados de voo recebidos da API Amadeus para identificar a opção de voo mais barata.

    Args:
        data (dict): Os dados JSON contendo informações de voo retornados pela API.

    Returns:
        FlightData: Uma instância da classe FlightData representando o voo mais barato encontrado,
        ou uma instância de FlightData com campos 'N/A' se nenhum dado de voo válido estiver disponível.

    Esta função inicialmente verifica se os dados contêm entradas de voo válidas. Se nenhum dado válido for encontrado,
    ela retorna um objeto FlightData contendo "N/A" para todos os campos. Caso contrário, ela assume que o primeiro
    voo na lista é o mais barato. Em seguida, itera por todos os voos disponíveis nos dados, atualizando
    os detalhes do voo mais barato sempre que um voo com preço mais baixo é encontrado. O resultado é um objeto
    FlightData preenchido com os detalhes do voo mais acessível.
    """

    # Lida com dados vazios se não houver voo ou limite de taxa da Amadeus excedido
    if data is None or not data.get("data"):
        print("Nenhum dado de voo disponível ou limite de taxa da API excedido.")
        return FlightData(
            price="N/A",
            origin_airport="N/A",
            destination_airport="N/A",
            out_date="N/A",
            return_date="N/A",
            stops="N/A"
        )

    # Inicializa o voo mais barato com o primeiro voo da lista
    # Usa o método de fábrica para criar o objeto FlightData
    cheapest_flight = FlightData.from_amadeus_data(data["data"][0])

    # Itera sobre os voos restantes para encontrar o mais barato
    for flight_json in data["data"]:
        current_flight = FlightData.from_amadeus_data(flight_json)
        if current_flight.price < cheapest_flight.price:
            cheapest_flight = current_flight

    print(f"O preço mais baixo para {cheapest_flight.destination_airport} é £{cheapest_flight.price}")
    return cheapest_flight


