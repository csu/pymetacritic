import metacritic
import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# result = metacritic.get_all_movie_critics()
# with open('data.json', 'w') as outfile:
#     json.dump(result, outfile)

metacritic.get_movie_critic('aa-dowd')
# metacritic.get_movie_critic('aaron-hillis')