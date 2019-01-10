import datetime

class bcolors:
    BLACK     = '\033[90m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    MAGENTA   = '\033[95m'
    CYAN      = '\033[96m'
    WHITE     = '\033[97m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'

class level:
    DEBUG   = 0
    INFO    = 1
    WARNING = 2
    ERROR   = 3

class mlog:
    @staticmethod
    def output(lvl, msg):
        if(lvl == level.DEBUG):     color = bcolors.GREEN
        elif(lvl == level.INFO):    color = bcolors.BLUE
        elif(lvl == level.WARNING): color = bcolors.YELLOW
        elif(lvl == level.ERROR):   color = bcolors.RED
        else:                       color = bcolors.WHITE
        tm = datetime.datetime.now().strftime("%d/%m/%Y %H:%m:%S")
        print(color+tm+": "+msg+bcolors.ENDC)

    @staticmethod
    def debug(msg):
        mlog.output(level.DEBUG, msg)

    @staticmethod
    def info( msg):
        mlog.output(level.INFO, msg)

    @staticmethod
    def warning(msg):
        mlog.output(level.WARNING, msg)

    @staticmethod
    def error(msg):
        mlog.output(level.ERROR, msg)
