import json
import copy


def get_hypergraph(net,id,lib_list,hyper_add):
    macro_list=['spsram_hd_256x23m4m','spsram_hd_2048x32m4s','spsram_hd_256x22m4m','sprf_hs_128x38m2s'\
    ,'TS1N40LPB1024X32M4FWBA','TS1N40LPB2048X36M4FWBA','TS1N40LPB256X23M4FWBA','TS1N40LPB128X63M4FWBA'\
    ,'TS1N40LPB256X12M4FWBA','TS1N40LPB512X23M4FWBA','TS1N40LPB1024X128M4FWBA','TS1N40LPB2048X32M4FWBA'\
    ,'TS1N40LPB256X22M4FWBA','spsram_hd_16384x32m32']

    with open(id,'r') as fw:
        temp_id=json.load(fw)
    fw.close()
    
    with open(net,'r') as fw:
        all_net=json.load(fw)
    fw.close()

    #### medium의 경우 macro를 제외한 standard cell의 ID에 'LVT'를 빼서 lib파일의 ID에 매칭한다.
    if net.split('/')[-2]=='medium':
        for ivalue in temp_id:
            if temp_id[ivalue]=='external_output_PIN' or temp_id[ivalue]=='external_input_PIN' or temp_id[ivalue] in macro_list:
                continue
            temp_id[ivalue]=temp_id[ivalue].split('LVT')[0]

        all_net['constant0'].append('temporary_tie_0 ZN')
        temp_id.update({'temporary_tie_0':'TIELBWP12TM1P'})
        all_net['constant1'].append('temporary_tie_1 Z')
        temp_id.update({'temporary_tie_1':'TIEHBWP12TM1P'})

    #### easy의 경우 macro를 제외한 standard cell의 ID에 '12TM1P' lib파일의 ID에 매칭한다.
    elif net.split('/')[-2]=='easy':
        for ivalue in temp_id:
            if temp_id[ivalue]=='external_output_PIN' or temp_id[ivalue]=='external_input_PIN' or temp_id[ivalue] in macro_list:
                continue
            temp_id[ivalue]=temp_id[ivalue]+'12TM1P'

    #### 해당 verilog에 쓰이는 component들의 lib집합을 만들어 저장
    lib_dict=dict()
    for ivalue in lib_list:
        with open (ivalue,'r')as fw:
            temp_dict=json.load(fw)
        fw.close()
        lib_dict.update(temp_dict)

    constant_cell_id_group=list()
    #### lib에서 선언된 tie 소자의 id를 저장
    for cell in lib_dict:
        for pin in lib_dict[cell]:
            if 'driver_type' in lib_dict[cell][pin]:
                if cell not in constant_cell_id_group:
                    constant_cell_id_group.append(cell)

    #### PIN의 내용을 'PIN '+nickname에서 nickname+' PIN'으로 변경
    will_add_pin=dict()
    will_del_pin=list()
    for ivalue in temp_id:
        if temp_id[ivalue]=='external_output_PIN' or temp_id[ivalue]=='external_input_PIN':
            #### pin의 nickname을 저장
            will_add_pin.update({ivalue.split(' ')[1]:temp_id[ivalue]})
            will_del_pin.append(ivalue)
    for ivalue in will_del_pin:
        del temp_id[ivalue]
    temp_id.update(will_add_pin)


    for ivalue in all_net:
        will_add_pin=list()
        will_del_pin=list()
        for kvalue in all_net[ivalue]:
            #### 임의의 net에 PIN이 있을 경우 PIN의 내용을 변경
            if 'PIN' in kvalue:
                will_add_pin.append(kvalue.split(' ')[1]+' PIN')
                will_del_pin.append(kvalue)
        for kvalue in will_del_pin:
            all_net[ivalue].remove(kvalue)
        all_net[ivalue].extend(will_add_pin)

    constant_group=list()
    #### checking 영역 해당 component들이 lib파일에 다 있는지 확인한다. 없을 경우 해당 component의 nickname과 id를 화면에 출력
    pins_group=list()
    for ivalue in temp_id:
        if temp_id[ivalue]=='external_output_PIN' or temp_id[ivalue]=='external_input_PIN':
            pins_group.append(ivalue)
            continue
        if temp_id[ivalue] not in lib_dict:
            print(ivalue,temp_id[ivalue])

        #### 임의의 cell id가 constant cell인 경우 constant_group에 추가
        elif temp_id[ivalue] in constant_cell_id_group:
            constant_group.append(ivalue)


    #### clock에 동기화되는 register들을 reg_components에 저장
    reg_components=set()
    all_component_dict=dict()
    for ivalue in temp_id:
        #### external_output_PIN의 경우 pin의 방향을 input으로 본다.
        if temp_id[ivalue]=='external_output_PIN':
            all_component_dict.update({ivalue:{'input':{'PIN':dict()}}})
            continue
        
        #### external_input_PIN의 경우 pin의 방향을 output으로 본다.
        if temp_id[ivalue]=='external_input_PIN':
            all_component_dict.update({ivalue:{'output':{'PIN':dict()}}})
            continue

        all_component_dict.update({ivalue:dict()})
        for pin in lib_dict[temp_id[ivalue]]:
            if pin=='ff' or pin=='latch' or pin=='clock_gating_integrated_cell':
                continue
            if 'direction' in lib_dict[temp_id[ivalue]][pin]:
            #### 해당 cell의 pin중 clock에 동기화된 pin이 있을 경우 reg_components에 추가
                if lib_dict[temp_id[ivalue]][pin]['direction']=='input':
                    if 'clock' in lib_dict[temp_id[ivalue]][pin] and ('ff' in lib_dict[temp_id[ivalue]] or 'latch' in lib_dict[temp_id[ivalue]] or temp_id[ivalue] in macro_list):
                        reg_components.add(ivalue)
                        
                    if 'input' not in all_component_dict[ivalue]:
                        all_component_dict[ivalue].update({'input':dict()})
                    all_component_dict[ivalue]['input'].update({pin:dict()})

                elif lib_dict[temp_id[ivalue]][pin]['direction']=='output':
                    if 'output' not in all_component_dict[ivalue]:
                        all_component_dict[ivalue].update({'output':dict()})
                    all_component_dict[ivalue]['output'].update({pin:dict()})
                
        
    #### 하나의 net에서 신호를 출력하는 단자를 파악한 후, 해당 cell의 output 혹은 해당 external_pin의 output에 저장
    for temp_net in all_net:
        #### constant0와 constant1에 대해선 추후 업데이트가 필요하다.

        out_data_in_a_net=list()
        for temp_component in all_net[temp_net]:
            if temp_component.split(' ')[1]=='PIN':
                #### 해당 net에 external_input_PIN이 있을 경우
                if temp_id[temp_component.split(' ')[0]]=='external_input_PIN':
                    out_data_in_a_net.append(temp_component)
            else:
                #### 해당 net에 임의의 cell의 output pin이 있을 경우
                if lib_dict[temp_id[temp_component.split(' ')[0]]][temp_component.split(' ')[1]]['direction']=='output':
                    out_data_in_a_net.append(temp_component)
        
        #### 하나의 net에서 신호를 다른 component나 external_output_PIN에 전달하는 component혹은 external_input_PIN은 하나여야만 한다.
        if len(out_data_in_a_net)!=1:
            print("Error : in ",temp_net,", output_direction element_group is",out_data_in_a_net)
        
        else:
            direction_output_port=out_data_in_a_net[0]
            other_list=copy.deepcopy(all_net[temp_net])
            #### 해당 net에서 신호를 출력하여 다른 component들에게 부여하는 component를 제외한 나머지들의 집합을 저장
            other_list.remove(direction_output_port)
            all_component_dict[direction_output_port.split(' ')[0]]['output'][direction_output_port.split(' ')[1]].update({'to':other_list})
            
            #### 해당 net에서 신호를 받는 component들에게 해당 net의 신호를 출력하는 component를 저장
            for other in other_list:
                all_component_dict[other.split(' ')[0]]['input'][other.split(' ')[1]].update({'from':direction_output_port})


    bre=''
    temp_output_group=dict()
    tt=int()
    constant_group=set(constant_group)
    reg_components=set(reg_components)
    pins_group=set(pins_group)
    reg_all=set()
    clk_group_components=set()
    #### total_set에는 register, constant_cell, 외부 pin의 내용이 있다.
    total_set=constant_group|reg_components|pins_group
    for reg in reg_components:
        if 'input' in all_component_dict[reg]:
            for input_pin in all_component_dict[reg]['input']:
                #### clock에 동기화된 register의 pin의 신호가 시작하는 외부 핀 혹은 register의 output 혹은 constant pin 등 해당 cell의 clock 신호가 작동하기 위해 필요한 component를 temp_output_group에 저장
                if 'clock' in lib_dict[temp_id[reg]][input_pin]:
                    if all_component_dict[reg]['input'][input_pin]['from'] not in temp_output_group:
                        #### get_origin_group을 통해 같은 net을 공유하는 register의 clock pin의 출처에 대한 데이터를 temp_output_group에 저장
                        temp_info=get_origin_group(all_component_dict,total_set,[all_component_dict[reg]['input'][input_pin]['from']],lib_dict,temp_id)
                        temp_output_group.update({all_component_dict[reg]['input'][input_pin]['from']:temp_info[0]})
                        #### register의 clk에 관련된 cell들을 reg_all에 저장
                        reg_all=reg_all|temp_info[1]




    current_clk_stage=int()
    reg_group=copy.deepcopy(reg_components)
    temp_reg_dict=dict()
    #### 각 register가 clock에 동기화되기 위해 필요한 pin, constant_cell과 임의의 register의 출력값을 필요로 하는 register를 리스트로 가진 temp_output_group을 통해 어떤 reg_cell부터 delay계산을 해야되는지 temp_reg_dict에 저장
    #### 몇번째로 처리를 해야되는지 명시된 register는 reg_components에서 제거, 모든 register가 제거될 때까지 while문 반복
    while len(reg_components)!=0:
        will_del=set()
        for reg in reg_components:
            if 'input' in all_component_dict[reg]:
                for input_pin in all_component_dict[reg]['input']:
                    #### 각 reg의 clock에 동기화된 pin의 출처 : origin_clk_group
                    if 'clock' in lib_dict[temp_id[reg]][input_pin]:
                        origin_clk_group=temp_output_group[all_component_dict[reg]['input'][input_pin]['from']]
                        break_str=''

                        for temp_component in origin_clk_group:
                            #### clock에 동기화된 cell이 해당 reg에 존재할 경우 break_str='break'으로 처리
                            if temp_component.split(' ')[0] in reg_components:
                                break_str='break'
                                break
                        #### clock에 동기화된 pin의 출처가 모두 reg_components에 포함되지 않을 때, will_del에 추가, 현재 current_clk_stage번째 처리해야 하는 reg로 temp_reg_dict에 저장
                        if break_str=='':
                            temp_reg_dict.update({reg:current_clk_stage})
                            will_del.add(reg)
        
        #### current_clk_stage단계에서 처리되지 못하는 남은 register group : reg_components
        reg_components=reg_components-will_del
        for temp_net in temp_output_group:
            temp_output_group[temp_net]=list(set(temp_output_group[temp_net])-will_del)
        current_clk_stage=current_clk_stage+1


    with open(hyper_add+'input_output.json','w')as fw:
        json.dump(all_component_dict,fw,indent=4)
    fw.close()

    reg_all=reg_all|reg_group

    clk_to_reg_dict=get_stage(reg_all,reg_group,pins_group,all_component_dict,temp_id,lib_dict)
    reg_to_reg_dict=get_stage(set(all_component_dict.keys()),reg_group,pins_group,all_component_dict,temp_id,lib_dict)

    with open(hyper_add+'stage_clk_to_reg.json','w')as fw:
        json.dump(clk_to_reg_dict[0],fw,indent=4)
    fw.close()

    with open(hyper_add+'related_pin_clk_to_reg.json','w')as fw:
        json.dump(clk_to_reg_dict[1],fw,indent=4)
    fw.close()

    with open(hyper_add+'stage_reg_to_reg.json','w')as fw:
        json.dump(reg_to_reg_dict[0],fw,indent=4)
    fw.close()

    with open(hyper_add+'related_pin_reg_to_reg.json','w')as fw:
        json.dump(reg_to_reg_dict[1],fw,indent=4)
    fw.close()

    with open(hyper_add+'reg_priority.json','w')as fw:
        json.dump(temp_reg_dict,fw,indent=4)
    fw.close()


    return 0







