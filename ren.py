from tkinter.constants import E
import spacy
from spacy.cli.train import train
from spacy.tokens import DocBin
import pandas as pd
from thinc.types import Fal
import util


def setup_spacy(*args):
    global nlp
    if(len(args) != 0 ):
        nlp = spacy.load(args[0])
    else:
        nlp = spacy.load("pt_core_news_lg")

def read_file(fileName,model):
    if model != None:
        setup_spacy(model)
    else:
        setup_spacy()

    dfs = pd.read_excel(fileName, sheet_name="Sheet1")

    sentimento = False
    if "positividade" in dfs:
        sentimento = True

    data = []
    i = 0

    for tweet in dfs["full_text"]:

        doc = nlp(str(tweet))
        entities = []

        for ent in doc.ents:
            entities.append((ent.text, ent.start_char, ent.end_char, "ENTITY"))
        
        if sentimento:
            data.append((tweet,entities,dfs["positividade"][i]))
            i += 1
        else:
            data.append((tweet,entities))
        
    
    return data, generate_stats(data)

def generate_stats(data):

    counter = {}
    average_pos = {}

    stats = []
    _,_,*aux = data[0]
    positivity = True
    if len(aux) == 0:
        positivity = False

    for tweet in data:
        for entity in tweet[1]:

            if positivity:
                if entity[0] in average_pos:
                    average_pos[entity[0]] = average_pos[entity[0]] + tweet[2]
                else:
                    average_pos[entity[0]] = tweet[2]

            
            if entity[0] in counter:
                counter[entity[0]] = counter[entity[0]] +1
            else:
                counter[entity[0]] = 1

    stats = [(entity, int(count),    "%.3f" %   (average_pos[entity]/int(count) )     ) for entity, count in counter.items()]
    
    
    return sorted(stats, key=lambda x: x[1], reverse=True)

def export_data(filename, annotations):
    df = pd.DataFrame.from_records(annotations, columns=['full_text','entities', 'positividade'])
    df.to_excel("annotations/" +filename+".xlsx")



def create_data(data, filename):
    new_nlp = spacy.blank("pt")
    db = DocBin()
    for item in data:
        text, entities, pos = item
        doc = new_nlp(text)
        ents = []
        for ent in entities:
            name, start, end, label = ent
            span = doc.char_span(start, end, label=label)
            if span != None:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk("./training_data/"+filename+".spacy")

def train_model(output):
    train("./config.cfg","./models/" + output,overrides={"paths.train": "./training_data/" + output + "_train.spacy", "paths.dev": "./training_data/" + output + "_dev.spacy"})

