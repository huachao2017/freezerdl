yolov3_train_params = {
    "JPEGImages_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/JPEGImages/",
    "Annotations_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/Annotations/",
    "Main_path":"/data/ai/ai_data/yolov3/VOCdevkit/{}_{}/VOC2007/ImageSets/Main/",
    "model_dir":"/data/ai/yolov3/model/{}_{}/",
    "log_dir":"/data/ai/yolov3/logs/{}_{}/",
    "convert_path":"/data/ai/yolov3/VOCdevkit/{}_{}/VOC2007/Convert/",
    "type_all_echos":2000,# 3000
    "type_add_echos":100,# 500
    "predict_wfile":"/data/ai/yolov3/model/{}_{}/wfile_{}.txt",
    "predict_wfile_path":"/data/ai/yolov3/model/{}_{}/",
    "default_config_params":{
        "1-1":{
            'Ap':'',
            'mAp':0,
            'score': 0.25,
            'iou': 0.45,
            "diff_switch_iou": (True, 0.6),
            "single_switch_iou_minscore": (True, 0.0, 0.28)
        },
        "1-2":{
            'Ap': '',
            'mAp': 0,
            'score': 0.25,
            'iou': 0.45,
            "diff_switch_iou": (False, 0.6),
            "single_switch_iou_minscore": (False, 0.0, 0.28)
        },
        "2-1": {
            'Ap': '',
            'mAp': 0,
            'score': 0.2,
            'iou': 0.45,
            "diff_switch_iou": (True, 0.6),
            "single_switch_iou_minscore": (True, 0.0, 0.28)
        },
        "2-2": {
            'Ap': '',
            'mAp': 0,
            'score': 0.2,
            'iou': 0.45,
            "diff_switch_iou": (False, 0.6),
            "single_switch_iou_minscore": (False, 0.0, 0.28)
        },
        "3-1": {
            'Ap': '',
            'mAp': 0,
            'score': 0.3,
            'iou': 0.45,
            "diff_switch_iou": (True, 0.6),
            "single_switch_iou_minscore": (True, 0.0, 0.28)
        },
        "3-2":{
            'Ap': '',
            'mAp': 0,
            'score': 0.3,
            'iou': 0.45,
            "diff_switch_iou": (False, 0.6),
            "single_switch_iou_minscore": (False, 0.0, 0.28)
        },
        "4-1": {
            'Ap': '',
            'mAp': 0,
            'score': 0.35,
            'iou': 0.45,
            "diff_switch_iou": (True, 0.6),
            "single_switch_iou_minscore": (True, 0.0, 0.38)
        },
        "4-2": {
            'Ap': '',
            'mAp': 0,
            'score': 0.35,
            'iou': 0.45,
            "diff_switch_iou": (False, 0.6),
            "single_switch_iou_minscore": (False, 0.0, 0.38)
        },
    },
}

yolov3_predict_params = {
    "font_file": './model_train/keras_yolo3/font/FiraMono-Medium.otf',
},

app_config = {
    "online_model_dir": "/data/model/online",
    "app_models_history": "/data/model/history/",
    "backend_dns": "http://admin.magexiot.com"
}

ai_config = {
    "img_download_file_dir_template": "/data/downloads/{}_{}/imgs/",
    "xml_download_file_dir_template": "/data/downloads/{}_{}/xmls/",
    "app_models_path": "/data/model/bak",
    "app_host": "101.133.133.221",
    "app_user": "root",
    "app_password": "megex007$",
}