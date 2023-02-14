import json
import os
import copy
import time

import sys




#### lib 파일에서 cell 이름별로 해당 파일이 있는 디렉토리에 하위 디렉토리 생성
def get_lib_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    new_directory_name=location_of_lib.split('/')[-1]
    #### 해당 lib파일이 있는 디렉토리에 lib파일의 파일명과 같은 디렉토리가 없을 경우 디렉토리 생성
    if new_directory_name not in os.listdir(address.split(address.split('/')[-1])[0]):
        os.mkdir(location_of_lib)

    return 0


#### lib 파일에서 cell 이름별로 파일을 나눈다.
def get_lib_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['cell','lu_table_template','type','operating_conditions',\
            'power_lut_template','output_current_template','pg_current_template',\
            'wire_load','wire_load_selection','input_voltage','output_voltage']

    #### parsing할 파일 : target_text
    target_text=address
    target_directory=target_text.split('.lib')[0]

    txt_index_start_and_end(target_text,target_directory,checking_group)

    return 0


#### lib 파일에서 cell 이름별로 lib을 나누어 각 cell 디렉토리에 txt파일로 저장.
def get_cell_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    first_keyword='cell'
    previous_txt_location=address
    
    if first_keyword+'_index.json' in os.listdir(location_of_lib):
        current_keyword=location_of_lib+'/'+first_keyword
        #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
        get_sub_txt(previous_txt_location,current_keyword,first_keyword)

    return 0





#### parsing한 각각의 cell의 내용에 대한 하위 디렉토리 생성
def get_cell_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='cell'

    #### 해당 cell에 대한 상위 디렉토리 : upper_directory

    if first_keyword+'_index.json' in os.listdir(location_of_lib):

        upper_directory=location_of_lib+'/'+first_keyword+'/'
        #### 해당 cell에 대해 txt파일의 파일명과 같은 디렉토리 생성
        get_directory_of_the_keyword(upper_directory)

    return 0


def get_cell_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['test_cell', 'leakage_current', 'intrinsic_parasitic',\
        'pg_pin', 'statetable', 'leakage_power', 'dynamic_current', 'bus', 'memory',\
        'pin', 'ff', 'latch']


    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell_text in os.listdir(location_of_lib+'/cell'):

            if cell_text.endswith('.txt'):

                target_text=location_of_lib+'/cell/'+cell_text
                target_directory=target_text.split('.txt')[0]
                
                
                txt_index_start_and_end(target_text,target_directory,checking_group)

    return 0


#### lib 파일에서 cell의 내용 중, pin에 대한 정보를 parsing하여 pin 디렉토리 생성 후, pin_name.txt파일로 저장
def get_pin_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='pin'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):

            if cell.endswith('.txt'):
                continue
            
            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                previous_txt_location=location_of_lib+'/cell/'+cell+'.txt'
                current_keyword=location_of_lib+'/cell/'+cell+'/'+text_keyword
                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                get_sub_txt(previous_txt_location,current_keyword,text_keyword)

    return 0








#### parsing한 각각의 pin의 내용에 대한 하위 디렉토리 생성
def get_pin_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='pin'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell_name in os.listdir(location_of_lib+'/cell/'):
            if cell_name.endswith('.txt'):
                continue
            
            if first_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell_name):

                #### 해당 pin에 대한 상위 디렉토리 : upper_directory
                upper_directory=location_of_lib+'/cell/'+cell_name+'/'+first_keyword+'/'
                #### 해당 pin에 대해 txt파일의 파일명과 같은 디렉토리 생성
                get_directory_of_the_keyword(upper_directory)

    return 0


def get_pin_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    checking_group=['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage','memory_write','memory_read']

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):

            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                for pin_txt in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_txt.endswith('.txt'):
                        
                        target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin_txt
                        
                        target_directory=target_text.split('.txt')[0]
                        txt_index_start_and_end(target_text,target_directory,checking_group)
    return 0








def get_timing_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='timing'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):
            if cell.endswith('.txt'):
                continue
            
            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for pin_name in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_name.endswith('.txt'):
                        continue
                
                    if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'):

                        previous_txt_location=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'.txt'
                        current_keyword=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'+text_keyword
                        #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                        get_sub_txt(previous_txt_location,current_keyword,text_keyword)

    return 0








#### parsing한 각각의 timing의 내용에 대한 하위 디렉토리 생성
def get_timing_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='timing'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell_name in os.listdir(location_of_lib+'/cell/'):
            if cell_name.endswith('.txt'):
                continue
            
            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell_name):

                for pin in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'):
                    if pin.endswith('.txt'):
                        continue

                    if first_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'+pin):

                        #### 해당 timing에 대한 상위 디렉토리 : upper_directory
                        upper_directory=location_of_lib+'/cell/'+cell_name+'/pin/'+pin+'/'+first_keyword+'/'
                        #### 해당 timing에 대해 txt파일의 파일명과 같은 디렉토리 생성
                        get_directory_of_the_keyword(upper_directory)

    return 0


def get_timing_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['cell_rise','rise_transition','cell_fall','fall_transition','ccsn_first_stage','ccsn_last_stage',\
                    'output_current_rise','receiver_capacitance1_rise', 'receiver_capacitance2_rise',\
                    'output_current_fall','receiver_capacitance1_fall','receiver_capacitance2_fall',\
                    'retaining_fall','retaining_rise','retain_rise_slew','retain_fall_slew',\
                    'rise_constraint','fall_constraint']


    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):

            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                for pin in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    
                    if pin.endswith('.txt'):
                        continue
                    
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing'):
                            if timingth.endswith('.txt'):
                            
                                target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth
                                target_directory=target_text.split('.txt')[0]
                                txt_index_start_and_end(target_text,target_directory,checking_group)

    return 0


