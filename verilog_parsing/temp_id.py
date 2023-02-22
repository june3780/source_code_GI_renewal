


import json
import os


def get_used_id(address,easy_or_medium):
    with open(address,'r')as fw:
        temp_dict=json.load(fw)
    fw.close()

    set_all=set()
    for ivalue in temp_dict:
        set_all.add(temp_dict[ivalue])
    
    easy_set={'CKLHQD20BWP12TM1P', 'CKLHQD2BWP12TM1P', 'CKLNQD4BWP12TM1P', 'CKLHQD24BWP12TM1P', 'CKLNQOPTMAD16BWP12TM1P', 'CKLNQD16BWP12TM1P', \
        'CKLNQD8BWP12TM1P', 'CKLHQD3BWP12TM1P', 'CKLNQD12BWP12TM1P', 'CKLNQOPTMAD20BWP12TM1P', 'CKLHQD8BWP12TM1P', 'CKLHQD12BWP12TM1P', 'CKLHQD1BWP12TM1P', \
        'CKLNQOPTMAD8BWP12TM1P', 'CKLHQD6BWP12TM1P', 'CKLNQD1BWP12TM1P', 'CKLNQD2BWP12TM1P', 'CKLHQD4BWP12TM1P', 'CKLNQD24BWP12TM1P', 'CKLNQD20BWP12TM1P', \
        'CKLNQD3BWP12TM1P', 'CKLNQD6BWP12TM1P', 'CKLNQOPTMAD24BWP12TM1P', 'CKLNQOPTMAD4BWP12TM1P', 'CKLNQOPTMAD1BWP12TM1P', 'CKLHQD16BWP12TM1P', 'CKLNQOPTMAD2BWP12TM1P'}
        
    medium_set={'CKLHQD16BWP12TM1PLVT', 'CKLNQD1BWP12TM1PLVT', 'CKLNQOPTMAD16BWP12TM1PLVT', 'CKLHQD6BWP12TM1PLVT', 'CKLHQD20BWP12TM1PLVT', 'CKLNQD12BWP12TM1PLVT', \
        'CKLHQD4BWP12TM1PLVT', 'CKLNQD24BWP12TM1PLVT', 'CKLHQD12BWP12TM1PLVT', 'CKLHQD8BWP12TM1PLVT', 'CKLNQOPTMAD2BWP12TM1PLVT', 'CKLHQD2BWP12TM1PLVT', \
        'CKLNQOPTMAD1BWP12TM1PLVT', 'CKLNQD2BWP12TM1PLVT', 'CKLNQD6BWP12TM1PLVT', 'CKLNQOPTMAD24BWP12TM1PLVT', 'CKLNQOPTMAD8BWP12TM1PLVT', 'CKLHQD24BWP12TM1PLVT', \
        'CKLHQD1BWP12TM1PLVT', 'CKLNQD8BWP12TM1PLVT', 'CKLNQD4BWP12TM1PLVT', 'CKLNQOPTMAD20BWP12TM1PLVT', 'CKLNQD16BWP12TM1PLVT', 'CKLHQD3BWP12TM1PLVT', \
        'CKLNQD20BWP12TM1PLVT', 'CKLNQD3BWP12TM1PLVT', 'CKLNQOPTMAD4BWP12TM1PLVT'}


    temp_set=set()
    for ivalue in set_all:
        if ivalue=='external_output_PIN' or ivalue=='external_input_PIN':
            continue

        if easy_or_medium=='easy' and ivalue+'12TM1P' in os.listdir('../../temp_data/lib/tcbn40lpbwp12tm1ptc_ccs/cell'):
            temp_set.add(ivalue+'12TM1P')
            #print(ivalue+'12TM1P')
            #if 'latch_index.json' in os.listdir('../../temp_data/lib/tcbn40lpbwp12tm1ptc_ccs/cell/'+ivalue+'12TM1P'):
            #    print(ivalue)
        elif easy_or_medium=='medium' and ivalue in os.listdir('../../temp_data/lib/tcbn40lpbwp12tm1plvttc_ccs/cell'):
            temp_set.add(ivalue)
            #print(ivalue)
            #if 'latch_index.json' in os.listdir('../../temp_data/lib/tcbn40lpbwp12tm1plvttc_ccs/cell/'+ivalue):
            #    print(ivalue)
    
    if easy_or_medium=='easy':
        intersection_set=easy_set&temp_set
        print(intersection_set)
    elif easy_or_medium=='medium':
        intersection_set=medium_set&temp_set
        print(intersection_set)

    return 0







if __name__=="__main__":
    checking='medium'
    id_group='../../data/'
    id_group=id_group+checking+'/'+checking+'/temp_id.json'


    get_used_id(id_group,checking)