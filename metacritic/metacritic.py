import urllib2
import time
from string import lowercase as lowercase_letters
from bs4 import BeautifulSoup
import re

def keep_trying_to_get_html(url):
    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        opener = urllib2.build_opener()
        html_doc = opener.open(request).read()
        return html_doc
    except:
        time.sleep(3)
        return keep_trying_to_get_html(url)

def get_movie_critics_for_letter(letter):
    url = 'http://www.metacritic.com/browse/movies/critic/name/' + letter + '?num_items=100'
    html_doc = keep_trying_to_get_html(url)
    soup = BeautifulSoup(html_doc)

    # if (soup.find('div', {'class': 'page_nav'})):
    #     print 'has pagination'

    critics_elements = soup.find_all('li', {'class': 'product'})

    critics = []
    for critic_element in critics_elements:
        link_element = critic_element.find('a', href=True)
        critics.append({
            'critic_name': link_element.getText(),
            'critic_url': link_element['href']
            })

    return critics

def get_all_movie_critics():
    result = []
    for letter in lowercase_letters:
        result += get_movie_critics_for_letter(letter)
    return result

def find_by_class(soup, class_, element_type='div'):
    return soup.find(element_type, attrs={'class': class_})

def get_movie_critic(slug):
    url = 'http://www.metacritic.com/critic/' + slug
    html_doc = keep_trying_to_get_html(url)
    soup = BeautifulSoup(html_doc)

    result = dict()

    result['critic_name'] = find_by_class(soup, 'critic_title').getText().strip()
    result['publication_title'] = find_by_class(soup, 'publication_title').find('a').getText()

    critscore_stats = find_by_class(soup, 'critscore_stats')

    result['review_count'] = int(find_by_class(critscore_stats, 'label').find('span').getText().replace(' reviews', ''))

    result['percent_higher_than_average'] = int(find_by_class(critscore_stats, 'data stats_score above_average', element_type='span').getText().replace('%', ''))
    result['percent_same_than_average'] = int(find_by_class(critscore_stats, 'data stats_score average', element_type='span').getText().replace('%', ''))
    result['percent_lower_than_average'] = int(find_by_class(critscore_stats, 'data stats_score below_average', element_type='span').getText().replace('%', ''))


    points_against_average = find_by_class(find_by_class(soup, 'summary'), re.compile(r".*\baverage_value\b.*"), element_type='span').getText()

    # Get just the point value
    points_against_average_num = float(points_against_average.split(' ')[0])

    # If the critic scores lower than the average, then make the value negative
    if 'lower' in points_against_average:
        points_against_average_num *= -1
    result['points_against_average'] = points_against_average_num

    

    print result