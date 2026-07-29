"""
backend/telemetry_streamer.py
Continuous background telemetry streaming daemon for HydroThermal Nexus-AI.
Simulates field IoT sensor nodes by streaming periodic telemetry into the database.
"""

import time
import datetime
import random
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend import database as db
import config


def generate_sensor_reading():
    """Generates a single realistic multi-sensor reading."""
    elec = round(random.normalvariate(config.ELEC_BASE_MEAN, config.ELEC_BASE_STD), 2)
    water = round(random.normalvariate(config.WATER_BASE_MEAN, config.WATER_BASE_STD), 2)
    outdoor_temp = round(random.uniform(28.0, 38.0), 1)
    humidity = round(random.uniform(45.0, 85.0), 1)
    pressure = round(random.normalvariate(42.5, 1.2), 2)
    thermal_temp = round(random.normalvariate(68.4, 2.5), 2)

    # 3% chance of natural anomaly injection
    if random.random() < 0.03:
        pressure = 27.5
        thermal_temp = 101.5

    return elec, water, outdoor_temp, humidity, pressure, thermal_temp


def run_streamer(interval_seconds: float = 10.0, max_iterations: int = None):
    """Runs the continuous telemetry streamer loop."""
    print(f"[STREAMER] Starting HydroThermal IoT Telemetry Streamer (interval={interval_seconds}s)...")
    db.initialize_all_databases()

    iterations = 0
    while True:
        try:
            elec, water, outdoor_temp, humidity, pressure, thermal_temp = generate_sensor_reading()
            db.save_telemetry(elec, water, outdoor_temp, humidity, pressure, thermal_temp)
            iterations += 1
            print(f"[STREAMER] Pushed reading #{iterations}: Elec={elec}kWh, Water={water}L, Pressure={pressure}PSI, Thermal={thermal_temp}°C")

            if max_iterations and iterations >= max_iterations:
                print("[STREAMER] Reached max iterations limit. Exiting.")
                break

            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("[STREAMER] Telemetry streamer stopped by user.")
            break
        except Exception as e:
            print(f"[STREAMER ERROR] {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    run_streamer(interval_seconds=10.0)
