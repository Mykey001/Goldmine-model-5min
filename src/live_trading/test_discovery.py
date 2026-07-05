"""
Test MT5 terminal discovery
"""
import sys
import logging
from mt5_terminal_manager import MT5TerminalManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def main():
    print("=" * 60)
    print("MT5 TERMINAL DISCOVERY TEST")
    print("=" * 60)
    
    # Create terminal manager
    tm = MT5TerminalManager()
    
    # Discover terminals
    print("\nDiscovering terminals...")
    terminals = tm.discover_terminals()
    
    print(f"\nFound {len(terminals)} terminal(s):\n")
    
    if not terminals:
        print("❌ No terminals found!")
        print("\nSearching in these paths:")
        search_paths = [
            r"C:\Program Files\MetaTrader 5",
            r"C:\Program Files (x86)\MetaTrader 5",
        ]
        for path in search_paths:
            print(f"  - {path}")
        print("\nPlease ensure MT5 is installed.")
    else:
        for i, terminal in enumerate(terminals, 1):
            print(f"Terminal {i}:")
            print(f"  ID: {terminal['id']}")
            print(f"  Name: {terminal['name']}")
            print(f"  Broker: {terminal['broker']}")
            print(f"  Path: {terminal['path']}")
            print(f"  Connected: {terminal['connected']}")
            print()
    
    print("=" * 60)
    
    return terminals

if __name__ == "__main__":
    terminals = main()
    sys.exit(0 if terminals else 1)
