import json
import sys
import copy




def get_hypergraph(net,id,lib_list):
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
    reg_components=list()
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
            #### 해당 cell의 pin중 clock에 동기화된 pin이 있을 경우 reg_components에 추가
            if pin=='ff' or pin=='latch':
                reg_components.append(ivalue)
                continue

            if pin=='clock_gating_integrated_cell':
                continue
            #### 해당 pin이 input이거나 output일 경우 all_component_dict에 저장
            if 'direction' in lib_dict[temp_id[ivalue]][pin]:
                if lib_dict[temp_id[ivalue]][pin]['direction']=='input':
                    if 'input' not in all_component_dict[ivalue]:
                        all_component_dict[ivalue].update({'input':dict()})
                    all_component_dict[ivalue]['input'].update({pin:dict()})

                elif lib_dict[temp_id[ivalue]][pin]['direction']=='output':
                    if 'output' not in all_component_dict[ivalue]:
                        all_component_dict[ivalue].update({'output':dict()})
                    all_component_dict[ivalue]['output'].update({pin:dict()})
                
    reg_components=list(set(reg_components))
        
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
    #### total_set에는 register, constant_cell, 외부 pin의 내용이 있다.
    total_set=constant_group|reg_components|pins_group
    for reg in reg_components:
        if 'input' in all_component_dict[reg]:
            for input_pin in all_component_dict[reg]['input']:
                #### clock에 동기화된 register의 pin의 신호가 시작하는 외부 핀 혹은 register의 output 혹은 constant pin 등 해당 cell의 clock 신호가 작동하기 위해 필요한 component를 temp_output_group에 저장
                if 'clock' in lib_dict[temp_id[reg]][input_pin]:
                    if all_component_dict[reg]['input'][input_pin]['from'] not in temp_output_group:
                        #### get_origin_group을 통해 같은 net을 공유하는 register의 clock pin의 출처에 대한 데이터를 temp_output_group에 저장
                        temp_output_group.update({all_component_dict[reg]['input'][input_pin]['from']:get_origin_group(all_component_dict,total_set,[all_component_dict[reg]['input'][input_pin]['from']],lib_dict,temp_id)})




    ########################################## 여기서부터!



    current_clk_stage=int()
    ee=int()
    print(len(reg_components))

    temp_reg_dict=dict()
    while len(reg_components)!=0:
        will_del=set()
        for reg in reg_components:
            if 'input' in all_component_dict[reg]:
                for input_pin in all_component_dict[reg]['input']:
                    if 'clock' in lib_dict[temp_id[reg]][input_pin]:
                        origin_clk_group=temp_output_group[all_component_dict[reg]['input'][input_pin]['from']]
                        break_str=''

                        '''if current_clk_stage==10 and ee==0:
                            print(all_component_dict[reg]['input'][input_pin]['from'])
                            print()
                            for kvale in origin_clk_group:
                                print(kvale)
                            ee=1'''
                        for temp_component in origin_clk_group:
                            if temp_component.split(' ')[0] in reg_components:
                                break_str='break'
                                break
                        if break_str=='':
                            temp_reg_dict.update({reg:current_clk_stage})
                            will_del.add(reg)
        reg_components=reg_components-will_del
        for temp_net in temp_output_group:
            temp_output_group[temp_net]=list(set(temp_output_group[temp_net])-will_del)
        current_clk_stage=current_clk_stage+1

    tt=int()
    for ivalue in temp_reg_dict:
        if temp_reg_dict[ivalue]==0 and tt==0:
            print(ivalue)
            print(temp_output_group[all_component_dict[ivalue]['input']['CP']['from']])
            tt=1
        
        if temp_reg_dict[ivalue]==1 and tt==1:
            print(ivalue)
            print(temp_output_group[all_component_dict[ivalue]['input']['CP']['from']])
            tt=2

    return 0


def get_origin_group(All,total,output_list,lib_all,id_all):

    last_list=list()
    con='con'
    while con=='con':
        con=''
        temp_inputs=list()
        result_list=list()
        will_change_list=list()
        for temp_output in output_list:
            if temp_output.split(' ')[0] in total:
                result_list.append(temp_output)
                continue
            con='con'
            will_change_list.append(temp_output)
            related_input_pin=list()
            for cases in lib_all[id_all[temp_output.split(' ')[0]]][temp_output.split(' ')[1]]:
                if cases.startswith('case_'):
                    related_input_pin=list(set(related_input_pin)|set(lib_all[id_all[temp_output.split(' ')[0]]][temp_output.split(' ')[1]][cases]['related_pin']))
            for temp_one_input in related_input_pin:
                temp_inputs.append(All[temp_output.split(' ')[0]]['input'][temp_one_input]['from'])

        output_list=list(set(output_list)-set(will_change_list))
        output_list=list(set(output_list)|set(temp_inputs))
        
        last_list=list(set(last_list)|set(result_list))
        output_list=list(set(output_list)-set(result_list))


    return last_list




if __name__=="__main__":
    #checking_now=sys.argv[1]


    posible_list=['superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','medium']
    posible_list=['medium']
    #posible_list=['superblue1']


    libs=list()
    for checking_now in posible_list:

        net_json='../../temp_data/verilog/'
        component_id='../../temp_data/verilog/'
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
        get_hypergraph(net_json,component_id,libs)
