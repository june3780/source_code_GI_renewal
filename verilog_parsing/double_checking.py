import json




def compare_1(first,second):
    with open(first,'r') as fw:
        data_doc=json.load(fw)
    fw.close()
    with open(second,'r') as fw:
        data_jun=json.load(fw)
    fw.close()

    jun=dict()
    for ivalue in data_jun:
        if '/' not in ivalue:
            che=str()
            for kvalue in data_jun[ivalue]:
                if 'PIN ' in kvalue:
                    che='che'
                    break
            if che=='che':
                jun.update({'PIN '+ivalue:data_jun[ivalue]})
            else:
                jun.update({'d25_core_top/'+ivalue:data_jun[ivalue]})
        else:
            jun.update({ivalue.split('/'+ivalue.split('/')[-1])[0].split('/')[-1]+'/'+ivalue.split('/')[-1]:data_jun[ivalue]})


    cheche=dict()
    chch=dict()
    temp=dict()
    for ivalue in jun:
        if ivalue not in data_doc:
            temp.update({ivalue:jun[ivalue]})
        else:
            temple=list()
            for kvalue in jun[ivalue]:
                if 'PIN ' not in kvalue:
                    temple.append(kvalue.split('/'+kvalue.split('/')[-1])[0].split('/')[-1]+'/'+kvalue.split('/')[-1])
                else:
                    temple.append(kvalue)

            if len(temple)!=len(data_doc[ivalue]['cell_list']):
                print('tpgmlwhnSAdtahjrjgfkahrt!@!@!@')
                break

            jun[ivalue]=temple
            yyy=len(cheche)
            for kvalue in temple:
                if kvalue not in data_doc[ivalue]['cell_list']:
                    if ivalue not in cheche:
                        cheche.update({ivalue:list()})
                    cheche[ivalue].append(kvalue)
            xxx=len(cheche)
            
            if yyy!=xxx:
                chch.update({ivalue:list()})
                for kvalue in data_doc[ivalue]['cell_list']:
                    if kvalue not in jun[ivalue]:
                        chch[ivalue].append(kvalue)

                
            
    for ivalue in temp:
        print(ivalue)
    for ivalue in cheche:
        print(chch[ivalue])
        print(cheche[ivalue])
        print()
    return temp







if __name__=="__main__":
    All=compare_1('net_list_easy.json','../data/easy/nets_from_june.json')
    with open('not_included.json','w') as fw:
        json.dump(All,fw,indent=4)