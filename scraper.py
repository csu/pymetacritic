import metacritic
import json
from string import lowercase

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

LETTER_RANGE = lowercase[0:6]

def save(obj, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(obj, outfile)

all_critics = []
for letter in LETTER_RANGE:
    critics = metacritic.get_movie_critics_for_letter(letter)
    save(critics, 'data/' + letter + '.json')
    all_critics += critics

for critic in all_critics:
    slug = critic['critic_url'].replace('/critic/', '')
    logging.debug('Scraping critic: ' + slug)
    save(metacritic.get_movie_critic(slug), 'data/critics/' + slug + '.json')