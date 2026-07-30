"""
currency_converter.py
Enterprise Multi-Currency Engine for HydroThermal Nexus-AI.
Provides conversion rates, currency formatting, and ESG financial savings calculations.
"""

from typing import Dict, Any, Optional


class CurrencyConverter:
    """
    Core Currency Converter engine for HydroThermal Nexus-AI.
    Uses USD as base anchor (1.0) and maintains exchange rates for global industrial hubs.
    """

    # Exchange rates relative to USD (1 USD = X Currency units)
    # Rates updated for global enterprise industrial baseline
    CURRENCIES: Dict[str, Dict[str, Any]] = {
        "USD": {"symbol": "$",    "rate_vs_usd": 1.0,      "name": "US Dollar",         "unit_prefix": True},
        "INR": {"symbol": "₹",    "rate_vs_usd": 83.5,     "name": "Indian Rupee",      "unit_prefix": True},
        "EUR": {"symbol": "€",    "rate_vs_usd": 0.92,     "name": "Euro",              "unit_prefix": True},
        "GBP": {"symbol": "£",    "rate_vs_usd": 0.79,     "name": "British Pound",     "unit_prefix": True},
        "JPY": {"symbol": "¥",    "rate_vs_usd": 155.0,    "name": "Japanese Yen",      "unit_prefix": True},
        "AED": {"symbol": "AED ", "rate_vs_usd": 3.67,     "name": "UAE Dirham",        "unit_prefix": True},
        "CAD": {"symbol": "C$",   "rate_vs_usd": 1.37,     "name": "Canadian Dollar",   "unit_prefix": True},
        "AUD": {"symbol": "A$",   "rate_vs_usd": 1.52,     "name": "Australian Dollar", "unit_prefix": True},
        "CHF": {"symbol": "CHF ", "rate_vs_usd": 0.90,     "name": "Swiss Franc",       "unit_prefix": True},
        "CNY": {"symbol": "¥",    "rate_vs_usd": 7.25,     "name": "Chinese Yuan",      "unit_prefix": True},
        "SGD": {"symbol": "S$",   "rate_vs_usd": 1.35,     "name": "Singapore Dollar",  "unit_prefix": True},
        "SAR": {"symbol": "SAR ", "rate_vs_usd": 3.75,     "name": "Saudi Riyal",       "unit_prefix": True},
        "BRL": {"symbol": "R$",   "rate_vs_usd": 5.45,     "name": "Brazilian Real",    "unit_prefix": True},
        "KRW": {"symbol": "₩",    "rate_vs_usd": 1380.0,   "name": "South Korean Won",  "unit_prefix": True},
    }

    @classmethod
    def get_supported_currencies(cls) -> Dict[str, Dict[str, Any]]:
        """Returns the dictionary of supported currencies and details."""
        return cls.CURRENCIES

    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Converts an amount from one currency to another.
        """
        from_curr = from_currency.upper().strip()
        to_curr = to_currency.upper().strip()

        if from_curr not in cls.CURRENCIES:
            raise ValueError(f"Unsupported source currency: '{from_currency}'")
        if to_curr not in cls.CURRENCIES:
            raise ValueError(f"Unsupported target currency: '{to_currency}'")

        if from_curr == to_curr:
            return float(amount)

        # Convert source amount to USD base, then to target currency
        usd_amount = amount / cls.CURRENCIES[from_curr]["rate_vs_usd"]
        converted_amount = usd_amount * cls.CURRENCIES[to_curr]["rate_vs_usd"]
        return round(converted_amount, 4)

    @classmethod
    def format_currency(cls, amount: float, currency_code: str = "USD", decimals: int = 2) -> str:
        """
        Formats an amount with its corresponding currency symbol and thousand separators.
        """
        curr_code = currency_code.upper().strip()
        if curr_code not in cls.CURRENCIES:
            curr_info = {"symbol": f"{curr_code} ", "unit_prefix": True}
        else:
            curr_info = cls.CURRENCIES[curr_code]

        symbol = curr_info["symbol"]
        formatted_val = f"{amount:,.{decimals}f}"

        if curr_info.get("unit_prefix", True):
            return f"{symbol}{formatted_val}"
        return f"{formatted_val} {symbol}"

    @classmethod
    def calculate_esg_savings(
        cls,
        water_litres: float,
        energy_kwh: float,
        co2_kg: float,
        water_cost_per_l: float = 0.05,
        energy_cost_per_kwh: float = 8.0,
        carbon_price_per_tonne_usd: float = 15.0,
        input_currency: str = "INR",
        target_currency: str = "INR",
    ) -> Dict[str, Any]:
        """
        Calculates total ESG financial savings given resource quantities and unit costs,
        converting results into the target currency.
        """
        # Calculate raw water & energy savings in input_currency
        water_savings_raw = water_litres * water_cost_per_l
        energy_savings_raw = energy_kwh * energy_cost_per_kwh

        # Convert water & energy savings to target currency
        water_savings_target = cls.convert(water_savings_raw, input_currency, target_currency)
        energy_savings_target = cls.convert(energy_savings_raw, input_currency, target_currency)

        # Carbon savings: CO2 (kg -> tonne) * price in USD, then converted to target_currency
        co2_tonnes = co2_kg / 1000.0
        carbon_savings_usd = co2_tonnes * carbon_price_per_tonne_usd
        carbon_savings_target = cls.convert(carbon_savings_usd, "USD", target_currency)

        total_savings_target = water_savings_target + energy_savings_target + carbon_savings_target

        curr_info = cls.CURRENCIES.get(target_currency.upper(), {"symbol": "$"})
        symbol = curr_info["symbol"]

        return {
            "target_currency": target_currency.upper(),
            "currency_symbol": symbol,
            "water_savings": round(water_savings_target, 2),
            "water_savings_formatted": cls.format_currency(water_savings_target, target_currency, 0),
            "energy_savings": round(energy_savings_target, 2),
            "energy_savings_formatted": cls.format_currency(energy_savings_target, target_currency, 0),
            "carbon_savings_usd": round(carbon_savings_usd, 2),
            "carbon_savings": round(carbon_savings_target, 2),
            "carbon_savings_formatted": cls.format_currency(carbon_savings_target, target_currency, 0),
            "total_savings": round(total_savings_target, 2),
            "total_savings_formatted": cls.format_currency(total_savings_target, target_currency, 0),
        }
