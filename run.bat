cd game/python

:: Open Game.py in a new window
start cmd /c "python game.py"

:: Open Server.py in a new window after Game.py finishes (use ping for delay)
start cmd /c "python server.py"

:: Open HTTP Server in a new window after Server.py finishes
cd ../Webpage
start cmd /c "http-server -p 3000 --cors"