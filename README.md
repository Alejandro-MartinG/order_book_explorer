# Order Book Explorer

Este proyecto proporciona una API para explorar estadísticas de órdenes de compra y venta para diferentes símbolos de trading.

La información es extraida de la API de blockchain.com: https://github.com/blockchain/lib-exchange-client/tree/master/python


## Requisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Alejandro-MartinG/order_book_explorer.git
```
```
cd order-book-explorer
```

2. Crea un entorno virtual y actívalo:

```bash
python -m venv .venv
source .venv/bin/activate # En Windows usa venv\Scripts\activate
```

3. Instala las dependencias:

``` bash
pip install -r requirements.txt
```

## Testing
Ejecutar el comando desde la raiz del proyecto para pasar los test unitarios:

```
python -m unittest discover -v 
```

## Uso

### Carga de datos

Es un comando que descarga los datos de un simbolo concreto para poder ser consultados posteriormente por la API.


```bash
python src/data_loader.py [symbol]
```
`symbol` debe ser reemplazado por el simbolo que se desea conslutar:

```bash
python src/data_loader.py near-usd
```

### Uso de la API

1. Inicia el servidor Flask:
```bash
 python src/api.py 
```


2. La API estará disponible en `http://localhost:5000`. Puedes usar los siguientes endpoints:

- GET `/bids/stats?symbol=BTC-USD`: Estadísticas de órdenes de compra para un símbolo específico.
- GET `/asks/stats?symbol=BTC-USD`: Estadísticas de órdenes de venta para un símbolo específico.
- GET `/general/stats`: Estadísticas globales para todos los símbolos.

Ejemplos:
```url
http://localhost:5000/bids/stats?symbol=BTC-USD
```
```url
http://localhost:5000/asks/stats?symbol=near-usd
```
```url
http://localhost:5000/general/stats
```

## Estructura del Proyecto

```bash
order-book-explorer/
├── src/
│ ├── api.py
│ ├── load_data.py
│ ├── services/
│ │ └── stats_service.py
│ └── db/
│   └── db.py
├── requirements.txt
└── README.md

```

## DECISIONES SOBRE LA IMPLEMENTACIÓN
He decidido usar Flask en lugar de Django por un tema de tiempos, no disponía de mucho tiempo y he preferido asegurar el uso de una herramienta que conozco mejor.

### Arquitectura
Para solucionar el problema por una lado hay una API que consulta datos guardados previamente en la bbdd, hace falta un tratamiento previo de esos datos para servirlos en el formato deseado entonces he decidido crear un servio de stats que es una "interfaz" para poder recolectar esos datos y no acoplar la bd de datos con la API.

API --> Stats Service --> DB

La carga de los datos hace referencia a lo que sería un proceso de ETL, mi diseño tiene un simple archivo que divide el proceso de ETL en diferentes funciones esto debería ser más complejo e incluir una validación y serialización de datos al menos para asegurar que no descargas datos que no vas a saber leer y no guardar nada incongruente en la base datos.

## TODO

Cambios que me habría gustado implementar en este proyecto:
- **Validación de datos** de la api externa: una validación de tipos contrastada con un contrato por ejemplo en formato .json donde están reflejados los tipos de datos que se deben recibir.
- Un **serializador** para realizar ahí la validación de los datos recibidos por la API externa y la conversión a mi modelo de la base de datos junto con el manejo de las posibles excepciones o diferentes respuestas de la API.
- El **tipado y manejo de Errores**
- **Dockerizar** la app

Ejemplo de un serializer sencillo:

```python
class BlockchainOrderBookSerializer:
    def __init__(self):
        self.schema = {
            "symbol": {"type": "string"},
            "bids": [{"px": {"type": "float"}, "qty": {"type": "float"}, "num": {"type": "integer"}}],
            "asks": [{"px": {"type": "float"}, "qty": {"type": "float"}, "num": {"type": "integer"}}]
        }

    def serialize(self, data):
        df = pd.DataFrame(data)
        df = self._transform_data(df)
        self._validate_types(df)
        return df.to_dict(orient="records")

    def _transform_data(self, df):
        df["symbol"] = df["symbol"].astype("string")
        df["bids"] = df["bids"].apply(lambda x: self._transform_bids(x))
        df["asks"] = df["asks"].apply(lambda x: self._transform_asks(x))
        return df

    def _transform_bids(self, bids):
        bids_df = pd.DataFrame(bids)
        bids_df["px"] = pd.to_numeric(bids_df["px"], errors="coerce")
        bids_df["qty"] = pd.to_numeric(bids_df["qty"], errors="coerce")
        bids_df["num"] = pd.to_numeric(bids_df["num"], errors="coerce")
        return bids_df.to_dict(orient="records")

    def _transform_asks(self, asks):
        asks_df = pd.DataFrame(asks)

        asks_df["px"] = pd.to_numeric(asks_df["px"], errors="coerce")
        asks_df["qty"] = pd.to_numeric(asks_df["qty"], errors="coerce")
        asks_df["num"] = pd.to_numeric(asks_df["num"], errors="coerce")

        return asks_df.to_dict(orient="records")

    def _validate_types(self, data):
        if not data["symbol"].apply(lambda x: isinstance(x, str)).all():
            raise ValueError("The 'symbol' column must be a string.")
        if not data["bids"].apply(lambda x: isinstance(x, list)).all():
            raise ValueError("The 'bids' column must be a list of dictionaries.")
        if not data["asks"].apply(lambda x: isinstance(x, list)).all():
            raise ValueError("The 'asks' column must be a list of dictionaries.")
        
        for index, row in data.iterrows():
            for bid in row["bids"]:
                if not isinstance(bid, dict):
                    raise ValueError("The 'bids' column must be a list of dictionaries.")
                if not isinstance(bid["px"], (int, float)):
                    raise ValueError("The 'px' column must be a number.")
                if not isinstance(bid["qty"], (int, float)):
                    raise ValueError("The 'qty' column must be a number.")
                if not isinstance(bid["num"], int):
                    raise ValueError("The 'num' column must be an integer.")
            for ask in row["asks"]:
                if not isinstance(ask, dict):
                    raise ValueError("The 'asks' column must be a list of dictionaries.")
                if not isinstance(ask["px"], (int, float)):
                    raise ValueError("The 'px' column must be a number.")
                if not isinstance(ask["qty"], (int, float)):
                    raise ValueError("The 'qty' column must be a number.")
                if not isinstance(ask["num"], int):
                    raise ValueError("The 'num' column must be an integer.")
        
        return data
```