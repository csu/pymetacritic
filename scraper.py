import metacritic
import os
import json
from string import lowercase

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

LETTER_RANGE = lowercase[0:13]

def save(obj, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(obj, outfile)

if not os.path.exists('data'):
    os.makedirs('data')
# if not os.path.exists('data/index'):
#     os.makedirs('data/index')
# if not os.path.exists('data/critics'):
#     os.makedirs('data/critics')

all_critics_index = []
for letter in LETTER_RANGE:
    critics = metacritic.get_movie_critics_for_letter(letter)
    all_critics_index += critics
    save(all_critics_index, 'data/index_' + str(LETTER_RANGE) + '.json')

all_critics = []
for critic in all_critics_index:
    slug = critic['critic_url'].replace('/critic/', '')
    all_critics.append(metacritic.get_movie_critic(slug))
    save(all_critics, 'data/critics_' + str(LETTER_RANGE) + '.json')