import detectron2
import main.google_colab.deskew as deskew
import main.google_colab.table_detection as table_detection
import main.google_colab.table_structure_recognition_all as tsra
import main.google_colab.table_structure_recognition_lines as tsrl
import main.google_colab.table_structure_recognition_wol as tsrwol
import main.google_colab.table_structure_recognition_lines_wol as tsrlwol
import main.google_colab.table_xml as txml
import main.google_colab.table_ocr as tocr
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
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data import DatasetCatalog, MetadataCatalog
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# from google.colab.patches import cv2_imshow
setup_logger()

# create detectron config
cfg = get_cfg()

# set yaml
cfg.merge_from_file("main/All_X152.yaml")

# set model weights
cfg.MODEL.WEIGHTS = "main/model_final.pth"  # Set path model .pth

predictor = DefaultPredictor(cfg)


model_version = "microsoft/trocr-base-printed"
processor = TrOCRProcessor.from_pretrained(model_version)
model = VisionEncoderDecoderModel.from_pretrained(model_version)

document_example = cv2.imread("main\extracted_tables\image_0.png")
# cv2.imshow('img',document_example)

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

                    if(erosion.sum() != erosion.shape[0]*erosion.shape[1]*255):
                        import IPython;IPython.embed();exit(1)
                        pixel_values = processor(erosion.reshape(*erosion.shape,1), return_tensors="pt").pixel_values
                        generated_ids = model.generate(pixel_values)
                        extract_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                        print(extract_text)


                    else:
                        out = ""

                    if(out == ""):
                        pixel_values = processor(erosion, return_tensors="pt").pixel_values
                        generated_ids = model.generate(pixel_values)
                        extract_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                        print(extract_text)


                        if(len(out[:-2]) >1):
                            out = ""

                    inner = inner + " " + out[:-2]
                outer.append(inner)

# Creating a dataframe of the generated OCR list
arr = np.array(outer)
dataframe = pd.DataFrame(arr.reshape(len(finalboxes), len(finalboxes[0])))
print(dataframe)
data = dataframe.style.set_properties(align="left")
# Converting dataframe into an excel-file
data.to_excel("output.xlsx")
    

# ! pip install transformers

