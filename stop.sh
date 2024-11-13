BOTPID=$(ps aux | grep '[a]lbumbot.py' | awk '{print $2}')
kill $BOTPID 2> /dev/null

echo Bot killed!