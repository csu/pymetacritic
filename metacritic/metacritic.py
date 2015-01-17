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

    ### Critic and publication name ###
    result['critic_name'] = find_by_class(soup, 'critic_title').getText().strip()
    result['publication_title'] = find_by_class(soup, 'publication_title').find('a').getText()

    # critscore_stats = find_by_class(soup, 'critscore_stats')

    ### Total review count ###
    # result['review_count'] = int(find_by_class(critscore_stats, 'label').find('span').getText().replace(' reviews', ''))

    ### Percent compared to average (across all reviews)###
    # result['compared_to_average'] = dict()
    # result['compared_to_average']['percent_higher'] = int(find_by_class(critscore_stats, 'data stats_score above_average', element_type='span').getText().replace('%', ''))
    # result['compared_to_average']['percent_same'] = int(find_by_class(critscore_stats, 'data stats_score average', element_type='span').getText().replace('%', ''))
    # result['compared_to_average']['percent_lower'] = int(find_by_class(critscore_stats, 'data stats_score below_average', element_type='span').getText().replace('%', ''))

    ### Points against the average (across all reviews) ###
    # points_against_average = find_by_class(find_by_class(soup, 'summary'), re.compile(r".*\baverage_value\b.*"), element_type='span').getText()
    # Get just the point value
    # points_against_average_num = float(points_against_average.split(' ')[0])
    # If the critic scores lower than the average, then make the value negative
    # if 'lower' in points_against_average:
    #     points_against_average_num *= -1
    # result['points_against_average'] = points_against_average_num

    ### Score distribution for movie reviews ###
    result['score_distribution'] = dict()
    score_counts = find_by_class(soup, 'score_counts', element_type='ol')
    for element in score_counts.find_all('li', class_='score_count'):
        label = element.find('span', class_='label').getText()
        count = int(element.find('span', class_='count').getText())
        if label == 'Positive:':
            result['score_distribution']['positive'] = count
        elif label == 'Mixed:':
            result['score_distribution']['mixed'] = count
        elif label == 'Negative:':
            result['score_distribution']['negative'] = count

    result['movie_reviews_count'] = int(find_by_class(find_by_class(soup, 'reviews_total'), 'count', element_type='span').find('a').getText())

    result['average_review_score'] = int(find_by_class(soup, re.compile(r".*\btextscore\b.*"), element_type='span').getText())
    result['highest_review_score'] = int(find_by_class(soup, 'metascore_w small movie positive indiv perfect', element_type='span').getText())
    result['lowest_review_score'] = int(find_by_class(soup, 'metascore_w small movie negative indiv', element_type='span').getText())

    print result