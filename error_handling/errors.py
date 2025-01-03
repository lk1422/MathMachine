import sys
from colorama import init, Fore
init() 

def report(line, message):
    print(f"Line [{line}] Error: {message}")
    sys.exit(1)

def critical_error(message):
    print(Fore.RED + "ERROR: " + message + Fore.RESET)
    sys.exit(1)
