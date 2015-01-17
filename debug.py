import metacritic
import json

result = metacritic.get_all_movie_critics()
with open('data.json', 'w') as outfile:
    json.dump(result, outfile)