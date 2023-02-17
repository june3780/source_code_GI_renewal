import json
import os
import sys
import copy
#import networkx as nx
import time
import pandas as pd
import numpy as np
#pd.options.display.float_format = '{:.0f}'.format



#### lef 파일에서 macro인 id를 parsing하여 해당 lef 파일의 위치에 하위 디렉토리 생성 후 저장
def get_macro_from_lef(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]

    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    #### 해당 lef 파일 열기
    with open(leflef,'r') as fw:
        fines=fw.readlines()
    fw.close()

    #### macro인 성분들이 시작하는 인덱스와 끝나는 인덱스를 각각 macro_start_idx와 macro_end_idx에 저장
    macro_start_idx=list()
    macro_end_idx=list()
    for idx in range(len(fines)):
        if fines[idx].strip().startswith('MACRO') and fines[idx].split('MACRO')[1].startswith(' '):
            macro_start_idx.append(idx)
            #### 해당 macro의 내용이 끝나는 인덱스를 get_end_idx로 저장
            macro_end_idx.append(get_end_idx(idx,fines))

    real_macro_list=list()
    #### 각 macro들 중 CLASS가 BLOCK으로 쓰여진 macro들을 MACRO_list에 저장
    MACRO_list=list()
    for idx in range(len(macro_start_idx)):
        temp_macro_name=fines[macro_start_idx[idx]].split('MACRO')[1].replace('\n','').strip()

        for kdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
            if fines[kdx+macro_start_idx[idx]].strip().startswith('CLASS') and fines[kdx+macro_start_idx[idx]].split('CLASS')[1].startswith(' '):
                #### 해당 macro의 CLASS가 BLOCK으로 쓰여있는 경우
                if fines[kdx+macro_start_idx[idx]].split('CLASS')[1].strip().startswith('BLOCK') and fines[kdx+macro_start_idx[idx]].split('BLOCK')[1].replace('\n','').strip()==';':
                   MACRO_list.append(temp_macro_name)
                   real_macro_list.append(idx)
                   break
    
    temp_macro_text=list()
    for idx in range(len(real_macro_list)):
        for kdx in range(macro_end_idx[real_macro_list[idx]]-macro_start_idx[real_macro_list[idx]]+1):
            temp_macro_text.append(fines[kdx+macro_start_idx[real_macro_list[idx]]])

    for idx in range(len(temp_macro_text)):
        if idx==0:
            with open(upper_directory+'/'+the_lef+'/lef_macro_list.lef','w') as fw:
                fw.write(temp_macro_text[idx])
            fw.close()
        else:
            with open(upper_directory+'/'+the_lef+'/lef_macro_list.lef','a') as fw:
                fw.write(temp_macro_text[idx])
            fw.close()


    #### MACRO_list를 lef_macro_list.json파일로 저장
    with open(upper_directory+'/'+the_lef+'/lef_macro_list.json','w') as fw:
        json.dump(MACRO_list,fw,indent=4)
    fw.close()
    
    return 0


#### 임의의 macro가 시작하는 인덱스를 통해 끝나는 인덱스를 반환하는 함수
def get_end_idx(start_idx,lines):
    #### 해당 macro의 내용이 시작할 때, 해당 macro의 이름 : start_macro_name
    start_macro_name=lines[start_idx].split('MACRO')[1].replace('\n','').strip()
    #### 해당 macro가 끝났을 때의 인덱스의 내용 : end_macro_name
    end_macro_name='END '+start_macro_name
    #### lef 파일에서 임의의 macro가 끝나는 인덱스의 내용을 만났을 때, 해당 인덱스를 반환
    for idx in range(len(lines)):
        if lines[idx].replace('\n','').strip()==end_macro_name:
            return idx




