import pickle
import json

yarn_weight_list = ['thread', 'cobweb', 'lace', 
'light-fingering', 'fingering', 
'sport', 'dk', 'worsted', 
'aran', 'bulky', 'super-bulky', 'jumbo']

id_list = list(range(0,len(yarn_weight_list)))

id_dict = dict(zip(id_list, yarn_weight_list))

with open("yarn_id_dict.json", 'w') as outfile:
    json.dump(id_dict, outfile)

def create_yarn_list(input_weight):
    id_dict = pickle.load( open( "yarn_id_dict.p", "rb" ) )
    input_weight = input_weight.lower()
    yarn_list = [input_weight]
    for num,name in id_dict.items():
        if name == input_weight:
            input_id = num
    if input_id == 0:
        yarn_list.append(id_dict[1])
    elif input_id == 11:
        yarn_list.append(id_dict[10])
    else:
        yarn_list.extend((id_dict[input_id-1], id_dict[input_id+1]))
    return yarn_list


