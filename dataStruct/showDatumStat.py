import stockdata
import os
from os.path import join, getsize


def getDirSize(dir):
    size = 0
    count ,errs = 0 , 0
    errfiles = list()
    for root, dirs, files in os.walk(dir):
        for name in files:
            try:
                size += getsize(join(root, name))
                count += 1
            except FileNotFoundError as e:
                errs += 1
                errfiles.append(e.filename)
            continue
    return (count, errs, size)

def getFullPath(upfold,code):
    """ given stockcode , make full path of day ,lc1 lc5 files with full path"""
    subdir = ["lday","fzline","minline"]
    sdir = "sh"
    pathlist = []
    if code[:2] in ["00","30","39"]:
        sdir = "sz"
    for sub in subdir:
        # fp = upfold + '/' +sdir +'/' + sub  # Unix like
        fp = upfold + '\\' +sdir +'\\' + sub
        if sub == "lday":
            ext= ".day"
        elif sub == "fzline":
            ext= ".lc5"
        elif sub == "minline":
            ext= ".lc1"
        # fullname = fp+'/' +sdir+code+ext
        fullname = fp+'\\' +sdir+code+ext
        try:
            assert os.path.isfile(fullname)
        except AssertionError as e:
            print(fullname, e)
        pathlist.append(fullname)

    return pathlist


def getTimeRange(names):
    tmranges = []
    for name in names:
        fn = name[-3:]  # filname suffix
        stockfile = name[-12:]
        if fn in ["lc1","lc5"]:
            tmfz = stockdata.minuteOfStock(name)
            dtrg = tmfz.getDatetimeRange()
            st = dtrg[0].strftime("%Y-%m-%d %X")
            end = dtrg[1].strftime("%Y-%m-%d %X")
            tmr = (stockfile,st,end)
        elif fn =="day":
            tmday = stockdata.daysDataOfStock(name)
            dtr = tmday.getDateRange()
            st = dtr[0].strftime("%Y-%m-%d")
            end = dtr[1].strftime("%Y-%m-%d")
            tmr  = (stockfile,st,end)
        if tmr not in tmranges:
            print("=======<<<<")
            tmranges.append(tmr)
    return tmranges

def printSubdirs(rtpath):
# traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(rtpath):
        path = root.split('/')
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            print(len(path) * '---', file)

if __name__ == '__main__':
    #upfold = r"/share/jcb_sina/vipdoc"  # Unix like
    #upfold = r"\share\jcb_sina\vipdoc"   # Windows Path
    #features = ["002594","600276","399001","601336"]
    features = ["399001","601336"]
    upfolder = r"X:\vipdoc"
    print (os.listdir(r"X:"))
    printSubdirs(upfolder)
    # upfolder = r"D:\tools\new_tdx\vipdoc"
    folderstat = getDirSize(upfolder)
    print("Folders Stat:", folderstat)
    for filename in features:
        tstfiles = getFullPath(upfolder,filename)
        timearray = getTimeRange(tstfiles)
        print ("Time Range Array==> ,",timearray)


