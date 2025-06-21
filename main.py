from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

# ---------------------------- CONSTANTES ------------------------------- #
ORIGIN_CITY_IATA = "LON"  # Código IATA da cidade de origem (Londres)

# ---------------------------- LÓGICA PRINCIPAL ------------------------------- #

def main():
    """Função principal para encontrar e notificar sobre ofertas de voos.

    Esta função orquestra o processo de:
    1. Obter dados de destinos de voos de uma planilha (via DataManager).
    2. Buscar códigos IATA para cidades sem eles (via FlightSearch).
    3. Pesquisar voos baratos para os destinos (via FlightSearch).
    4. Enviar notificações (e-mails/SMS) sobre as ofertas encontradas (via NotificationManager).
    """
    print("Iniciando o Flight Deal Finder...")

    # Inicializa os gerenciadores de dados, busca de voos e notificações
    data_manager = DataManager()
    flight_search = FlightSearch()
    notification_manager = NotificationManager()

    # Obtém os dados de destino da planilha Google Sheets
    sheet_data = data_manager.get_destination_data()

    # Se algum destino não tiver um código IATA, busca e atualiza na planilha
    if sheet_data[0]["iataCode"] == "":
        print("Atualizando códigos IATA na planilha...")
        for row in sheet_data:
            row["iataCode"] = flight_search.get_destination_code(row["city"])
        data_manager.destination_data = sheet_data
        data_manager.update_destination_codes()

    # Define as datas de busca para os voos (próximos 6 meses)
    tomorrow = datetime.now() + timedelta(days=1)
    six_month_from_today = datetime.now() + timedelta(days=6 * 30)

    # Itera sobre cada destino para buscar voos
    for destination in sheet_data:
        print(f"Buscando voos para {destination["city"]}...")
        flight = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=six_month_from_today
        )

        # Se um voo for encontrado e for mais barato que o preço na planilha, envia notificação
        if flight and flight.price < destination["lowestPrice"]:
            print(f"Oferta de voo encontrada para {destination["city"]}: £{flight.price}")

            # Obtém os e-mails dos clientes para enviar notificações
            users = data_manager.get_customer_emails()
            emails = [row["email"] for row in users]
            names = [row["firstName"] for row in users]

            # Cria a mensagem de notificação
            message = f"Preço baixo de voo! Apenas £{flight.price} para voar de {flight.origin_airport} para {flight.destination_airport}, de {flight.out_date} a {flight.return_date}."

            # Se o voo tiver escalas, adiciona essa informação à mensagem
            if flight.stops > 0:
                message += f"\nO voo tem {flight.stops} escala(s)."

            # Envia a notificação para todos os usuários
            notification_manager.send_emails(emails, message)
            # notification_manager.send_sms(message) # Descomente para enviar SMS

        elif flight:
            print(f"Nenhuma oferta mais barata encontrada para {destination["city"]}. Preço atual: £{flight.price}, Preço mais baixo registrado: £{destination["lowestPrice"]}")
        else:
            print(f"Nenhum voo encontrado para {destination["city"]}.")

    print("Busca de ofertas de voos concluída.")


if __name__ == "__main__":
    main()


