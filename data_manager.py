import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

class DataManager:
    """Gerencia a interação com a API Sheety para obter e atualizar dados de preços e usuários.

    Esta classe é responsável por:
    - Obter dados de destinos de voos (preços) da planilha Google Sheets.
    - Obter dados de e-mails de clientes (usuários) da planilha Google Sheets.
    - Atualizar códigos IATA para destinos na planilha de preços.

    Atributos:
        _user (str): Nome de usuário para autenticação Sheety.
        _password (str): Senha para autenticação Sheety.
        prices_endpoint (str): Endpoint da API Sheety para a planilha de preços.
        users_endpoint (str): Endpoint da API Sheety para a planilha de usuários.
        _authorization (HTTPBasicAuth): Objeto de autenticação HTTP Basic.
        destination_data (dict): Dados de destinos de voos obtidos da Sheety.
        customer_data (dict): Dados de e-mails de clientes obtidos da Sheety.
    """

    def __init__(self):
        """Inicializa o DataManager, carregando credenciais e endpoints da Sheety.
        """
        # As credenciais e endpoints são carregados de variáveis de ambiente para segurança.
        # Certifique-se de que as variáveis de ambiente SHEETY_USERNAME, SHEETY_PASSWORD,
        # SHEETY_PRICES_ENDPOINT e SHEETY_USERS_ENDPOINT estejam configuradas.
        self._user = os.environ.get("SHEETY_USERNAME")
        self._password = os.environ.get("SHEETY_PASSWORD")
        self.prices_endpoint = os.environ.get("SHEETY_PRICES_ENDPOINT")
        self.users_endpoint = os.environ.get("SHEETY_USERS_ENDPOINT")

        # Verifica se as variáveis de ambiente foram carregadas corretamente
        if not all([self._user, self._password, self.prices_endpoint, self.users_endpoint]):
            raise ValueError("Variáveis de ambiente Sheety (USERNAME, PASSWORD, PRICES_ENDPOINT, USERS_ENDPOINT) não configuradas.")

        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.destination_data = {}  # Inicializa vazio, será preenchido por get_destination_data
        self.customer_data = {}     # Inicializa vazio, será preenchido por get_customer_emails

    def get_destination_data(self) -> list[dict]:
        """Obtém todos os dados de destinos de voos da planilha de preços da Sheety.

        Returns:
            list[dict]: Uma lista de dicionários, onde cada dicionário representa um destino
                        com seus detalhes (cidade, código IATA, preço, etc.).

        Raises:
            requests.exceptions.RequestException: Se a requisição à API Sheety falhar.
        """
        print("Obtendo dados de destinos...")
        response = requests.get(url=self.prices_endpoint, auth=self._authorization)
        response.raise_for_status()  # Levanta uma exceção para erros de status HTTP
        data = response.json()
        self.destination_data = data["prices"]
        # pprint(self.destination_data) # Descomente para imprimir os dados formatados
        return self.destination_data

    def update_destination_codes(self) -> None:
        """Atualiza os códigos IATA para cada destino na planilha de preços da Sheety.

        Itera sobre os dados de destino já carregados e faz uma requisição PUT
        para cada linha na planilha, atualizando o campo 'iataCode'.

        Raises:
            requests.exceptions.RequestException: Se a requisição à API Sheety falhar.
        """
        print("Atualizando códigos IATA dos destinos...")
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            # A URL para atualização inclui o ID da linha na planilha
            update_url = f"{self.prices_endpoint}/{city["id"]}"
            response = requests.put(
                url=update_url,
                json=new_data,
                auth=self._authorization
            )
            response.raise_for_status() # Levanta uma exceção para erros de status HTTP
            print(f"Código IATA para {city['city']} atualizado: {response.text}")

    def get_customer_emails(self) -> list[dict]:
        """Obtém todos os e-mails de clientes da planilha de usuários da Sheety.

        Returns:
            list[dict]: Uma lista de dicionários, onde cada dicionário representa um usuário
                        com seus detalhes (nome, e-mail, etc.).

        Raises:
            requests.exceptions.RequestException: Se a requisição à API Sheety falhar.
        """
        print("Obtendo e-mails de clientes...")
        response = requests.get(url=self.users_endpoint, auth=self._authorization)
        response.raise_for_status()  # Levanta uma exceção para erros de status HTTP
        data = response.json()
        self.customer_data = data["users"]
        # pprint(self.customer_data) # Descomente para imprimir os dados formatados
        return self.customer_data

# Exemplo de uso (pode ser removido se este arquivo for apenas um módulo)
if __name__ == "__main__":
    try:
        data_manager = DataManager()
        # Exemplo de como usar:
        # destinos = data_manager.get_destination_data()
        # print("Destinos:", destinos)
        # data_manager.update_destination_codes() # Se houver códigos IATA para atualizar
        # emails = data_manager.get_customer_emails()
        # print("E-mails de clientes:", emails)
    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de API Sheety: {e}")


