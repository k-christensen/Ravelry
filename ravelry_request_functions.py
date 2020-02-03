def get_favs_list(username):
    fav_list = []
    favs_url = 'https://api.ravelry.com/people/{}/favorites/list.json'.format(username)
#     following request returns json with two keys: favorites and paginator
#     for the following request, I've added the params page size, which is 100 (maximum size), and page number (first page in the following request)
    favs = requests.get(favs_url, auth = (personal_keys.username(),personal_keys.password()),
                        params={'page_size':100, 'page':1})
#     the following will add a list of all the pattern ids for the favorited patterns and turns them into a list, which is then appended to the fav_list defined at the beginning of the function
    fav_list.append([favs.json()['favorites'][item]['favorited']['id'] for item in range(0,len(favs.json()['favorites']))])
#     in the event the user has more than 100 favorites, this loop will essentially go in and make a new request for the next page of likes, this loop finishes when the page number (which starts at 2 because we've already requested page one above) equals the last page
    if favs.json()['paginator']['page_count']>1:
#         page_number is 2 because first page is already in fav_list
        page_number = 2
#         loop to do successive requests for new pages of favorited pattern ids
        while page_number <= favs.json()['paginator']['last_page']:
            new_request_favs = requests.get(favs_url, auth = (personal_keys.username(),personal_keys.password()),
                        params={'page_size':100, 'page':page_number})
#             append the new list of favorites to the old list containing the first 100 favorites
            fav_list.append([new_request_favs.json()['favorites'][item]['favorited']['id'] 
                         for item in range(0,len(new_request_favs.json()['favorites']))])
#             add one to the page number so it will request the page following page 2, this will be done for as long as there are more pages to be requested
            page_number += 1
#     since the fav_list is currently a list of lists, the following function flattens the fav_list into one long list of ids
    flat_list = [item for sublist in fav_list for item in sublist]
    return flat_list

def pattern_list_to_tf_idf_df(pattern_list):
#     create url to request from api
    patterns_url = 'https://api.ravelry.com/patterns.json?ids={}'.format('+'.join(id_list))
#     make the request to the api
    patterns = requests.get(patterns_url,auth=
                            (personal_keys.username(),
                             personal_keys.password()))
#     create a dictionary for the attributes for each pattern where each attribute = 1
    attr_list = []
    for key in patterns.json()['patterns'].keys():
        attr_list.append({attr['permalink']:1 
                          for attr in patterns.json()
                          ['patterns'][key]['pattern_attributes']})
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

