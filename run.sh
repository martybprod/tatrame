#!/bin/zsh
# Align — coach de vie quotidien, 100 % local et déterministe (port 5073)
#
# Vibe Station cherche un run.sh en PREMIER (avant le chemin app.py), et
# c'est la convention de l'écosystème. `exec` remplace le shell par Python :
# le PID vu par Vibe est donc celui du vrai serveur, pas d'un wrapper — sinon
# le « Stop » tuerait le shell en laissant l'app orpheline sur le port.
cd "$(dirname "$0")"
exec ./venv/bin/python3 app.py
