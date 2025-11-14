"""
AquaDreams Main Entry Point Module

This module provides the command-line interface (CLI) entry point for the AquaDreams
IoT aquarium monitoring system. It handles argument parsing and dispatches to the
appropriate sensor modules based on user input.

The main function can be invoked as a script or as an installed console script entry point,
making it the primary way to interact with the AquaDreams sensor suite from the command line.

Functions:
    main(): Primary entry point that handles CLI argument parsing and sensor dispatch.

Usage:
    As a module:
        $ python -m AquaSensors.main --temp_sensor true
    
    As an installed console script (if configured in pyproject.toml):
        $ aquadreams --temp_sensor true

Command-line Options:
    -t, --temp_sensor: Enable temperature sensor monitoring mode
    
Future Extensions:
    This module is designed to be extended with additional sensor types and monitoring
    modes as the AquaDreams system grows (e.g., pH sensors, water level sensors, etc.).
"""

import argparse
from .aqua_dream_temp_reader import TemperaturePublisher

def main():
    """
    Entry point for the AquaDreams IoT monitoring system.
    
    This function serves as the command-line interface for the AquaDreams aquarium
    monitoring system. It parses command-line arguments to determine which sensor
    functionality to run.
    
    Command-line Arguments:
        -t, --temp_sensor (str): Enable temperature sensor monitoring.
            Set to "true" to start continuous temperature monitoring.
            Default: False
    
    Examples:
        Run temperature monitoring:
            $ python -m AquaSensors.main --temp_sensor true
        
        Run in default/main mode:
            $ python -m AquaSensors.main
    
    Notes:
        - When temp_sensor is set to "true", the function starts the TemperaturePublisher
          in continuous monitoring mode, which will run indefinitely until interrupted.
        - Use Ctrl+C to stop the temperature monitoring loop.
    """
    parser = argparse.ArgumentParser(description="Aqua Dreams IoT project")
    parser.add_argument('-t', '--temp_sensor', default=False, type=str, help='Read temperature sensor') 
    args = parser.parse_args()
    if args.temp_sensor == "true":
        print("Reading temperature sensor")
        publisher = TemperaturePublisher()
        publisher.run()
    else:
        print("Running main mode")


if __name__ == "__main__":
    pass
