#Модуль розбору айдіофайлу з кодуванням id3v2.3 і id3v2.4

#Словник, що зберігатиме знайдені теги
frameList={}

def readChar(file):
    c=file.read(1)
    c=chr(ord(c))
    return c

def readByte(file):
    c=file.read(1)
    c=ord(c)
    return c

def readString(file,size):
    s=""
    for i in range(size):
        s+=readChar(file)
    return s

#фія розбору розміру тегу
def compileSize(file):
    res=0;
    for i in range(3):
        tmp=readByte(file)
        tmp=tmp*(2**(8*(3-i)))
        tmp=tmp/(2**(3-i))
        res+=tmp
    res+=readByte(file)
    res=int(res)
    return res

def parsHeader(file):
    head ={"id":"","version":0,"falgs":0,"size":0}
    name=readString(file, 3)
    if(name=="ID3"):
        head["id"]=name
        ver=readByte(file)
        head["version"]=ver
        file.seek(file.tell()+1)    #пропустимо revision
        flag=readByte(file)
        head["flags"]=flag
        head["size"]=int(compileSize(file))
    return head

def parsFile(fileName):
    passed = 0  # ксть розібраних байтів
    with open(fileName,"rb") as f:
        header = parsHeader(f)
        while( passed<header["size"] ):
            passed += parsFrame(f)    
    info=compileRecordInfo(f)
    print (header)
    print (info)


def parsFrame(file):
    name=readString(file,4)
    frame = {"id":"","size":0,"flags":0,"text":""}
    frame["id"]=name
    size=compileSize(file)
    frame["size"]=size
    flag=readByte(file)
    flag=flag*(2**8)            #зсув на 8
    flag=flag+readByte(file)
    text=readString(file, size)
    frame["text"]=text
    frameList[name]=frame
    return size

def compileRecordInfo(file):
    listOfMust = [ "TALB", "TIT1", "TIT2", "TOPE",
                   "TRCK", "TYER", "TPE1", "TOFN"]
    dictOfMust = {}
    for i in range(len(listOfMust)):
        if (frameList.get(listOfMust[i])!=None):
            dictOfMust[listOfMust[i]] = frameList[listOfMust[i]]["text"]
    return dictOfMust
        
parsFile ("NC 2 U.mp3")


