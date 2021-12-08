import tkinter as tk
from tkinter import ttk
import pandas as pd
import argparse
import random
import util
import ren as ren
from tkinter.constants import CENTER, DISABLED, E, END, FALSE, N, NO, NORMAL, S, W

def add_args():
    parser = argparse.ArgumentParser(description='Tool for annotation of named entities in tweets.')
    parser.add_argument('-f', '--file', metavar='', required=True, help='CSV file from which to extract tweets.')
    parser.add_argument('-m', '--model', required=False, help='Spacy model for initialization. Optional.')
    parser.add_argument('-o', '--output', required=False, help='Output name for annotation and model.')
    return parser.parse_args()

#Verifies if selection overlaps with an existing entity.
#   If so: returns false and the name of the overlapping enitity
#   else: returns true and none
def check_selection_conflict(text: tk.Text,startIndex, endIndex):
    for tagname in text.tag_names():
        if tagname != 'sel':
            if not ((text.compare(endIndex, "<=", '%s.first' % tagname)) or (text.compare(startIndex, ">=", '%s.last' % tagname))):
                return False , tagname
    return True , None

#Saves the selected text as an entity in both the text tag system and the spacy annotations array.
def save_name(text: tk.Text, label,data):
    try:
        tag_start = text.index(tk.SEL_FIRST)
        tag_end = text.index(tk.SEL_LAST)
        check, conflictTag = check_selection_conflict(text, tag_start, tag_end)

        if check:
            tagname = text.get(tag_start, tag_end)
            text.tag_add(tagname, tag_start, tag_end)
            text.tag_config(tagname, background="green")
            label.set("New entity '%s' saved!" % tagname)
            char_start, char_end = util.tag_index_to_char_index(text, tag_start,tag_end)
            #print((tagname,char_start, char_end,'ENTITY'))
            data[-1][1].append((tagname,char_start, char_end,'ENTITY'))

        else:
            label.set("Conflict detected with entity \"%s\"! New entity NOT saved!" % conflictTag)
        return
    except tk.TclError:
        label.set("Nothing is selected.")
    
#Deletes an entity from the text
def delete_name(text: tk.Text,label,data):
    try:
        check, tagname = check_selection_conflict(text, tk.SEL_FIRST, tk.SEL_LAST)
        if check:
            label.set("There is nothing to delete here.")
        else:
            text.tag_delete(tagname)
            entities = data[-1][1]
            data[-1] = (data[-1][0],[x for x in entities if x[0] != tagname], data[-1][2])
            #print(data[-1])
            label.set("Entity '%s' deletes." % tagname)
    except tk.TclError:
        label.set("Nothing is selected.")

def setup_tweetview(text: tk.Text, data):
    text.config(state=NORMAL)
    text.delete("1.0",tk.END)
    for tag in text.tag_names():
        if tag != 'sel':
            text.tag_delete(tag)
    tweetText, entities, _ = data[-1]
    text.insert("1.0",tweetText)
    text.config(state=DISABLED)
    #Tuple entity is defined as (name, start_char, end_char, label)
    for entity in entities:
        text.tag_add(entity[0],util.char_index_to_tag_index(entity[1]), util.char_index_to_tag_index(entity[2]))
        text.tag_config(entity[0], background="green")

def validate_tweet(text: tk.Text,label,data,annotations):
    annotations.append(data.pop())
    setup_tweetview(text,data)
    label.set("You've annotated %d tweets so far!" % len(annotations))

def list_stats(listing, stats):
    
    for entity in stats:
        listing.insert('', 'end', values=entity)

    
def retrain_tweets(label,annotations, output):
    if len(annotations) < 30:
        label.set("Please, annotate %d more tweets before training the model please ." %(30 - len(annotations)))
        return

    if output == None:
       output = "new_model"
    label.set("Retraining the model. This will take a while. Please wait.")
    random.shuffle(annotations)
    size = len(annotations)
    fatia = size//10 * 3
    train = annotations[fatia:]
    dev = annotations[:fatia]
    ren.export_data(output,annotations)
    ren.create_data(train,output + "_train")
    ren.create_data(dev,output + "_dev")
    ren.train_model(output)
    label.set("Model has been retrained and can be accessed at models/" + output)
    

def init():
    args = add_args()
    
    data, stats = ren.read_file(args.file,args.model) #Loads entry data with NER from Spacy.
    random.shuffle(data)
    annotations = [] #Array that stores annotations
    
   

    root=tk.Tk() #Tkinter function for initializing the interface

    content = tk.Frame(root) #Frame to store every other widget in.

    currentText = tk.Text(content,borderwidth=5,relief="ridge", width=120, height=10) #The textbox in which tweets are shown.

    setup_tweetview(currentText,data) #Loads a tweet in the textbox with its entities.
    

    messageText = tk.StringVar() #String var for messages and warnings
    message = tk.Label(content, textvariable=messageText) #Label widget that displays the message var
    messageText.set("Welcome to the tweet annotation tool!")

    #Button that call the function for saving a new entity
    saveNameButton = tk.Button(content, text="Save Name", command= lambda: save_name(currentText,messageText,data))
    #Button that calls the function for deleting an entity
    deleteNameButton = tk.Button(content, text="Delete Name", command= lambda: delete_name(currentText, messageText,data))
    #Button that calls the function for validating current tweets and loading new ones.
    validateButton = tk.Button(content, text="Validate Tweet", command= lambda: validate_tweet(currentText, messageText, data, annotations))
    #Button that calls the function for retraining the model with the validated tweets.
    retrainButton = tk.Button(content, text="Retrain Tweet", command= lambda: retrain_tweets(messageText,annotations, args.output))

    #Widget for showing stats
    statsListing = ttk.Treeview(content)
    statsListing['columns'] = ('Entity','#', 'Positivity')
    statsListing.heading(0, text="Entity")
    statsListing.heading(1, text="#")
    statsListing.heading(2, text="Average Positivity")
    statsListing.column('#0', width=0, stretch=NO)
    statsListing.column('Entity', anchor=CENTER, width=80)
    statsListing.column('#', anchor=CENTER, width=80)
    statsListing.column('Positivity', anchor=CENTER, width=80)
    list_stats(statsListing, stats=stats)

    listingText = tk.StringVar() #String var for messages and warnings
    listingLabel = tk.Label(content, textvariable=listingText) #Label widget that displays the message var
    listingText.set("List of entities and their number of ocurrences across all dataset")

    #From here, code for placement of interface 

    content.grid(column=0,row=0,sticky=(N,S,E,W))
    currentText.grid(column=0,row=0,columnspan=4,rowspan = 2,sticky=(N,S,E,W))
    message.grid(column=1,row=2,columnspan=2)
    saveNameButton.grid(column=1,row=3)
    deleteNameButton.grid(column=1,row=4)
    validateButton.grid(column=2,row=3)
    retrainButton.grid(column=2,row =4)

    statsListing.grid(column=5, row=1, rowspan=3, sticky=(N,S,E,W))
    listingLabel.grid(column=5, row=0)

    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)


    root.mainloop()


if __name__== "__main__":
    init()
