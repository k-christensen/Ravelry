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