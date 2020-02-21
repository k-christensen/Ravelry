import requests
import time
import pandas as pd
import numpy as np
import re
import json
import pdb
from bs4 import BeautifulSoup
import personal_keys

def get_favs_list(username):
    fav_list = []
    favs_url = 'https://api.ravelry.com/people/{}/favorites/list.json'.format(username)
#     following request returns json with two keys: favorites and paginator
#     for the following request, I've added the params page size, 
#     which is 100 (maximum size), and page number (first page in the following request)
    favs = requests.get(favs_url, auth = (personal_keys.username(),personal_keys.password()),
                        params={'page_size':100, 'page':1})
#     the following will add a list of all the pattern ids for the favorited patterns and turns them into a list, which is then appended to the fav_list defined at the beginning of the function
    for item in range(0,len(favs.json()['favorites'])):
        if favs.json()['favorites'][item]['favorited'] is not None:
            if 'pattern_id' in favs.json()['favorites'][item]['favorited'].keys():
                fav_list.append(favs.json()['favorites'][item]['favorited']['pattern_id'])
            elif 'id' in favs.json()['favorites'][item]['favorited'].keys():
                fav_list.append(favs.json()['favorites'][item]['favorited']['id'])

#     in the event the user has more than 100 favorites, 
# this loop will essentially go in and make a new request for the next page of likes, 
# this loop finishes when the page number (which starts at 2 because we've already requested page one above) 
# equals the last page
    if favs.json()['paginator']['page_count']>1:
#         page_number is 2 because first page is already in fav_list
        page_number = 2
#         loop to do successive requests for new pages of favorited pattern ids
        while page_number <= favs.json()['paginator']['last_page']:
            new_request_favs = requests.get(favs_url, auth = (personal_keys.username(),personal_keys.password()),
                        params={'page_size':100, 'page':page_number})
#             append the new list of favorites to the old list containing the first 100 favorites
            for item in range(0,len(new_request_favs.json()['favorites'])):
                if new_request_favs.json()['favorites'][item]['favorited'] is not None:
                    if 'pattern_id' in new_request_favs.json()['favorites'][item]['favorited'].keys():
                        fav_list.append(new_request_favs.json()['favorites'][item]['favorited']['pattern_id'])
                    elif 'id' in new_request_favs.json()['favorites'][item]['favorited'].keys():
                        fav_list.append(new_request_favs.json()['favorites'][item]['favorited']['id'])
#             add one to the page number so it will request the page following page 2, this will be done for as long as there are more pages to be requested
            page_number += 1
#     since the fav_list is currently a list of lists, the following function flattens the fav_list into one long list of ids
    return fav_list

def get_friend_favs(username):    
    friend_list = friend_username_list(username)
    all_friend_projs = []
    for user in friend_list:
        all_friend_projs.append(get_favs_list(user))   
    flat_list = [item for sublist in all_friend_projs for item in sublist]
    edited_flat_list = [item for item in flat_list if item is not None]
    return edited_flat_list

def get_project_list(username):
    proj_list = []
    projects_url = 'https://api.ravelry.com/projects/{}/list.json'.format(username)
#     following request returns json with all project info
    projects = requests.get(projects_url, 
                        auth = (personal_keys.username(),personal_keys.password()))
#     the following will add a list of all the pattern ids for the patterns and turns them into a list
    proj_list.append([projects.json()['projects'][item]['pattern_id'] for item in range(0,len(projects.json()['projects']))])
    return [item for sublist in proj_list for item in sublist]

def get_friend_projs(username):    
    friend_list = friend_username_list(username)
    all_friend_projs = []
    for user in friend_list:
        all_friend_projs.append(get_project_list(user))        
    flat_list = [item for sublist in all_friend_projs for item in sublist]
    edited_flat_list = [item for item in flat_list if item is not None]
    return edited_flat_list


