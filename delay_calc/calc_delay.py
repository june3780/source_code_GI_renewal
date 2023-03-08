import json


def get_delay(net,id,lib_list,hyper_add,clk_pins):

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
    


    with open(hyper_add+'input_output.json','r')as fw:
        all_component_dict=json.load(fw)
    fw.close()

    with open(hyper_add+'reg_priority.json','r')as fw:
        temp_reg_dict=json.load(fw)
    fw.close()

    with open(hyper_add+'stage_clk_to_reg.json','r')as fw:
        clk_to_reg_stage_dict=json.load(fw)
    fw.close()

    with open(hyper_add+'related_pin_clk_to_reg.json','r')as fw:
        clk_to_reg_related_pin_dict=json.load(fw)
    fw.close()


    calc_delay_clk(all_component_dict,clk_to_reg_stage_dict,clk_to_reg_related_pin_dict,temp_id,lib_dict,temp_reg_dict,clk_pins)

    '''with open(hyper_add+'stage_reg_to_reg.json','r')as fw:
        reg_to_reg_stage_dict=json.load(fw)
    fw.close()

    with open(hyper_add+'related_pin_reg_to_reg.json','r')as fw:
        reg_to_reg_related_pin_dict=json.load(fw)
    fw.close()'''








    return 0



def calc_delay_clk(All,stage_dict,relation_dict,id_dict,lib_dict,reg_priority,clk_pins):
    Delay_all=dict()



    max_reg_priority=int()
    zero_group=list()
    for ivalue in reg_priority:
        if max_reg_priority<reg_priority[ivalue]:
            max_reg_priority=reg_priority[ivalue]
        if reg_priority[ivalue]==0:
            zero_group.append(ivalue)
    

    for temp_clk in clk_pins:
        Delay_all.update({temp_clk:{'PIN':{'F_delay':float(0),'R_delay':float(0),'T_fall':float(0),'T_rise':float(0)}}})
    
    for temp_component in relation_dict:
        for temp_output in relation_dict[temp_component]:
            if len(relation_dict[temp_component][temp_output])==0:
                Delay_all.update({temp_component:{temp_output:{'F_delay':float(0),'R_delay':float(0),'T_fall':float(0),'T_rise':float(0)}}})

    zero_dict=dict()
    for ivalue in zero_group:
        if 'input' in All[ivalue]:
            for temp_input in All[ivalue]['input']:
                if 'clock' in lib_dict[id_dict[ivalue]][temp_input]:
                    if ivalue not in zero_dict:
                        zero_dict.update({ivalue:list()})
                    zero_dict[ivalue].append(temp_input)

    calc_delay(Delay_all,All,stage_dict,clk_pins,zero_dict,relation_dict,id_dict,lib_dict)

    current_priority=0
    for idx in range(max_reg_priority):

        origin_groups=list()
        end_groups=list()

        for ivalue in reg_priority:
            if reg_priority[ivalue]==current_priority:
                origin_groups.append(ivalue)
            elif reg_priority[ivalue]==current_priority+1:
                end_groups.append(ivalue)

        end_dict=dict()
        for ivalue in end_groups:
            if 'input' in All[ivalue]:
                for temp_input in All[ivalue]['input']:
                    if 'clock' in lib_dict[id_dict[ivalue]][temp_input]:
                        if ivalue not in end_dict:
                            end_dict.update({ivalue:list()})
                        end_dict[ivalue].append(temp_input)

        #calc_delay(Delay_all,All,stage_dict,origin_groups,end_groups,relation_dict,id_dict,lib_dict)

    return 0



def calc_delay(Delay,All,stage,origin_group,end_group,relation,id_dict,lib_dict):
    current_stage=int()

    next_components=set()
    for ivalue in origin_group:
        if 'output' in All[ivalue]:
            for temp_output in All[ivalue]['output']:
                for temp_next_component in All[ivalue]['output'][temp_output]['to']:
                    next_components.add(temp_next_component.split(' ')[0])

    current_stage=1

    while len(end_group)!=0:
        for ivalue in next_components:
            for temp_output in All[ivalue]['output']:
                if stage[ivalue][temp_output]==current_stage:
                    print(ivalue,temp_output)
        
        break



    return 0




if __name__=="__main__":

    posible_list=['superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','medium']
    #posible_list=['superblue10']
    posible_list=['superblue1']
    posible_list=['medium']



    libs=list()
    for checking_now in posible_list:
        hypergraph_address='../../temp_data/hypergraph/'
        net_json='../../temp_data/verilog/'
        component_id='../../temp_data/verilog/'


        clk_groups=list()
        if checking_now!='medium':
            clk_groups=['iccad_clk']
        else:
            clk_groups=['clk_i']

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
        get_delay(net_json,component_id,libs,hypergraph_address,clk_groups)