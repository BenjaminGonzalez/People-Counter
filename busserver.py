import numpy as np
import os

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import time

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from PIL import Image
import urllib.request

import cloudinary
import re

import urllib3
import time

try:
    import config
except ImportError:
    print("Please copy template-config.py to config.py and configure appropriately !");
    exit();


# This is needed to display the images.


# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

from utils import label_map_util

from utils import visualization_utils as vis_util

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'#rfcn_resnet101_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

opener = urllib.request.URLopener()
opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
tar_file = tarfile.open(MODEL_FILE)
for file in tar_file.getmembers():
  file_name = os.path.basename(file.name)
  if 'frozen_inference_graph.pb' in file_name:
    tar_file.extract(file, os.getcwd())

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')



label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = [{'name': 'person', 'id': 1}]#label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = {1: {'name': 'person', 'id': 1}}

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

debug_communication = 0

def send_to_hcp(http, url, headers, qltty):
    timestamp = int(time.time())
    timestamp = ', "timestamp":' + str(timestamp)
    quantity = '", "messages":[{"people":' + qltty
    body = '{"mode":"async", "messageType":"' + str(
        config.message_type_id_From_device) + quantity + timestamp + '}]}'
    #print('msg ID, ', config.message_type_id_From_device)
    print(body)
    r = http.urlopen('POST', url, body=body, headers=headers)
    #print('POST', url, body, headers)
    if (debug_communication == 1):
        print("send_to_hcp():" + str(r.status))
    print(r.data)


def sendinfo(long):
    try:
        urllib3.disable_warnings()
    except:
        print(
            "urllib3.disable_warnings() failed - get a recent enough urllib3 version to avoid potential InsecureRequestWarning warnings! Can and will continue though.")

    # use with or without proxy
    if (config.proxy_url == ''):
        http = urllib3.PoolManager()
    else:
        http = urllib3.proxy_from_url(config.proxy_url)

    url = 'https://iotmms' + config.hcp_account_id + config.hcp_landscape_host + '/com.sap.iotservices.mms/v1/api/http/data/' + str(
        config.device_id)
    # print("Host   " + config.hcp_account_id + config.hcp_landscape_host)

    headers = urllib3.util.make_headers(user_agent=None)

    # use with authentication
    headers['Authorization'] = 'Bearer ' + config.oauth_credentials_for_device
    headers['Content-Type'] = 'application/json;charset=utf-8'

    send_to_hcp(http, url, headers, str(long))


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'opencv_frame_{}.png'.format(i)) for i in range(0, 5) ]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        lastversion = ""
        while True:
            start_time = time.time()
            # ret, image_np = cap.read() #EDIT THISS TO ACCESS COUDINARY ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            # image = Image.open(image_path)
            # image_np = load_image_into_numpy_array(image)

            # print(type(image_np))
            # print(image_np)
            # URL = 'http://res.cloudinary.com/projecteve/image/upload/v1507252167/boiiiii.png'

            result = str(cloudinary.api.resources(cloud_name="projecteve", api_key=156733677359362,
                                                  api_secret="gUf5tbocYS8dZvA94bps3f_ALNE"))
            try:
                result = re.compile("'version': (.*?),", re.DOTALL | re.IGNORECASE).findall(result)[1]
            except:
                pass
            if lastversion == result:
                print("Same As Before")
                time.sleep(10)
            else:
                URL = "http://res.cloudinary.com/projecteve/image/upload/v" + result + "/boiiiii.png"
                lastversion = result
                with urllib.request.urlopen(URL) as url:
                    with open('temp.jpg', 'wb') as f:
                        f.write(url.read())
                image_np = load_image_into_numpy_array(Image.open('temp.jpg'))
                print(type(image_np))
                # print(image_np)
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = detection_graph.get_tensor_by_name('detection_scores:0')
                classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                pepes = vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)
                # cv2.imshow('object detection', cv2.resize(image_np, (800,600)))
                # if cv2.waitKey(25) & 0xFF == ord('q'):
                #  cv2.destroyAllWindows()
                #  break
                # time.sleep(20)
                sendinfo(pepes)
                print(start_time, time.time(), (start_time + time.time()))
                print(pepes)
                # time.sleep(abs(3 -start_time+time.time()))

