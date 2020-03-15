#!/usr/local/bin/python3
import sys,json,time,math
data = json.loads(sys.argv[1])
def out(string):
    print(str(string),end="")
    exit(0)
#print(data,file=sys.stderr)
if data["tor_status"] == 2:
    val = math.floor(int(data["seeders"])*2**40//int(data["size"])*24*60*60//(time.time()-int(data["seeder_last_seen"])))
    out(val)
else:
    out(0)