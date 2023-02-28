import json
import sys
import os
import copy







#### 각 cell에서 output pin이 가지는 timing에 대한 정보를 parsing
def get_lib_info_for_delay_v(address):

    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    nldm_v1=dict()
    if 'cell_index.json' in os.listdir(location_of_lib):
        for cell in os.listdir(location_of_lib+'/cell/'):
            if cell.endswith('.txt'):
                continue

            #### pin이 있는 cell에 경우만 접근
            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/'):
                for pin in os.listdir(location_of_lib+'/cell/'+cell+'/pin'):
                    if pin.endswith('.txt'):
                        continue
                    
                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/pin_info.json','r') as fw:
                        temp_pin=json.load(fw)
                    fw.close()

                    if cell not in nldm_v1:
                        nldm_v1.update({cell:dict()})
                    if pin not in nldm_v1[cell]:
                        nldm_v1[cell].update({pin:dict()})
                    
                    #### direction 먼저 정한다.
                    if 'direction' in temp_pin:
                        nldm_v1[cell][pin].update({'direction':temp_pin['direction']})

                    #### 해당 pin이 input일 경우
                    if temp_pin['direction']=='input':
                        if 'fall_capacitance' in temp_pin:
                            nldm_v1[cell][pin].update({'fall_capacitance':float(temp_pin['fall_capacitance'])})
                        #### fall_capacitance가 없을 경우, capacitance를 사용한다.
                        elif 'capacitance' in temp_pin:
                            nldm_v1[cell][pin].update({'fall_capacitance':float(temp_pin['capacitance'])})

                        if 'rise_capacitance' in temp_pin:
                            nldm_v1[cell][pin].update({'rise_capacitance':float(temp_pin['rise_capacitance'])})
                        #### rise_capacitance가 없을 경우, capacitance를 사용한다.
                        elif 'capacitance' in temp_pin:
                            nldm_v1[cell][pin].update({'rise_capacitance':float(temp_pin['capacitance'])})
                        
                        #### clock에 대한 내용일 경우 저장
                        if 'clock' in temp_pin:
                            nldm_v1[cell][pin].update({'clock':temp_pin['clock']})
                        
                        #### nextstate_type에 대한 내용일 경우 저장
                        if 'nextstate_type' in temp_pin:
                            nldm_v1[cell][pin].update({'nextstate_type':temp_pin['nextstate_type']})

                        #### clock_gate_enable_pin에 대한 내용일 경우 저장
                        if 'clock_gate_enable_pin' in temp_pin:
                            nldm_v1[cell][pin].update({'clock_gate_enable_pin':temp_pin['clock_gate_enable_pin']})

                        #### clock_gate_clock_pin에 대한 내용일 경우 저장
                        if 'clock_gate_clock_pin' in temp_pin:
                            nldm_v1[cell][pin].update({'clock_gate_clock_pin':temp_pin['clock_gate_clock_pin']})

                        #### clock_gate_test_pin에 대한 내용일 경우 저장
                        if 'clock_gate_test_pin' in temp_pin:
                            nldm_v1[cell][pin].update({'clock_gate_test_pin':temp_pin['clock_gate_test_pin']})

                        #### max_transition에 대한 내용일 경우 저장
                        if 'max_transition' in temp_pin:
                            nldm_v1[cell][pin].update({'max_transition':float(temp_pin['max_transition'])})

                    
                    elif temp_pin['direction']=='output':
                        #### timing이 정의된 pin만 고려한다.
                        if 'timing' not in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin):
                            continue
                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing'):
                            if timingth.endswith('.txt'):
                                continue
                            
                            #### 해당 pin에 cell_rise의 경우가 있을 경우
                            if 'cell_rise_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_cell_rise in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_rise'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_rise/'+txt_cell_rise,'r') as fw:
                                        temp_cell_ri=fw.readlines()
                                    fw.close()
                                    
                                    if 'case_'+timingth.split('_')[1] not in nldm_v1[cell][pin]:
                                        nldm_v1[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'cell_rise' not in nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]].update({'cell_rise':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_cell_ri:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]['cell_rise'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 cell_fall의 경우가 있을 경우
                            if 'cell_fall_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_cell_fall in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_fall'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_fall/'+txt_cell_fall,'r') as fw:
                                        temp_cell_fa=fw.readlines()
                                    fw.close()
                                    
                                    if 'case_'+timingth.split('_')[1] not in nldm_v1[cell][pin]:
                                        nldm_v1[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'cell_fall' not in nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]].update({'cell_fall':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_cell_fa:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]['cell_fall'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 rise_transition의 경우가 있을 경우
                            if 'rise_transition_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_rise_tr in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/rise_transition'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/rise_transition/'+txt_rise_tr,'r') as fw:
                                        temp_rise_tr=fw.readlines()
                                    fw.close()
                                                                        
                                    if 'case_'+timingth.split('_')[1] not in nldm_v1[cell][pin]:
                                        nldm_v1[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'rise_transition' not in nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]].update({'rise_transition':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_rise_tr:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]['rise_transition'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 fall_transition의 경우가 있을 경우
                            if 'fall_transition_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_fall_tr in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/fall_transition'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/fall_transition/'+txt_fall_tr,'r') as fw:
                                        temp_fall_tr=fw.readlines()
                                    fw.close()
                                                                        
                                    if 'case_'+timingth.split('_')[1] not in nldm_v1[cell][pin]:
                                        nldm_v1[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'fall_transition' not in nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]].update({'fall_transition':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_fall_tr:
                                        nldm_v1[cell][pin]['case_'+timingth.split('_')[1]]['fall_transition'].append(ivalue.replace('\n',''))
                            
                            #### timing의 특성이 있을 경우, 해당 timing의 조건을 파악한다. (related_pin과 timing_sense)
                            for key_of_timing in nldm_v1[cell][pin]:
                                if key_of_timing=='direction':
                                    continue
                                with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/timing_'+key_of_timing.split('_')[1]+'/timing_info.json','r') as fw:
                                    temp_case_info=json.load(fw)
                                fw.close()

                                nldm_v1[cell][pin][key_of_timing].update({'timing_sense':temp_case_info['timing_sense']})
                                nldm_v1[cell][pin][key_of_timing].update({'related_pin':temp_case_info['related_pin']})

                                if 'timing_type' in temp_case_info:
                                    nldm_v1[cell][pin][key_of_timing].update({'timing_type':temp_case_info['timing_type']})


#### 특수한 cell인 latch, flip_flop(ff), clock_gating_integrated_cell인 경우 해당 특성을 해당 cell에 부여
    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):
            if cell.endswith('.txt'):
                continue
            
            #### 해당 cell이 ff인 경우
            if 'ff' in os.listdir(location_of_lib+'/cell/'+cell):
                nldm_v1[cell].update({'ff':'True'})

            #### 해당 cell이 latch인 경우
            if 'latch' in os.listdir(location_of_lib+'/cell/'+cell):
                nldm_v1[cell].update({'latch':'True'})

            if 'cell_info.json' not in os.listdir(location_of_lib+'/cell/'+cell):
                continue

            with open(location_of_lib+'/cell/'+cell+'/cell_info.json') as fw:
                temp_dict=json.load(fw)
            fw.close()

            #### 해당 cell이 clock_gating_integrated_cell인 경우
            if 'clock_gating_integrated_cell' in temp_dict:
                nldm_v1[cell].update({'clock_gating_integrated_cell':'True'})
            




#### 임의의 cell의 임의의 pin이 bus의 pin일 경우 bus에서의 내용임을 표시
    for cell in nldm_v1:
        for pin in nldm_v1[cell]:
            #### 임의의 cell의 임의의 pin이 multi_bit 중 하나의 bit일 경우
            if '[' in pin and ']' in pin and 'direction' in nldm_v1[cell][pin]:
                #### 해당 cell이 bus를 가지고 있는 경우
                if 'bus' in os.listdir(location_of_lib+'/cell/'+cell):
                    #### 확인하는 pin이 해당 cell의 bus의 pin들 중 하나일 경우
                    if pin.split('[')[0]+'.txt' in os.listdir(location_of_lib+'/cell/'+cell+'/bus'):
                        nldm_v1[cell][pin].update({'from_bus':'True'})




#### related_pin에 대한 내용을 정확히 parsing
#### 추후에 bus에 대해서 related_pin처리를 제대로 해야된다.
    input_list_dict=dict()
    for cell in nldm_v1:
        for pin in nldm_v1[cell]:
            #### pin이 아닌 cell의 내용인 경우 continue로 처리
            if 'direction' not in nldm_v1[cell][pin]:
                continue

            #### 해당 cell에 input pin이 있을 경우 해당 pin의 이름을 input_list_dict에 저장
            if nldm_v1[cell][pin]['direction']=='input':
                if cell not in input_list_dict:
                    input_list_dict.update({cell:list()})
                temp_real_pin=pin.replace('\'','').replace('\"','').strip()
                input_list_dict[cell].append(temp_real_pin)

        #### input_list_dict에 각 cell마다 input pin를 원소로 가지고, 각 pin의 이름이 긴 pin부터 정렬하여 저장
        if cell in input_list_dict:
            input_list_dict[cell].sort(key=len)
            input_list_dict[cell].reverse()



    for cell in nldm_v1:
        for pin in nldm_v1[cell]:
            #### pin이 아닌 cell의 내용인 경우 continue로 처리
            if 'direction' not in nldm_v1[cell][pin]:
                continue
            
            for cases in nldm_v1[cell][pin]:
                #### 해당 cases가 딕션너리가 아닌 경우 continue로 처리
                if str(type(nldm_v1[cell][pin][cases]))!='<class \'dict\'>':
                    continue
                #### related_pin이 없는 경우 해당 딕션너리를 continue로 처리
                if 'related_pin' not in nldm_v1[cell][pin][cases]:
                    continue
                
                #print(input_list_dict[cell])
                temp_line=copy.deepcopy(nldm_v1[cell][pin][cases]['related_pin'])
                temp_line=temp_line.replace('\'','').replace('\"','').strip()
                temp_related_pin_list=list()
                for temp_input in input_list_dict[cell]:
                    if temp_input in temp_line:
                        temp_line=temp_line.replace(temp_input,'')
                        temp_related_pin_list.append(temp_input)


                if len(temp_related_pin_list)==0:
                    for temp_input in input_list_dict[cell]:
                        if '[' in temp_input:
                            if temp_input.split('[')[0] in temp_line:
                                if pin.split('[')[1].split(']')[0]==temp_input.split('[')[1].split(']')[0]:
                                    temp_line=temp_line.replace(temp_input.split('[')[0],'')
                                    temp_related_pin_list.append(temp_input)

                nldm_v1[cell][pin][cases]['related_pin']=temp_related_pin_list




#### 따옴표로 처리된 내용에서 작은 따옴표 및 큰 따옴표를 없애고, delay에 대한 template를 참고하여 nldm table 완성시키기
    #### 각 cell의 output의 timing에 관련된 template를 미리 얻는다.
    get_template_dict=dict()
    if 'lu_table_template_index.json' in os.listdir(location_of_lib):
        for template in os.listdir(location_of_lib+'/lu_table_template/'):
            if template.endswith('.txt'):
                continue
            with open(location_of_lib+'/lu_table_template/'+template+'/lu_table_template_info.json','r') as fw:
                temp_one_dict=json.load(fw)
            fw.close()
            #### 각 template의 이름과 해당 template의 정보를 get_template_dict에 저장
            get_template_dict.update({template:temp_one_dict})

    #### 각 template마다 주어진 default값들을 parsing하여 저장
    for one_template in get_template_dict:
        for kindex in get_template_dict[one_template]:
            #### variable의 경우 따옴표 제거
            if kindex.startswith('variable_'):
                get_template_dict[one_template][kindex]=get_template_dict[one_template][kindex].replace("'",'').replace('"','').strip()
            #### index의 경우 따옴표 제거 및 실수화
            else:
                temp_list_of_kindex=list()
                for should_be_float in get_template_dict[one_template][kindex][0].replace('"','').replace("'",'').strip().split(','):
                    temp_list_of_kindex.append(float(should_be_float.strip()))
                get_template_dict[one_template][kindex]=temp_list_of_kindex

    for cell in nldm_v1:

        for pin in nldm_v1[cell]:
            #### cell의 내용 중 ff, latch, clock_gating_integrated_cell에 대한 내용을 continue로 처리
            if pin=='ff' or pin=='latch' or pin=='clock_gating_integrated_cell':
                continue

            #### 해당 cell의 모든 pin에 접근
            for case in nldm_v1[cell][pin]:
    
                if case=='direction':
                    #### 해당 pin의 direction이 input, output, internal, inout이 아닌 경우 화면에 출력
                    if nldm_v1[cell][pin][case]!='input' and nldm_v1[cell][pin][case]!='output' and nldm_v1[cell][pin][case]!='internal' and nldm_v1[cell][pin][case]!='inout':                    
                        print(cell,pin,case,nldm_v1[cell][pin][case])

                elif case=='fall_capacitance':
                    #### 해당 pin이 fall_capacitance의 값을 가질 때, 해당 값이 실수가 아닌 경우 화면에 출력
                    if str(type(nldm_v1[cell][pin][case]))!="<class 'float'>":
                        print(cell,pin,case)

                elif case=='rise_capacitance':
                    #### 해당 pin이 rise_capacitance의 값을 가질 때, 해당 값이 실수가 아닌 경우 화면에 출력
                    if str(type(nldm_v1[cell][pin][case]))!="<class 'float'>":
                        print(cell,pin,case)

                elif case=='max_transition':
                    #### 해당 pin이 max_transition의 값을 가질 때, 해당 값이 실수가 아닌 경우 화면에 출력
                    if str(type(nldm_v1[cell][pin][case]))!="<class 'float'>":
                        print(cell,pin,case)


                #### 해당 정보가 case가 아닌 경우 continue로 처리
                elif case=='from_bus' or case=='clock' or case=='nextstate_type' or \
                    case=='clock_gate_enable_pin' or case=='clock_gate_clock_pin' or case=='clock_gate_test_pin':
                    continue

                else:
                    #### 각 case마다 접근
                    for info in nldm_v1[cell][pin][case]:
                        
                        #### 각 case의 정보의 내용에 따옴표가 있을 경우 제거
                        if info=='timing_sense':
                            nldm_v1[cell][pin][case][info]=nldm_v1[cell][pin][case][info].replace('"','').replace("'",'').strip()
                        elif info=='timing_type':
                            nldm_v1[cell][pin][case][info]=nldm_v1[cell][pin][case][info].replace('"','').replace("'",'').strip()
                        elif info=='related_pin':
                            for tdx in range(len(nldm_v1[cell][pin][case][info])):
                                nldm_v1[cell][pin][case][info][tdx]=nldm_v1[cell][pin][case][info][tdx].replace('"','').replace("'",'').strip()
                        
                        #### delay에 대한 table의 내용 전처리
                        else:
                            scalar_str=str()
                            template_str=str()
                            all_line=str()
                            #### 각 내용을 한 문장으로 정리 : all_line
                            for temp_line in (nldm_v1[cell][pin][case][info]):
                                all_line=all_line+' '+temp_line.strip()
                                all_line=all_line.strip()
                            
                            #### 해당 table이 scalar인 경우 scalar_str='y'로 처리
                            temporary_template=all_line.split('(')[1].split(')')[0].replace('"','').replace("'",'').strip()
                            if temporary_template.lower()=='scalar':
                                scalar_str='y'
                            
                            #### 아닌 경우 해당 table에서 쓰인 template : temporary_template
                            else:
                                template_str=temporary_template

                            #### 해당 정보가 scalar값을 가질 경우, 해당 값을 실수화 하여 저장
                            if scalar_str=='y':
                                temp_scalar_value=float(all_line.split('values')[1].split(';')[0].split('(')[1].split(')')[0].replace("'",'').replace('"','').replace('\\','').strip())
                                nldm_v1[cell][pin][case][info]={'scalar':temp_scalar_value}
                            
                            #### 해당 정보가 scalar가 아닌 경우
                            else:
                                new_temp_dict=dict()
                                #### ';'을 기준으로 all_line을 분리한다.
                                temp_timing=all_line.split('{')[1].split('}')[0].strip().split(';')
                                input_tr=str()
                                load_cap=str()
                                indexing_dict=dict()
                                for ivalue in temp_timing:
                                    
                                    if '(' not in ivalue or ')' not in ivalue:
                                        continue
                                    #### index 및 value의 내용을 indexing_dict에 저장
                                    indexing_dict.update({ivalue.split('(')[0].strip():ivalue.split('(')[1].split(')')[0].strip()})
                                    if ivalue.split('(')[0].strip() in get_template_dict[template_str]:
                                        #### index의 경우 해당 template에서 input_net_transition일 경우 input_tr에 해당 index 저장
                                        if get_template_dict[template_str]['variable_'+ivalue.split('(')[0].strip().split('_')[1]]=='input_net_transition':
                                            input_tr=ivalue.split('(')[0].strip()

                                        #### index의 경우 해당 template에서 total_output_net_capacitance일 경우 load_cap에 해당 index 저장
                                        elif get_template_dict[template_str]['variable_'+ivalue.split('(')[0].strip().split('_')[1]]=='total_output_net_capacitance':
                                            load_cap=ivalue.split('(')[0].strip()

                                input_transition_index=list()
                                #### indexing_dict에 input_net_transition에 대한 내용이 없는 경우 template의 default값을 가져온다.
                                if input_tr=='':
                                    for ivalue in get_template_dict[template_str]:
                                        if get_template_dict[template_str][ivalue]=='input_net_transition':
                                            input_transition_index=get_template_dict[template_str]['index_'+ivalue.split('_')[1]]
                                #### 그렇지 않은 경우 indexing_dict에 있는 인덱스의 내용을 실수화하여 저장
                                else:
                                    temp_tr_list=indexing_dict[input_tr].replace('"','').replace("'",'').strip().split(',')
                                    for temp_tr_value in temp_tr_list:
                                        input_transition_index.append(float(temp_tr_value.strip()))

                                #### indexing_dict에 total_output_net_capacitance에 대한 내용이 없는 경우 template의 default값을 가져온다.
                                load_capacitance_index=list()
                                if load_cap=='':
                                    for ivalue in get_template_dict[template_str]:
                                        if get_template_dict[template_str][ivalue]=='total_output_net_capacitance':
                                            load_capacitance_index=get_template_dict[template_str]['index_'+ivalue.split('_')[1]]
                                #### 그렇지 않은 경우 indexing_dict에 있는 인덱스의 내용을 실수화하여 저장
                                else:
                                    temp_cap_list=indexing_dict[load_cap].replace('"','').replace("'",'').strip().split(',')
                                    for temp_cap_value in temp_cap_list:
                                        load_capacitance_index.append(float(temp_cap_value.strip()))
                                
                                #### input_net_transition과 total_output_net_capacitance의 내용이 둘 다 있을 경우
                                if len(input_transition_index)>0 and len(load_capacitance_index)>0:
                                    new_temp_dict.update({'input_transition':input_transition_index})
                                    new_temp_dict.update({'load_capacitance':load_capacitance_index})

                                    #### template에서 선언한 variable_1이 input_net_transition을 가리킬 경우
                                    if get_template_dict[template_str]['variable_1']=='input_net_transition':
                                        
                                        #### 해당 테이블의 내용을 '\\'을 기준으로 분리하여 저장
                                        temp_value_lines=indexing_dict['values'].split('\\')
                                        real_lines=list()
                                        for ivalue in temp_value_lines:
                                            if ivalue.strip()==',' or ivalue.strip()=='':
                                                continue
                                            real_lines.append(ivalue)
                                        
                                        data_list=list()
                                        for ivalue in real_lines:
                                            temp_data_list=ivalue.split('"')[1].split(',')
                                            temp_data_one_sentence=list()
                                            for kvalue in temp_data_list:
                                                temp_data_one_sentence.append(float(kvalue))
                                            data_list.append(temp_data_one_sentence)
                                        
                                        new_temp_dict.update({'data':data_list})
                                            
                                    #### template에서 선언한 variable_1이 total_output_net_capacitance을 가리킬 경우
                                    elif get_template_dict[template_str]['variable_1']=='total_output_net_capacitance':

                                        #### 해당 테이블의 내용을 '\\'을 기준으로 분리하여 저장
                                        temp_value_lines=indexing_dict['values'].split('\\')
                                        real_lines=list()
                                        for ivalue in temp_value_lines:
                                            if ivalue.strip()==',' or ivalue.strip()=='':
                                                continue
                                            real_lines.append(ivalue)
                                        
                                        data_list=list()
                                        real_data_list=list()
                                        tt=int()
                                        for ivalue in real_lines:
                                            temp_data_list=ivalue.split('"')[1].split(',')
                                            temp_data_one_sentence=list()
                                            for kvalue in temp_data_list:
                                                temp_data_one_sentence.append(float(kvalue.strip()))
                                            tt=len(temp_data_one_sentence)
                                            data_list.append(temp_data_one_sentence)

                                        #### template에서 선언한 variable_1이 total_output_net_capacitance을 가리킬 경우, 테이블의 내용을 transpose하여 저장한다.
                                        for idx in range(tt):
                                            real_data_list.append(list())
                                            for kdx in range(len(data_list)):
                                                real_data_list[idx].append(float())
                                        
                                        for idx in range(len(data_list)):
                                            for kdx in range(len(data_list[idx])):
                                                real_data_list[kdx][idx]=data_list[idx][kdx]
                                        
                                        new_temp_dict.update({'data':real_data_list})

                                #### 해당 template에서 total_output_net_capacitance의 내용이 없는 경우
                                elif len(input_transition_index)>0:
                                    new_temp_dict.update({'input_transition':input_transition_index})
                                    data_list=list()
                                    temp_value_str=indexing_dict['values'].split('"')[1].split(',')
                                    for kvalue in temp_value_str:
                                        data_list.append(float(kvalue.strip()))
                                    
                                    new_temp_dict.update({'data':data_list})
                                
                                #### 해당 template에서 input_net_transition의 내용이 없는 경우
                                elif len(load_capacitance_index)>0:
                                    new_temp_dict.update({'load_capacitance':load_capacitance_index})
                                    data_list=list()
                                    temp_value_str=indexing_dict['values'].split('"')[1].split(',')
                                    for kvalue in temp_value_str:
                                        data_list.append(float(kvalue.strip()))
                                    new_temp_dict.update({'data':data_list})
                            
                                nldm_v1[cell][pin][case][info]=new_temp_dict
    

    #### 특수한 output pin에 대한 처리
    for cell in nldm_v1:
        for pin in nldm_v1[cell]:
            if 'direction' not in nldm_v1[cell][pin]:
                continue
            if nldm_v1[cell][pin]['direction']=='output':
                #### pin 정보가 있는 output pin에만 접근
                if 'pin_info.json' not in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin):
                    continue
                with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/pin_info.json','r') as fw:
                    temp_pin=json.load(fw)
                fw.close()
                for temp_attri in temp_pin:
                    #### 해당 pin의 max_capacitance 저장
                    if temp_attri=='max_capacitance':
                        nldm_v1[cell][pin].update({'max_capacitance':float(temp_pin[temp_attri].replace('"','').replace("'",'').replace('\\','').strip())})
                    #### 해당 pin의 driver_type 저장
                    elif temp_attri=='driver_type':
                        nldm_v1[cell][pin].update({'driver_type':temp_pin[temp_attri].replace('"','').replace("'",'').replace('\\','').strip()})
                    #### 해당 pin의 clock_gate_out_pin 저장
                    elif temp_attri=='clock_gate_out_pin':
                        nldm_v1[cell][pin].update({'clock_gate_out_pin':'True'})

    #### 특정 cell의 특정 pin의 이름에 따옴표가 있을 경우 처리
    for cell in nldm_v1:
        will_del=list()
        for pin in nldm_v1[cell]:
            #### cell의 내용 중 ff, latch, clock_gating_integrated_cell에 대한 내용을 continue로 처리
            if pin=='ff' or pin=='latch' or pin=='clock_gating_integrated_cell':
                continue
            
            #### 해당 pin이 따옴표가 있을 경우
            if '"' in pin or "'" in pin or '\\' in pin:
                will_del.append(pin)
        
        for ivalue in will_del:
            #### 따옴표를 제거한 pin이름으로 내용을 저장한다.
            nldm_v1[cell].update({ivalue.replace("\'",'').replace('\"','').replace('\\','').strip():nldm_v1[cell][ivalue]})
            #### 기존에 따옴표를 가지고 있던 pin은 제거한다.
            del nldm_v1[cell][ivalue]

    will_del=list()
    #### 특정 cell의 이름에 따옴표가 있을 경우 처리
    for cell in nldm_v1:
        #### 해당 cell에 따옴표가 있을 경우
        if "'" in cell or '"' in cell or '\\' in cell:
            will_del.append(cell)
    
    for ivalue in will_del:
        #### 따옴표를 제거한 cell이름으로 내용을 저장한다.
        nldm_v1.update({ivalue.replace("\'",'').replace('\"','').replace('\\','').strip():nldm_v1[ivalue]})
        #### 기존에 따옴포를 가지고 있던 cell은 제거한다.
        del nldm_v1[ivalue]



    with open(location_of_lib+'/lib_dict_for_nldm_delay_v.json','w') as fw:
        json.dump(nldm_v1,fw,indent=4)
    fw.close()


    return 0









if __name__=="__main__":
    checking=sys.argv[1]
    lib_address='../../data/test_LIB_groups/'
    lib_address='../../temp_data/lib/'
    lib_address=lib_address+checking

    get_lib_info_for_delay_v(lib_address)
    

