#!/usr/local/bin/python3
import sys,json,time,math
LOG = False
KP = True
data = json.loads(sys.argv[1])
def out(string):
    print(str(string),end="")
    exit(0)
if LOG: print(data,file=sys.stderr)
if data["tor_status"] == 2:
    val = math.floor(int(data["seeders"])*2**40//int(data["size"])*24*60*60//(time.time()-int(data["seeder_last_seen"])))
    if KP:
        try:
            if LOG:print("KP lib found",file=sys.stderr)
            from kinopoisk.movie import Movie
            movie = Movie.objects.search( data["topic_title"].split("/")[0])[0]
            if LOG: print(movie.title,file=sys.stderr)
            r= (movie.rating if not movie.rating is None else 0)
            if LOG: print(r,file=sys.stderr)
            val= math.floor((r+1)*val)
        except ImportError:
            pass
    out(val)
else:
    out(0)