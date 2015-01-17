import metacritic
import string

for letter in string.lowercase:
    print 'running on: ' + letter
    metacritic.get_movie_critics_for_letter(letter)