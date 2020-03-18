#!/usr/bin/python
import sys,json,time,math
LOG = False
KP = True
data = json.loads(sys.argv[1])
def out(string):
    sys.stdout.write(str(int(string)))
    sys.stdout.flush()
    exit(0)
def log(msg):
    if LOG:
        sys.stderr.write(str(msg)+"\n")
        sys.stderr.flush()

log(data)
if data["tor_status"] == 2:
    val = math.floor(int(data["seeders"])*2**40//int(data["size"])*24*60*60//(time.time()-int(data["seeder_last_seen"])))
    if KP:
        try:
            log("KP lib found")
            from kinopoisk.movie import Movie
            movie = Movie.objects.search( data["topic_title"].split("/")[0])[0]
            log(movie.title)
            r= (movie.rating if not movie.rating is None else 0)
            log(r)
            val= math.floor((r+1)*val)
        except ImportError:
            pass
    out(val)
else:
    out(0)