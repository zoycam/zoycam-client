import json
import os
import util

class monitor:
    def __init__(self):
        self.dir     = "monitor/"
        self.dblimit = 5
        self.dbfile  = self.dir + "db.mnc"
        self.latest  = {}
        loaded       = self.load()
        if(loaded != {}):
            self.latest = loaded[list(loaded)[:1][0]]

    def store(self, dct):
        dct = dict(sorted(dct.items()))
        enc = ""
        if(len(dct) > self.dblimit):
            lst = sorted(dct.items())
            cmd = "rm %s%s" % (self.dir, list(lst)[0][0])
            os.system(cmd)
            enc = json.dumps(dict(list(lst)[1:]), sort_keys=True)
        else:
            enc = json.dumps(dict(sorted(dct.items())), sort_keys=True)
        util.fwrite(self.dbfile, "w", enc)

    def load(self):
        try:
            return json.loads(util.fread(self.dbfile, "r"))
        except:
            return {}

    def update(self, imagefile, objects, timestamp):
        dct = self.load()
        key = round(timestamp)
        cmd = "mv %s %s%s" % (imagefile, self.dir, key)
        os.system(cmd)
        self.latest   = { "imagefile" : str(key), "objects" : objects }
        dct[str(key)] = self.latest
        self.store(dct)

    def get_latest(self):
        if "imagefile" in self.latest and "objects" in self.latest:
            return self.dir + self.latest["imagefile"],\
                   self.latest["objects"],\
                   self.latest["imagefile"]
        else:
            return "", 0, 0