def get_stage(All, reg_group, pin_group, from_to,id_dict,lib_dict):
    #### 한 component의 output_port가 모두 stage를 갖게 되면 temp_dict에서 소거하는 방식으로 각 component에 stage를 부여
    temp_dict=copy.deepcopy(All)
    got_stage=dict()
    related_group=dict()

    #### related_group을 통해 각 component의 output_port의 delay를 계산하기 위한 해당 component의 input_port를 list로 저장
    for ivalue in All:
        related_group.update({ivalue:dict()})
        #### 해당 component가 external_input_PIN인 경우
        if ivalue in pin_group:
            if id_dict[ivalue]=='external_input_PIN':
                related_group.update({ivalue:{'PIN':list()}})
        
        #### 해당 component가 standard_cell 혹은 macro인 경우
        elif 'output' in from_to[ivalue]:
            for temp_output in from_to[ivalue]['output']:
                related_group[ivalue].update({temp_output:list()})
                for cases in lib_dict[id_dict[ivalue]][temp_output]:
                    #### 각 case마다 related_pin이 다르므로 해당 case에서의 related_pin을 합집합으로 list에 저장
                    if cases.startswith('case_'):
                        related_group[ivalue][temp_output]=list(set(related_group[ivalue][temp_output])|(set(lib_dict[id_dict[ivalue]][temp_output][cases]['related_pin'])))

    #### 임의의 component의 임의의 output_port의 delay를 계산하기 위한 related_pin이 하나도 없을 경우 해당 output_port는 stage를 0으로 갖는다.
    for ivalue in related_group:
        for temp_output in related_group[ivalue]:
            #### 임의의 component의 임의의 output_port의 delay를 계산하기 위한 related_pin이 하나도 없을 경우
            if len(related_group[ivalue][temp_output])==0:
                if ivalue not in got_stage:
                    got_stage.update({ivalue:dict()})
                got_stage[ivalue].update({temp_output:0})
    
    #### register의 경우 강제로 해당 component의 output_port들의 stage를 0으로 부여한다.
    for ivalue in reg_group:
        if ivalue not in got_stage:
            got_stage.update({ivalue:dict()})
        for temp_output in from_to[ivalue]['output']:
            got_stage[ivalue].update({temp_output:0})

    #### external_output_PIN은 output_port가 없으므로 해당 함수에서 제거한다.
    for ivalue in pin_group&All:
        if id_dict[ivalue]=='external_output_PIN':
            temp_dict.remove(ivalue)


    current_stage=1
    #### stage를 부여받지 못한 component들을 갯수 : len(temp_dict)
    while len(temp_dict)!=0:
        ttt=int()
        will_del_set=set()
        for ivalue in temp_dict:
            #### 각 output_port에 접근
            for temp_output in from_to[ivalue]['output']:

                #### 해당 component의 output_port 중 stage를 부여받은 port가 있고, 현재 접근한 output_port가 stage를 부여받았으면 continue로 처리
                if ivalue in got_stage:
                    if temp_output in got_stage[ivalue]:
                        continue

                #### max_stage 초기화
                max_stage=int()
                #### current_status 초기화
                current_status=str()

                #### 해당 output_port의 related_pin인 input들에 접근
                for related_input_pin in related_group[ivalue][temp_output]:
                    
                    #### related_pin 중의 임의의 input_port의 신호를 받는 component와 해당 component의 output_port : origin
                    origin=from_to[ivalue]['input'][related_input_pin]['from']
                    #### 해당 component가 All 집합 안에 있을 경우만 고려한다.
                    if origin.split(' ')[0] in All:
                        #### 해당 component 중 임의의 output_port가 하나라도 stage를 부여받은 경우만 고려한다.
                        if origin.split(' ')[0] in got_stage:
                            #### origin에서의 output_port가 stage를 받은 경우만 고려한다.
                            if origin.split(' ')[1] in got_stage[origin.split(' ')[0]]:
                                #### max_stage 최신화 (related_pin들중 가장 높은 stage로부터 온 신호의 stage를 max_stage에 저장한다.)
                                if max_stage<got_stage[origin.split(' ')[0]][origin.split(' ')[1]]:
                                    max_stage=got_stage[origin.split(' ')[0]][origin.split(' ')[1]]
                            #### case를 만족하지 못한 경우 current_status='break'로 처리
                            else:
                                current_status='break'
                                break
                        else:
                            current_status='break'
                            break
                    else:
                        current_status='break'
                        break
                #### current_status가 'break'인 경우 continue로 처리
                if current_status=='break':
                    continue

                #### max_stage가 current_stage-1 인 경우 해당 output_port에 stage를 부여
                if max_stage==current_stage-1:
                    if ivalue not in got_stage:
                        got_stage.update({ivalue:dict()})
                    got_stage[ivalue].update({temp_output:current_stage})

        #### 각 component의 모든 output_port에 stage가 부여된 경우 will_del_set에 추가
        for ivalue in temp_dict:
            checking_str=str()
            if 'output' in from_to[ivalue]:
                for temp_output in from_to[ivalue]['output']:
                    current_status=str()
                    for related_input_pin in related_group[ivalue][temp_output]:
                        origin=from_to[ivalue]['input'][related_input_pin]['from']
                        #### 임의의 output_port의 related_pin의 출처가 All 집합에 없을 경우 current_status='break'로 처리
                        if origin.split(' ')[0] not in All:
                            current_status='break'
                            break
                    
                    #### current_status=='break'일 경우 checking_str='str'로 남기기
                    if current_status=='break':
                        checking_str='str'
                        continue

                    #### 해당 component의 output_port중 stage가 부여되지 않은 경우 checking_str=str()와 break
                    if ivalue not in got_stage:
                        checking_str=str()
                        break
                    
                    #### 해당 output_port가 stage가 부여되지 않은 경우 checking_str=str()와 break
                    if temp_output not in got_stage[ivalue]:
                        checking_str=str()
                        break
                    
                    #### 해당 component에 stage가 있는 output_port가 있고, 해당 output_port에도 stage가 부여된 경우 checking_str='str'
                    checking_str='str'

                #### 해당 component에 대해 모든 checking을 끝냈을 때 checking_str=='str'일 경우 will_del_set에 추가 (current_stage를 부여받은 component들의 집합)
                if checking_str=='str':
                    will_del_set.add(ivalue)

        #### will_del_set에 있는 component들을 temp_dict에서 제거
        for ivalue in will_del_set:
            temp_dict.remove(ivalue)
        
        #### current_stage를 1 더해서 최신화
        current_stage=current_stage+1

    #### stage의 내용과 related_pin에 대한 정보를 return 
    return [got_stage,related_group]






