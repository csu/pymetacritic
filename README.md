# pymetacritic
Python API for Metacritic. Made at PennApps Winter 2015.

## Usage
```python
import metacritic

metacritic.get_movie_critics_for_letter('a')
metacritic.get_all_movie_critics()
metacritic.get_movie_critic('person-name')
```

### Scraper quick start (for Ubuntu)
```shell
wget https://raw.githubusercontent.com/csu/pymetacritic/master/scraper.sh
# replace arguments with letter indices:
sh scraper.sh 0 6
```

Or (replace arg1 and arg2 with letter indices):
```shell
curl -s http://server/path/script.sh | bash /dev/stdin arg1 arg2
```