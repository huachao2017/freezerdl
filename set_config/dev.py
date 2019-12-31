yolov3_train_params = {
    "JPEGImages_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/JPEGImages/",
    "Annotations_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/Annotations/",
    "Main_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/ImageSets/Main/",
    "model_dir":"/data/ai/yolov3/model/{}_{}/",
    "log_dir":"/data/ai/yolov3/logs/{}_{}/",
    "convert_path":"/data/ai/yolov3/VOCdevkit/{}_{}/VOC2007/Convert/",
    "type_all_echos":20,# 3000
    "type_add_echos":5,# 500
}

yolov3_predict_params = {
    "good_model_path": '/data/ai/model/{}_{}.h5',
    "score": 0.23,
    "iou": 0.45,
    "font_file": './model_train/keras_yolo3/font/FiraMono-Medium.otf',
    "diff_switch_iou": (True, 0.6),
    "single_switch_iou_minscore": (True, 0.0, 0.28)
},