def get_origin_group(All,total,output_list,lib_all,id_all):

    last_list=list()
    all_list=set()
    con='con'
    #### output_list에 있는 모든 component들이 register 혹은 constant_cell 혹은 external_PIN일 때까지 while문 반복
    while con=='con':
        con=''
        temp_inputs=list()
        result_list=list()
        will_change_list=list()

        for temp_output in output_list:
            #### 관련된 모든 cell들을 all_list에 저장
            all_list.add(temp_output.split(' ')[0])

            #### temp_output이 reg, constant, 외부 핀 중 하나일 경우
            if temp_output.split(' ')[0] in total:
                result_list.append(temp_output)
                continue
            #### 동기화 되지 않은 component인 경우 해당 component의 port의 related_pin들을 리스트로 저장하고 해당 pin들의 from을 output_list에 추가
            con='con'
            will_change_list.append(temp_output)
            related_input_pin=list()
            for cases in lib_all[id_all[temp_output.split(' ')[0]]][temp_output.split(' ')[1]]:
                if cases.startswith('case_'):
                    #### 해당 case에서의 related_pin : related_input_pin
                    related_input_pin=list(set(related_input_pin)|set(lib_all[id_all[temp_output.split(' ')[0]]][temp_output.split(' ')[1]][cases]['related_pin']))
            
            #### 각 case의 related_pin의 from을 temp_inputs에 저장
            for temp_one_input in related_input_pin:
                temp_inputs.append(All[temp_output.split(' ')[0]]['input'][temp_one_input]['from'])

        #### output_list 최신화
        output_list=list(set(output_list)-set(will_change_list))
        output_list=list(set(output_list)-set(result_list))
        output_list=list(set(output_list)|set(temp_inputs))
        
        #### output_list에서 reg나 constant_cell, 외부 핀의 경우를 저장한 result_list을 last_list에 최신화
        last_list=list(set(last_list)|set(result_list))


    return [last_list,all_list]



