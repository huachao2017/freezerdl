from sklearn.model_selection import train_test_split
import os
from random import shuffle
from set_config import config
def generate_main_txt(shop_id,batch_id):
   filenames=[]
   JPEGImages_path = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id,batch_id)
   files=os.listdir(JPEGImages_path)
   for filename in files:
      filenames.append(str(filename).split('.')[0])
   shuffle(filenames)
   #train,val=train_test_split(filenames,test_size=0.5)
   Main_path =  str(config.yolov3_train_params['Main_path']).format(shop_id,batch_id)
   with open(Main_path+"train.txt",'w') as f:
      for tr in filenames:
         f.write(tr)
         f.write("\n")

#with open("/home/ai/ai_data/yolov3/VOCdevkit/VOC2007/ImageSets/Main/val.txt",'w') as f:
#   for v in val:
#      f.write(v)
#      f.write("\n")