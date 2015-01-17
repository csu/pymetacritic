import urllib2
import time
from bs4 import BeautifulSoup

def keep_trying_to_get_html(letter):
    try:
        url = 'http://www.metacritic.com/browse/movies/critic/name/' + letter + '?num_items=100'
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        opener = urllib2.build_opener()
        html_doc = opener.open(request).read()
        return html_doc
    except:
        print 'error on: ' + letter + '. trying again.'
        time.sleep(3)
        return keep_trying_to_get_html(letter)

def get_movie_critics_for_letter(letter):
    html_doc = keep_trying_to_get_html(letter)
    soup = BeautifulSoup(html_doc)

    if (soup.find('div', {'class': 'page_nav'})):
        print 'has pagination'

    critics_elements = soup.find_all('li', {'class': 'product'})

    critics = []
    for critic_element in critics_elements:
        link_element = critic_element.find('a', href=True)
        critics.append({
            'critic_name': link_element.getText(),
            'critic_url': link_element['href']
            })

    return critics