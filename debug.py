import metacritic
import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

result = metacritic.get_movie_critic('aa-dowd')
with open('data_one_critic.json', 'w') as outfile:
    json.dump(result, outfile)

# metacritic.get_movie_critic('aa-dowd')
metacritic.get_movie_critic('aaron-hillis')