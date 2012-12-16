import os, time, io
"""
Модуль розбору айдіофайлу з кодуванням id3v2.4
"""
# Словник, що зберігатиме знайдені теги
frameList = {}
# список, що зберігає назви потрібних вреймів
listOfDefFrame = [ "TALB", "TIT1", "TIT2", "TOPE", "TPE2","TRCK", "TYER", "TPE1", "TOFN", "LINK", ]
header = {}

def readChar(file):
    c = file.read(1)
    c = chr(ord(c))
    return c

def readByte(file):
    c = file.read(1)
    c = ord(c)
    return c

def readString(file, size):        
    s = ""
    for i in range(size):
        s += readChar(file)   
    return s

 
def readInteger(file, numOfBytes=4):
    """
    Читання чілочислених даних,
    кожен старший біт байта дорівнює нулю
    """
    res = 0;
    for i in range(numOfBytes - 1):
        tmp = readByte(file)
        tmp = tmp << 8 * (numOfBytes- 1 - i)
        tmp = tmp >> (numOfBytes- 1 - i)
        res += tmp
    res += readByte(file)
    res = int(res)
    return res


def parseHeader(file):
    """
    Розбір заголовка файла
    """
    def parse():
        head = {"id":"", "version":0, "flags":0, "size":0}
        head["id"] = "ID3"
        ver = readByte(file)
        head["version"] = ver
        file.seek(file.tell() + 1)  # пропустимо revision версію
        flag = readByte(file)
        if ver == 4:
            head["flags"] = parseHeadFlags(flag)
        else:
            head["flags"]=flag
        head["size"] = int(readInteger(file))
        return head
        
    def parseHeadFlags(flagByte):
        flags = {"Unsynchronisation":0, "Extended header":0, "Experimental indicator":0, "Footer present":0}
        if flagByte & 0b10000000:
            flags["Unsynchronisation"] = 1
        if flagByte & 0b01000000:
            flags["Extended header"] = 1
        if flagByte & 0b00100000:
            flags["Experimental indicator"] = 1
        if flagByte & 0b00010000:
            flags["Footer present"] = 1
        return flags
    
    def parseExtendedHeader(file):
        
        def parseFlags(flagByte):
            flags = {"isUpdate":0, "CRC":0, "restrictions": 0}   
            if flagByte & 0b01000000:
                flags["isUpdate"] = 1
            if flagByte & 0b00100000:
                flags["CRC"] = 1
            if flagByte & 0b00010000:
                flags["restrictions"] = 1    
            return flags
        
        def parseRestrictions(flagByte):
            restrictions = {"tag size":0, "text encoding":0, "text size": 0, "image encoding":0, "image size":0}
            tmp = flagByte & 0b11000000
            tmp = tmp >> 6
            restrictions["tag size"] = tmp
            if [flagByte & ob00100000]:
                restrictions["text encoding"] = 1
            tmp = flagByte & 0b00011000   
            tmp = tmp >> 3
            restrictions["text size"] = tmp
            if [flagByte & 0b00000100]:
                restrictions["image encoding"] = 1
            tmp = flagByte & 0b00000011   
            restrictions["text size"] = tmp
            return restrictions
        
        ExtHeader = {"size":0, "flags":{}}
        ExtHeader["size"] = int(readInteger(file))
        file.seek(file.tell() + 1)    
        # пропустимо кількість байтів з пропорами (за стандартом для 2.4 вона дорівнює 1)
        ExtHeader["flags"] = parseFlags(readByte(file))
        
            
        if ExtHeader["flags"]["CRC"]:
            file.seek(file.tell() + 1) 
            # пропустимо кількість байтів з CRC (за стандартом для 2.4 вона дорівнює 5)
            ExtHeader["CRC"] = readInteger(file, 5)
        if ExtHeader["flags"]["restrictions"]:
            file.seek(file.tell() + 1) 
            # пропустимо кількість байтів з прапорами (за стандартом для 2.4 вона дорівнює 1)
            ExtHeader["restrictions"] = parseRestrictions(readByte(file))
        
    name = readString(file, 3)
    global header
    header = None
    if(name == "ID3"):
        header = parse()
    elif(file.__class__ == io.BufferedReader):
        file.seek(os.stat(file.name).size - 10)
        name = readString(file, 3)
        if (name == "3DI"):
            header = parse()
            file.seek(os.stat(file.name).size- 10 - header["size"] )
        
        if header["version"] == 4:
            if header["flags"]["Extended header"] :
                header["Extended header"] = parseExtendedHeader(file)
            
    return header



