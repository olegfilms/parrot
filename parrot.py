#!/usr/local/bin/python3
import json,gzip,os,urllib.request,re,urllib.parse,urllib.error
import pathlib,configparser,sqlite3,argparse,time,subprocess
class Config:
    def __init__(self,config_path,init_config=lambda x: {}):
        self.path = pathlib.Path(config_path).resolve()
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
TEST=True
RUTRACKER_API = "http://api.rutracker.org/v1"
RUTRACKER_FORUM="http://rutracker.org/forum/index.php"
DEFAULT_CFG={
    "DEFAULT":{
        "api":RUTRACKER_API,
        "forum":RUTRACKER_FORUM,

        "subforum_regex":"^Фильмы.*",
        "torrent_db_path":".parrot/torrent.db",
        "request_delay":5000,
        "subforums":[
            
        ],
        "populate_db":True,
        "rating_script":"./3_14rate.py",
        "min_rating":0,
        "announcers":'["http://bt.t-ru.org/ann","http://bt2.t-ru.org/ann","http://bt3.t-ru.org/ann","http://bt4.t-ru.org/ann","http://bt5.t-ru.org/ann","http://retracker.local/announce"]',
        
    }
}
DB_CREATE_QUERY="""
CREATE VIRTUAL TABLE IF NOT EXISTS torrent USING fts4(
    name text,
    topic_id INTEGER,
    size INTEGER,
    hash text,
    rating INTEGER
);
"""

DB_DELETE_QUERY="""
DELETE FROM torrent;
"""

DB_INSERT_QUERY="""
INSERT INTO torrent(name,topic_id,size,hash,rating) VALUES (?,?,?,?,?);
"""

DB_SEARCH_QUERY="""
SELECT * FROM torrent WHERE name MATCH ? ORDER BY CAST(rating AS NUMERIC)DESC;
"""
parser = argparse.ArgumentParser()
parser.add_argument("-s","--search",help="Query to search in topic database")
parser.add_argument("-d","--repopulate",help="Force repopulation of the topic database",action="store_true")
parser.add_argument("-S","--silent",help="Do not output log",action="store_true")
parser.add_argument("-n","--option",help="Get link for nth search result")
args = parser.parse_args()
cfg = Config(".parrot/parrot_config.ini",lambda x: DEFAULT_CFG)
def get_subforums():
    return json.load(gzip.open(urllib.request.urlopen(cfg.api+"/static/cat_forum_tree")))
def get_topics(topic_id):
    try:
        time.sleep(int(cfg.request_delay)/1000.0)
        return json.load(gzip.open(urllib.request.urlopen(cfg.api+"/static/pvc/f/"+str(topic_id))))
    except urllib.error.HTTPError as http:
        print("Could not get topics at "+cfg.api+"/static/pvc/f/"+str(topic_id)+" : "+str(http))
        return {"result":[]}
def get_tor_data(topics):
    time.sleep(int(cfg.request_delay)/1000.0)
    url = cfg.api+"/get_tor_topic_data?"+urllib.parse.urlencode({"by":"topic_id","val":",".join(topics)})
    #print(url)
    data = urllib.request.urlopen(url)
    
    try:
        dataj = gzip.open(data)
        return json.load(dataj)
    except OSError:
        dataj = urllib.request.urlopen(url)
        
    try:
        return json.load(dataj)
    except json.JSONDecodeError:
        #print(dataj.read())
        return {"result":[]}
def split_topics_by_limit(t):
    time.sleep(int(cfg.request_delay)/1000.0)
    limit = json.load(urllib.request.urlopen(cfg.api+"/get_limit"))["result"]["limit"]
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
        return subprocess.check_output([cfg.rating_script,json.dumps(tor_data)]).decode("utf-8")
    except subprocess.CalledProcessError:
        return str(0)
    return str(0)
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
    for forum in subforums:
        #break

        topics=list(get_topics(forum)["result"].keys())
        
        for batch in split_topics_by_limit(topics):
            data = get_tor_data(list(batch))["result"]
            for k in data:
                if data[k]:
                    if not args.silent:
                        print("Found topic: "+data[k]["topic_title"])
                    rating = str(get_rating(data[k]))
                    if not args.silent:
                        print("Rating:"+rating)
                    if int(rating) >=int(cfg.min_rating):
                        if not args.silent:
                            print("Rating is at least "+cfg.min_rating+". Adding topic to DB...")
                        db_cursor.execute(DB_INSERT_QUERY,(data[k]["topic_title"],str(k),data[k]["size"],data[k]["info_hash"],rating))
                    
            db_con.commit()
            if TEST:
                break
        if TEST:
            break

if args.search:
    bind = tuple([str(args.search)])
    search_result = list(db_cursor.execute(DB_SEARCH_QUERY,bind))
    if args.option:
        print(get_magnet(search_result[int(args.option)][0],search_result[int(args.option)][3]))
    else:
        for row in search_result:
            print(row[0],"| [ "+row[4]+" * ]")

