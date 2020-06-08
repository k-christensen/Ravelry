import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys
from pattern_attr_funcs import *
from yarn_weights import create_yarn_list

# search term goes in, search json comes out
def search(term):
    search_url = 'https://api.ravelry.com/patterns/search.json?query={}'.format(term)
    search = requests.get(search_url, auth = (personal_keys.username(),personal_keys.password()))
    s_json = search.json()
    return s_json

# json file of patterns goes in, list of pattern ids comes out
def search_pattern_list(s_json):
    p_list = s_json['patterns']
    return [p_list[ind]['id'] for ind in list(range(0,len(p_list)))]

def search_to_list(term):
    s_json = search(term)
    return search_pattern_list(s_json)

# turns list into string separated by '%7C', which is 'or' in the rav search url
def or_string(attr_list):
    return '%7C'.join(attr_list)

# some of the attributes are actually listed under 'fit' for search, 
# so the pattern attributes need to be split into two lists 
# the first list is the list of attributes that would be searched under 'fit'
# and the other list is the attributes that would actually be listed under pa
def fit_and_attr_split(attr_list):
    fit_name_list = ['adult','baby','child','doll-size',
 'newborn-size','preemie','teen','toddler',
 'negative-ease','no-ease','positive-ease',
 'maternity','fitted','miniature','oversized',
 'petite','plus','tall','female','male','unisex']
    attribute_list = []
    fit_list = []
    for item in attr_list:
        if item in fit_name_list:
            fit_list.append(item)
        else:
            attribute_list.append(item)
    return [fit_list, attribute_list]

# creates the unique part of the search url
def unique_search_url_section(attr_dict):
    attr_and_fit_list = fit_and_attr_split(attr_dict['pattern_attributes'])
    attr_list = attr_and_fit_list[1]
    url_sect = None
    if len(attr_list) > 0:
        attr_str = or_string(attr_list)
        url_sect = 'pa={}&'.format(attr_str)
    fit_list = attr_and_fit_list[0]
    if len(fit_list) > 0:
        fit_str = or_string(fit_list)
        fit_url_sect = 'fit={}&'.format(fit_str)
        if url_sect is not None:
            url_sect = url_sect + fit_url_sect
        else:
            url_sect = fit_url_sect
    cat_str = or_string(attr_dict['pattern_categories'])
    cat_url_sect = 'pc={}&'.format(cat_str)
    url_sect = url_sect + cat_url_sect
    if attr_dict['yarn_weight'] is not None:
        yarn_list = create_yarn_list(attr_dict['yarn_weight'])
        yarn_str = or_string(yarn_list)
        yarn_url_sect = 'weight={}&'.format(yarn_str)
        url_sect = yarn_url_sect + url_sect
    if url_sect.endswith('&'):
        url_sect = url_sect[:-1]
    return url_sect

# creates full search url
def full_search_url(url_sect):
    return 'https://api.ravelry.com/patterns/search.json?{}&sort=recently-popular&view=captioned_thumbs'.format(url_sect)

# combo of previous two functions
def create_search_url(attr_dict):
    url_sect = unique_search_url_section(attr_dict)
    return full_search_url(url_sect)

def pattern_to_search(url):
    attr_dict = url_to_attrs(url)
    search_url = create_search_url(attr_dict)
    return search_url

def search_using_url(search_url):
    search = requests.get(search_url, auth = (personal_keys.username(),personal_keys.password()))
    s_json = search.json()
    return s_json

def similar_patterns(url):
    search_url = pattern_to_search(url)
    return search_using_url(search_url)

def default_search():
    search_url = 'https://api.ravelry.com/patterns/search.json?sort=recently-popular&view=captioned_thumbs'
    return search_using_url(search_url)

# returns list of pattern_ids from the search json
def create_pattern_id_list(pattern_json):
    pattern_id_list = []
    patterns = pattern_json['patterns']
    for item in list(range(0,len(patterns))):
        pattern_id_list.append(patterns[item]['id'])
    return pattern_id_list

# creating a pattern pool using either the default search or the similar patterns search
def pattern_pool_json(item):
    search_json = None
    if item.startswith('https://www.ravelry.com/patterns/library'):
        search_json = similar_patterns(item)
    elif item == 'default_search':
        search_json = default_search()
    return search_json

def pattern_pool_list(item):
    pattern_json = pattern_pool_json(item)
    if pattern_json is not None:
        return create_pattern_id_list(pattern_json)

