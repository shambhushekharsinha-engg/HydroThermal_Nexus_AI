"""
tests/test_currency.py
Automated unit test suite for HydroThermal Nexus-AI Multi-Currency Engine.
"""

import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from currency_converter import CurrencyConverter


def test_supported_currencies_list():
    currencies = CurrencyConverter.get_supported_currencies()
    assert isinstance(currencies, dict)
    assert "USD" in currencies
    assert "INR" in currencies
    assert "EUR" in currencies
    assert "GBP" in currencies
    assert "JPY" in currencies
    assert "AED" in currencies
    assert "CAD" in currencies
    assert "AUD" in currencies
    assert "CHF" in currencies
    assert "CNY" in currencies
    assert "SGD" in currencies
    assert "SAR" in currencies
    assert "BRL" in currencies
    assert "KRW" in currencies
    assert len(currencies) >= 14


def test_currency_conversion_usd_to_inr():
    converted = CurrencyConverter.convert(100.0, "USD", "INR")
    assert converted == 8350.0


def test_currency_conversion_same_currency():
    converted = CurrencyConverter.convert(250.0, "EUR", "EUR")
    assert converted == 250.0


def test_currency_conversion_cross_rates():
    # Convert 83.5 INR -> USD -> EUR
    usd_val = CurrencyConverter.convert(83.5, "INR", "USD")
    assert usd_val == 1.0
    eur_val = CurrencyConverter.convert(83.5, "INR", "EUR")
    assert eur_val == 0.92


def test_currency_formatting():
    fmt_usd = CurrencyConverter.format_currency(1234.56, "USD")
    assert fmt_usd == "$1,234.56"

    fmt_inr = CurrencyConverter.format_currency(50000.0, "INR", decimals=0)
    assert fmt_inr == "₹50,000"

    fmt_eur = CurrencyConverter.format_currency(89.9, "EUR")
    assert fmt_eur == "€89.90"


def test_unsupported_currency_error():
    with pytest.raises(ValueError, match="Unsupported source currency"):
        CurrencyConverter.convert(100, "XYZ", "USD")

    with pytest.raises(ValueError, match="Unsupported target currency"):
        CurrencyConverter.convert(100, "USD", "INVALID")


def test_esg_savings_calculation_inr():
    res = CurrencyConverter.calculate_esg_savings(
        water_litres=1000.0,
        energy_kwh=500.0,
        co2_kg=200.0,
        water_cost_per_l=0.05,
        energy_cost_per_kwh=8.0,
        carbon_price_per_tonne_usd=15.0,
        input_currency="INR",
        target_currency="INR",
    )
    assert res["target_currency"] == "INR"
    assert res["water_savings"] == 50.0
    assert res["energy_savings"] == 4000.0
    # CO2: 200kg = 0.2 tonne * $15 = $3 USD -> 3 * 83.5 = 250.5 INR
    assert res["carbon_savings_usd"] == 3.0
    assert res["carbon_savings"] == 250.5
    assert res["total_savings"] == 4300.5
    assert "₹" in res["total_savings_formatted"]


def test_esg_savings_calculation_usd_target():
    res = CurrencyConverter.calculate_esg_savings(
        water_litres=1000.0,
        energy_kwh=500.0,
        co2_kg=200.0,
        water_cost_per_l=0.05,
        energy_cost_per_kwh=8.0,
        carbon_price_per_tonne_usd=15.0,
        input_currency="INR",
        target_currency="USD",
    )
    assert res["target_currency"] == "USD"
    assert res["total_savings"] > 0
    assert "$" in res["total_savings_formatted"]
