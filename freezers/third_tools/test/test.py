from freezers.third_tools import visualization_utils as vis_util
import cv2
import numpy as np
from PIL import Image


if __name__ == "__main__":
    image_np = cv2.imread('1.jpg')

    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.array([[1,1,100,100],]),
        np.array(['6576431987657',]),
        np.array([0.88,]),
        ['6576431987657','6576431987659'],
        use_normalized_coordinates=False,
        max_boxes_to_draw=None,
        min_score_thresh=0,
        line_thickness=4)
    output_image = Image.fromarray(image_np)
    output_image.thumbnail((int(image_np.shape[1]), int(image_np.shape[0])), Image.ANTIALIAS)
    output_image.save('out.jpg')
