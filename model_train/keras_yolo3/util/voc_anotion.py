import xml.etree.ElementTree as ET
from set_config import config
sets=[('2007', 'train'), ('2007', 'val'), ('2007', 'test')]
def convert_annotation(image_id, list_file,class_names,Annotations_path):
    in_file = open((Annotations_path+'%s.xml')%(image_id))
    tree=ET.parse(in_file)
    root = tree.getroot()
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in class_names or int(difficult)==1:
            continue
        cls_id = class_names.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))

def convert(shop_id,batch_id,class_names):
    Main_path = str(config.yolov3_train_params['Main_path']).format(shop_id,batch_id)
    JPEGImages_path = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id,batch_id)
    convert_path = str(config.yolov3_train_params['convert_path']).format(shop_id,batch_id)
    Annotations_path = str(config.yolov3_train_params['Annotations_path']).format(shop_id, batch_id)
    for year, image_set in sets:
        image_ids = open(Main_path+'%s.txt'%(image_set)).read().strip().split()
        list_file = open((convert_path+'%s_%s.txt')%(year, image_set), 'w')
        for image_id in image_ids:
            list_file.write((JPEGImages_path+'%s.jpg')%(image_id))
            convert_annotation(image_id, list_file,class_names,Annotations_path)
            list_file.write('\n')
        list_file.close()