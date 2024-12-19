import sys

def report(line, message):
    print(f"Line [{line}] Error: {message}")
    sys.exit(1)
