#!/usr/bin/python3
import sys,json,time,math,re
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
            title = re.sub(r"(^[ \-_+ \t*$%@!()+=\"'/\\]*\[[^\[\]]*\])|(\[[^\]\[]*\][^\[\]]*)", "",data["topic_title"]).split("/")[0]
            movie = Movie.objects.search(title)[0]
            log(title)
            log(movie.title)
            r= (movie.rating if not movie.rating is None else 0)
            log(r)
            val= math.floor((r+1)*val)
        except ImportError:
            pass
        except ConnectionError:
            pass
        except IndexError:
            pass
    out(val)
else:
    out(0)
