PCB_Coil

Dieses Projekt enthält ein Python-Skript zur parametrischen Erstellung von Spulen auf einer Leiterplatte (PCB) mithilfe von Matplotlib.

Projektstruktur

   •	venv/: Virtuelles Python-Environment.
   •	requirements.txt: Liste der Python-Abhängigkeiten.
   •	README.md: Projektbeschreibung und Installationsanleitung.
   •	Coil_Generator.py: Hauptscript, wird noch in mehrere Skripte aufgeteilt.

Installation und Einrichtung

1. Repository klonen oder herunterladen:
   ```bash
   git clone github.com/nathans-lab/........
   cd PCB_Coil
   ```
2. Erstellen und Aktivieren des virtuellen Environments:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   Nach der Aktivierung sollte (venv) im Terminal angezeigt werden.
3. Installieren der Abhängigkeiten:
   ```bash
   pip3 install -r requirements.txt
   ```
  

Verwendung

Führe dein Python-Skript aus, um die parametrischen Spulen zu erstellen:

   ```bash
   python3 Coil_Generator.py
   ```