import datetime
import importlib
import json
import os
import torch
import typing 

from common import utils
from pathlib import PurePath
from torch.autograd import Variable

importlib.reload(utils)

bundle_root = os.environ.get('LABS_BUNDLE_ROOT', '/labs')

# define RNN class (necessary to load the trained model)
RNN = utils.RNN

# load rnn 
rnn = torch.load(str(PurePath(bundle_root, 'data/processed/char-rnn-classification.pt')))


def predict(line: str, n_predictions: int=3) ->str:
    output = utils.evaluate(Variable(utils.lineToTensor(line)), rnn)

    # Get top N categories
    topv, topi = output.data.topk(n_predictions, 1, True)
    predictions = []

    for i in range(n_predictions):
        value = topv[0][i]
        category_index = topi[0][i]
        predictions.append([str(value).split('tensor')[1], utils.all_categories[category_index]])

    return predictions
        

def handle(input_string: str) -> None:
    # handle empty input
    if not input_string:
        return 'No input provided'
    else:
        name = input_string

    output = predict(name) 
    
    return json.dumps(output, ensure_ascii=False)



