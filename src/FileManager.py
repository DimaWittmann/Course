import os

listOfFiles=[]
startDir=os.getcwd()
def searchFor(root, extension):
    """
    Пошук у заданій директорії і підерикторіях файлів
    із заданим розширенням
    """
    listOfFiles=[]
    os.chdir(root)
    for file in os.listdir(root):
        path = os.path.join(root,file)
        if os.path.isfile(path):
            if os.path.splitext(file)[1] == extension:
                listOfFiles.append(path)
        else:
            searchFor(path, extension)
    os.chdir(startDir)
    return listOfFiles


    