if __name__=="__main__":
    #checking_now=sys.argv[1]


    posible_list=['superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','medium']
    posible_list=['superblue10']
    #posible_list=['superblue1']


    libs=list()
    for checking_now in posible_list:
        hypergraph_address='../../temp_data/hypergraph/'
        net_json='../../temp_data/verilog/'
        component_id='../../temp_data/verilog/'


        hypergraph_address=hypergraph_address+checking_now+'/'
        net_json=net_json+checking_now+'/'
        component_id=component_id+checking_now+'/'
        lib_address='../../temp_data/lib/'

        if checking_now=='easy' or checking_now=='medium':
            net_json=net_json+'nets_from_02.json'
            component_id=component_id+'checking_id_components.json'
            #libs.append(lib_address+'tcbn40lpbwp12tm1plvttc_ccs/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'tcbn40lpbwp12tm1ptc_ccs/lib_dict_for_nldm_delay_v.json')

            libs.append(lib_address+'TS1N40LPB128X63M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB256X12M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB256X22M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB256X23M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB512X23M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB512X32M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB1024X32M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB1024X128M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB2048X32M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB2048X36M4FWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')
            libs.append(lib_address+'TS1N40LPB4096X32M8MWBA_tt1p1v25c/lib_dict_for_nldm_delay_v.json')

        else:
            net_json=net_json+'temp_net.json'
            component_id=component_id+'temp_id.json'
            libs.append(lib_address+checking_now+'_Late/lib_dict_for_nldm_delay_v.json')



        print(checking_now)

        get_hypergraph(net_json,component_id,libs,hypergraph_address)
        
