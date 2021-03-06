#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json,gzip,os,urllib.request,re,urllib.parse,urllib.error
import pathlib,configparser,sqlite3,argparse,time,subprocess,random
class Config:
    def __init__(self,config_path,init_config=lambda x: {}):
        self.path = pathlib.Path(config_path)
        self.path.parent.mkdir(0o777,True,True)
        self.parser=configparser.ConfigParser()
        if not self.path.exists():
            self.parser.read_dict(init_config(self.path))
            with self.path.open("w") as file:
                self.parser.write(file)
        with self.path.open("r") as file:
            self.parser.read_file(file)
    def __getattr__(self, name):
        return self.parser.get("DEFAULT",name)
    def set(self, name, value):
        self.parser.set("DEFAULT",name,str(value))
    def save(self):
        with self.path.open("w") as file:
                self.parser.write(file)
TEST=False
RUTRACKER_API = "http://api.rutracker.org/v1"
RUTRACKER_FORUM="http://rutracker.org/forum/index.php"
DEFAULT_CFG={
    "DEFAULT":{
        "api":RUTRACKER_API,
        "forum":RUTRACKER_FORUM,
        "subforum_regex":"^Фильмы.*",
        "torrent_db_path":".parrot/torrent.db",
        "request_delay":500,
        "parallel_rating":False,
        "subforums":[
            
        ],
        "populate_db":False,
        "limit_row_count":-1,
        "rating_script":"./3_14rate.py",
        "min_rating":0,
        "w2w_percentile":70,
        "add_torrent_cmd":"transmission-remote -a ",
        "announcers":'["http://bt.t-ru.org/ann","http://bt2.t-ru.org/ann","http://bt3.t-ru.org/ann","http://bt4.t-ru.org/ann","http://bt5.t-ru.org/ann","http://retracker.local/announce"]',
        
    }
}
DB_CREATE_QUERY="""
CREATE VIRTUAL TABLE IF NOT EXISTS torrent USING fts4(
    name text,
    topic_id INTEGER,
    size INTEGER,
    hash text,
    rating INTEGER,
    watched INTEGER
);
"""

DB_DELETE_QUERY="""
DELETE FROM torrent;
"""

DB_INSERT_QUERY="""
INSERT INTO torrent(name,topic_id,size,hash,rating,watched) VALUES (?,?,?,?,?,0);
"""

DB_SEARCH_QUERY="""
SELECT rowid,* FROM torrent WHERE name MATCH ? ORDER BY CAST(rating AS NUMERIC) DESC;
"""

DB_W2W_GET_QUERY = """
SELECT * FROM ( SELECT rowid,* FROM torrent WHERE watched MATCH 0 ORDER BY CAST(rating AS NUMERIC) LIMIT 10 OFFSET (SELECT COUNT(*) FROM torrent WHERE watched MATCH 0) * ? /100 - 1) ORDER BY CAST(rating AS NUMERIC) DESC;
"""

DB_SET_WATCHED_QUERY="""
UPDATE torrent SET watched=1 WHERE rowid=?
"""

parser = argparse.ArgumentParser()
parser.add_argument("-s","--search",nargs='+',help="Query to search in topic database")
parser.add_argument("-w","--what2watch",help="Select n-th percentile by rating and choose random entry",action='store_true')
parser.add_argument("-d","--repopulate",help="Force repopulation of the topic database",action="store_true")
parser.add_argument("-S","--silent",help="Do not output log",action="store_true")
parser.add_argument("-n","--option",help="Get link for n-th search result")
parser.add_argument("-a","--add",help="Add torrent to torrent client",action="store_true")
args = parser.parse_args()
cfg = Config(".parrot/parrot_config.ini",lambda x: DEFAULT_CFG)
def get_subforums():
    return json.loads(gzip.open(urllib.request.urlopen(cfg.api+"/static/cat_forum_tree")).read().decode("utf-8"))
def get_topics(topic_id):
    try:
        time.sleep(int(cfg.request_delay)/1000.0)
        return json.loads(gzip.open(urllib.request.urlopen(cfg.api+"/static/pvc/f/"+str(topic_id))).read().decode("utf-8"))
    except urllib.error.HTTPError as http:
        print("Could not get topics at "+cfg.api+"/static/pvc/f/"+str(topic_id)+" : "+str(http))
        return {"result":{}}
def get_tor_data(topics):
    time.sleep(int(cfg.request_delay)/1000.0)
    url = cfg.api+"/get_tor_topic_data?"+urllib.parse.urlencode({"by":"topic_id","val":",".join(topics)})
    #print(url)
    data = urllib.request.urlopen(url)
    
    try:
        dataj = gzip.open(data).read().decode("utf-8")
        return json.loads(dataj)
    except OSError:
        dataj = urllib.request.urlopen(url)
        
    try:
        return json.loads(dataj.read().decode("utf-8"))
    except json.JSONDecodeError:
        #print(dataj.read())
        return {"result":[]}
def split_topics_by_limit(t):
    time.sleep(int(cfg.request_delay)/1000.0)
    limit = json.loads(urllib.request.urlopen(cfg.api+"/get_limit").read().decode("utf-8"))["result"]["limit"]
    k=0
    l=[]
    while k<len(t):
        l.append(list(t[k:min(k+limit,len(t))]))
        k+=limit
    return l
