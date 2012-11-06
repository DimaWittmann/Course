
"""
Модуль розбору айдіофайлу з кодуванням id3v2.3
"""
#Словник, що зберігатиме знайдені теги
__frameList={}
#список, що зберігає назви потрібних вреймів
__listOfDefFrame= [ "TALB", "TIT1", "TIT2", "TOPE",
                   "TRCK", "TYER", "TPE1", "TOFN"]


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

 
def compileSize(file):
    """
    Розбір байтів з розмрім фрейма,
    кожеy старший біт байта дорівнює нулю
    """
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

def parsFile(fileName,requiredFrames=__listOfDefFrame):
    """
    Виконує розбір файла від початку до кінця
    і повертає словник з фреймами, назви яких
    описані в RequiredFrames 
    """
    passed = 0  # ксть розібраних байтів
    try:
        with open(fileName,"rb") as f:
            header = parsHeader(f)
            while( passed<header["size"] ):
                passed += parsFrame(f)
    except:
        return
    
    info=compileRecordInfo(f,requiredFrames)
    return info


def parsFrame(file,encoding="Latin-1"):
    """
    Розбір наступного фрейму в файлі
    """
    name=readString(file,4)
    frame = {"id":"","size":0,"flags":0,"text":""}
    frame["id"]=name
    size=compileSize(file)
    frame["size"]=size
    flag=readByte(file)
    flag=flag*(2**8)            #зсув на 8
    flag=flag+readByte(file)
    text=file.read(size)
    frame["text"]=text
    __frameList[name]=frame
    return size


def decodeFrameInfo(dictOfFrames,encoding="Windows-1251"):
    """
    Декодувати текстові поля відповідним кодування Latin-1(windows-1251) чи utf-16 
    """
    decodedInfo={}
    for frame in dictOfFrames:
        if dictOfFrames[frame][0]==0:
            decodedInfo[frame] = bytes.decode( dictOfFrames[frame][1:],encoding)                
        elif dictOfFrames[frame][0]==1:
            decodedInfo[frame] = bytes.decode( dictOfFrames[frame][1:],encoding="utf-16")
        elif dictOfFrames[frame][0]==2:
            decodedInfo[frame] = bytes.decode( dictOfFrames[frame][1:],encoding="utf-16")
        elif dictOfFrames[frame][0]==3:
            decodedInfo[frame] = bytes.decode( dictOfFrames[frame][1:],encoding="utf-8")
    return decodedInfo
                

def compileRecordInfo(file,listOfRequir):
    """
    Збираєму з всіх розібраних фреймів потрібні для нас інформацію
    Отримуємо словник frameId : value
    @
    """
    dictOfRequir = {}
    for i in range(len(listOfRequir)):
        if (__frameList.get(listOfRequir[i])!=None):
            dictOfRequir[listOfRequir[i]] = __frameList[listOfRequir[i]]["text"]
    return dictOfRequir

       
info=parsFile ("C://Users//Wittmann//Documents//GitHub//Course//res//NC 2 U.mp3")
if (info):
    print(decodeFrameInfo(info))


