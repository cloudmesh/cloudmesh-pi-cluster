import os

class Led:

    @staticmethod
    def set(led, status):
        if str(led) not in ["1", "0"]:
            raise ValueError("Led number is wrong")
        state = str(status).lower in ["1", "on", "true", "+"]
        if state:
            state = 1
        else:
            state = 0

        os.system(f"echo {state} | sudo tee /sys/class/leds/led{led}/brightness")