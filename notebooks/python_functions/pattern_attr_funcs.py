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
    patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(pattern_list))
    patterns = requests.get(patterns_url, 
                            auth = (personal_keys.username(),personal_keys.password()))
    if patterns.status_code is 200:
        return patterns.json()
    else:
        return 404

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
        attr_dict.update(({key:{attr['permalink']:1 
        for attr in patterns[key]['pattern_attributes']}}))
    return attr_dict

# returns dict of pattern codes and the yarn weight associated
# in the event there is not a yarn weight listed because the pattern writer was an idiot, 
# pattern is assigned the yarn weight "yarn_id_None" as a placeholder
def yarn_dict(pattern_list):
    patterns = pattern_req(pattern_list)
    yarn_dict = {}
    for key in patterns.keys():
        if 'yarn_weight' in patterns[key]:    
            yarn_dict.update({key:
            {"yarn_id_{}".format(patterns[key]['yarn_weight']['id']):1}})
        else:
            yarn_dict.update({key:{"yarn_id_None":1}})
    return yarn_dict

# returns a dict of the pattern code and the different categories that the given pattern is in
def categ_dict(pattern_list):
    patterns = pattern_req(pattern_list)
    categ_dict = {}
    for key in patterns.keys():
        data = patterns[key]['pattern_categories'][0]    
        df = pd.io.json.json_normalize(data)
        df = df.filter(regex = 'permalink$', axis = 1)
        atrib_dict = df.to_dict(orient='records')[0]
        filtered_attrib_dict = {k:v for k,v in 
                                atrib_dict.items() if v != 'categories'}
        cat_dict = {v:1 for v in filtered_attrib_dict.values()}
        categ_dict.update({key:cat_dict})
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

# from proj_funcs import *
# import math

# from fav_funcs import *

# over_50_ex = get_favs_list("katec125")

# pattern_attr(over_50_ex)


# fav_pattern_req = multiple_pattern_request(over_50_ex)

# fav_pattern_req['patterns']['522775']['yarn_weight']

# example_list = get_project_list_from_username("katec125")

# ex_pattern_request = multiple_pattern_request(example_list)

# len(ex_pattern_request['patterns']['91776']['pattern_attributes'])

# ex_attr_list = []
# for key in ex_pattern_request['patterns'].keys():
#     ex_attr_list.append({attr['permalink']:
#                         (1/math.sqrt(len(ex_pattern_request['patterns'][key]['pattern_attributes']))) 
#                         for attr in ex_pattern_request['patterns'][key]['pattern_attributes']})

# ex_pattern_request['patterns']['91776']['yarn_weight']['name']

# len(ex_attr_list[0])

# ones_ex_attr_dict = {}
# yarn_dict = {}
# categ_dict = {}

# for key in ex_pattern_request['patterns'].keys():
#     ones_ex_attr_dict.update(({key:{attr['permalink']:1 for attr in ex_pattern_request['patterns'][key]['pattern_attributes']}}))
#     yarn_dict.update({key:{"yarn_id_{}".format(ex_pattern_request['patterns'][key]['yarn_weight']['id']):1}})
#     data = ex_pattern_request['patterns'][key]['pattern_categories'][0]    
#     df = pd.io.json.json_normalize(data)
#     df = df.filter(regex = 'permalink$', axis = 1)
#     atrib_dict = df.to_dict(orient='records')[0]
#     filtered_attrib_dict = {k:v for k,v in atrib_dict.items() if v != 'categories'}
#     cat_dict = {v:1 for v in filtered_attrib_dict.values()}
#     categ_dict.update({key:cat_dict})

# finaldict = {key:[ones_ex_attr_dict[key], yarn_dict[key], categ_dict[key]] for key in ones_ex_attr_dict}
# for key in finaldict:
#     while len(finaldict[key])>1:
#         finaldict[key][0].update(finaldict[key][1])
#         finaldict[key].pop(1)

# finaldict

# while len(finaldict['91776'])>1:
#         finaldict['91776'][0].update(finaldict['91776'][1])
#         finaldict['91776'].pop(1)
# finaldict['91776']

# categ_dict

# yarn_dict


# ex_pattern_request['patterns']['91776']['pattern_categories']
# 828182    
#     # ones_ex_attr_dict.update({key:{"yarn_id_{}".format(ex_pattern_request['patterns'][key]['yarn_weight']['id']):1}})

# data = ex_pattern_request['patterns']['91776']['pattern_categories'][0]    
# df = pd.io.json.json_normalize(data)
# df = df.filter(regex = 'permalink$', axis = 1)
# atrib_dict = df.to_dict(orient='records')[0]
# filtered_attrib_dict = {k:v for k,v in atrib_dict.items() if v != 'categories'}
# cat_dict = {v:1 for v in filtered_attrib_dict.values()}

# cat_list = []
# for key in ex_pattern_request['patterns'].keys():
#     data = ex_pattern_request['patterns'][key]['pattern_categories'][0]    
#     df = pd.io.json.json_normalize(data)
#     df = df.filter(regex = 'permalink$', axis = 1)
#     atrib_dict = df.to_dict(orient='records')[0]
#     filtered_attrib_dict = {k:v for k,v in atrib_dict.items() if v != 'categories'}
#     cat_dict = {v:1 for v in filtered_attrib_dict.values()}
#     cat_list.append(cat_dict)

# cat_list

# finaldict = {key:(dict1[key], dict2[key]) for key in dict1}

