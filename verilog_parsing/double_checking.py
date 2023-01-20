import json
import sys



def compare_1(first,second):

    with open(first,'r') as fw:
        data_doc=json.load(fw)
    fw.close()
    with open(second,'r') as fw:
        jun=json.load(fw)
    fw.close()


    temp=dict()

    for ivalue in data_doc:
        data_doc[ivalue]=data_doc[ivalue]['cell_list']

    '''constant0={'constant0':[]}
    constant1={'constant1':[]}
    will_del=list()

    for ivalue in data_doc:
        if ivalue.split('/')[-1]=='1\'b0':
            for kvalue in data_doc[ivalue]:
                constant0['constant0'].append(kvalue)
            will_del.append(ivalue)
        elif ivalue.split('/')[-1]=='1\'b1':
            for kvalue in data_doc[ivalue]:
                constant1['constant1'].append(kvalue)
            will_del.append(ivalue)

    for ivalue in will_del:
        del data_doc[ivalue]

    data_doc.update(constant0)
    data_doc.update(constant1)'''


    tt=int()
    test=dict()
    for ivalue in jun:
        if ivalue.startswith('assignModule'):
            continue
        for kvalue in jun[ivalue]:
            if kvalue not in data_doc[ivalue]:
                if ivalue not in test:
                    test.update({ivalue:[]})
                test[ivalue].append(kvalue)
                tt=tt+1
    print(tt)
    print('\n')
    tt=int()
    test=dict()
    for ivalue in data_doc:
        if ivalue.startswith('assignModule'):
            continue
        for kvalue in data_doc[ivalue]:
            if kvalue not in jun[ivalue]:
                if ivalue not in test:
                    test.update({ivalue:[]})
                test[ivalue].append(kvalue)
                tt=tt+1
    print(tt)
    '''for ivalue in temp:
        print(ivalue)
    for ivalue in cheche:
        print(chch[ivalue])
        print(cheche[ivalue])
        print()'''
    return temp







if __name__=="__main__":
    diff='easy'
    diff=sys.argv[1]
    All=compare_1('../../data/'+diff+'/net_list_'+diff+'.json','../../data/'+diff+'/nets_modified_by_june.json')
    with open('not_included.json','w') as fw:
        json.dump(All,fw,indent=4)