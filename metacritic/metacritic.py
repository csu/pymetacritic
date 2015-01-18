import urllib2
import time
from string import lowercase as lowercase_letters
from bs4 import BeautifulSoup
import re
import logging

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def cast_int(string):
    try:
        return int(string.replace(',', ''))
    except:
        return None

def cast_float(string):
    try:
        return float(string.replace(',', ''))    
    except:
        return None

def keep_trying_to_get_html(url, attempt=0):
    logging.debug('[keep_trying_to_get_html] Making request to: ' + url)
    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        opener = urllib2.build_opener()
        html_doc = opener.open(request).read()
        return html_doc
    except:
        if attempt > 10:
            logging.error("Giving up on HTTP request: " + url)
            raise Exception("Failed to fetch " + url)
        logging.debug('[keep_trying_to_get_html] HTTP error on ' + url + '. Retrying...')
        time.sleep(3)
        return keep_trying_to_get_html(url, attempt=attempt+1)

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
    try:
        url = 'http://www.metacritic.com/critic/' + slug + '?filter=movies&num_items=100&sort_options=critic_score&page=0'
        # url = 'http://www.metacritic.com/critic/' + slug
        html_doc = keep_trying_to_get_html(url)
        soup = BeautifulSoup(html_doc)

        result = dict()

        ### Critic and publication name ###
        result['critic_name'] = find_by_class(soup, 'critic_title').getText().strip()

        try:
            result['publication_title'] = find_by_class(soup, 'publication_title').find('a').getText()
        except:
            result['publication_title'] = None

        result['all_reviews'] = dict() # contains data that pertains to all reviews, not just movie reviews

        critscore_stats = find_by_class(soup, 'critscore_stats')

        ### Total review count ###
        try:
            result['all_reviews']['count'] = cast_int(find_by_class(critscore_stats, 'label').find('span').getText().replace(' reviews', ''))
        except:
            result['all_reviews']['count'] = None

        ### Percent compared to average (across all reviews)###
        result['all_reviews']['compared_to_average'] = dict()

        try:
            result['all_reviews']['compared_to_average']['percent_higher'] = cast_int(find_by_class(critscore_stats, 'data stats_score above_average', element_type='span').getText().replace('%', ''))
        except:
            result['all_reviews']['compared_to_average']['percent_higher'] = None

        try:
            result['all_reviews']['compared_to_average']['percent_same'] = cast_int(find_by_class(critscore_stats, 'data stats_score average', element_type='span').getText().replace('%', ''))
        except:
            result['all_reviews']['compared_to_average']['percent_same'] = None

        try:
            result['all_reviews']['compared_to_average']['percent_lower'] = cast_int(find_by_class(critscore_stats, 'data stats_score below_average', element_type='span').getText().replace('%', ''))
        except:
            result['all_reviews']['compared_to_average']['percent_lower'] = None

        ### Points against the average (across all reviews) ###
        points_against_average = find_by_class(find_by_class(soup, 'summary'), re.compile(r".*\baverage_value\b.*"), element_type='span').getText()
        # Get just the point value
        points_against_average_num = cast_float(points_against_average.split(' ')[0])
        # If the critic scores lower than the average, then make the value negative
        if 'lower' in points_against_average:
            points_against_average_num *= -1
        result['all_reviews']['points_against_average'] = points_against_average_num

        ### Score distribution for movie reviews ###
        result['score_distribution'] = dict()
        score_counts = find_by_class(soup, 'score_counts', element_type='ol')
        for element in score_counts.find_all('li', class_='score_count'):
            label = element.find('span', class_='label').getText()
            count = cast_int(element.find('span', class_='count').getText())
            if label == 'Positive:':
                result['score_distribution']['positive'] = count
            elif label == 'Mixed:':
                result['score_distribution']['mixed'] = count
            elif label == 'Negative:':
                result['score_distribution']['negative'] = count

        result['movie_reviews_count'] = cast_int(find_by_class(find_by_class(soup, 'reviews_total'), 'count', element_type='span').find('a').getText())


        review_scores_element = find_by_class(soup, 'profile_score_summary critscore_summary')
        try:
            result['average_review_score'] = cast_int(find_by_class(soup, re.compile(r".*\btextscore\b.*"), element_type='span').getText())
        except:
            result['average_review_score'] = None

        try:
            result['highest_review_score'] = cast_int(find_by_class(review_scores_element, 'highest_review', element_type='tr').find('span').getText())
        except:
            result['highest_review_score'] = None

        try:
            result['lowest_review_score'] = cast_int(find_by_class(review_scores_element, 'lowest_review', element_type='tr').find('span').getText())
        except:
            result['lowest_review_score'] = None

        result['reviews'] = get_reviews_by_critic(url)

        logging.debug(str(len(result['reviews'])) + ' reviews found in total for ' + slug)

        return result

    except:
        # Give up on the critic if an exception makes it all the way to this level
        logging.error("Giving up on critic: " + slug)

def get_reviews_by_critic(url):
    html_doc = keep_trying_to_get_html(url)
    soup = BeautifulSoup(html_doc)

    reviews = []

    for review in soup.find_all('div', class_='review_wrap'):
        review_dict = dict()

        review_dict['movie_name'] = find_by_class(review, 'review_product').find('a').getText()

        # Gets the release year of the movie
        # try:
        #     movie_url = find_by_class(review, 'review_product').find('a')['href']
        #     movie_html = keep_trying_to_get_html('http://www.metacritic.com' + movie_url)
        #     movie_soup = BeautifulSoup(movie_html)
        #     movie_date = movie_soup.find('li', class_='summary_detail release_data').find('span', class_='data').getText().strip()
        #     review_dict['movie_year'] = int(movie_date.split(', ')[-1])
        # except:
        #     review_dict['movie_year'] = None

        # Gets the slug of the movie
        try:
            review_dict['movie_slug'] = find_by_class(review, 'review_product').find('a')['href'].replace('/movie/', '')
        except:
            review_dict['movie_slug'] = None

        try:
            review_dict['review_body'] = find_by_class(review, 'review_body').getText().strip()
        except:
            review_dict['review_body'] = None

        try:
            review_dict['publication_title'] = find_by_class(review, 'review_action publication_title', element_type='li').getText()
        except:
            review_dict['publication_title'] = None

        try:
            score_element = find_by_class(review, 'review_product_score brief_critscore', element_type='li')
            review_dict['score'] = cast_int(find_by_class(score_element, re.compile(r".*\bmetascore_w\b.*"), element_type='span').getText())
        except:
            review_dict['score'] = None
            
        try:
            posted_date = find_by_class(review, 'review_action post_date', element_type='li')
            if posted_date:
                review_dict['post_date'] = posted_date.getText().replace('Posted ', '')
            else:
                review_dict['post_date'] = None
        except:
            review_dict['post_date'] = None

        reviews.append(review_dict)

    logging.debug('[keep_trying_to_get_html] ' + str(len(reviews)) + ' reviews found on page.')
    
    pagination = find_by_class(soup, 'flipper next', element_type='span')
    if pagination:
        pagination = pagination.find('a')
    if pagination:
        logging.debug('[get_reviews_by_critic] Next page found. Recursing.')
        next_page_reviews = get_reviews_by_critic('http://www.metacritic.com' + pagination['href'])

        # Don't add duplicate reviews that Metacritic for some reason shows (their pagination is broken)
        for new_review in next_page_reviews:
            already_exists = False
            for old_review in reviews:
                if new_review['movie_name'] == old_review['movie_name']:
                    already_exists = True
            if not already_exists:
                reviews.append(new_review)

    return reviews