def get_cell_rise_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='cell_rise'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):
            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for pin_name in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_name.endswith('.txt'):
                        continue
                
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'):
                            if timingth.endswith('.txt'):
                                continue

                            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth):
                    
                                previous_txt_location=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                                current_keyword=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword
                                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                                get_sub_txt(previous_txt_location,current_keyword,text_keyword)

    return 0


def get_cell_fall_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='cell_fall'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):
            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for pin_name in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_name.endswith('.txt'):
                        continue
                
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'):
                            if timingth.endswith('.txt'):
                                continue

                            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth):

                                previous_txt_location=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                                current_keyword=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword
                                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                                get_sub_txt(previous_txt_location,current_keyword,text_keyword)
    return 0


def get_rise_transition_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='rise_transition'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):
            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for pin_name in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_name.endswith('.txt'):
                        continue
                
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'):
                            if timingth.endswith('.txt'):
                                continue

                            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth):

                                previous_txt_location=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                                current_keyword=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword
                                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                                get_sub_txt(previous_txt_location,current_keyword,text_keyword)

    return 0


def get_fall_transition_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='fall_transition'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):
            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for pin_name in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_name.endswith('.txt'):
                        continue
                
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'):
                            if timingth.endswith('.txt'):
                                continue

                            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth):

                                previous_txt_location=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                                current_keyword=location_of_lib+'/cell/'+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword
                                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                                get_sub_txt(previous_txt_location,current_keyword,text_keyword)
    return 0