# below function takes a pattern list and returns a pattern list where all the pattern codes do not return errors 
def problem_children(pattern_list):
    del_list = []
    batch_50_prob = []
    batch_10_prob = []
    pattern_list_str = [str(item) for item in pattern_list]
    #     below checks in batches of 50 if the patterns status code is not 200
    l_of_l_patterns_50 = [pattern_list_str[i:i + 50] for i in range(0, len(pattern_list_str), 50)]
    batch_num = 0
    while batch_num < len(l_of_l_patterns_50):
        #     create url to request from api
        patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns_50[batch_num]))
        #     make the request to the api
        patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
        if patterns.status_code is not 200:
            batch_50_prob.append(l_of_l_patterns_50[batch_num])
        batch_num += 1
    #         if any of the batches come back with an error, then we go into figuring out which pattern codes are the issue
    if len(batch_50_prob)>0:
    #         below I break the list of 50 or more into batches of 10 so we're not individually testing 50+ pattern codes
        flat_50 = [item for sublist in batch_50_prob for item in sublist]
        l_of_l_patterns_10 = [flat_50[i:i + 10] for i in range(0, len(flat_50), 10)]
        new_batch_num = 0
        while new_batch_num < len(l_of_l_patterns_10):
        #     create url to request from api
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns_10[new_batch_num]))
        #     make the request to the api
            patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
            if patterns.status_code is not 200:
                batch_10_prob.append(l_of_l_patterns_10[new_batch_num])
            new_batch_num += 1
        flat_10 = [item for sublist in batch_10_prob for item in sublist]
        for item in flat_10:
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(item))
            patterns = requests.get(patterns_url, auth = (personal_keys.username(),personal_keys.password()))
            if patterns.status_code is not 200:
                del_list.append(item)
    return [item for item in pattern_list_str if item not in del_list]

# simple function to return easy list of a user's friends' usernames
def friend_username_list(username):
    user_url = 'https://api.ravelry.com/people/{}/friends/list.json'.format(username)
    user = requests.get(user_url, 
                        auth = (personal_keys.username(),personal_keys.password()))

    return [user.json()['friendships'][item]['friend_username'] for item in range(0,len(user.json()['friendships']))]
def problem_children_large_scale(pattern_list):
    del_list = []
    batch_100_prob = []
    batch_50_prob = []
    batch_10_prob = []
    pattern_list_str = [str(item) for item in pattern_list]
        #     below checks in batches of 100 if the patterns status code is not 200
    l_of_l_patterns_100 = [pattern_list_str[i:i + 100] for i in range(0, len(pattern_list_str), 100)]
    batch_num = 0
    while batch_num < len(l_of_l_patterns_100):
        #     create url to request from api
        patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns_100[batch_num]))
        #     make the request to the api
        patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
        if patterns.status_code is not 200:
            batch_100_prob.append(l_of_l_patterns_100[batch_num])
        batch_num += 1
    #         if any of the batches come back with an error, then we go into figuring out which pattern codes are the issue
    if len(batch_100_prob)>0:
    #         below I break the list of 50 or more into batches of 10 so we're not individually testing 50+ pattern codes
        flat_100 = [item for sublist in batch_100_prob for item in sublist]
    #     below checks in batches of 50 if the patterns status code is not 200
        l_of_l_patterns_50 = [pattern_list_str[i:i + 50] for i in range(0, len(flat_100), 50)]
        batch_num = 0
        while batch_num < len(l_of_l_patterns_50):
        #     create url to request from api
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns_50[batch_num]))
        #     make the request to the api
            patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
            if patterns.status_code is not 200:
                batch_50_prob.append(l_of_l_patterns_50[batch_num])
            batch_num += 1
    #         if any of the batches come back with an error, then we go into figuring out which pattern codes are the issue
    if len(batch_50_prob)>0:
    #         below I break the list of 50 or more into batches of 10 so we're not individually testing 50+ pattern codes
        flat_50 = [item for sublist in batch_50_prob for item in sublist]
        l_of_l_patterns_10 = [flat_50[i:i + 10] for i in range(0, len(flat_50), 10)]
        new_batch_num = 0
        while new_batch_num < len(l_of_l_patterns_10):
        #     create url to request from api
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns_10[new_batch_num]))
        #     make the request to the api
            patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
            if patterns.status_code is not 200:
                batch_10_prob.append(l_of_l_patterns_10[new_batch_num])
            new_batch_num += 1
        flat_10 = [item for sublist in batch_10_prob for item in sublist]
        for item in flat_10:
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(item))
            patterns = requests.get(patterns_url, auth = (personal_keys.username(),personal_keys.password()))
            if patterns.status_code is not 200:
                del_list.append(item)
    return [item for item in pattern_list_str if item not in del_list]
    
