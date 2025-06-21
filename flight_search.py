import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# ---------------------------- CONSTANTES DE API ------------------------------- #
IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/cities" # Endpoint para buscar códigos IATA de cidades
FLIGHT_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers" # Endpoint para buscar ofertas de voos
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token" # Endpoint para obter o token de autenticação

# ---------------------------- CLASSE FlightSearch ------------------------------- #

class FlightSearch:
    """Gerencia a busca por voos e códigos IATA usando a API Amadeus.

    Esta classe é responsável por:
    - Obter e gerenciar o token de autenticação da API Amadeus.
    - Buscar códigos IATA para cidades.
    - Pesquisar ofertas de voos com base em critérios específicos.

    Atributos:
        _api_key (str): A chave da API Amadeus, carregada de variáveis de ambiente.
        _api_secret (str): O segredo da API Amadeus, carregado de variáveis de ambiente.
        _token (str): O token de autenticação atual para a API Amadeus.
    """

    def __init__(self):
        """Inicializa o FlightSearch, carregando credenciais e obtendo um token de autenticação.
        """
        # Carrega as chaves da API de variáveis de ambiente para segurança.
        # Certifique-se de que as variáveis de ambiente AMADEUS_API_KEY e AMADEUS_SECRET estejam configuradas.
        self._api_key = os.environ.get("AMADEUS_API_KEY")
        self._api_secret = os.environ.get("AMADEUS_SECRET")

        if not self._api_key or not self._api_secret:
            raise ValueError("As variáveis de ambiente AMADEUS_API_KEY e AMADEUS_SECRET devem ser configuradas.")

        # Obtém um novo token de autenticação ao inicializar a classe.
        # Uma extensão futura poderia reutilizar tokens não expirados.
        self._token = self._get_new_token()

    def _get_new_token(self) -> str:
        """Gera e retorna um novo token de autenticação para a API Amadeus.

        Faz uma requisição POST para o endpoint de token da Amadeus com as credenciais
        necessárias (API key e API secret) para obter um novo token de credenciais de cliente.

        Returns:
            str: O novo token de acesso obtido da resposta da API.

        Raises:
            requests.exceptions.RequestException: Se a requisição para obter o token falhar.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        response = requests.post(url=TOKEN_ENDPOINT, headers=headers, data=body)
        response.raise_for_status()  # Levanta uma exceção para erros de status HTTP

        token_data = response.json()
        print(f"Seu token é {token_data['access_token']}")
        print(f"Seu token expira em {token_data['expires_in']} segundos")
        return token_data['access_token']

    def get_destination_code(self, city_name: str) -> str:
        """Recupera o código IATA para uma cidade especificada usando a API Amadeus Location.

        Args:
            city_name (str): O nome da cidade para a qual encontrar o código IATA.

        Returns:
            str: O código IATA da primeira cidade correspondente, se encontrado;
                 "N/A" se nenhum código IATA for encontrado ou ocorrer um erro.

        A função envia uma requisição GET para o IATA_ENDPOINT com uma consulta que especifica o nome da cidade
        e outros parâmetros para refinar a busca. Em seguida, tenta extrair o código IATA da resposta JSON.
        """
        print(f"Usando este token para obter o código de destino: {self._token}")
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "keyword": city_name,
            "max": "2",  # Limita o número de resultados
            "include": "AIRPORTS", # Inclui aeroportos na busca
        }
        try:
            response = requests.get(
                url=IATA_ENDPOINT,
                headers=headers,
                params=query
            )
            response.raise_for_status() # Levanta uma exceção para erros de status HTTP
            data = response.json()

            if data and data["data"]:
                code = data["data"][0]["iataCode"]
                print(f"Código IATA para {city_name}: {code}")
                return code
            else:
                print(f"Nenhum código IATA encontrado para {city_name}.")
                return "N/A"
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar código IATA para {city_name}: {e}")
            return "N/A"
        except KeyError:
            print(f"Erro de chave ao processar resposta IATA para {city_name}.")
            return "N/A"

    def check_flights(self, origin_city_code: str, destination_city_code: str, from_time: datetime, to_time: datetime, is_direct: bool = True) -> dict or None:
        """Pesquisa opções de voo entre duas cidades em datas de partida e retorno especificadas
        usando a API Amadeus.

        Args:
            origin_city_code (str): O código IATA da cidade de partida.
            destination_city_code (str): O código IATA da cidade de destino.
            from_time (datetime): A data de partida desejada.
            to_time (datetime): A data de retorno desejada.
            is_direct (bool): True para voos sem escalas (diretos), False para permitir escalas. Padrão: True.

        Returns:
            dict or None: Um dicionário contendo os dados da oferta de voo se a consulta for bem-sucedida;
                          None se houver um erro ou nenhum voo for encontrado.

        A função constrói uma consulta com os parâmetros de busca de voo e envia uma requisição GET para
        a API. Ela lida com a resposta, verificando o código de status e analisando os dados JSON se a
        requisição for bem-sucedida. Se o código de status da resposta não for 200, ela registra uma mensagem de erro.
        """
        print(f"Verificando voos de {origin_city_code} para {destination_city_code}...")
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            "nonStop": "true" if is_direct else "false", # Converte booleano Python para string exigida pela API
            "currencyCode": "GBP", # Moeda da busca
            "max": "10", # Número máximo de resultados
        }

        try:
            response = requests.get(
                url=FLIGHT_ENDPOINT,
                headers=headers,
                params=query,
            )
            response.raise_for_status() # Levanta uma exceção para erros de status HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao verificar voos: {e}")
            print(f"Status code: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Corpo da resposta: {response.text if 'response' in locals() else 'N/A'}")
            print("Para detalhes sobre códigos de status, verifique a documentação da API:")
            print("https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api-reference")
            return None

# Exemplo de uso (pode ser removido se este arquivo for apenas um módulo)
if __name__ == "__main__":
    try:
        flight_search = FlightSearch()
        # Exemplo de busca de código IATA
        # iata_code = flight_search.get_destination_code("London")
        # print(f"Código IATA para Londres: {iata_code}")

        # Exemplo de busca de voos
        # from_date = datetime(2024, 7, 1)
        # to_date = datetime(2024, 7, 10)
        # flights = flight_search.check_flights("LON", "PAR", from_date, to_date)
        # if flights:
        #     print("Voos encontrados:", flights)
        # else:
        #     print("Nenhum voo encontrado.")

    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de API Amadeus: {e}")


