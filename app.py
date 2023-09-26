import os 
import argparse
import cv2
from paddleocr import PPStructure,draw_structure_result,save_structure_res


parser = argparse.ArgumentParser(
    description="Detect table and using OCR store it in excel file."
)

parser.add_argument(
    "--input_folder",
    default= 'extracted_tables',
    type=str,
    required=False,
    help="path to input folder"
)
parser.add_argument(
    "--save_folder",
    default= './output_excels',
    type=str,
    required=False,
    help="path to save folder for excel and bboxes"
)

args = parser.parse_args()

def detect_table():
    os.system('python recognition.py --input_folder screenshot --output_folder tables')

def TableOCR():
    table_engine = PPStructure(show_log=True)
    for filename in os.listdir(args.input_folder):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(args.input_folder, filename)
            img = cv2.imread(path)
            result = table_engine(img)
            pathhtml = os.path.join(args.save_folder,filename.split('.')[0],filename.split('.')[0]+'.html')
            file = open(pathhtml,'w',encoding='utf-8')
            try:
                file.write(result[0]['res']['html'])
            except Exception as e:
                print(e)
                continue
            file.close()
            save_structure_res(result, args.save_folder,os.path.basename(path).split('.')[0])



if __name__=='__main__':
    detect_table()
    TableOCR()
    
