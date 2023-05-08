import RPi.GPIO as GPIO
import argparse
from time import sleep
from os import system
from texttable import Texttable

'''torcheck.py: Werkstatt-Tor Überwachung
Verwendung:
    python torcheck.py [-h] [-m MODE]

optionale Argumente:
 -h, --help  zeigt diese Hilfsmeldung an und beendet das Programm
 -m, --mode  verwendet den BCM- oder BOARD-Modus (Standard ist BCM)
'''

__author__ = "Robert Richardson"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Robert Richardson"
__email__ = "robert-richardson@web.de"

parser = argparse.ArgumentParser(description="Werkstatt-Tor Überwachung")
parser.add_argument('-m', '--mode', type=str, help='manuell den Modus BCM oder BOARD einstellen (Standard ist BCM)')
args = parser.parse_args()

NEW_LINE = '\n'

def print_logo(mode):
    if mode == "BCM":
        m = "  " + mode
    else:
        m = mode
    print(" ┌┬┐┌─┐┬─┐┌─┐┬ ┬┌─┐┌─┐┬┌─ ┌─┐┬ ┬  GPIO-Modus:")
    print("  │ │ │├┬┘│  ├─┤├┤ │  ├┴┐ ├─┘└┬┘  ><    ", m)
    print("  ┴ └─┘┴└─└─┘┴ ┴└─┘└─┘┴ ┴o┴   ┴")


def print_illustration(gates_ascii):
    print(" ´ / | \ `     |Y| _ _ _ _          ><   ><")
    print("   _ _ _ _ _ _/| | |Y|   /|_ _ _       _ _ _")
    print(" /_ _ _ _ _ _/- - - - - - - - -/| _ _/_ _ _/|")
    print(" | |_| |_| |_| N e t t m a n n |/_ _ | |_| ||")
    print(" | 1__  2__  3__  4__  5__  6__  7__  8__  ||")
    print(gates_ascii, "/")
    print("___/ /__/ /__/ /__/ /__/ /__/ /__/ /__/ /___")
    print("_  _  _  _  _  _  _  _  _  _  _  _  _  _  _")
    print("__________________________________________")

if args.mode: # WENN args.mode vorhanden -> Argument wurde übergeben
    mode = args.mode.upper() # überschreibe mode mit Argument
else:
    mode = "BCM"

if mode == "BCM":
    # [(Taster-Pin,LED-Pin),(Taster-Pin,LED-Pin),...]
    pins = [(2, 14), (3, 15), (4, 23), (17, 24), (27, 25), (22, 8), (10, 7), (9, 12)]
    GPIO.setmode(GPIO.BCM)

elif mode == "BOARD":
    pins = [(3, 8), (5, 10), (7, 16), (11, 18), (13, 22), (15, 24), (19, 26), (21, 32)]
    GPIO.setmode(GPIO.BOARD)

else:
    print(f"Der angegebene Modus existiert nicht.{NEW_LINE}Bitte einen gültigen Modus angeben (BOARD oder BCM)")
    raise SystemExit(0)

# Pin-Initialisierung
for pinTuple in pins:
    GPIO.setup(pinTuple[0], GPIO.IN)
    GPIO.setup(pinTuple[1], GPIO.OUT)

# Bool, um den ersten Durchlauf zu unterscheiden
first_loop = True

try:
    # Während das Programm läuft
    while True:

        # Loop-Verzögerung
        sleep(0.25)

        # Variablen initialisieren bzw. zurücksetzen
        sth_happened = False
        open_amount = 0

        # Leeres Tabellenobjekt erstellen
        table = Texttable()

        # Tabellenspalten definieren
        table.add_row(["Tor-Nummer", "Input (Tast.)", "Output (LED)"])

        # Letzte Zeile der ASCII-Illustration initialisieren
        gates_ascii = " |_|"

        # Für jede Taste:
        for index in range(len(pins)):

            # GPIO Pin-Nummer
            taster = pins[index][0]

            # GPIO Pin-Nummer
            led = pins[index][1]

            # Wenn der Input-Wert nicht mit dem Output-Wert übereinstimmt:
            if GPIO.input(taster) != GPIO.input(led):

                # LED entsprechend an bzw aus schalten
                GPIO.output(led, GPIO.input(taster))
                sth_happened = True  # -> Bildschirm muss aktualisiert werden

            # Wenn Taster gedrückt (Tor geöffnet):
            if GPIO.input(taster):
                open_amount += 1

                # Aktives Tor und zugehörige Pinbelegung der Tabelle hinzufügen
                table.add_row([index + 1, pins[index][0], pins[index][1]])

                # ASCII-Illustration (offenes Tor hinzufügen)
                gates_ascii += "  |_|"
            else:
                # ASCII-Illustration (geschlossenes Tor hinzufügen)
                gates_ascii += "‡‡|_|"

        # Wenn der Bildschirm aktualisiert werden muss:
        if sth_happened or first_loop:
            first_loop = False

            # Bisherige Ausgabe löschen
            system('clear')
            print_logo(mode)
            print_illustration(gates_ascii)

            if open_amount == 1:
                print(" Es ist ein Werkstatt-Tor geöffnet:")

            elif open_amount > 1:
                print(f" Es sind {open_amount} Werkstatt-Tore geöffnet:")

            else:
                print(" Alle Werkstatt-Tore sind geschlossen.")

            if open_amount > 0:
                print(table.draw())

except KeyboardInterrupt:
    print(f"{NEW_LINE}Programm wird beendet.")

finally:
    GPIO.cleanup()
