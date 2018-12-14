import os
import string
import torch
import typing
import json
import pathlib
import requests

import torch.nn as nn
from torch.autograd import Variable
import pandas as pd

bundle_root = pathlib.Path(os.environ['LABS_BUNDLE_ROOT'])

all_letters = string.ascii_letters + " .,;'"
n_letters = len(all_letters)
n_hidden = 128

# Build the category_lines dictionary, a list of names per language

all_categories = ['German',
 'English',
 'Czech',
 'Portuguese',
 'Japanese',
 'Polish',
 'Chinese',
 'Scottish',
 'Spanish',
 'Irish',
 'French',
 'Italian',
 'Russian',
 'Vietnamese',
 'Greek',
 'Arabic',
 'Dutch',
 'Korean']
n_categories = len(all_categories)

# Just return an output given a line


def evaluate(line_tensor, rnn):
    hidden = rnn.initHidden()

    for i in range(line_tensor.size()[0]):
        output, hidden = rnn(line_tensor[i], hidden)

    return output


class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(RNN, self).__init__()

        self.hidden_size = hidden_size
        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        combined = torch.cat((input, hidden), 1)
        hidden = self.i2h(combined)
        output = self.i2o(combined)
        output = self.softmax(output)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, self.hidden_size)



def lineToTensor(line):
    tensor = torch.zeros(len(line), 1, n_letters)
    for li, letter in enumerate(line):
        tensor[li][0][letterToIndex(letter)] = 1
    return tensor


def letterToIndex(letter):
    return all_letters.find(letter)


def add_this(a: int, b: int) -> int:
    return a + b


# init model
rnn = RNN(n_letters, n_hidden, n_categories)
# fill in weights
rnn.load_state_dict(torch.load(str(bundle_root / 'common/char-rnn-classification.pt')))

def predict(line: str, n_predictions: int=3) -> typing.List[typing.Tuple]:
    output = evaluate(Variable(lineToTensor(line)), rnn)

    # Get top N categories
    topv, topi = output.data.topk(n_predictions, 1, True)
    predictions: List[Any] = []

    for i in range(n_predictions):
        value = topv[0][i]
        category_index = topi[0][i]
        predictions += [(str(value).split('tensor')[1], all_categories[category_index])]

    return predictions


def get_name_nationality(name: str) -> pd.DataFrame:
    #print(name)
    name = name.strip()
    df_l = []
    name_l = name.split(' ')
    if '' in name_l:
        name_l.remove('')
    for name in name_l:
        #print(name)
        try:
            s = predict(name)
        except:            
            s = ['(0)', 'Unknown']
        df_l += [pd.DataFrame([(float(t[0][1:-1]), t[1]) for t in s])]
    return pd.concat(df_l).groupby(1)[0].sum().sort_values(ascending=False).index[0]


## Pantheon query
endpoint = 'https://pantheon.cloud.contiamo.com/contiamo-next/catalogs/73399930-b7b6-5206-82f8-40fad7134ccf/savedQueries/f89a4580-fed1-11e8-b5b1-1b599c08eaab/execute'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer fc0032234bbbb447a08fb1e6df6b494fb165806f837df07dd6d07cc09e3c2f09'}

def query_pantheon(endpoint: str) -> pd.DataFrame:
    r = json.loads(requests.post(endpoint, data='{}', headers=headers).text)
    df = pd.DataFrame(r['rows'], columns = [col['ref'] for col in r['columns']])
    df.columns = df.columns.map(lambda s:s.split('.')[-1])
    return df