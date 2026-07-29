"""
backend/modbus_edge_simulator.py
Siemens Modbus TCP / PLC Hardware Edge Simulator for HydroThermal Nexus-AI.
Simulates Modbus register reads/writes for industrial PLCs and Raspberry Pi edge gateways.
Registers:
  - 40001: Electricity kWh (Scaled x10)
  - 40002: Water Litres (Scaled x10)
  - 40003: Main Header Pressure PSI (Scaled x10)
  - 40004: Thermal Return Temp °C (Scaled x10)
  - 40005: Actuator Valve Position % (0-100)
"""

import time
import random
import datetime
from typing import Dict, Any


class ModbusPLCSimulator:
    """Simulates a Siemens S7-1200 / Modbus TCP Industrial PLC Controller."""

    def __init__(self, ip_address: str = "192.168.1.100", port: int = 502):
        self.ip_address = ip_address
        self.port = port
        self.connected = True
        self.holding_registers = {
            40001: 22000,  # 2200.0 kWh
            40002: 31000,  # 3100.0 L
            40003: 425,    # 42.5 PSI
            40004: 684,    # 68.4 °C
            40005: 100,    # 100% valve open
        }

    def read_holding_registers(self, start_register: int = 40001, count: int = 5) -> Dict[str, Any]:
        """Reads holding registers from the simulated PLC hardware."""
        if not self.connected:
            return {"error": "PLC connection offline", "connected": False}

        # Add mild sensor variance
        self.holding_registers[40001] = int(random.normalvariate(22000, 500))
        self.holding_registers[40002] = int(random.normalvariate(31000, 800))
        self.holding_registers[40003] = int(random.normalvariate(425, 10))
        self.holding_registers[40004] = int(random.normalvariate(684, 15))

        return {
            "connected": True,
            "plc_ip": self.ip_address,
            "timestamp": datetime.datetime.now().isoformat(),
            "telemetry": {
                "electricity_kwh": round(self.holding_registers[40001] / 10.0, 2),
                "water_litres": round(self.holding_registers[40002] / 10.0, 2),
                "pressure_psi": round(self.holding_registers[40003] / 10.0, 2),
                "thermal_temp_c": round(self.holding_registers[40004] / 10.0, 2),
                "valve_position_pct": self.holding_registers[40005]
            }
        }

    def write_actuator_coil(self, register: int, value: int) -> Dict[str, Any]:
        """Writes an actuation command to a PLC register (e.g. throttling valve relay)."""
        if register in self.holding_registers:
            self.holding_registers[register] = value
            return {"status": "success", "register": register, "new_value": value}
        return {"status": "error", "message": f"Register {register} out of bounds"}
