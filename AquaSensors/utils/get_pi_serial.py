def get_pi_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.strip().split(": ")[1]
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    print(get_pi_serial())
