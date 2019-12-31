import os
import shutil
filelist=[]
def remove_path_file(rootdir):
    filelist=os.listdir(rootdir)
    for f in filelist:
        filepath = os.path.join( rootdir, f )
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath,True)
    shutil.rmtree(rootdir,True)
    print (rootdir+str("file remove sucess"))