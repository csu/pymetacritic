import metacritic
import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# result = metacritic.get_movie_critic('aa-dowd')
# with open('data_one_critic.json', 'w') as outfile:
#     json.dump(result, outfile)

# test = metacritic.get_movie_critic('aa-dowd')
# print test['highest_review_score']
# print test['lowest_review_score']
print json.dumps(metacritic.get_movie_critic('aaron-hillis'))
# metacritic.get_movie_critic('aaron-cutler')
# metacritic.get_movie_critic('ao-scott') 