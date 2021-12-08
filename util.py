from tkinter import Text
import argparse
import pandas as pd
import ren
#Converts a tag index from tkinter (which follows a "X.Y" format where X is the line and Y the collum of the index)
#to a conventional character index
def tag_index_to_char_index(text: Text, tagStart, tagEnd):
    aux = text.count("1.0", tagStart)
    if aux != None:
        start_char = aux[0]
    else:
        start_char = 0
    end_char = text.count("1.0", tagEnd)[0]
    return (start_char,end_char)

#Does the opposite
def char_index_to_tag_index(charIndex):
    return "1.0 + {}c".format(charIndex)


def add_args():
    parser = argparse.ArgumentParser(description='Utility tool for annotation of named entities in tweets.')
    parser.add_argument('-f', '--file', metavar='', required=True, help='CSV file to transform to ".spacy" format.')
    return parser.parse_args()

def transform_to_binary():
    args = add_args()
    dfs = pd.read_excel(args.file, sheet_name="Sheet1")
    data = []
    for row in dfs.iterrows():
        aux = row[1]
        txt = aux["entities"]
        
        txt = txt.replace('[','')
        txt = txt.replace(']','')
        txt = txt.replace('(','')
        txt = txt.replace(')','')
        txt = txt.replace("'",'')
        txt = txt.replace(' ','')
        string = txt.split(',')

        ents = []
        if string[0] != '':
            i  = 0
            while i < len(string):
                ents.append((str(string[i]), int(string[i+1]), int(string[i+2]), str(string[i+3])))
                i += 4
        data.append((aux["full_text"],ents, aux["positividade"]))
    ren.create_data( data,"case_study",)

if __name__== "__main__":
    transform_to_binary()