def checking_macro_relationship(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)


    #### lef 파일의 위치에 있는 하위 디렉토리의 lef_macro_list.json파일을 통해 해당 lef파일의 macro인 id를 MACRO_list에 저장
    with open(upper_directory+'/'+the_lef+'/lef_macro_list.json','r') as fw:
        MACRO_list=json.load(fw)
    fw.close()

    #### verilog 파일의 위치에 있는 하위 디렉토리의 temp_net.json파일을 통해 해당 verilog파일의 net정보를 net_all에 저장
    with open(upper_directory+'/'+the_lef+'/temp_net.json','r') as fw:
        net_all=json.load(fw)
    fw.close()

    #### verilog 파일의 위치에 있는 하위 디렉토리의 temp_id.json파일을 통해 해당 verilog파일에서 각 components들의 id 정보를 component_id에 저장
    with open(upper_directory+'/'+the_lef+'/temp_id.json','r') as fw:
        component_id=json.load(fw)
    fw.close()

    #### macro에 대한 내용만 있는 lef파일 불러오기
    with open(upper_directory+'/'+the_lef+'/lef_macro_list.lef','r') as fw:
        temp_macro_text=fw.readlines()
    fw.close()

    size_of_macro=dict()
    temp_idx=int()
    #### 각 MACRO가 가지는 width와 height를 구해서 size_of_macro에 저장
    for idx in range(len(temp_macro_text)):
        if temp_macro_text[idx].strip().startswith('MACRO '):
            temp_idx=idx
            size_of_macro.update({temp_macro_text[idx].split(' ')[1].replace('\n','').strip():dict()})
        if temp_macro_text[idx].strip().startswith('SIZE '):
            size_of_macro[temp_macro_text[temp_idx].split(' ')[1].replace('\n','').strip()].update({'width':float(temp_macro_text[idx].split('SIZE')[1].split('BY')[0].strip()),\
                'height':float(temp_macro_text[idx].split('BY')[1].split(';')[0].strip())})
    


    used_macro_with_pin=list()
    components_connected_net=dict()
    ext_pins_group=list()
    net_which_has_ext_pin=list()
    
    for ivalue in net_all:
        #### temp_group에는 해당 net이 가지는 모든 components들의 이름만 뽑아서 해당 net에 저장
        temp_group=list()
        for kvalue in  net_all[ivalue]:
            if kvalue.split(' ')[0] not in temp_group:
                temp_group.append(kvalue.split(' ')[0])
            
            #### 각 components들마다 연결되어 있는 net들을 components_connected_net에 저장
            if kvalue.split(' ')[0] not in components_connected_net:
                components_connected_net.update({kvalue.split(' ')[0]:list()})
            components_connected_net[kvalue.split(' ')[0]].append(ivalue)
            
            #### 각 net에 존재하는 component들중, macro인 id를 갖는 components들을 used_macro_with_pin에 해당 components의 이름을 저장
            if kvalue.split(' ')[0] in component_id:
                if component_id[kvalue.split(' ')[0]] in MACRO_list:
                    if kvalue.split(' ')[0] not in used_macro_with_pin:
                        used_macro_with_pin.append(kvalue.split(' ')[0])
            
            #### 해당 component가 external_pin의 경우 ext_pins_group에 저장
            if kvalue.split(' ')[0]=='PIN':
                if kvalue.split(' ')[1] not in ext_pins_group:
                    ext_pins_group.append(kvalue.split(' ')[1])
                if ivalue not in net_which_has_ext_pin:
                    net_which_has_ext_pin.append(ivalue)



        net_all[ivalue]=copy.deepcopy(temp_group)


    with open(upper_directory+'/'+the_lef+'/temp_components_no_pins.json','w') as fw:
        json.dump(components_connected_net,fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/temp_nets_no_pins.json','w') as fw:
        json.dump(net_all,fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/who_are_macro.json','w') as fw:
        json.dump(used_macro_with_pin,fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/ext_pins_group.json','w') as fw:
        json.dump(ext_pins_group,fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/nets_who_has_ext_pins.json','w') as fw:
        json.dump(net_which_has_ext_pin,fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/macro_width_height.json','w') as fw:
        json.dump(size_of_macro,fw,indent=4)
    fw.close()
    return 0





def checking_4case_net(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    with open(upper_directory+'/'+the_lef+'/temp_nets_no_pins.json','r') as fw:
        net_all=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/who_are_macro.json','r') as fw:
        used_macro_with_pin=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/ext_pins_group.json','r') as fw:
        ext_pins_group=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/nets_who_has_ext_pins.json','r') as fw:
        net_which_has_ext_pin=json.load(fw)
    fw.close()


    pin_and_macro_in=list()
    only_pin_in=list()
    only_macro_in=list()
    only_standard_in=list()

    #### external_pin가 있는 net의 경우
    for ivalue in net_which_has_ext_pin:
        macro_in=int()
        #### 해당 net에 pin이 있는 macro가 있는지 확인한다.
        for kvalue in net_all[ivalue]:
            #### 해당 net에 pin이 있는 macro가 있을 경우, 해당 net을 pin_and_macro_in에 저장
            if kvalue in used_macro_with_pin:
                pin_and_macro_in.append(ivalue)
                macro_in=1
                break
        #### 해당 net에 pin이 있는 macro가 없을 경우, 해당 net을 only_pin_in에 저장
        if macro_in==0:
            only_pin_in.append(ivalue)
    

    #### external_pin가 없는 net의 경우
    for ivalue in net_all:
        if ivalue not in net_which_has_ext_pin:

            macro_in=int()
            #### 해당 net에 pin이 있는 macro가 있는지 확인한다.
            for kvalue in net_all[ivalue]:
                #### 해당 net에 pin이 있는 macro가 있을 경우, 해당 net을 only_macro_in에 저장
                if kvalue in used_macro_with_pin:
                    only_macro_in.append(ivalue)
                    macro_in=1
                    break
            #### 해당 net에 pin이 없는 macro가 있을 경우, 해당 net을 only_standard_in에 저장
            if macro_in==0:
                only_standard_in.append(ivalue)

    checking_group={'macro':used_macro_with_pin,'pin':ext_pins_group}
    each_case={'macro_and_pin':pin_and_macro_in,'pin':only_pin_in,'macro':only_macro_in,'only_standard':only_standard_in}
    
    with open(upper_directory+'/'+the_lef+'/nets_who_has_each_case.json','w') as fw:
        json.dump(each_case,fw,indent=4)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_ports.json','w') as fw:
        json.dump(checking_group,fw,indent=4)
    fw.close()

    return 0



def checking_relation_the_macro_and_pin(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_ports.json','r') as fw:
        checking_group=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/temp_components_no_pins.json','r') as fw:
        components_connected_net=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/temp_nets_no_pins.json','r') as fw:
        net_all=json.load(fw)
    fw.close()

    groups=list()
    groups=copy.deepcopy(checking_group['macro'])
    #groups.extend(checking_group['macro'])

    #### macro끼리 가지는 관계에 대한 txt파일 초기화
    with open(upper_directory+'/'+the_lef+'/connected_macro.txt','w') as fw:
        fw.write('\n')
    fw.close()

    will_del=list()
    
    for ivalue in net_all:
        con=''
        for kvalue in groups:
            if kvalue not in net_all[ivalue]:
                break
            con='con'
        if con=='con':
            will_del.append(ivalue)
    #print(will_del)
  
    
    for idx in range(len(groups)):
        list_1=list()
        list_current_1=copy.deepcopy(components_connected_net[groups[idx]])
        list_current_1=list(set(list_current_1))
        for wvalue in will_del:
            if wvalue in list_current_1:
                list_current_1.remove(wvalue)
        for ivalue in components_connected_net[groups[idx]]:

            list_1.extend(net_all[ivalue])
        list_1=list(set(list_1))
        if groups[idx] in list_1:
            list_1.remove(groups[idx])
        

            
        for each_macro in checking_group['macro']:
            if each_macro==groups[idx]:
                continue
            list_2=list()
            list_current_2=copy.deepcopy(components_connected_net[each_macro])
            list_current_2=list(set(list_current_2))
            for wvalue in will_del:
                if wvalue in list_current_2:
                    list_current_2.remove(wvalue)
            intersection_list_same_net=list(set(list_current_1)&set(list_current_2))
            if len(intersection_list_same_net)!=0:
                #print(each_macro+' '+groups[idx]+' '+str(len(intersection_list_same_net))+' zero_bridge',intersection_list_same_net)
                with open(upper_directory+'/'+the_lef+'/connected_macro.txt','a') as fw:
                    fw.write(each_macro+' '+groups[idx]+' '+str(len(intersection_list_same_net))+' zero_bridge\n')
                fw.close()

            for each_net in components_connected_net[each_macro]:
                list_2.extend(net_all[each_net])
            list_2=list(set(list_2))
            if each_macro in list_2:
                list_2.remove(each_macro)

            intersection_list=list(set(list_1)&set(list_2))
            if len(intersection_list)!=0:
                #print(each_macro+' '+groups[idx]+' '+str(len(intersection_list))+' one_bridge',intersection_list)
                with open(upper_directory+'/'+the_lef+'/connected_macro.txt','a') as fw:
                    fw.write(each_macro+' '+groups[idx]+' '+str(len(intersection_list))+' one_bridge\n')
                fw.close()


    return 0



def checking_relation_with_standard_cell_except_macro(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)
        
    with open(upper_directory+'/'+the_lef+'/nets_who_has_each_case.json','r') as fw:
        each_case=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_ports.json','r') as fw:
        checking_group=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/temp_components_no_pins.json','r') as fw:
        components_connected_net=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/temp_nets_no_pins.json','r') as fw:
        net_all=json.load(fw)
    fw.close()

    groups=list()
    groups=copy.deepcopy(checking_group['macro'])



    groups_direct=dict()
    for ivalue in groups:
        groups_direct.update({ivalue:set()})
        for kdx in range(len(components_connected_net[ivalue])):
            for tdx in range(len(net_all[components_connected_net[ivalue][kdx]])):
                groups_direct[ivalue].add(net_all[components_connected_net[ivalue][kdx]][tdx])
        groups_direct[ivalue]=groups_direct[ivalue]-set(groups)
        groups_direct[ivalue]=list(groups_direct[ivalue])

    groups_one_bridge=dict()
    for ivalue in groups_direct:
        temp_net_set=set()
        for kdx in range(len(groups_direct[ivalue])):
            for tdx in range(len(components_connected_net[groups_direct[ivalue][kdx]])):
                temp_net_set.add(components_connected_net[groups_direct[ivalue][kdx]][tdx])
        temp_net_set=list(temp_net_set)
        temp_next_set=set()
        for kdx in range(len(temp_net_set)):
            for tdx in range(len(net_all[temp_net_set[kdx]])):
                temp_next_set.add(net_all[temp_net_set[kdx]][tdx])
        temp_next_set=temp_next_set-set(groups)
        temp_next_set=temp_next_set-set(groups_direct[ivalue])
        temp_next_set=list(temp_next_set)
        groups_one_bridge.update({ivalue:temp_next_set})


    with open(upper_directory+'/'+the_lef+'/pins_macro_zero_bridge_standard.json','w') as fw:
        json.dump(groups_direct,fw,indent=4)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/pins_macro_one_bridge_standard.json','w') as fw:
        json.dump(groups_one_bridge,fw,indent=4)
    fw.close()

    return 0


def get_standard_table(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    with open(upper_directory+'/'+the_lef+'/pins_macro_zero_bridge_standard.json','r') as fw:
        groups_direct=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/pins_macro_one_bridge_standard.json','r') as fw:
        groups_one_bridge=json.load(fw)
    fw.close()


    temp_zero_dict=dict()
    temp_one_dict=dict()
    for ivalue in groups_direct:
        temp_one_dict.update({ivalue:len(groups_one_bridge[ivalue])})
        temp_zero_dict.update({ivalue:len(groups_direct[ivalue])})

    #df_new=pd.DataFrame(columns=list(temp_one_dict.keys()),data=[list(temp_zero_dict.values()),list(temp_one_dict.values())])

    if len(sys.argv)>2 and sys.argv[2]=='naming':
        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()

        temp_zero_dict=dict()
        temp_one_dict=dict()
        
        name_dict=dict()
        for ivalue in liness:
            name_dict.update({ivalue.replace('\n','').split(' ')[1].strip():ivalue.replace('\n','').split(' ')[0].strip()})
        
        for ivalue in groups_direct:
            temp_one_dict.update({name_dict[ivalue]:len(groups_one_bridge[ivalue])})
            temp_zero_dict.update({name_dict[ivalue]:len(groups_direct[ivalue])})

    df_new=pd.DataFrame(columns=list(temp_one_dict.keys()),data=[list(temp_zero_dict.values()),list(temp_one_dict.values())])
    df_new['count']=['zero','one']
    df_new=df_new.set_index('count')
    df_new=df_new.transpose()
    df_new=df_new.sort_values(by='zero',ascending=False)
    df_new.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'Macro_with_standard_cells.csv',sep='\t')
    return 0





 #@# 마진 추가
def sorting_1(leflef,k):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)
        

    #### verilog 파일의 위치에 있는 하위 디렉토리의 temp_id.json파일을 통해 해당 verilog파일에서 각 components들의 id 정보를 component_id에 저장
    with open(upper_directory+'/'+the_lef+'/temp_id.json','r') as fw:
        component_id=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/macro_width_height.json','r') as fw:
        size_of_macro=json.load(fw)
    fw.close()


    with open(upper_directory+'/'+the_lef+'/connected_macro.txt','r') as fw:
        lines=fw.readlines()
    fw.close()

    temp_dict=dict()
    for ivalue in lines:
        if ivalue.replace('\n','').strip()=='':
            continue

        if ivalue.split(' ')[1]+' '+ivalue.split(' ')[0]+' '+ivalue.split(' ')[3] not in temp_dict:
            temp_dict.update({ivalue.split(' ')[0].replace('\n','').strip()+' '+ivalue.split(' ')[1].replace('\n','').strip()+' '+ivalue.split(' ')[3].replace('\n','').strip():int(ivalue.split(' ')[2])})


    all_group=dict()
    for ivalue in temp_dict:
        if ivalue.split(' ')[1]+' '+ivalue.split(' ')[0]+' '+ivalue.split(' ')[2] in all_group:
            continue
        
        all_group.update({ivalue:temp_dict[ivalue]})

    new_new_dict=dict()
    for ivalue in all_group:
        if ivalue.split(' ')[0]+' '+ivalue.split(' ')[1] not in new_new_dict:
            new_new_dict.update({ivalue.split(' ')[0]+' '+ivalue.split(' ')[1]:{'zero_bridge':int(),'one_bridge':int()}})
        new_new_dict[ivalue.split(' ')[0]+' '+ivalue.split(' ')[1]][ivalue.split(' ')[2]]=all_group[ivalue]

    temp_macro_1=list()
    temp_macro_2=list()
    size_of_zero=list()
    size_of_one=list()
    size_of_total=list()
    
    for ivalue in new_new_dict:
        temp_macro_1.append(ivalue.split(' ')[0])
        temp_macro_2.append(ivalue.split(' ')[1])
        size_of_zero.append(new_new_dict[ivalue]['zero_bridge'])
        size_of_one.append(new_new_dict[ivalue]['one_bridge'])
    
    for idx in range(len(size_of_zero)):
        size_of_total.append(size_of_zero[idx]+size_of_one[idx])


    temp_df=pd.DataFrame()
    temp_df['macro1']=temp_macro_1
    temp_df['macro2']=temp_macro_2
    temp_df['zero_bridge_size']=size_of_zero
    temp_df['one_bridge_size']=size_of_one
    temp_df['total_size']=size_of_total

    macro_1_margin=list()
    for ivalue in temp_df['macro1']:
        macro_1_margin.append((size_of_macro[component_id[ivalue]]['width']+size_of_macro[component_id[ivalue]]['height'])*1000/2)

    macro_2_margin=list()
    for ivalue in temp_df['macro2']:
        macro_2_margin.append((size_of_macro[component_id[ivalue]]['width']+size_of_macro[component_id[ivalue]]['height'])*1000/2)
    
    total_margin=list()
    for idx in range(len(macro_1_margin)):
        total_margin.append((macro_1_margin[idx]+macro_2_margin[idx])*k)

    temp_df['margin']=total_margin

    if len(sys.argv)>2 and sys.argv[2]=='naming':

        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()

        name_dict=dict()
        for ivalue in liness:
            name_dict.update({ivalue.replace('\n','').split(' ')[1].strip():ivalue.replace('\n','').split(' ')[0].strip()})

        new_macro_1_list=list()
        new_macro_2_list=list()
        for ivalue in (temp_df['macro1']):
            new_macro_1_list.append(name_dict[ivalue])
        for ivalue in (temp_df['macro2']):
            new_macro_2_list.append(name_dict[ivalue])
        
        temp_df['macro1']=new_macro_1_list
        temp_df['macro2']=new_macro_2_list

    temp_df.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df.csv',sep='\t')


    return 0




def calc_distance(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)
        


    with open(upper_directory+'/'+the_lef+'/temp_macro_location.txt','r') as fw:
        linesdd=fw.readlines()
    fw.close()

    temp_df=pd.read_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df.csv',sep='\t',index_col=0)

    location_dict=dict()
    for ivalue in linesdd:
        location_dict.update({ivalue.replace('\n','').split(' ')[0]:{'x':ivalue.replace('\n','').split(' ')[1],'y':ivalue.replace('\n','').split(' ')[2]}})


    distance_list=list()
    for idx in range(len(temp_df['macro1'])):
        distance_list.append(get_hpwl(location_dict[str(temp_df['macro1'][idx])],location_dict[str(temp_df['macro2'][idx])]))

    temp_df['distance']=distance_list
    status_list=list()
    term_list=list()

    for idx in range(len(temp_df['margin'])):
        term_list.append(temp_df['margin'][idx]-temp_df['distance'][idx])
        if temp_df['distance'][idx]>temp_df['margin'][idx]:
            status_list.append('F')
        else:
            status_list.append('T')
    temp_df['status']=status_list
    temp_df['term']=term_list

    temp_df.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df_total_size.csv',sep='\t')

    return 0



def get_hpwl(first,sencond):

    dis=float()
    dis=abs(float(first['x'])-float(sencond['x']))+abs(float(first['y'])-float(sencond['y']))

    return dis




def get_W_value_and_F_function(leflef,lamda):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)
        
    temp_df=pd.read_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df_total_size.csv',sep='\t',index_col=0)

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_ports.json','r') as fw:
        checking_group=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/macro_width_height.json','r') as fw:
        size_of_macro=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/temp_macro_location.txt','r') as fw:
        linesdd=fw.readlines()
    fw.close()
    with open(upper_directory+'/'+the_lef+'/temp_id.json','r') as fw:
        component_id=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/macro_width_height.json','r') as fw:
        size_of_macro=json.load(fw)
    fw.close()

    location_dict=dict()
    for ivalue in linesdd:
        location_dict.update({ivalue.replace('\n','').split(' ')[0]:{'x':ivalue.replace('\n','').split(' ')[1],'y':ivalue.replace('\n','').split(' ')[2]}})


    checking_macro_groups=copy.deepcopy(checking_group['macro'])

    if len(sys.argv)>2 and sys.argv[2]=='naming':

        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()
        temp_id=dict()
        for ivalue in liness:
            temp_id.update({ivalue.replace('\n','').split(' ')[0].strip():component_id[ivalue.replace('\n','').split(' ')[1].strip()]})

        checking_macro_groups=list()
        for ivalue in liness:
            checking_macro_groups.append(ivalue.replace('\n','').split(' ')[0].strip())

        component_id=copy.deepcopy(temp_id)


    W_df=pd.DataFrame()
    F_df=pd.DataFrame()

    reset_1_list=list()
    will_be_index=copy.deepcopy(checking_macro_groups)
    for idx in range(len(checking_macro_groups)):
        reset_1_list.append(float(0))

    for idx in range(len(checking_macro_groups)):
        F_df[checking_macro_groups[idx]]=copy.deepcopy(reset_1_list)
        W_df[checking_macro_groups[idx]]=copy.deepcopy(reset_1_list)

    F_df['list']=will_be_index
    F_df=F_df.set_index(keys='list')
    W_df['list']=will_be_index
    W_df=W_df.set_index(keys='list')
    


    for idx in range(len(temp_df['macro1'])):
        temp_W=get_W_value(temp_df['zero_bridge_size'][idx],temp_df['one_bridge_size'][idx],temp_df['total_size'][idx])
        W_df.loc[str(temp_df['macro1'][idx])][str(temp_df['macro2'][idx])]=temp_W
        W_df.loc[str(temp_df['macro2'][idx])][str(temp_df['macro1'][idx])]=temp_W


    max_value=float()
    for idx in range(len(list(W_df.columns))):
        for kdx in range(len(list(W_df.index))):
            if idx==kdx:
                continue
            if W_df.iloc[idx,kdx]>max_value:
                max_value=W_df.iloc[idx,kdx]

    min_value=max_value
    for idx in range(len(list(W_df.columns))):
        for kdx in range(len(list(W_df.index))):
            if idx==kdx:
                continue
            if W_df.iloc[idx,kdx]<min_value:
                min_value=W_df.iloc[idx,kdx]

    for idx in range(len(list(W_df.columns))):
        for kdx in range(len(list(W_df.index))):
            if idx==kdx:
                continue
            W_df.iloc[idx,kdx]=round(W_df.iloc[idx,kdx]/min_value,2)

    W_df.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'W_df.csv',sep='\t')


    for idx in range(len(list(F_df.columns))):
        for kdx in range(len(list(F_df.index))):
            if idx==kdx:
                continue
            temp_F=get_F_value(list(F_df.columns)[idx],list(F_df.index)[kdx],component_id,location_dict,size_of_macro,lamda,W_df.iloc[idx,kdx])
            F_df.iloc[idx,kdx]=temp_F

    F_df.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'F_df.csv',sep='\t')

    total_cost=float()
    for idx in range(len(F_df.columns)):
        for kdx in range(len(F_df.columns)):
            if idx==kdx:
                continue
            total_cost=total_cost+F_df.iloc[idx,kdx]
    
    with open(upper_directory+'/'+the_lef+'/cost.txt','w') as fw:
        fw.write(str(total_cost/2))
    fw.close()

    return 0


def get_F_value(macro_1,macro_2,temp_id,location,size_of_macro,lamda,wvalue):
    #print(type(macro_1))
    #print(temp_id)
    x_candidate=size_of_macro[temp_id[macro_1]]['width']+size_of_macro[temp_id[macro_2]]['width']
    y_candidate=size_of_macro[temp_id[macro_1]]['height']+size_of_macro[temp_id[macro_2]]['height']
    min_distance=min(x_candidate,y_candidate)
    min_distance=min_distance*1000/2
    distance_between=abs(float(location[macro_1]['x'])-float(location[macro_2]['x']))+abs(float(location[macro_1]['y'])-float(location[macro_2]['y']))
    temp_Dij=distance_between-min_distance

    #temp_Dij=np.exp((-1)*lamda*temp_Dij)
    temp_Dij=wvalue*(np.exp((-1)*lamda*temp_Dij))
    return temp_Dij



def get_W_value(zero,one,total):
    tt=float()
    if zero!=0:
        tt=20*(total**(1/2))
    elif one!=0:
        tt=10*(total**(1/2))

    return tt



def get_net_just_standard(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)
    
    with open(upper_directory+'/'+the_lef+'/nets_who_has_each_case.json','r') as fw:
        each_case=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_ports.json','r') as fw:
        checking_group=json.load(fw)
    fw.close()

    with open(upper_directory+'/'+the_lef+'/temp_nets_no_pins.json','r') as fw:
        net_all=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_lef+'/temp_components_no_pins.json','r') as fw:
        components_connected_net=json.load(fw)
    fw.close()

    checking_macro_groups=copy.deepcopy(checking_group['macro'])



    each_set=dict()
    for macro1 in checking_macro_groups:
        each_set.update({macro1:list()})
        temp_plus=set()
        temp_other_macro=copy.deepcopy(checking_macro_groups)
        temp_other_macro.remove(macro1)
        temp_other_macro=set(temp_other_macro)
        for net1_from_macro1 in components_connected_net[macro1]:
            temp_net_test=set(net_all[net1_from_macro1])
            if len(temp_other_macro&temp_net_test)>0:
                continue
            temp_plus=(temp_plus|set(list(net_all[net1_from_macro1])))
        if macro1 in temp_plus:
            temp_plus.remove(macro1)
        temp_all=set()

        for idx in range(len(each_case['only_standard'])):
            temp_all=temp_all|(temp_plus&set(net_all[each_case['only_standard'][idx]]))
        each_set[macro1]=list(temp_all)

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_standard_set.json','w') as fw:
        json.dump(each_set,fw,indent=4)
    fw.close()

    return 0




def get_macro_and_only_standard(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    with open(upper_directory+'/'+the_lef+'/pins_macro_with_standard_set.json','r') as fw:
        each_set=json.load(fw)
    fw.close()

    if len(sys.argv)>2 and sys.argv[2]=='naming':
        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()

        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()

        temp_dict=dict()
        name_dict=dict()
        for ivalue in liness:
            name_dict.update({ivalue.replace('\n','').split(' ')[1].strip():ivalue.replace('\n','').split(' ')[0].strip()})

        for ivalue in each_set:
            temp_dict.update({name_dict[ivalue]:each_set[ivalue]})

        each_set=copy.deepcopy(temp_dict)
    

    data_list=list()
    columnlist=list()

    for ivalue in each_set:
        columnlist.append(ivalue)
        data_list.append(len(each_set[ivalue]))
    df_stand=pd.DataFrame(columns=columnlist,data=[data_list])
    df_stand['macro_number']=['counts']
    df_stand=df_stand.set_index(keys='macro_number')

    df_stand=df_stand.transpose()

    df_stand.to_csv(upper_directory+'/'+the_lef+'/counts_only_standard_cell_set.csv',sep='\t')
    return 0





def get_lamda(defdef):
    #### 해당 verilog 파일의 파일명: where_the_def+'.v'
    where_the_def=defdef.split('.def')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_def
    the_def=where_the_def.split('/')[-1]
    upper_directory=defdef.split('/'+the_def+'.def')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성

    with open(upper_directory+'/'+the_def+'/die_area.txt','r') as fw:
        lines=fw.readlines()
    fw.close()


    temp_line=lines[0].replace('\n','')
    first_x=float(temp_line.split(')')[0].split('(')[1].strip().split(' ')[0])
    first_y=float(temp_line.split(')')[0].split('(')[1].strip().split(' ')[1])
    second_x=float(temp_line.split('(')[-1].split(')')[0].strip().split(' ')[0])
    second_y=float(temp_line.split('(')[-1].split(')')[0].strip().split(' ')[1])
    x_value=abs(second_x-first_x)
    y_value=abs(second_y-first_y)
    
    return 50/max(x_value,y_value)


if __name__=="__main__":

    
    start=time.time()
    
    superblue=['superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD']
    superblue=['easy','medium']
    ivalue=''
    #ivalue='medium'
    #ivalue='easy'
    #ivalue='toy'
    for ivalue in superblue:
        checking_def='../../data/'
        checking_lef='../../data/'
        checking_def=checking_def+ivalue+'/'+ivalue+'.def'
        checking_lef=checking_lef+ivalue+'/'+ivalue+'.lef'
        lamda=float()

        print(ivalue)
        if len(sys.argv)!=0:
            lamda=get_lamda(checking_def)

        if sys.argv[1]=='0':
            get_macro_from_lef(checking_lef)
        
        elif sys.argv[1]=='1':
            checking_macro_relationship(checking_lef)

        elif sys.argv[1]=='2':
            checking_4case_net(checking_lef)

        elif sys.argv[1]=='3':
            checking_relation_the_macro_and_pin(checking_lef)
        
        elif sys.argv[1]=='4': #### naming
            sorting_1(checking_lef,2)
        
        elif sys.argv[1]=='5':
            calc_distance(checking_lef)

        elif sys.argv[1]=='6': #### naming
            get_W_value_and_F_function(checking_lef,lamda)
        
        elif sys.argv[1]=='7':
            checking_relation_with_standard_cell_except_macro(checking_lef)

        elif sys.argv[1]=='8':
            get_standard_table(checking_lef) #### naming
    
        elif sys.argv[1]=='9':
            get_net_just_standard(checking_lef)
        
        elif sys.argv[1]=='10':
            get_macro_and_only_standard(checking_lef) #### naming
        
        
            


    print('end :',time.time()-start)