def printTree(tree,captions1,captions2,indent=0):

    for i in tree:
        try:
            print("    "*indent+"+ "+captions1[str(i)])
        except KeyError:
            try:
                print("    "*indent+"+ "+captions2[str(i)])
            except KeyError as e:
                print("    "*indent+"+ @"+str(i))
                raise e
        
        if type(tree)==dict:
            printTree(tree[i],captions1,captions2,indent+1)
def get_rating(tor_data):
    if not len(cfg.rating_script):
        return str(0)
    try:
        return subprocess.check_output([os.path.realpath(cfg.rating_script),json.dumps(tor_data)]).decode("utf-8")
    except subprocess.CalledProcessError:
        return str(0)
    return str(0)
def r8_batch(data):
    rating={}
    ps={}
    for k in data:
        if data[k]:
            if not args.silent:
                print("Spawning process for rating topic",k,"...")
            ps[k]=subprocess.Popen([os.path.realpath(cfg.rating_script),json.dumps(data[k])],stdout=subprocess.PIPE)
    for k in data:
        if data[k]:
            out,err = ps[k].communicate()
            if not args.silent:
                print("Finished rating topic",k)
            rating [k]=out.decode("utf-8") if out and len(out) else str(0)
    return rating
    
def get_magnet(name,t_hash):
    return "magnet:?xt=urn:btih:"+t_hash.lower()+"&dn="+urllib.parse.quote(name)+"&"+"&".join(map(lambda x:"tr="+str(x),json.loads(cfg.announcers)))#"&tr=http://bt.t-ru.org/ann&tr=http://retracker.local/announce"
if len(json.loads(cfg.subforums))==0:
    subs = get_subforums()['result']
    sub_pattern = re.compile(cfg.subforum_regex)
    if not args.silent:
        printTree(subs["tree"],subs["c"],subs["f"])
    selected=[]
    for fid in subs['f']:
        if sub_pattern.match(subs['f'][fid]):
            if not args.silent:
                print("Selecting subforum ["+str(fid)+"] "+str(subs['f'][fid]))
            selected.append(fid)
    cfg.set("subforums",json.dumps(selected))
    cfg.set("populate_db",True)
    cfg.save()
    subforums = selected
else:
    subforums = json.loads(cfg.subforums)
db_con = sqlite3.connect(cfg.torrent_db_path)
db_cursor = db_con.cursor()
db_cursor.execute(DB_CREATE_QUERY)
if cfg.populate_db == "True" or args.repopulate:
    cfg.set("populate_db",False)
    cfg.save()
    db_cursor.execute(DB_DELETE_QUERY)
    size = 0
    if subforums:
        random.shuffle(subforums)
    for forum in subforums:
        #break

        topics=list(get_topics(forum)["result"].keys())
        
        for batch in split_topics_by_limit(topics):
            data = get_tor_data(list(batch))["result"]
            p = cfg.parallel_rating == "True"
            if p:
                r8 = r8_batch(data)
            for k in data:
                if data[k]:
                    if not args.silent:
                        print("Found topic: "+data[k]["topic_title"])
                    rating = str(r8[k])if p else str (get_rating(data[k]))
                    if not args.silent:
                        print("Rating:"+rating)
                    if int(rating) >=int(cfg.min_rating):
                        if not args.silent:
                            print("Rating is at least "+cfg.min_rating+". Adding topic to DB...")
                        db_cursor.execute(DB_INSERT_QUERY,(data[k]["topic_title"],str(k),data[k]["size"],data[k]["info_hash"],rating))
                        size += 1
                        if size>=int(cfg.limit_row_count) and int(cfg.limit_row_count)>0:
                            db_con.commit()
                            break
                    
            db_con.commit()
            if TEST or size>=int(cfg.limit_row_count) and int(cfg.limit_row_count)>0:
                break
        
        if TEST or size>=int(cfg.limit_row_count) and int(cfg.limit_row_count)>0:
            break

if args.search:
    bind = tuple([' '.join(map(str,args.search))])
    search_result = list(db_cursor.execute(DB_SEARCH_QUERY,bind))
    if args.option:
        N=int(args.option)
        db_cursor.execute(DB_SET_WATCHED_QUERY,tuple([search_result[N][0]]))
        db_con.commit()
        if args.add:
            os.system(cfg.add_torrent_cmd +" '"+get_magnet(search_result[N][1],search_result[N][4])+"'")
        else:
            print(get_magnet(search_result[N][1],search_result[N][4]))
    else:
        for i,row in enumerate(search_result):
            watched = row[6] != 0
          
            formatted = not args.silent
            s = str(i)+". "+row[1]+"| [ "+row[5]+" * ]"
            print(("\033[1m{}\033[0m" if watched and formatted else "{}").format(s))
elif args.what2watch:
    bind = tuple([str(cfg.w2w_percentile)])
    search_result = list(db_cursor.execute(DB_W2W_GET_QUERY,bind))
    if args.option:
        N=int(args.option)
        if N<0:
            N=random.randrange(len(search_result))
        db_cursor.execute(DB_SET_WATCHED_QUERY,tuple([search_result[N][0]]))
        db_con.commit()
        if args.add:
            os.system(cfg.add_torrent_cmd +" '"+get_magnet(search_result[N][1],search_result[N][4])+"'")
        else:
            print(get_magnet(search_result[N][1],search_result[N][4]))
    else:
        for i,row in enumerate(search_result):
            print(str(i)+". ",row[1],"| [ "+row[5]+" * ]")



