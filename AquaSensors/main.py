import argparse

def main():
    parser = argparse.ArgumentParser(description="Aqua Dreams IoT project")
    parser.add_argument('-t', '--temp_sensor', default=False, type=str, help='Read temperature sensor') 
    args = parser.parse_args()
    if args.temp_sensor == "true":
        print("Reading temperature sensor")
    else:
        print("Running main mode")


if __name__ == "__main__":
    pass
