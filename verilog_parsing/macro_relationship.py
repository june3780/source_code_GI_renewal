import json
import os
import sys
import copy
#import networkx as nx
import time
import pandas as pd


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

    #### 각 macro들 중 CLASS가 BLOCK으로 쓰여진 macro들을 MACRO_list에 저장
    MACRO_list=list()
    for idx in range(len(macro_start_idx)):
        temp_macro_name=fines[macro_start_idx[idx]].split('MACRO')[1].replace('\n','').strip()

        for kdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
            if fines[kdx+macro_start_idx[idx]].strip().startswith('CLASS') and fines[kdx+macro_start_idx[idx]].split('CLASS')[1].startswith(' '):
                #### 해당 macro의 CLASS가 BLOCK으로 쓰여있는 경우
                if fines[kdx+macro_start_idx[idx]].split('CLASS')[1].strip().startswith('BLOCK') and fines[kdx+macro_start_idx[idx]].split('BLOCK')[1].replace('\n','').strip()==';':
                   MACRO_list.append(temp_macro_name)
                   break

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

    return 0





def checking_4case_net(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]

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




def sorting_1(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]

    with open(upper_directory+'/'+the_lef+'/connected_macro.txt','r') as fw:
        lines=fw.readlines()
    fw.close()

    temp_dict=dict()
    for ivalue in lines:
        if ivalue.replace('\n','').strip()=='':
            continue

        if ivalue.split(' ')[1]+' '+ivalue.split(' ')[0]+' '+ivalue.split(' ')[3] not in temp_dict:
            temp_dict.update({ivalue.split(' ')[0].replace('\n','').strip()+' '+ivalue.split(' ')[1].replace('\n','').strip()+' '+ivalue.split(' ')[3].replace('\n','').strip():int(ivalue.split(' ')[2])})


    max_count=int()
    zero_group=dict()
    one_bridge_group=dict()
    all_group=dict()
    for ivalue in temp_dict:
        
        if ivalue.split(' ')[1]+' '+ivalue.split(' ')[0]+' '+ivalue.split(' ')[2] in all_group:
            continue
        
        all_group.update({ivalue:temp_dict[ivalue]})



    index_list=list()
    data_group=list()

    new_dict=dict()
    for idx,ivalue in enumerate(all_group):
        index_list.append(idx)
        if ivalue.split(' ')[0]+' '+ivalue.split(' ')[1] not in new_dict:
            new_dict.update({ivalue.split(' ')[0]+' '+ivalue.split(' ')[1]:int()})
        new_dict[ivalue.split(' ')[0]+' '+ivalue.split(' ')[1]]=new_dict[ivalue.split(' ')[0]+' '+ivalue.split(' ')[1]]+all_group[ivalue]

        data_group.append([ivalue.split(' ')[0], ivalue.split(' ')[1],all_group[ivalue],ivalue.split(' ')[2]])

    index_new_list=list()
    all_data_group=list()
    for idx,ivalue in enumerate(new_dict):
        index_new_list.append(idx)
        all_data_group.append([ivalue.split(' ')[0],ivalue.split(' ')[1],new_dict[ivalue]])


    df_new=pd.DataFrame(data=all_data_group,columns=['macro1','macro2','size'])
    df_new=df_new.sort_values(['macro1','macro2','size'],ascending=False)
    df_new.index=index_new_list
    df_new.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df_total_size.csv',sep='\t')

    df=pd.DataFrame(data=data_group,columns=['macro1','macro2','size','status'])
    df=df.sort_values(['status','size','macro1','macro2'],ascending=False)
    df.index=index_list
    df.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df.csv',sep='\t')


    if len(sys.argv)>2 and sys.argv[2]=='naming':
        with open(upper_directory+'/'+the_lef+'/naming.txt','r') as fw:
            liness=fw.readlines()
        fw.close()

        with open(upper_directory+'/'+the_lef+'/temp_macro_location.txt','r') as fw:
            linesx=fw.readlines()
        fw.close()

        location_dict=dict()
        for ivalue in linesx:
            location_dict.update({ivalue.replace('\n','').split(' ')[0]:{'x':ivalue.replace('\n','').split(' ')[1],'y':ivalue.replace('\n','').split(' ')[2]}})

        name_dict=dict()
        for ivalue in liness:
            name_dict.update({ivalue.replace('\n','').split(' ')[1].strip():ivalue.replace('\n','').split(' ')[0].strip()})

        
        macro_1=list()
        macro_2=list()

        for ivalue in list(df['macro1']):
            macro_1.append(name_dict[ivalue])
        df['macro1']=macro_1

        for ivalue in list(df['macro2']):
            macro_2.append(name_dict[ivalue])
        df['macro2']=macro_2



        df=df.sort_values(['macro1','macro2','size','status'],ascending=False)
        df.index=index_list
        location=list()
        for idx in range(len(list(df.index))):
            temp_distance=get_hpwl(location_dict[df['macro1'][idx]],location_dict[df['macro2'][idx]])
            location.append(temp_distance)
        df['distance']=location
        df=df.sort_values(['distance'],ascending=True)
        
        df_1=df[df['status']=='zero_bridge']
        



        df_1=df_1.reset_index()
        
        

        df_1.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df.csv',sep='\t',index=False)




        macro_1=list()
        macro_2=list()

        for ivalue in list(df_new['macro1']):
            macro_1.append(name_dict[ivalue])
        df_new['macro1']=macro_1

        for ivalue in list(df_new['macro2']):
            macro_2.append(name_dict[ivalue])
        df_new['macro2']=macro_2
        
        df_new=df_new.sort_values(['macro1','macro2','size'],ascending=False)
        df_new.index=index_new_list
        location=list()
        for idx in range(len(list(df_new.index))):
            #print(df_new['macro1'][idx],df_new['macro2'][idx])
            temp_distance=get_hpwl(location_dict[df_new['macro1'][idx]],location_dict[df_new['macro2'][idx]])
            location.append(temp_distance)
        df_new['distance']=location
        df_new=df_new.sort_values(['distance','macro1','macro2','size'],ascending=True)
        df_new.index=index_new_list
        df_new.to_csv(upper_directory+'/'+the_lef+'/'+the_lef+'_df_total_size.csv',sep='\t')





    return 0




def get_hpwl(first,sencond):

    dis=float()
    dis=abs(float(first['x'])-float(sencond['x']))+abs(float(first['y'])-float(sencond['y']))


    return dis






if __name__=="__main__":

    start=time.time()

    superblue=['superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD']
    #superblue=['superblue11_ISPD','superblue12_ISPD','superblue16_ISPD']
    ivalue='superblue16_ISPD'
    ivalue='medium'
    ivalue='easy'
    #ivalue='toy'
    checking_def='../../data/'
    checking_lef='../../data/'
    checking_def=checking_def+ivalue+'/'+ivalue+'.def'
    checking_lef=checking_lef+ivalue+'/'+ivalue+'.lef'
    
    if sys.argv[1]=='0':
        get_macro_from_lef(checking_lef)
    
    elif sys.argv[1]=='1':
        checking_macro_relationship(checking_lef)

    elif sys.argv[1]=='2':
        checking_4case_net(checking_lef)

    elif sys.argv[1]=='3':
        checking_relation_the_macro_and_pin(checking_lef)
    
    elif sys.argv[1]=='4':
        sorting_1(checking_lef)


    print('end :',time.time()-start)