def pattern_list_to_tf_idf_df(pattern_list):
#     turn ints into strings for the request url
    pattern_list = [str(item) for item in pattern_list]
#     if the pattern list is less than 50, just one request is needed, otherwise, multiple requests are needed
    if len(pattern_list) < 50:
    #     create url to request from api
        patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(pattern_list))
    #     make the request to the api
        patterns = requests.get(patterns_url, 
                            auth = (personal_keys.username(),personal_keys.password()))
    #     create a dictionary for the attributes for each pattern where each attribute = 1
        attr_list = []
        for key in patterns.json()['patterns'].keys():
            attr_list.append({attr['permalink']:1 for attr in patterns.json()['patterns'][key]['pattern_attributes']})
    else:
#         create nested list that contains lists of either 50 patterns or the remainder of length of list/50
        l_of_l_patterns = [pattern_list[i:i + 25] for i in range(0, len(pattern_list), 25)]
        batch_num = 0
        attr_list = []
        while batch_num < len(l_of_l_patterns):
        #     create url to request from api
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns[batch_num]))
        #     make the request to the api
            patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
#             create a dictionary for the attributes for each pattern where each attribute = 1
            for key in patterns.json()['patterns'].keys():
                    attr_list.append({attr['permalink']:1 for attr in patterns.json()['patterns'][key]['pattern_attributes']})
            batch_num += 1       
#     in case pattern list is list of strings, make it into list of integers
    p_l = [int(item) for item in pattern_list]
#     turn list of dictionaries into a dataframe, turn all the NaN values into zero so the dataframe is ones and zeroes
    df_attr = pd.DataFrame(attr_list).fillna(0)
#     make a new column that is the pattern id number for each pattern
    df_attr['pattern_id'] = p_l
#     set the pattern id number as the index
    df_attr = df_attr.set_index('pattern_id')
#     instate argument for the tf/idf transformer
    tfidf = TfidfTransformer()
#     transform dataframe into tf/idf array
    tf_array = tfidf.fit_transform(df_attr).toarray()
#     turn tf/idf array into dataframe
    df_tf = pd.DataFrame(tf_array, columns=df_attr.columns)
#     create pattern id column
    df_tf['pattern_id'] = p_l
#     set pattern id column as index of tf/idf dataframe
    df_tf = df_tf.set_index('pattern_id')
    return df_tf

def pattern_attr(pattern_list):
#     turn ints into strings for the request url
    pattern_list = [str(item) for item in pattern_list]
#     if the pattern list is less than 50, just one request is needed, otherwise, multiple requests are needed
    if len(pattern_list) < 50:
    #     create url to request from api
        patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(pattern_list))
    #     make the request to the api
        patterns = requests.get(patterns_url, 
                            auth = (personal_keys.username(),personal_keys.password()))
    #     create a dictionary for the attributes for each pattern where each attribute = 1
        attr_list = []
        for key in patterns.json()['patterns'].keys():
            attr_list.append({attr['permalink']:1 for attr in patterns.json()['patterns'][key]['pattern_attributes']})
    else:
