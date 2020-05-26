import json
import pickle

with open('sample.json') as json_file:
    final_json = json.load(json_file)

pref_sort_20 = pickle.load( open( "pref_sort_20.p", "rb" ) )

rank_list = ['rank_{}'.format(num) for num in list(range(1,len(list(pref_sort_20))+1))]

rank_dict = dict(zip(rank_list, list(pref_sort_20)))

with open("rank_dict.json", 'w') as outfile:
    json.dump(rank_dict, outfile)

with open('rank_dict.json') as dict_file:
    opened_rank_dict = json.load(dict_file)

pref_sort_20

final_json['patterns']['rank_1']['user_preference_score']

for k,v in rank_dict.items():
    if v in final_json['patterns'].keys():
        final_json['patterns'][k] = final_json['patterns'][v]

final_json['patterns'] = dict([(k,v) for k,v in final_json['patterns'].items()][20:])

final_json['patterns'].keys()

exp_copy_json['patterns']['rank_1']['id']

final_json['patterns'] = dict([(k,v) for k,v in final_json['patterns'].items()][20:])

exp_copy_json['patterns']['rank_1']['user_preference_score']

[final_json['patterns'][item]['permalink'] for item in exp_copy_json['patterns'].keys()]
