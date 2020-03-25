import os

class LED:

    @staticmethod
    def set(led=None, value=1):
        if led not in [1, 0]:
            raise ValueError("Led number is wrong")
        state = value.lower() in ["1", "on", "true", "+"]
        if state:
            state = 1
        else:
            state = 0

        if led == 0:
            # switch it first off, technically we should disable the trigger first
            # then we do not have to switch it off
            command = f"echo 0 | sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"
            os.system(command)
            
        command = f"echo {state} | sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"

        os.system(command)
        
