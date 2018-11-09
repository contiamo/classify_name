import datetime
import importlib
import json
import os
import sys
import torch

from pathlib import PurePath
from torch.autograd import Variable
from typing import List, Any

bundle_root = os.environ.get('LABS_BUNDLE_ROOT', '/labs')
sys.path.append(str(PurePath(bundle_root, 'common')))
import utils
importlib.reload(utils)

# load base classe
RNN = utils.RNN
# init model
rnn = RNN(utils.n_letters, utils.n_hidden, utils.n_categories)
# fill in weights
rnn.load_state_dict(torch.load(str(PurePath(bundle_root, 'common/char-rnn-classification.pt'))))

def predict(line: str, n_predictions: int=3) -> List[Any]:
    output = utils.evaluate(Variable(utils.lineToTensor(line)), rnn)

    # Get top N categories
    topv, topi = output.data.topk(n_predictions, 1, True)
    predictions: List[Any] = []

    for i in range(n_predictions):
        value = topv[0][i]
        category_index = topi[0][i]
        predictions += [(str(value).split('tensor')[1], utils.all_categories[category_index])]

    return predictions
        

def handle(input_string: str) -> str:
    print('Input string is {} and type is {}'.format(input_string, type(input_string)))
    # handle empty input
    if not input_string:
        return 'No input provided'
    else:
        name = str(input_string)

    output = predict(name) 
    
    return json.dumps(output)



