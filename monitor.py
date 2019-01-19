import json
import os
import util

class monitor:
    def __init__(self):
        self.dir     = "monitor/"
        self.dblimit = 5
        self.dbfile  = self.dir + "db.mnc"
        self.latest  = {}
        self.snapshots_cnt = 0
        self.snapshots = {}
        loaded       = self.load()
        if(loaded != {}):
            self.latest    = loaded[list(loaded)[:1][0]]
            self.snapshots_cnt = len(loaded)
            self.snapshots = list(loaded)

    def store(self, dct):
        dct = dict(sorted(dct.items()))
        enc = ""
        if(len(dct) > self.dblimit):
            lst = sorted(dct.items())
            cmd = "rm %s%s" % (self.dir, list(lst)[0][0])
            os.system(cmd)
            cut = dict(list(lst)[1:])
            enc = json.dumps(cut, sort_keys=True)
            self.snapshots_cnt = len(cut)
            self.snapshots = cut
        else:
            dct = dict(sorted(dct.items()))
            enc = json.dumps(dct, sort_keys=True)
            self.snapshots_cnt = len(dct)
            self.snapshots = dct
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

    def get_latest(self, snapshot):
        if "imagefile" in self.latest and "objects" in self.latest:
            if snapshot == 0:
                return self.dir + self.latest["imagefile"],\
                       self.latest["objects"],\
                       self.latest["imagefile"],\
                       self.snapshots_cnt
            else:
                if snapshot >= 1 and snapshot <= len(self.snapshots):
                    itm = list(self.snapshots.items())[snapshot - 1]
                    return self.dir + itm[1]['imagefile'],\
                           itm[1]['objects'],\
                           itm[0],\
                           self.snapshots_cnt
                else:
                    return "", 0, 0, self.snapshots_cnt
        else:
            return "", 0, 0, 0