def get_one_sentence_info_lib(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    target_o_info=['delay_model', 'time_unit', 'voltage_unit', 'current_unit', 'leakage_power_unit', 'pulling_resistance_unit', \
        'default_fanout_load', 'default_inout_pin_cap', 'default_input_pin_cap', 'default_output_pin_cap', \
        'slew_lower_threshold_pct_rise', 'slew_lower_threshold_pct_fall', 'slew_upper_threshold_pct_rise', 'slew_upper_threshold_pct_fall', \
        'input_threshold_pct_rise', 'input_threshold_pct_fall', 'output_threshold_pct_rise', 'output_threshold_pct_fall', \
        'nom_voltage', 'nom_temperature', 'nom_process', 'default_operating_conditions',\
        'date','revision','comment','in_place_swap_mode', 'slew_derate_from_library', \
        'default_leakage_power_density', 'default_cell_leakage_power', 'default_max_transition', 'default_wire_load',\
        'simulation', 'default_max_fanout', \
        'k_volt_cell_leakage_power', 'k_temp_cell_leakage_power', 'k_process_cell_leakage_power', 'k_volt_internal_power', 'k_temp_internal_power', 'k_process_internal_power',\
        'default_wire_load_selection', 'default_wire_load_mode']

    target_n_info=['technology','library_features','capacitive_load_unit','voltage_map','define','define_cell_area']

    #### lib파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
    info_dict=get_one_info(address,target_o_info,target_n_info,'library')

    if len(info_dict)!=0:
        with open(location_of_lib+'/lib_info.json','w') as fw:
            json.dump(info_dict,fw,indent=4)
        fw.close()

    return 0





def get_one_sentence_info_cell(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    target_o_info=['area', 'interface_timing', 'dont_use', 'dont_touch', 'map_only', 'drive_strength', 'cell_leakage_power', 'clock_gating_integrated_cell', 'cell_footprint']


    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell_text in os.listdir(location_of_lib+'/cell'):

            if cell_text.endswith('.txt'):

                target_text=location_of_lib+'/cell/'+cell_text
                target_directory=target_text.split('.txt')[0]
                #### txt파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
                info_dict=get_one_info(target_text,target_o_info,list(),'cell')
                if len(info_dict)!=0:
                    with open(target_directory+'/cell_info.json','w') as fw:
                        json.dump(info_dict,fw,indent=4)
                    fw.close()

    return 0




def get_one_sentence_info_pin(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    target_o_info=['direction','fall_capacitance','rise_capacitance','capacitance','nextstate_type','clock','max_transition','internal_node',\
                'capacitance','min_capacitance','max_capacitance','power_down_function','state_function','function',\
                'three_state','clock_gate_clock_pin','clock_gate_test_pin','clock_gate_enable_pin',\
                'related_ground_pin','related_power_pin','clock_gate_out_pin','driver_type']



    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):

            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                for pin_txt in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    if pin_txt.endswith('.txt'):

                        target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin_txt
                        target_directory=target_text.split('.txt')[0]
                        #### txt파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
                        info_dict=get_one_info(target_text,target_o_info,list(),'pin')

                        if len(info_dict)!=0:                        
                            with open(target_directory+'/pin_info.json','w') as fw:
                                json.dump(info_dict,fw,indent=4)
                            fw.close()

    return 0


def get_one_sentence_info_timing(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    target_o_info=['timing_sense','related_pin','timing_type','sdf_cond','when']

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):

            if cell.endswith('.txt'):
                continue

            if 'pin_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                for pin in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
                    
                    if pin.endswith('.txt'):
                        continue
                    
                    if 'timing_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/'):

                        for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing'):
                            if timingth.endswith('.txt'):
                            
                                target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth
                                target_directory=target_text.split('.txt')[0]

                                #### txt파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
                                info_dict=get_one_info(target_text,target_o_info,list(),'timing')

                                if len(info_dict)!=0:                        
                                    with open(target_directory+'/timing_info.json','w') as fw:
                                        json.dump(info_dict,fw,indent=4)
                                    fw.close()

    return 0



#### lib 파일에서 lu_table_template 이름별로 lib을 나누어 각 lu_table_template 디렉토리에 txt파일로 저장.
def get_lu_table_template_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    first_keyword='lu_table_template'
    previous_txt_location=address
    
    if first_keyword+'_index.json' in os.listdir(location_of_lib):
        current_keyword=location_of_lib+'/'+first_keyword
        #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
        get_sub_txt(previous_txt_location,current_keyword,first_keyword)

    return 0



def get_lu_table_template_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='lu_table_template'

    #### 해당 lu_table_template에 대한 상위 디렉토리 : upper_directory

    if first_keyword+'_index.json' in os.listdir(location_of_lib):

        upper_directory=location_of_lib+'/'+first_keyword+'/'
        #### 해당 lu_table_template에 대해 txt파일의 파일명과 같은 디렉토리 생성
        get_directory_of_the_keyword(upper_directory)

    return 0




def get_one_sentence_info_lu_table_template(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    target_o_info=['variable_1', 'variable_2', 'variable_3', 'variable_4']
    target_n_info=['index_1','index_2']


    if 'lu_table_template_index.json' in os.listdir(location_of_lib):

        for cell_text in os.listdir(location_of_lib+'/lu_table_template'):

            if cell_text.endswith('.txt'):

                target_text=location_of_lib+'/lu_table_template/'+cell_text
                target_directory=target_text.split('.txt')[0]
                #### txt파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
                info_dict=get_one_info(target_text,target_o_info,target_n_info,'lu_table_template')
                if len(info_dict)!=0:
                    with open(target_directory+'/lu_table_template_info.json','w') as fw:
                        json.dump(info_dict,fw,indent=4)
                    fw.close()

    return 0


#### lib 파일에서 type 이름별로 lib을 나누어 각 type 디렉토리에 txt파일로 저장.
def get_type_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    first_keyword='type'
    previous_txt_location=address
    
    if first_keyword+'_index.json' in os.listdir(location_of_lib):
        current_keyword=location_of_lib+'/'+first_keyword
        #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
        get_sub_txt(previous_txt_location,current_keyword,first_keyword)

    return 0



def get_type_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='type'

    #### 해당 cell에 대한 상위 디렉토리 : upper_directory

    if first_keyword+'_index.json' in os.listdir(location_of_lib):

        upper_directory=location_of_lib+'/'+first_keyword+'/'
        #### 해당 cell에 대해 txt파일의 파일명과 같은 디렉토리 생성
        get_directory_of_the_keyword(upper_directory)

    return 0




def get_one_sentence_info_type(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    target_o_info=['base_type', 'data_type', 'bit_width', 'bit_from','bit_to','downto']
    target_n_info=[]


    if 'type_index.json' in os.listdir(location_of_lib):

        for cell_text in os.listdir(location_of_lib+'/type'):

            if cell_text.endswith('.txt'):

                target_text=location_of_lib+'/type/'+cell_text
                target_directory=target_text.split('.txt')[0]
                #### txt파일에서 구간의 정보를 제외한 한 문장으로 표현되는 특성들을 parsing하여 저장
                info_dict=get_one_info(target_text,target_o_info,target_n_info,'type')
                if len(info_dict)!=0:
                    with open(target_directory+'/type_info.json','w') as fw:
                        json.dump(info_dict,fw,indent=4)
                    fw.close()

    return 0




#### lib 파일에서 cell의 내용 중, bus에 대한 정보를 parsing하여 bus 디렉토리 생성 후, bus_name.txt파일로 저장
def get_bus_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='bus'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in (os.listdir(location_of_lib+'/cell/')):

            if cell.endswith('.txt'):
                continue
            
            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell):
            
                previous_txt_location=location_of_lib+'/cell/'+cell+'.txt'
                current_keyword=location_of_lib+'/cell/'+cell+'/'+text_keyword
                #### 해당 keyword에 대한 구간에 대한 정보만 parsing하여 하위 디렉토리 생성 후, txt파일로 저장
                get_sub_txt(previous_txt_location,current_keyword,text_keyword)

    return 0








def copy_text_pin_from_bus(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='bus'

    if 'cell_index.json' in os.listdir(location_of_lib):

        for cell in os.listdir(location_of_lib+'/cell/'):

            if cell.endswith('.txt'):
                continue
            if text_keyword+'_index.json' in os.listdir(location_of_lib+'/cell/'+cell):

                for bus in os.listdir(location_of_lib+'/cell/'+cell+'/bus'):
                    with open(location_of_lib+'/cell/'+cell+'/bus/'+bus,'r') as fw:
                        lines=fw.readlines()
                    fw.close()

                    other_lines=list()
                    pins_start_idx=list()
                    pins_end_idx=list()
                    bus_dict=dict()

                    for idx in range(len(lines)):
                        if lines[idx].strip().startswith('pin') and lines[idx].split('pin')[1].strip().startswith('('):
                            bus_dict.update({'pin_array':lines[idx].split('(')[1].split(')')[0].strip()})
                            pins_start_idx.append(idx)
                            pins_end_idx.append(counting_function(idx,lines))

                    for idx in range(len(pins_start_idx)):
                        for kdx in range(pins_end_idx[idx]-pins_start_idx[idx]-1):
                            other_lines.append(lines[pins_start_idx[idx]+kdx+1])

                    checking_idx=-1
                    for idx in range(len(lines)):
                        #### parsing_keyword의 parsing 이전에 parsing한 다른 구간의 특성들이 있을경우
                        if len(pins_start_idx)!=0:
                            check_out=except_lines(pins_start_idx,pins_end_idx,idx,checking_idx)
                            checking_idx=check_out[1]
                            #### 해당 idx가 다른 특성의 구간 내에 있을 경우
                            if check_out[0]=='not_pass':
                                continue
                            if lines[idx].strip().startswith('bus') and lines[idx].split('bus')[1].strip().startswith('('):
                                continue
                            if lines[idx].strip().startswith('bus_type') and lines[idx].split('bus_type')[1].strip().startswith(':'):
                                bus_dict.update({'bus_type':lines[idx].split(':')[1].split(';')[0].strip()})
                                continue
                            other_lines.append(lines[idx])

                    
                    with open(location_of_lib+'/type/'+bus_dict['bus_type']+'/type_info.json','r') as fw:
                        type_dict=json.load(fw)
                    fw.close()

                    pin_name=bus_dict['pin_array'].split('[')[0].strip()
                    list_pins=list()
                    
                    if type_dict['base_type']=='array' and type_dict['data_type']=='bit':
                        if type_dict['downto']=='true':
                            for idx in range((int(type_dict['bit_width']))):
                                list_pins.append(pin_name+'['+str(int(type_dict['bit_from'])-idx)+']')
                        else:
                            for idx in range((int(type_dict['bit_width']))):
                                list_pins.append(pin_name+'['+str(int(type_dict['bit_from'])+idx)+']')
                    
                    if 'pin_index.json' not in os.listdir(location_of_lib+'/cell/'+cell):
                        temp_dict=dict()
                        with open(location_of_lib+'/cell/'+cell+'/pin_index.json','w') as fw:
                            json.dump(temp_dict,fw,indent=4)
                        fw.close()

                        os.mkdir(location_of_lib+'/cell/'+cell+'/pin')

                    for ivalue in list_pins:
                        with open(location_of_lib+'/cell/'+cell+'/pin/'+ivalue+'.txt','w') as fw:
                            fw.write('pin('+ivalue+') {\n')
                        fw.close()
                        with open(location_of_lib+'/cell/'+cell+'/pin/'+ivalue+'.txt','a') as fw:
                            for ivalue in other_lines:
                                fw.write(ivalue)
                        fw.close()
            
    return 0




def get_lib_info_for_delay_v1(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    bre=''
    delay_dict=dict()
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

                    if cell not in delay_dict:
                        delay_dict.update({cell:dict()})
                    if pin not in delay_dict[cell]:
                        delay_dict[cell].update({pin:dict()})
                    
                    #### direction 먼저 정한다.
                    if 'direction' in temp_pin:
                        delay_dict[cell][pin].update({'direction':temp_pin['direction']})

                    #### 해당 pin이 input일 경우
                    if temp_pin['direction']=='input':
                        if 'fall_capacitance' in temp_pin:
                            delay_dict[cell][pin].update({'fall_capacitance':float(temp_pin['fall_capacitance'])})
                        #### fall_capacitance가 없을 경우, capacitance를 사용한다.
                        elif 'capacitance' in temp_pin:
                            delay_dict[cell][pin].update({'fall_capacitance':float(temp_pin['capacitance'])})

                        if 'rise_capacitance' in temp_pin:
                            delay_dict[cell][pin].update({'rise_capacitance':float(temp_pin['rise_capacitance'])})
                        #### rise_capacitance가 없을 경우, capacitance를 사용한다.
                        elif 'capacitance' in temp_pin:
                            delay_dict[cell][pin].update({'rise_capacitance':float(temp_pin['capacitance'])})
                    
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
                                    
                                    if 'case_'+timingth.split('_')[1] not in delay_dict[cell][pin]:
                                        delay_dict[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'cell_rise' not in delay_dict[cell][pin]['case_'+timingth.split('_')[1]]:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]].update({'cell_rise':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_cell_ri:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]]['cell_rise'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 cell_fall의 경우가 있을 경우
                            if 'cell_fall_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_cell_fall in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_fall'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/cell_fall/'+txt_cell_fall,'r') as fw:
                                        temp_cell_fa=fw.readlines()
                                    fw.close()
                                    
                                    if 'case_'+timingth.split('_')[1] not in delay_dict[cell][pin]:
                                        delay_dict[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'cell_fall' not in delay_dict[cell][pin]['case_'+timingth.split('_')[1]]:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]].update({'cell_fall':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_cell_fa:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]]['cell_fall'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 rise_transition의 경우가 있을 경우
                            if 'rise_transition_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_rise_tr in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/rise_transition'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/rise_transition/'+txt_rise_tr,'r') as fw:
                                        temp_rise_tr=fw.readlines()
                                    fw.close()
                                                                        
                                    if 'case_'+timingth.split('_')[1] not in delay_dict[cell][pin]:
                                        delay_dict[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'rise_transition' not in delay_dict[cell][pin]['case_'+timingth.split('_')[1]]:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]].update({'rise_transition':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_rise_tr:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]]['rise_transition'].append(ivalue.replace('\n',''))

                            #### 해당 pin에 fall_transition의 경우가 있을 경우
                            if 'fall_transition_index.json' in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth):
                                for txt_fall_tr in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/fall_transition'):
                                    with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth+'/fall_transition/'+txt_fall_tr,'r') as fw:
                                        temp_fall_tr=fw.readlines()
                                    fw.close()
                                                                        
                                    if 'case_'+timingth.split('_')[1] not in delay_dict[cell][pin]:
                                        delay_dict[cell][pin].update({'case_'+timingth.split('_')[1]:dict()})
                                    if 'fall_transition' not in delay_dict[cell][pin]['case_'+timingth.split('_')[1]]:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]].update({'fall_transition':list()})
                                    
                                    ####해당 문자열을 다 저장한다.
                                    for ivalue in temp_fall_tr:
                                        delay_dict[cell][pin]['case_'+timingth.split('_')[1]]['fall_transition'].append(ivalue.replace('\n',''))
                            
                            #### timing의 특성이 있을 경우, 해당 timing의 조건을 파악한다. (related_pin과 timing_sense)
                            for key_of_timing in delay_dict[cell][pin]:
                                if key_of_timing=='direction':
                                    continue
                                with open(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/timing_'+key_of_timing.split('_')[1]+'/timing_info.json','r') as fw:
                                    temp_case_info=json.load(fw)
                                fw.close()

                                delay_dict[cell][pin][key_of_timing].update({'timing_sense':temp_case_info['timing_sense']})
                                delay_dict[cell][pin][key_of_timing].update({'related_pin':temp_case_info['related_pin']})

                                if 'timing_type' in temp_case_info:
                                    delay_dict[cell][pin][key_of_timing].update({'timing_type':temp_case_info['timing_type']})


    #### parsing한 lib파일의 파일명과 같은 디렉토리에 lib_dict_for_nldm_delay_v1.json으로 저장
    with open(location_of_lib+'/lib_dict_for_nldm_delay_v1.json','w') as fw:
        json.dump(delay_dict,fw,indent=4)
    return 0





def get_lib_info_for_delay_v2(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    with open(location_of_lib+'/lib_dict_for_nldm_delay_v1.json','r') as fw:
        nldm_v1=json.load(fw)
    fw.close()



    return 0
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################


def get_one_info(target_address,target_o_info,target_n_info,keyword):
    target_directory=str()
    #### target_directory : lib 파일 혹은 txt파일과 이름이 같은 디렉토리
    if '.lib' in target_address:
        target_directory=target_address.split('.lib')[0]
    elif '.txt' in target_address:
        target_directory=target_address.split('.txt')[0]

    
    info_dict=dict()
    previous_etc_start_idx=list()
    previous_etc_end_idx=list()
    

    #### parsing할 text 혹은 lib 파일 : address
    with open(target_address,'r') as fw:
        lines=fw.readlines()
    fw.close()

    for index_group in os.listdir(target_directory):
        if index_group.endswith('_index.json'):
            temp_id=index_group.split('_index.json')[0]

            with open(target_directory+'/'+index_group,'r') as fw:
                temp_dict=json.load(fw)
            fw.close()
            #### temp_etc_start_idx와 temp_etc_end_idx에 해당 구간의 시작과 끝을 저장
            temp_etc_start_idx=temp_dict[temp_id+'_start_idx']
            temp_etc_end_idx=temp_dict[temp_id+'_end_idx']

            #### parsing한 다른 keyword들과의 합집합으로 각각 start와 end끼리 합쳐서 previous_etc_start_idx와 previous_etc_end_idx에 저장
            previous_etc_start_idx.extend(temp_etc_start_idx)
            previous_etc_end_idx.extend(temp_etc_end_idx)

    previous_etc_start_idx.sort()
    previous_etc_end_idx.sort()

    other_lines=list()
    checking_idx=-1
    for idx in range(len(lines)):
        #### parsing_keyword의 parsing 이전에 parsing한 다른 구간의 특성들이 있을경우
        if len(previous_etc_start_idx)!=0:
            check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
            checking_idx=check_out[1]
            #### 해당 idx가 다른 특성의 구간 내에 있을 경우
            if check_out[0]=='not_pass':
                continue
        
        #### 해당 idx가 다른 특성의 구간 외에 있을 경우
        other_lines.append(lines[idx])

    #### real_lines에는 other_lines에 있는 공백과 주석을 제거한 문자열의 집합이다.
    real_lines=get_lines_uncomment(other_lines)
    temp_lines=list()
    for idx in range(len(real_lines)):
        bre=''
        #### real_line에 idx번째 문자열이 target_o_info 안의 요소일 때
        for kvalue in target_o_info:
            if real_lines[idx].strip().startswith(kvalue) and real_lines[idx].split(kvalue)[1].strip().startswith(':'):
                info_dict.update({kvalue:real_lines[idx].split(':')[1].split(';')[0].strip()})
                bre='con'
        
        #### real_line에 idx번째 문자열이 target_n_info 안의 요소일 때
        for kvalue in target_n_info:
            if real_lines[idx].strip().startswith(kvalue) and real_lines[idx].split(kvalue)[1].strip().startswith('('):
                if kvalue not in info_dict:
                    info_dict.update({kvalue:list()})
                info_dict[kvalue].append(real_lines[idx].split(kvalue)[1].split('(')[1].split(')')[0].strip())
                bre='con'
        if bre=='con':
            continue

        #### real_lines에 idx번째 문자열이 '}'일 때
        if real_lines[idx].strip().startswith('}'):
            continue
        #### real_lines에 idx번째 문자열이 해당 keyword가 시작하는 문장일 경우 continue로 처리한다.
        if real_lines[idx].strip().startswith(keyword) and real_lines[idx].split(keyword)[1].strip().startswith('('):
            continue

        #### 처리되지 않은 문자열은 temp_lines에 저장
        temp_lines.append(real_lines[idx])
    
    ### temp_lines에 요소가 하나라도 있다면 parsing의 과정에서 놓친 특성이 있다.
    if len(temp_lines)!=0:
        for idx in range(len(temp_lines)):
            print(temp_lines[idx].replace('\n',''))
        print()
        #### 놓친 특성이 있을 경우 'MISSING_ATTRIBUTES'를 화면에 출력
        print('MISSING_ATTRIBUTES')
    

    return info_dict






def txt_index_start_and_end(target_text,target_directory,checking_group):
    #### parsing할 text 혹은 lib 파일 : target_text
    with open(target_text,'r') as fw:
        lines=fw.readlines()
    fw.close()

    #### checking_group에는 parsing할 대상인 파일의 구간을 가지는 특성들의 집합이다.
    #### parsing_keyword : 현재 반복문에서 parsing할 keyword
    for parsing_keyword in checking_group:
        previous_etc_start_idx=list()
        previous_etc_end_idx=list()
        
        #### previous_keyword : parsing_keyword의 parsing 전에 이미 parsing한 특성
        for previous_keyword in checking_group:
            temp_etc_start_idx=list()
            temp_etc_end_idx=list()
            if previous_keyword==parsing_keyword:
                break

            #### location_of_temp: previous_keyword의 구간이 저장된 json파일의 위치
            location_of_temp=target_directory+'/'+previous_keyword+'_index.json'
            if previous_keyword+'_index.json' in os.listdir(target_directory):
                
                with open(location_of_temp,'r') as fw:
                    temp_dict=json.load(fw)
                fw.close()
                #### temp_etc_start_idx와 temp_etc_end_idx에 해당 구간의 시작과 끝을 저장
                temp_etc_start_idx=temp_dict[previous_keyword+'_start_idx']
                temp_etc_end_idx=temp_dict[previous_keyword+'_end_idx']

                #### parsing한 다른 keyword들과의 합집합으로 각각 start와 end끼리 합쳐서 previous_etc_start_idx와 previous_etc_end_idx에 저장
                previous_etc_start_idx.extend(temp_etc_start_idx)
                previous_etc_end_idx.extend(temp_etc_end_idx)

        #### previous_etc_start_idx과 previous_etc_end_idx를 오름차순으로 정렬
        previous_etc_start_idx.sort()
        previous_etc_end_idx.sort()

        start_idx_list=list()
        end_idx_list=list()

        checking_idx=-1
        for idx in range(len(lines)):
            #### parsing_keyword의 parsing 이전에 parsing한 다른 구간의 특성들이 있을경우
            if len(previous_etc_start_idx)!=0:
                check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
                checking_idx=check_out[1]
                #### 해당 idx가 다른 특성의 구간 내에 있을 경우
                if check_out[0]=='not_pass':
                    continue

            #### 해당 idx가 다른 특성의 구간 외에 있을 경우
            if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
                start_idx_list.append(idx) #### n개의 parsing_keyword가 시작하는 문장의 인덱스 번호
                end_idx_list.append(counting_function(idx,lines)) #### n개의 parsing_keyword가 끝나는 문장의 인덱스 번호

        #### parsing_keyword에 대한 정보가 있을 경우 json파일로 해당 특성의 index들을 저장
        if len(start_idx_list)!=0:
            idx_info={parsing_keyword+'_start_idx':start_idx_list,parsing_keyword+'_end_idx':end_idx_list}
            
            with open(target_directory+'/'+parsing_keyword+'_index.json','w') as fw:
                json.dump(idx_info,fw,indent=4)
            fw.close()

    return 0


################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################



def get_sub_txt(previous_txt_location,current_keyword,text_keyword):
    #### previous_txt_location : text keyword의 내용을 포함한, parsing의 대상이 되는 파일
    with open(previous_txt_location,'r') as fw:
        lines=fw.readlines()
    fw.close()
    #### current_keyword+'_index.json' : previous_txt_location에서 text_keyword에 대한 index가 저장된 파일
    with open(current_keyword+'_index.json','r') as fw:
        temp_dict=json.load(fw)
    fw.close()

    start_idx=temp_dict[text_keyword+'_start_idx']
    end_idx=temp_dict[text_keyword+'_end_idx']

    #### 해당 keyword에 대한 하위 디렉토리 생성
    #### temp_location 은 해당 lib 파일 혹은 txt파일의 위치
    temp_location=str()
    if previous_txt_location.endswith('.txt'):
        temp_location=previous_txt_location.split('.txt')[0]
    elif previous_txt_location.endswith('.lib'):
        temp_location=previous_txt_location.split('.lib')[0]

    if text_keyword not in os.listdir(temp_location):
        os.mkdir(current_keyword)

    for idx in range(len(start_idx)):
        #### 저장할 txt파일의 파일명 : name_directory
        name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
        if name_directory=='':
            name_directory=text_keyword+'_'+str(idx)
    
        #### 구간의 내용을 해당 keyword의 디렉토리 안에 txt로 저장
        for jdx in range(end_idx[idx]-start_idx[idx]+1):
            if jdx==0:
                with open(current_keyword+'/'+name_directory+'.txt','w')as fw:
                    fw.write(lines[start_idx[idx]+jdx])
                fw.close()
            else:
                with open(current_keyword+'/'+name_directory+'.txt','a')as fw:
                    fw.write(lines[start_idx[idx]+jdx])
                fw.close()

    return 0


#### 상위 디렉토리의 이름을 받으면 해당 keyword에 대한 하위 디렉토리를 만드는 함수
def get_directory_of_the_keyword(upper_directory):
    #### 상위 디렉토리에서 txt파일의 파일명이 해당 상위 디렉토리 안에 하위디렉토리로 없을 경우, 하위 디렉토리를 만든다.
    for ivalue in os.listdir(upper_directory):
        if ivalue.endswith('.txt'):
            if ivalue.split('.txt')[0] not in os.listdir(upper_directory):
                os.mkdir(upper_directory+ivalue.split('.txt')[0])

    return 0


#### nldm_table이 시작하는 인덱스와 끝나는 인덱스를 참고하여, template_id와 index및 value를 반환하는 함수
def get_temporary_nldm_table(start_list,end_list,lines,keyword): #### keyword: cell_rise, rise_transition, cell_fall, fall_transition 이 있다.
    #### 하나의 case에 같은 keyword를 갖는 nldm_table이 여러 개 있을 경우, warning 표시
    if len(start_list)!=1:
        print('Warning : There are nldm_tables in a case of the output_pin')

    temp_id=str()
    index_and_values=['']
    for qdx in range(end_list[0]-start_list[0]+1):
        #### 해당 keyword가 시작하는 문장의 '()'안에 template_id가 있다.
        if lines[start_list[0]+qdx].replace('\n','').strip().startswith(keyword):
            temp_id=lines[start_list[0]+qdx].replace('\n','').split('(')[1].split(')')[0].strip()
            continue
        elif lines[start_list[0]+qdx].replace('\n','').strip().startswith('}'):
            continue
        #### 매 문장마다 index_and_values의 마지막 원소에 해당 문장을 붙인다.
        #### 문장의 끝이 ';'로 끝날 경우 index_and_values에 str()인 원소 추가
        index_and_values[-1]=index_and_values[-1]+lines[start_list[0]+qdx].replace('\n','').strip()
        if lines[start_list[0]+qdx].replace('\n','').endswith(';'):
            index_and_values.append('')
    #### index_and_values의 마지막 원소는 str()이므로 제거한다.
    del index_and_values[-1]

    return [temp_id,index_and_values]


#### '{}'으로 나뉘어진 문단의 마지막 문장의 인덱스 번호를 반환하는 함수
def counting_function(start_number,lines):
    left=int()
    right=int()
    #### 첫줄에 괄호가 몇개 있는지 탐색
    if  '{' in lines[start_number]:
        left=left+1
    if  '}' in lines[start_number]:
        right=right+1

    #### n 번째 줄에서 왼괄호의 총 수와 오른괄호의 총 수가 같을 경우 n을 반환
    for idx in range(len(lines)-start_number-1):
        if '{' in lines[start_number+idx+1]:
            left=left+1
        if '}' in lines[start_number+idx+1]:
            right=right+1
        if left==right:
            return start_number+idx+1


#### starts_list와 ends_list에 저장된 n번째 구간안에 current가 있을 경우 not_pass를 반환, 그렇지 않은 경우 pass를 반환
#### n번째 구간은 checking_idx로 본다. (starts_list의 첫번째 인덱스보다 더 앞의 구간인 초기 구간에서의 checking_idx는 -1로 본다.)
def except_lines(starts_list,ends_list,current,checking_idx):
    #### 초기 상태 : current가 첫번째 구간의 starts 인덱스보다 더 작거나 같을 경우
    #### 첫번째 구간의 starts 인덱스 : starts_list[0]
    if checking_idx==-1:
        if current<starts_list[0]:
            return ['pass',checking_idx]
        else:
            return ['not_pass',checking_idx+1]

    else:
        #### 마지막 구간의 end_list 인덱스보다 더 클 경우
        if checking_idx==len(starts_list) and current>ends_list[-1]:
                return ['pass',checking_idx]

        #### checking_idx번째 구간에서의 경우
        else:
            #### current가 checking_idx번째 구간 사이에 있을 경우
            if current>=starts_list[checking_idx] and current<ends_list[checking_idx]:
                return ['not_pass',checking_idx]
            elif current==ends_list[checking_idx]:
                return ['not_pass',checking_idx+1]
            
            #### current가 starts_list의 checking_idx번째 인덱스와 ends_list checking_idx-1번째 인덱스 사이에 있을 경우
            elif current<starts_list[checking_idx] and current>ends_list[checking_idx-1]:
                return ['pass',checking_idx]


#### 주석이 있는 lines문자열의 집합 중 해당 원소들에 주석문구를 지운 문자열을 list로 저장
def get_lines_uncomment(with_comment_lines):
    real_lines=list()
    new_lines=['']
    for idx in range(len(with_comment_lines)):
        #### with_comment_lines에 주석으로 처리될 때마다 new_lines에 저장
        new_lines[-1]=new_lines[-1]+'\n'+with_comment_lines[idx].replace('\n','')
        if '*/' in with_comment_lines[idx]:
            new_lines.append('')

    for idx in range(len(new_lines)):
        #### 매 new_line에 있는 원소에 주석으로 처리된 부분을 제거하고 real_lines에 해당 문장 추가
        if '*/' in new_lines[idx]:
            new_lines[idx]=new_lines[idx].split('/*')[0]+new_lines[idx].split('*/')[1]
        if new_lines[idx].strip()=='':
            continue
        for kdx in range(len(new_lines[idx].split('\n'))):
            #### 문장에 내용이 없는 빈 문장일 경우 continue
            if new_lines[idx].split('\n')[kdx].strip()=='':
                continue
            real_lines.append(new_lines[idx].split('\n')[kdx])

    return real_lines


if __name__=="__main__":

    #checking='example1_slow.lib'
    #checking='example1_typ.lib'
    #checking='example1_fast.lib'
    #checking='superblue1_Late.lib'
    #checking='superblue1_Early.lib'
    #checking='superblue3_Late.lib'
    #checking='superblue3_Early.lib'
    #checking='superblue4_Late.lib'
    #checking='superblue4_Early.lib'
    #checking='superblue5_Late.lib'
    #checking='superblue5_Early.lib'
    #checking='superblue7_Late.lib'    
    #checking='superblue7_Early.lib'
    #checking='superblue10_Late.lib'
    #checking='superblue10_Early.lib'
    #checking='superblue16_Late.lib'
    ##checking='superblue16_Early.lib'
    #checking='superblue18_Late.lib'    
    #checking='superblue18_Early.lib'
    #checking='tcbn40lpbwp12tm1ptc_ccs.lib'
    #checking='tcbn40lpbwp12tm1plvttc_ccs.lib'
    #checking='TS1N40LPB2048X32M4FWBA_tt1p1v25c.lib'
    #checking='TS1N40LPB4096X32M8MWBA_tt1p1v25c.lib',
    #checking='TS1N40LPB1024X128M4FWBA_tt1p1v25c.lib'
    #checking='TS1N40LPB2048X36M4FWBA_tt1p1v25c.lib',
    #checking='TS1N40LPB1024X32M4FWBA_tt1p1v25c.lib'
    #checking='TS1N40LPB256X22M4FWBA_tt1p1v25c.lib',
    #checking='TS1N40LPB512X23M4FWBA_tt1p1v25c.lib'
    #checking='TS1N40LPB256X12M4FWBA_tt1p1v25c.lib',
    #checking='TS1N40LPB512X32M4FWBA_tt1p1v25c.lib'
    #checking='TS1N40LPB128X63M4FWBA_tt1p1v25c.lib',
    #checking='TS1N40LPB256X23M4FWBA_tt1p1v25c.lib'    

    checking=sys.argv[2]


    lib_address='../../data/test_LIB_groups/'
    lib_address='../../data/LIB_groups/'
    lib_address=lib_address+checking
    #print(checking)
    #print('start')
    #start=time.time()

    #### 초기 lib파일에 대한 디렉토리 생성
    if sys.argv[1]=='0':
        get_lib_directory(lib_address)

    #### 구간 정보 뽑기 : ['cell','lu_table_template','type','operating_conditions','power_lut_template','output_current_template','pg_current_template',
                        # 'wire_load','wire_load_selection','input_voltage','output_voltage']
    elif sys.argv[1]=='1':
        get_lib_idx(lib_address)
    
    #### 원하는 구간 정보를 txt로 저장 : cell
    elif sys.argv[1]=='2':
        get_cell_txt(lib_address)
    









    elif sys.argv[1]=='3':
        get_lu_table_template_txt(lib_address)

    elif sys.argv[1]=='4':
        get_lu_table_template_directory(lib_address)

    elif sys.argv[1]=='5':
        get_one_sentence_info_lu_table_template(lib_address)
    
    elif sys.argv[1]=='6':
        get_type_txt(lib_address)
    
    elif sys.argv[1]=='7':
        get_type_directory(lib_address)
    
    elif sys.argv[1]=='8':
        get_one_sentence_info_type(lib_address)










    #### cell에 대한 디렉토리 생성
    elif sys.argv[1]=='9':
        get_cell_directory(lib_address)
    
    #### 구간정보 parsing : ['test_cell', 'leakage_current', 'intrinsic_parasitic',
                        # 'pg_pin', 'statetable', 'leakage_power', 'dynamic_current', 'bus', 'memory',
                        #   'pin', 'ff', 'latch']
    elif sys.argv[1]=='10':
        get_cell_idx(lib_address)

    elif sys.argv[1]=='11':
        get_bus_txt(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : pin
    elif sys.argv[1]=='12':
        get_pin_txt(lib_address)

    elif sys.argv[1]=='13':
        copy_text_pin_from_bus(lib_address)










    #### pin에 대한 디렉토리 생성
    elif sys.argv[1]=='14':
        get_pin_directory(lib_address)

    #### 구간정보 parsing : ['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage']
    elif sys.argv[1]=='15':
        get_pin_idx(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : timing
    elif sys.argv[1]=='16':
        get_timing_txt(lib_address)
    









    #### timing에 대한 디렉토리 생성
    elif sys.argv[1]=='17':
        get_timing_directory(lib_address)

    #### 구간정보 parsing : ['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage']
    elif sys.argv[1]=='18':
        get_timing_idx(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : cell_rise, cell_fall, rise_transition, fall_transition
    elif sys.argv[1]=='19':
        get_cell_rise_txt(lib_address)
        get_cell_fall_txt(lib_address)
        get_rise_transition_txt(lib_address)
        get_fall_transition_txt(lib_address)

    elif sys.argv[1]=='20':
        get_one_sentence_info_lib(lib_address)
    
    elif sys.argv[1]=='21':
        get_one_sentence_info_cell(lib_address)

    elif sys.argv[1]=='22':
        get_one_sentence_info_pin(lib_address)

    elif sys.argv[1]=='23':
        get_one_sentence_info_timing(lib_address)










    elif sys.argv[1]=='24':
        get_lib_info_for_delay_v1(lib_address)

    elif sys.argv[1]=='25':
        get_lib_info_for_delay_v2(lib_address)





    #print('end',time.time()-start)
    #print()