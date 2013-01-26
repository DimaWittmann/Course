import os, id3v2_4 as parser, os.path, time, sqlite3 as sql
from multiprocessing import Process, Queue



def findFiles(root, extensions, fileSearched):
    for directory,subdir, files in os.walk(root):
        for file in files:
            for ext in extensions:
                if file.endswith(ext):
                    fileSearched.append(os.path.join(directory, file))
                    
        for direct in subdir:
            findFiles(direct, ext, fileSearched)
            
print(time.localtime(time.time()))
files =[]
findFiles("D:/", [".mp3",".AAC"], files)


connection = sql.connect("MusicData.db")
cursor = connection.cursor()
print(time.localtime(time.time()))
try:
    cursor.execute("select * from files")
except:
    cursor.execute(
                   """
                   CREATE TABLE files
                   (path text not null primary key)
                   """
                   )

for path in files:
    try:
        cursor.execute("INSERT INTO files VALUES(?)",(path,))
    except:
        pass
connection.commit()
cursor.close()

print(time.localtime(time.time()))    
    
    
    
    
    
    
    

