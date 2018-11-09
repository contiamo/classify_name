import datetime
import importlib
import json
import os
import sys
import torch

import pandas as pd

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
rnn.eval()

def predict(line: str, n_predictions: int=3) -> List[Any]:
    with torch.no_grad():
        output = utils.evaluate(utils.lineToTensor(line), rnn)

        # Get top N categories
        topv, topi = output.topk(n_predictions, 1, True)
        predictions = []

        for i in range(n_predictions):
            value = topv[0][i].item()
            category_index = topi[0][i].item()
            #print('(%.2f) %s' % (value, utils.all_categories[category_index]))
            predictions.append([value, utils.all_categories[category_index]])
    #output = utils.evaluate(utils.lineToTensor(line), rnn)

    ## Get top N categories
    #topv, topi = output.data.topk(n_predictions, 1, True)
    #predictions: List[Any] = []

    #for i in range(n_predictions):
    #    value = topv[0][i]
    #    category_index = topi[0][i]
    #    predictions += [(str(value).split('tensor')[1], utils.all_categories[category_index])]
    #predictions.reverse()
    return predictions
        

def handle(input_string: str) -> str:
    #print('Input string is {} and type is {}'.format(input_string, type(input_string)))
    # handle empty input
    if not input_string:
        return 'No input provided'
    else:
        name = str(input_string)

    output = (pd.DataFrame(predict(name), columns=['score', 'language'])
              .sort_values('score', ascending=False)
              .set_index('score')
              .squeeze()
              .to_dict()
             )
    
    return json.dumps(output)



