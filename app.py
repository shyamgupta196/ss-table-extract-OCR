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
    default= r'.\output_excels',
    type=str,
    required=False,
    help="path to save folder for excel and bboxes"
)

args = parser.parse_args()

def detect_table():
    os.system('python recognition.py --input_folder screenshot --output_folder tables')

def TableOCR():
    for filename in os.listdir(args.input_folder):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(args.input_folder, filename)
            img = cv2.imread(path)
            result = table_engine(img)
            save_structure_res(result, args.save_folder,os.path.basename(path).split('.')[0])
            pathhtml = os.path.join(args.save_folder,filename.split('.')[0],filename.split('.')[0]+'.html')
            file = open(pathhtml,'w',encoding='utf-8')
            try:
                file.write(result[0]['res']['html'])
            except Exception as e:
                print(e)
                import IPython; IPython.embed();exit()
                continue
            file.close()



if __name__=='__main__':
    table_engine = PPStructure(show_log=True,det_db_box_thresh=0.3,det_pse_box_thresh=0.3)
    # detect_table()
    TableOCR()

## psuedocode
# read output.xlsx
# take x_max
# In [7]: differences = np.diff(df['x_max'])
#In [10]: indices = np.where(-differences > 500)[0]
# In [11]: indices
# df.iloc[indices,:]
# In [17]: df['Text']
# In [19]: df['Text'].iloc[indices+1]
# In [20]: df['Text'].iloc[indices]
# In [22]: data = df['x_max'].values
# In [30]: subarrays = np.split(data, indices + 1)
# In [32]: pd.DataFrame(subarrays)