def parseFile(fileName, requiredFrames=listOfDefFrame, encoding="Latin-1"):
    """
    Виконує розбір файла від початку до кінця
    і повертає словник з фреймами, назви яких
    описані в RequiredFrames 
    """
    frameList = []
    passed = 0  # ксть розібраних байтів
    try:
        with open(fileName, "rb") as f:

            header = parseHeader(f)
            if not header:
                raise ValueError()
            while(passed < header["size"]):
                passed += parseFrame(f)
    except ValueError:     
        print("File whithout tag")
        return       

    
    info = decodeFrameInfo(compileRecordInfo(requiredFrames), encoding)
    return info


def parseFrame(file):
    """
    Розбір наступного фрейму в файлі
    
    """
    
    def parseFlag(flagByte):
        flags = {"Tag alter":0, "File alter":0, "Read only":0, "Grouping identify":0,
               "Compresion":0, "Encryption": 0, "Unsynchronisation": 0, "Data length indicator": 0}
        
        if flagByte & 0x4000:
            flags["Tag alter"] = 1
        if flagByte & 0x2000:
            flags["File alter"] = 1    
        if flagByte & 0x1000:
            flags["Read only"] = 1
        if flagByte & 0x40:
            flags["Grouping identify"] = 1
        if flagByte & 0x8:
            flags["Compresion"] = 1  
        if flagByte & 0x4:
            flags["Encryption"] = 1  
        if flagByte & 0x2:
            flags["Unsynchronisation"] = 1  
        if flagByte & 0x1:
            flags["Data length indicator"] = 1
            return flags    
            
    name = readString(file, 4)
    
    if not all(name):  # виявлення padding
        return  header['size'] - file.tell() + 14  # розмір тегу - пройдено + розмір заголовку
    
    frame = {"id":"", "size":0, "flags":0, "text":""}
    frame["id"] = name
    size = readInteger(file)
    frame["size"] = size
    flagByte = readByte(file)
    flagByte = flagByte << 8            
    flagByte = flagByte + readByte(file)
    frame["flags"] = parseFlag(flagByte)
    text = file.read(size)
    frame["text"] = text
    frameList[name] = frame
    return size + 10


def decodeFrameInfo(dictOfFrames, encoding):
    """
    Декодувати текстові поля відповідним кодування Latin-1 чи utf
    """
    decodedInfo = {}
    for frame in dictOfFrames:
        if frame[0] =='T':
            while dictOfFrames[frame][-1] == 0:
                dictOfFrames[frame] = dictOfFrames[frame][:-1]
            if dictOfFrames[frame][0] == 0:
                decodedInfo[frame] = bytes.decode(dictOfFrames[frame][1:], encoding)                
            elif dictOfFrames[frame][0] == 1:
                decodedInfo[frame] = bytes.decode(dictOfFrames[frame][1:], encoding="utf-16")
            elif dictOfFrames[frame][0] == 2:
                decodedInfo[frame] = bytes.decode(dictOfFrames[frame][1:], encoding="utf-16be")
            elif dictOfFrames[frame][0] == 3:
                decodedInfo[frame] = bytes.decode(dictOfFrames[frame][1:], encoding="utf-8")

    return decodedInfo
                

def compileRecordInfo(listOfRequir):
    """
    Вибираємо з всіх розібраних фреймів потрібні для нас
    Отримуємо словник {frameId : value}
    """
    dictOfRequir = {}
    for i in range(len(listOfRequir)):
        if (frameList.get(listOfRequir[i]) != None):
            dictOfRequir[listOfRequir[i]] = frameList[listOfRequir[i]]["text"]
    return dictOfRequir

if __name__ == "__main__":
    info = parseFile ("C://Users//Wittmann//Documents//GitHub//Course//res//Sealed With A Kiss.AAC", encoding="Latin-1")
    if (info):
        print((info))
    print(header)


