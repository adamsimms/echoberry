ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i sounds/forest_reduced5db.mp3 -filter_complex amerge=inputs=2 -f mp3  icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul -af "aecho=0.8:0.88:100:1"

ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i sounds/forest_reduced15db.mp3 -filter_complex amerge=inputs=2 -f mp3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul

ffmpeg
-ac 1
-re
-f alsa
-i hw:1,0
-re
-i sounds/forest_reduced15db.mp3 
-filter_complex amerge=inputs=2
-f mp3 aecho=0.8:0.9:1000:0.3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul

aecho=0.8:0.9:1000:0.3



-af "aecho=0.8:0.9:1000:0.3"


ffmpeg -ac 1 -re -f alsa -i hw:1,0 -map 0 -c:v copy -af aecho=0.8:0.88:1:0.7 -f mp3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul -re -i sounds/forest_reduced5db.mp3 -filter_complex amerge=inputs=2


ffmpeg -ac 1 -re -f alsa -i hw:1,0 -af "aecho=0.8:0.88:100:1" -re -i sounds/forest_1h30.mp3 -filter_complex amerge=inputs=2 -f mp3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul


ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i sounds/forest_reduced5db.mp3 -filter_complex amerge=inputs=2 -f mp3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul

mplayer -ao alsa:device=hw=1.0 http://54.89.215.33:8000/echoberry-yul
