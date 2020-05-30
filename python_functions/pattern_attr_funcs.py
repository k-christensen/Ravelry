import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
import math
from bs4 import BeautifulSoup
import personal_keys as personal_keys
from fav_funcs import *
from proj_funcs import *

# input: list of patterns, output: json file with patterns
def multiple_pattern_request(pattern_list):
    pattern_list = [str(code) for code in pattern_list]
    if len(pattern_list) > 500:
        first_pattern_list = pattern_list[:500]
        second_pattern_list = pattern_list[500:]
        first_patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(first_pattern_list))
        first_patterns = requests.get(first_patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
        if first_patterns.status_code is not 200:
            return "first pattern batch bad"
        second_patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(second_pattern_list))
        second_patterns = requests.get(second_patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
        if second_patterns.status_code is not 200:
            return "second pattern batch bad"
        large_patterns = first_patterns.json()
        large_patterns['patterns'].update(second_patterns.json()['patterns'])
        return large_patterns 
    else:
        patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(pattern_list))
        patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
    if patterns.status_code is 200:
        return patterns.json()
    else:
        return 404

# single pattern equivalent of mpr
def single_pattern_request(code):
    if type(code) is not str:
        code = str(code)
    pattern_url = 'https://api.ravelry.com/patterns/{}.json'.format(code)
    pattern = requests.get(pattern_url, 
                            auth = (personal_keys.username(),personal_keys.password()))
    return pattern.json()['pattern']

# returns the last part of a given pattern url
# this last part can be used to look up the pattern
def url_to_code(url):
    split_list = url.split('https://www.ravelry.com/patterns/library/')
    return split_list[-1]

# combo of above two, put in url, output is a json of the pattern
def url_to_request(url):
    code = url_to_code(url)
    return single_pattern_request(code)


# input of this is the output of single pattern request
# output is a dictionary containing 
# yarn weight, pattern cats, and pattern attrs
def attrs_single_pattern(pattern):
    cat_dict = pattern['pattern_categories'][0]
    cat_list = [cat_dict['permalink']]
    new_dict = cat_dict['parent']
    while 'parent' in new_dict.keys():
        cat_list.append(new_dict['permalink'])
        new_dict = new_dict['parent']
    if len(cat_list)>1:
        cat_list = cat_list[:2]
    if 'yarn_weight' in pattern.keys():
        yarn_weight = '-'.join(pattern['yarn_weight']['name'].split(' '))
    else:
        yarn_weight = None
    attr_dict = {'yarn_weight':yarn_weight,
    'pattern_attributes': [attr['permalink'] for attr in pattern['pattern_attributes']],
    'pattern_categories':cat_list}
    return attr_dict

# combo of above two funcs
def single_request_to_attrs(code):
    pattern = single_pattern_request(code)
    return attrs_single_pattern(pattern)

def url_to_attrs(url):
    code = url_to_code(url)
    return single_request_to_attrs(code)
    
# similar to multiple pattern request except it returns just patterns section of json returned in mpr
def pattern_req(pattern_list):
    pattern_req = multiple_pattern_request(pattern_list)
    patterns = pattern_req['patterns']
    return patterns

#returns dict of pattern codes and attributes associated with those patterns 
def attr_dict(pattern_list):
    patterns = pattern_req(pattern_list)
    attr_dict = {}
    for key in patterns.keys():
        attr_dict.update(({key:{"pa_{}".format(attr['permalink']):1 
        for attr in patterns[key]['pattern_attributes']}}))
    return attr_dict

# returns dict of pattern codes and the yarn weight associated
# yarn weight is given as "yarn_id_[what you would put in for url]"
# note: since the name contains spaces 
# the name is split and put back together with dash where the space was

# in the event there is not a yarn weight listed 
# because the pattern writer was an idiot, 
# pattern is assigned the yarn weight "yarn_id_None" as a placeholder
def yarn_dict(pattern_list):
    patterns = pattern_req(pattern_list)
    yarn_dict = {}
    for key in patterns.keys():
        if 'yarn_weight' in patterns[key]:    
            yarn_dict.update({key:
            {"yarn_id_{}".format('-'.join(patterns[key]['yarn_weight']['name'].split(' '))):1}})
        else:
            yarn_dict.update({key:{"yarn_id_None":1}})
    return yarn_dict

