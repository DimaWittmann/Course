def printInfo(file):
    import glob, os, time, id3v2_4 as parser
    info = parser.parseFile(file);
    (dirName, fileName) = os.path.split(file)
    metadata = os.stat(file)
    (name, ext)=os.path.splitext(fileName)
    print("filename:",name)
    print("type:", ext[1:])
    print("size:",  metadata.st_size, "bites")
    print("Last change ",time.localtime(time.time()).tm_yday-time.localtime(metadata.st_mtime).tm_yday, "day ago" )

    if info.get("TPE1"):
        print("Solist(s): ",info.get("TPE1"))
    if info.get("TPE2"):
        print("Band/orchestra: ",info.get("TPE2"))    
    if info.get("TIT2"):
        print("Title/songname: ",info.get("TIT2"))

    print (info)
