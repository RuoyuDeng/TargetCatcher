import re
import string
import json
from os import listdir,mkdir, remove, removedirs,rmdir
from os.path import isfile,join,splitext,exists
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
import argparse

from IPython import embed

# set up arguments
parser = argparse.ArgumentParser(prog="WordCloud_Generator")
parser.add_argument("--startover", type=bool, default=False,help="Whether to re-generate all wordcloud pictures from the first file or not")
parser.add_argument("--data_file",type=str, default='', help="generate a wordcloud for one specific json file under data directory" )


# helper functions
def contains_punctuation(w):
    return any(char in string.punctuation for char in w)

def contains_numeric(w):
    return any(char.isdigit() for char in w)

def regex_text(text_str):
    '''
    input: a str

    return: the original str will all lower case letters and removed all numbers and punctuations
    
    '''
    output = re.findall(r'''[\w']+|[.,!?;-~{}`´_<=>:/@*()&'$%#"]''', text_str)
    output = [w.lower() for w in output if not contains_punctuation(w)]
    output = [w for w in output if not contains_numeric(w)]
    output = [w for w in output if len(w) > 1]
    output = " ".join(output)
    return output

def process_json(jfile_name):
    '''
    input: a json file name in str

    return: a dict, 
        key: id of job
        value: long string of the corresponding job description seperated by space
    
    '''
    output_dict = {}
    with open(jfile_name, "r") as f:
        data = json.load(f)

    if type(data) is list:
        ids = [data[i]["id"] for i in range(len(data)) if data[i]["Description"] != None and data[i]["Description"] != ""]
        descriptions = [data[i]["Description"] for i in range(len(data)) if data[i]["Description"] != None and data[i]["Description"] != ""]
        for i,id in enumerate(ids):
            text = regex_text(descriptions[i])
            if text != "":
                output_dict[id] = text
    else:
        ids = data["id"].keys()
        descriptions = data["Description"]      
        for id in ids:
            if descriptions[id] != None and descriptions[id] != "": # handle None string case
                text = regex_text(descriptions[id])
                if text != "":
                    output_dict[id] = text
    return output_dict


def generate_wc_img(jfile,data_dir,wc_img_path,all_stopwords):
    """
    input: 
        jfile: the path to a json file
        data_dir: the path where all json files are stored
        wc_img_path: the path to store all directories of wc images
        all_stopwords: a set (or list) of stop words in str

    return: None, output the word cloud (wc) images based on information stored in json file
    
    """
    file_no_ext = splitext(jfile)[0]
    jfile = join(data_dir,jfile)
    data = process_json(jfile)

    for id,desccription in data.items():
        img_subdir = join(wc_img_path,file_no_ext) # the path to the sub "dir" for storing imgs
        img_store_dir = join(img_subdir, file_no_ext+"_"+id) # paths to "all imgs"
        if not exists(img_subdir):
            mkdir(img_subdir)
        all_imgs = listdir(img_subdir)
        cur_imgnum = len(all_imgs)
        max_imgnum = len(data)

        
        # if startover == False -> check current sub dir is done or not by checking the img amount
        #                               -> if done: break the inner loop, go to next file
        #                               -> if not done, skip the file existing and start save the imgs not existing

        # if startover == True -> remove all files under subdir if there is any, and then simply strart saving plots
        
        # no need to remove, then continue
        if cur_imgnum == max_imgnum: # done
            break
        else:
            if not exists(img_store_dir):
                print(img_store_dir)
                desccription = data[id]
                # embed()
                word_cloud = WordCloud(collocations = False, background_color="white",stopwords=all_stopwords).generate(desccription)
                plt.imshow(word_cloud,interpolation="bilinear")
                plt.axis("off")
                
                # print(img_store_dir+" saved!")
                plt.savefig(img_store_dir) # does not overwrite old files
                plt.clf() # clean the figure to speed up performance

if __name__ == "__main__":

    # set up arguments
    args = parser.parse_args()
    startover = args.startover
    

    # json file path and img store path
    data_path = "Format_JSON"
    wc_img_path = "wordcloud_imgs"
    if not exists(wc_img_path):
        mkdir(wc_img_path)


    one_jfile = args.data_file
    # one_jfile = "DatasetINDEED_2022-04-21.json"

    # get all json files
    json_filenames = [f for f in listdir(data_path) if isfile(join(data_path,f))]
    json_filepaths = [join(data_path,fn) for fn in json_filenames]

    # get all stopwords
    with open(r"stopwords/stopwords-fr.json", "r") as f:
        fr_stopwords = json.load(f)
    en_stopwords = list(STOPWORDS)    
    all_stopwords = en_stopwords + fr_stopwords
    # print(all_stopwords)

    if startover == True:
        for img_dir in listdir(wc_img_path):
            img_dir_path = join(wc_img_path,img_dir)
            imgs = listdir(img_dir_path)
            imgs_num = len(imgs)
            if imgs_num > 0:
                for img in listdir(img_dir_path):
                    remove(join(img_dir_path,img))

            removedirs(join(wc_img_path,img_dir))


    if one_jfile == "":
        for jfile in json_filenames:
            generate_wc_img(jfile,data_path,wc_img_path,all_stopwords)
        

    else:
        generate_wc_img(one_jfile,data_path,wc_img_path,all_stopwords)