# returns a dict of the pattern code and the different categories that the given pattern is in
def categ_dict(pattern_list):
    patterns = pattern_req(pattern_list)
    categ_dict = {}
    for key in patterns.keys():
        cat_dict = patterns[key]['pattern_categories'][0]
        cat_list = [cat_dict['permalink']]
        new_dict = cat_dict['parent']
        while 'parent' in new_dict.keys():
            cat_list.append(new_dict['permalink'])
            new_dict = new_dict['parent']
        full_cat_dict = {'pc_{}'.format(cat):1 for cat in cat_list}
        categ_dict.update({key:full_cat_dict})
    return categ_dict

# creates dictionary of the pattern and the pattern attributes, categories, and yarn weight all in one dict
# essentially combines three previous functions plus compressing all three dictionaries into one
def all_attr_dict(pattern_list):
    attrib_dict = attr_dict(pattern_list)
    y_dict = yarn_dict(pattern_list)
    ca_dict = categ_dict(pattern_list)
    finaldict = {key:[attrib_dict[key], y_dict[key], ca_dict[key]] 
                for key in y_dict.keys()}
    for key in finaldict:
        while len(finaldict[key])>1:
            finaldict[key][0].update(finaldict[key][1])
            finaldict[key].pop(1)
        finaldict[key] = finaldict[key][0]
    normed_fd = {key:{k:1/math.sqrt(len(d)) for k in d} for key,d in finaldict.items()}
    return normed_fd

#funcs no longer used~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# # creates list of attributes from pattern list
# def create_attr_list(pattern_list):
#     attr_list = []
#     patterns = multiple_pattern_request(pattern_list)
#     if patterns != 404:
#         for key in patterns['patterns'].keys():
#             attr_list.append({attr['permalink']:1 for attr in 
#             patterns['patterns'][key]['pattern_attributes']})
#     return attr_list

# # output is a dict where the key is the pattern code and value is 
# def create_all_attrib_dict(pattern_list):
#     patterns = multiple_pattern_request(pattern_list)
#     ones_ex_attr_dict = {}
#     yarn_dict = {}
#     categ_dict = {}

#     for key in patterns['patterns'].keys():
#         ones_ex_attr_dict.update(({key:{attr['permalink']:1 for attr in patterns['patterns'][key]['pattern_attributes']}}))
#         data = patterns['patterns'][key]['pattern_categories'][0]    
#         df = pd.io.json.json_normalize(data)
#         df = df.filter(regex = 'permalink$', axis = 1)
#         atrib_dict = df.to_dict(orient='records')[0]
#         filtered_attrib_dict = {k:v for k,v in atrib_dict.items() if v != 'categories'}
#         cat_dict = {v:1 for v in filtered_attrib_dict.values()}
#         categ_dict.update({key:cat_dict})

#         if 'yarn_weight' in patterns['patterns'][key]:    
#             yarn_dict.update({key:{"yarn_id_{}".format(patterns['patterns'][key]['yarn_weight']['id']):1}})
#         else:
#             yarn_dict.update({key:{"yarn_id_None":1}})

#     finaldict = {key:[ones_ex_attr_dict[key], yarn_dict[key], categ_dict[key]] for key in yarn_dict.keys()}
#     for other_key in finaldict:
#         while len(finaldict[other_key])>1:
#             finaldict[other_key][0].update(finaldict[other_key][1])
#             finaldict[other_key].pop(1)
#     return finaldict



# # input: list of pattern id's, 
# # output: dictionary where keys are pattern id's and values are a dict of attributes
# def pattern_attr(pattern_list):
#     pattern_list = [str(item) for item in pattern_list]
#     if len(pattern_list) < 50:
#         attr_list = create_attr_list(pattern_list)
#     else:
# #         create nested list that contains lists of either 50 patterns or the remainder of length of list/50
#         l_of_l_patterns = [pattern_list[i:i + 50] for i in range(0, len(pattern_list), 50)]
#         batch_num = 0
#         attr_dict = {}
#         while batch_num < len(l_of_l_patterns):
#             batch_attr_dict = create_all_attrib_dict(l_of_l_patterns[batch_num])
#             attr_dict.update(batch_attr_dict)
#             batch_num += 1
#     return attr_dict

# #testing area~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~