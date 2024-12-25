import sys
from colorama import init, Fore
init() 

def report(line, message):
    print(f"Line [{line}] Error: {message}")
    sys.exit(1)

def critical_error(message):
    print("CRITICAL ERROR")
    print(message)
    print(Fore.RED + message + Fore.RESET)
    sys.exit(1)
