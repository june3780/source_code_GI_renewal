import json
import sys



def compare_1(first,second):

    with open(first,'r') as fw:
        other_file=json.load(fw)
    fw.close()
    with open(second,'r') as fw:
        own_file=json.load(fw)
    fw.close()


    temp=dict()
    #### 타 컴퓨터의 코드로 parsing한 netlist의 내용인 cell_list를 딕션너리의 value로 설정
    for ivalue in other_file:
        other_file[ivalue]=other_file[ivalue]['cell_list']


    tt=int()
    test=dict()
    #### assignModule을 제외한 나머지 net들의 구성요소들이 own_file과 비교하여 other_file에 다 있는지, 없다면 몇개가 없는지 화면에 출력
    for ivalue in own_file:
        if ivalue.startswith('assignModule'):
            continue
        #### assignModule이 아닌 net의 경우
        for kvalue in own_file[ivalue]:
            if kvalue not in other_file[ivalue]:
                if ivalue not in test:
                    test.update({ivalue:[]})
                test[ivalue].append(kvalue)
                tt=tt+1
    #### 누락된 components 및 ports의 수 tt를 화면에 출력
    print(tt)
    tt=int()
    test=dict()
    #### assignModule을 제외한 나머지 net들의 구성요소들이 other_file과 비교하여 own_file에 다 있는지, 없다면 몇개가 없는지 화면에 출력
    for ivalue in other_file:
        if ivalue.startswith('assignModule'):
            continue
        #### assignModule이 아닌 net의 경우
        for kvalue in other_file[ivalue]:
            if kvalue not in own_file[ivalue]:
                if ivalue not in test:
                    test.update({ivalue:[]})
                test[ivalue].append(kvalue)
                tt=tt+1
    #### 누락된 components 및 ports의 수 tt를 화면에 출력
    print(tt)

    return temp







if __name__=="__main__":
    diff='easy'
    diff=sys.argv[1]

    file_from_other_computer='../../data/'+diff+'/net_list_'+diff+'.json'
    file_in_this_computer='../../data/'+diff+'/'+diff+'/nets_modified_by_02.json'
    file_not_include='../../data/'+diff+'/'+diff+'/not_included.json'
    All=compare_1(file_from_other_computer,file_in_this_computer)
    with open(file_not_include,'w') as fw:
        json.dump(All,fw,indent=4)
    fw.close()