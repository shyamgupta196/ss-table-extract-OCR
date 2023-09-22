import detectron2
import main.google_colab.deskew as deskew
import main.google_colab.table_detection as table_detection
# import main.google_colab.table_structure_recognition_all as tsra
# import main.google_colab.table_structure_recognition_lines as tsrl
# import main.google_colab.table_structure_recognition_wol as tsrwol
import main.google_colab.table_structure_recognition_lines_wol as tsrlwol
# import main.google_colab.table_xml as txml
# import main.google_colab.table_ocr as tocr
import pandas as pd
import os
import json
import itertools
import random
from detectron2.utils.logger import setup_logger

# import some common libraries
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data import DatasetCatalog, MetadataCatalog
# import pytesseract
import easyocr

# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# from google.colab.patches import cv2_imshow
setup_logger()

# create detectron config
cfg = get_cfg()

# set yaml
cfg.merge_from_file("main/All_X152.yaml")

# set model weights
cfg.MODEL.WEIGHTS = "main/model_final.pth"  # Set path model .pth

predictor = DefaultPredictor(cfg)
reader = easyocr.Reader(['en'])

document_example = cv2.imread("extracted_tables\image_0.png")

table_list, table_coords,_ = table_detection.make_prediction(document_example, predictor)
list_table_boxes = []
outer = []
for table in table_list:
    finalboxes, output_img = tsrlwol.recognize_structure(table)

    list_table_boxes.append(finalboxes)
    for i in range(len(finalboxes)):
        for j in range(len(finalboxes[i])):
            inner = ''
            if (len(finalboxes[i][j]) == 0):
                outer.append(' ')
            else:
                for k in range(len(finalboxes[i][j])):
                    print(k)
                    y, x, w, h = finalboxes[i][j][k][0], finalboxes[i][j][k][1], finalboxes[i][j][k][2], finalboxes[i][j][k][3]

                    finalimg = output_img[x:x + h, y:y + w]

                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                    border = cv2.copyMakeBorder(finalimg, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255, 255])
                    resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    dilation = cv2.dilate(resizing, kernel, iterations=1)
                    erosion = cv2.erode(dilation, kernel, iterations=2)
                    try:
                        if(erosion.sum() != erosion.shape[0]*erosion.shape[1]*255):
                            out = reader.readtext(finalimg)[0][1]
                            print(out)


                        else:
                            out = ""

                        if(out == ""):
                            out = reader.readtext(finalimg)[0][1]
                            print(out)


                            if(len(out[:-2]) >1):
                                out = ""
                    except Exception as e:
                        print(e)
                        out = 'N/A'
                        # import IPython;IPython.embed();exit(1)
                    inner = inner + " " + out + ' '
                outer.append(inner)

# Creating a dataframe of the generated OCR list
arr = np.array(outer)
dataframe = pd.DataFrame(arr.reshape(len(finalboxes), len(finalboxes[0])))
print(dataframe)
data = dataframe.style.set_properties(align="left")
# Converting dataframe into an excel-file
data.to_excel("output1.xlsx")
    

# ! pip install transformers