#         create nested list that contains lists of either 50 patterns or the remainder of length of list/50
        l_of_l_patterns = [pattern_list[i:i + 50] for i in range(0, len(pattern_list), 50)]
        batch_num = 0
        attr_list = []
        while batch_num < len(l_of_l_patterns):
        #     create url to request from api
            patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(l_of_l_patterns[batch_num]))
        #     make the request to the api
            patterns = requests.get(patterns_url, 
                                auth = (personal_keys.username(),personal_keys.password()))
#             create a dictionary for the attributes for each pattern where each attribute = 1
            for key in patterns.json()['patterns'].keys():
                    attr_list.append({attr['permalink']:1 for attr in patterns.json()['patterns'][key]['pattern_attributes']})
            batch_num += 1
    return dict(zip(pattern_list, attr_list))

def fav_pattern_attr_to_count_df(pattern_list, attr_list):
#     in case pattern list is list of strings, make it into list of integers
    p_l = [int(item) for item in pattern_list]
#     turn list of dictionaries into a dataframe, turn all the NaN values into zero so the dataframe is ones and zeroes
    df_attr = pd.DataFrame(attr_list).fillna(0)
    df_attr['pattern_id'] = p_l
    df_attr = df_attr.set_index('pattern_id')
    return df_attr
    
def proj_pattern_attr_to_count_df(pattern_list, attr_list):
#     in case pattern list is list of strings, make it into list of integers
    p_l = [int(item) for item in pattern_list]
#     turn list of dictionaries into a dataframe, turn all the NaN values into zero so the dataframe is ones and zeroes
    df_attr = pd.DataFrame(attr_list).fillna(0)
    df_attr = df_attr*2
    df_attr['pattern_id'] = p_l
    df_attr = df_attr.set_index('pattern_id')
#     in order to weight the attributes in patterns higher than favs, 
#     instead of each attr being one, like in the favs function, they're counted twice
    return df_attr

def proj_and_fav_count_df(project_list, proj_attr, fav_list, fav_attr):
    proj_df = proj_pattern_attr_to_count_df(project_list, proj_attr)
    modified_fav_list = [pattern for pattern in fav_list if pattern not in project_list]
    fav_df = fav_pattern_attr_to_count_df(modified_fav_list, fav_attr)
    proj_and_fav = pd.concat([proj_df, fav_df])
    return proj_and_fav

# below function combines many of above functions such that all you put in is someone's username and it spits out dataframe of favs and projects
def get_user_favs_and_projects(username):
    fav_list = get_favs_list(username)
    proj_list = get_project_list(username)
    checked_fav_list = problem_children(fav_list)
    checked_proj_list = problem_children(proj_list)
    favs = pattern_attr(checked_fav_list)
    projs = pattern_attr(checked_proj_list)
    pf_df = proj_and_fav_count_df(projs, favs)
    return pf_df

def pattern_attr_to_tf_idf_df(pattern_list, attr_list):
#     in case pattern list is list of strings, make it into list of integers
    p_l = [int(item) for item in pattern_list]
#     turn list of dictionaries into a dataframe, turn all the NaN values into zero so the dataframe is ones and zeroes
    df_attr = pd.DataFrame(attr_list).fillna(0)
#     make a new column that is the pattern id number for each pattern
    df_attr['pattern_id'] = p_l
#     set the pattern id number as the index
    df_attr = df_attr.set_index('pattern_id')
#     instate argument for the tf/idf transformer
    tfidf = TfidfTransformer()
#     transform dataframe into tf/idf array
    tf_array = tfidf.fit_transform(df_attr).toarray()
#     turn tf/idf array into dataframe
    df_tf = pd.DataFrame(tf_array, columns=df_attr.columns)
#     create pattern id column
    df_tf['pattern_id'] = p_l
#     set pattern id column as index of tf/idf dataframe
    df_tf = df_tf.set_index('pattern_id')
    return df_tf