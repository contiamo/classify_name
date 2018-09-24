import datetime
import importlib
import json
import os
import torch

from common import utils
from pathlib import PurePath
from torch.autograd import Variable

importlib.reload(utils)

bundle_root = os.environ.get('LABS_BUNDLE_ROOT', '/labs')

# define RNN class (necessary to load the trained model)
RNN = utils.RNN

# load rnn 
rnn = torch.load(str(PurePath(bundle_root, 'data/processed/char-rnn-classification.pt')))


def predict(line, n_predictions=3):
    output = utils.evaluate(Variable(utils.lineToTensor(line)), rnn)

    # Get top N categories
    topv, topi = output.data.topk(n_predictions, 1, True)
    predictions = []

    for i in range(n_predictions):
        value = topv[0][i]
        category_index = topi[0][i]
        predictions.append([str(value).split('tensor')[1], utils.all_categories[category_index]])

    return predictions
        

def handle(input_json: str) -> None:
    # handle empty input
    if not input_json:
        return 'No input provided'
    # parse input
    input_dict = json.loads(input_json)
    if 'name' in input_dict.keys():
        name = input_dict['name']
    else:
        name = None       
   
    output = predict(name) 
    
    return output #json.dumps(output, ensure_ascii=False)



