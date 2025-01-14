import ast

import requests


class CurrencyService:
    def __init__(self, final_currency: str):
        self.final_currency: str = final_currency

    @staticmethod
    def convert(amount_with_currency) -> int:
        # Parsing del valore e della valuta
        # amount, currency = amount_with_currency.split()
        dict_amount_with_currency = ast.literal_eval(amount_with_currency)
        amount = float(dict_amount_with_currency.get('revenue', 0))
        currency = dict_amount_with_currency.get('currency', 'N/A')
        if currency == 'N/A':
            return 0
        if currency == "EUR":
            return int(amount)  # Nessuna conversione necessaria
        # Chiamata all'API di conversione valutaria
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
        data = response.json()
        exchange_rate = data["rates"]["EUR"]
        return int(amount * exchange_rate)