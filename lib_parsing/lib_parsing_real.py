import json
import os
import copy
import time

import sys




def checking_lib(address):
    with open(address,'r') as fw:
        lines=fw.readlines()
    fw.close()

    temp_lines=[]
    for idx in range(len(lines)):
        temp_lines.append(lines[idx])
        if lines[idx].strip().startswith('cell') and lines[idx].split('cell')[1].strip().startswith('('):
            break

    checking_list=['lu_table_template','type','operating_conditions','power_lut_template','output_current_template','pg_current_template','wire_load','wire_load_selection','input_voltage','output_voltage']
    real_lines=get_lines_uncomment(temp_lines)

    total_etc_start=list()
    total_etc_end=list()
    for keyword in checking_list:
        etc_start_idx=list()
        etc_end_idx=list()
        for idx in range(len(real_lines)):
            if real_lines[idx].strip().startswith(keyword) and real_lines[idx].split(keyword)[1].strip().startswith('('):
                etc_start_idx.append(idx)
                etc_end_idx.append(counting_function(idx,real_lines))
        total_etc_start.extend(etc_start_idx)
        total_etc_end.extend(etc_end_idx)
    total_etc_start.sort()
    total_etc_end.sort()


    one_line_keyword=['delay_model', 'time_unit', 'voltage_unit', 'current_unit', 'leakage_power_unit', 'pulling_resistance_unit', \
        'default_fanout_load', 'default_inout_pin_cap', 'default_input_pin_cap', 'default_output_pin_cap', \
        'slew_lower_threshold_pct_rise', 'slew_lower_threshold_pct_fall', 'slew_upper_threshold_pct_rise', 'slew_upper_threshold_pct_fall', \
        'input_threshold_pct_rise', 'input_threshold_pct_fall', 'output_threshold_pct_rise', 'output_threshold_pct_fall', \
        'nom_voltage', 'nom_temperature', 'nom_process', 'default_operating_conditions',\
        'date','revision','comment','in_place_swap_mode', 'slew_derate_from_library', \
        'default_leakage_power_density', 'default_cell_leakage_power', 'default_max_transition', 'default_wire_load',\
        'simulation', 'default_max_fanout', \
        'k_volt_cell_leakage_power', 'k_temp_cell_leakage_power', 'k_process_cell_leakage_power', 'k_volt_internal_power', 'k_temp_internal_power', 'k_process_internal_power',\
        'default_wire_load_selection', 'default_wire_load_mode']
    
    one_info=['technology','library_features','capacitive_load_unit','voltage_map','define','define_cell_area']

    else_list=list()
    checking_idx=-1
    for kdx in range(len(real_lines)):
        #### kdx가 get_frist_etc_list에서 parsing한 내용의 인덱스에 포함되면 continue로 예외처리한다.
        if len(total_etc_start)!=0:
            check_out=except_lines(total_etc_start,total_etc_end,kdx,checking_idx)
            checking_idx=check_out[1]
            if check_out[0]=='not_pass':
                continue

            if ':' in real_lines[kdx]:
                if real_lines[kdx].split(':')[0].strip() in one_line_keyword:
                    continue

            che=''
            if real_lines[kdx].replace('\n','').endswith(';'):
                for jvalue in one_info:
                    if real_lines[kdx].strip().startswith(jvalue) and real_lines[kdx].split(jvalue)[1].strip().startswith('('):
                        che='che'
                        break
            if che=='che':
                continue

            if real_lines[kdx].strip().startswith('library') and real_lines[kdx].split('library')[1].strip().startswith('('):
                continue
            if real_lines[kdx].strip().startswith('cell') and real_lines[kdx].split('cell')[1].strip().startswith('('):
                continue
            print(real_lines[kdx].replace('\n',''))

    return 0





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

    target_text=address

    #### parsing할 파일 : where_the_txt
    where_the_txt=address

    #### parsing할 대상이 되는 파일을 가져온다.
    with open(where_the_txt,'r') as fw:
        lines=fw.readlines()
    fw.close()

    target_directory=target_text.split('.txt')[0]
    for parsing_keyword in checking_group:
        previous_etc_start_idx=list()
        previous_etc_end_idx=list()
        for previous_keyword in checking_group:
            temp_etc_start_idx=list()
            temp_etc_end_idx=list()
            if previous_keyword==parsing_keyword:
                break
            location_of_temp=location_of_lib+'/'+previous_keyword+'_index.json'
            with open(location_of_temp,'r') as fw:
                temp_dict=json.load(fw)
            fw.close()
            temp_etc_start_idx=temp_dict[previous_keyword+'_start_idx']
            temp_etc_end_idx=temp_dict[previous_keyword+'_end_idx']

            previous_etc_start_idx.extend(temp_etc_start_idx)
            previous_etc_end_idx.extend(temp_etc_end_idx)
        previous_etc_start_idx.sort()
        previous_etc_end_idx.sort()


        #### 구간에 대한 keyword가 시작하는 인덱스와 끝나는 인덱스에 대한 정보를 저장할 json파일의 위치 : location_of_idx
        location_of_idx=location_of_lib+'/'+parsing_keyword+'_index.json'

    
        start_idx_list=list()
        end_idx_list=list()
        
        checking_idx=-1


        for idx in range(len(lines)):
            if len(previous_etc_start_idx)!=0:
                check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
                checking_idx=check_out[1]
                if check_out[0]=='not_pass':
                    continue
            #### cell의 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
            if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
                start_idx_list.append(idx) #### n개의 cell의 시작하는 문장의 인덱스 번호
                end_idx_list.append(counting_function(idx,lines)) #### n개의 cell의 끝나는 문장의 인덱스 번호
            
        #### cell이외의 내용을 parsing할 때 참고할 각 cell들의 시작 인덱스 정보를 저장
        idx_info={parsing_keyword+'_start_idx':start_idx_list,parsing_keyword+'_end_idx':end_idx_list}
        with open(location_of_idx,'w') as fw:
            json.dump(idx_info,fw,indent=4)
        fw.close()

    return 0



#### lib 파일에서 cell 이름별로 lib을 나누어 각 cell 디렉토리에 txt파일로 저장.
def get_cell_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    text_keyword='cell'
    previous_txt_location=address
    upper_directory_of_keyword=location_of_lib+'/'

    with open(upper_directory_of_keyword+text_keyword+'_index.json','r') as fw:
        temp_dict=json.load(fw)
    fw.close()

    start_idx=temp_dict[text_keyword+'_start_idx']
    end_idx=temp_dict[text_keyword+'_end_idx']

    with open(previous_txt_location,'r') as fw:
        lines=fw.readlines()
    fw.close()

    #### 해당 keyword에 대한 하위 디렉토리 생성
    if text_keyword not in os.listdir(upper_directory_of_keyword):
        os.mkdir(upper_directory_of_keyword+text_keyword)

    for idx in range(len(start_idx)):
        #### 저장할 txt파일의 파일명 : name_directory
        name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
        if name_directory=='':
            name_directory=text_keyword+'_'+str(idx)
    
        #### 구간의 내용을 해당 keyword의 디렉토리 안에 txt로 저장
        for jdx in range(end_idx[idx]-start_idx[idx]+1):
            if jdx==0:
                with open(upper_directory_of_keyword+text_keyword+'/'+name_directory+'.txt','w')as fw:
                    fw.write(lines[start_idx[idx]+jdx])
                fw.close()
            else:
                with open(upper_directory_of_keyword+text_keyword+'/'+name_directory+'.txt','a')as fw:
                    fw.write(lines[start_idx[idx]+jdx])
                fw.close()

    return 0





#### parsing한 각각의 cell의 내용에 대한 하위 디렉토리 생성
def get_cell_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='cell'

    for cell_name in os.listdir(location_of_lib+'/'+first_keyword):
        new_directory_name=cell_name.split('.txt')[0]

        if new_directory_name not in os.listdir(location_of_lib+'/'+first_keyword):
            os.mkdir(location_of_lib+'/'+first_keyword+'/'+new_directory_name)

    return 0





def get_cell_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['test_cell', 'leakage_current', 'intrinsic_parasitic',\
        'pg_pin', 'statetable', 'leakage_power', 'dynamic_current', 'bus', 'memory',\
        'pin', 'ff', 'latch']
    
    for cell_text in os.listdir(location_of_lib+'/cell'):

        if not cell_text.endswith('.txt'):
            continue

        target_text=location_of_lib+'/cell/'+cell_text
        target_directory=target_text.split('.txt')[0]

        with open(target_text,'r') as fw:
            lines=fw.readlines()
        fw.close()

        for parsing_keyword in checking_group:
            previous_etc_start_idx=list()
            previous_etc_end_idx=list()
            for previous_keyword in checking_group:
                temp_etc_start_idx=list()
                temp_etc_end_idx=list()
                if previous_keyword==parsing_keyword:
                    break
                
                location_of_temp=target_directory+'/'+previous_keyword+'_index.json'
                if previous_keyword+'_index.json' in os.listdir(target_directory):
                    
                    with open(location_of_temp,'r') as fw:
                        temp_dict=json.load(fw)
                    fw.close()
                    temp_etc_start_idx=temp_dict[previous_keyword+'_start_idx']
                    temp_etc_end_idx=temp_dict[previous_keyword+'_end_idx']

                    previous_etc_start_idx.extend(temp_etc_start_idx)
                    previous_etc_end_idx.extend(temp_etc_end_idx)

            previous_etc_start_idx.sort()
            previous_etc_end_idx.sort()

            start_idx_list=list()
            end_idx_list=list()

            checking_idx=-1
            for idx in range(len(lines)):
                if len(previous_etc_start_idx)!=0:
                    check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
                    checking_idx=check_out[1]
                    if check_out[0]=='not_pass':
                        continue
                if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
                    start_idx_list.append(idx) #### n개의 parsing_keyword가 시작하는 문장의 인덱스 번호
                    end_idx_list.append(counting_function(idx,lines)) #### n개의 parsing_keyword가 끝나는 문장의 인덱스 번호

            if len(start_idx_list)!=0:
                idx_info={parsing_keyword+'_start_idx':start_idx_list,parsing_keyword+'_end_idx':end_idx_list}

                with open(target_directory+'/'+parsing_keyword+'_index.json','w') as fw:
                    json.dump(idx_info,fw,indent=4)
                fw.close()

    return 0






#### lib 파일에서 cell의 내용 중, pin에 대한 정보를 parsing하여 pin 디렉토리 생성 후, pin_name.txt파일로 저장
def get_pin_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'
    text_keyword='pin'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt') or cell.endswith('.txt'):
            continue
        
        if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell):
            continue
        

        previous_txt_location=location_of_cell+cell+'.txt'
        with open(previous_txt_location,'r') as fw:
            lines=fw.readlines()
        fw.close()

        with open(location_of_cell+cell+'/'+text_keyword+'_index.json','r') as fw:
            temp_dict=json.load(fw)
        fw.close()

        start_idx=temp_dict[text_keyword+'_start_idx']
        end_idx=temp_dict[text_keyword+'_end_idx']

        if text_keyword not in os.listdir(location_of_cell+cell+'/'):
            os.mkdir(location_of_cell+cell+'/'+text_keyword)
        
        for idx in range(len(start_idx)):
            name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
            if name_directory=='':
                name_directory=text_keyword+'_'+str(idx)

            for jdx in range(end_idx[idx]-start_idx[idx]+1):
                if jdx==0:
                    with open(location_of_cell+cell+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                        fw.write(lines[start_idx[idx]+jdx])
                    fw.close()
                else:
                    with open(location_of_cell+cell+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                        fw.write(lines[start_idx[idx]+jdx])
                    fw.close()

    return 0






#### parsing한 각각의 pin의 내용에 대한 하위 디렉토리 생성
def get_pin_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='pin'

    for cell_name in os.listdir(location_of_lib+'/cell/'):
        if cell_name.endswith('.txt') or cell_name.endswith('.json'):
            continue
        
        if first_keyword+'_index.json' not in os.listdir(location_of_lib+'/cell/'+cell_name):
            continue

        for pin_name in os.listdir(location_of_lib+'/cell/'+cell_name+'/'+first_keyword):
            if pin_name.endswith('.txt'):
                will_new_directory=location_of_lib+'/cell/'+cell_name+'/'+first_keyword+'/'+pin_name.split('.txt')[0]
                if pin_name.split('.txt')[0] not in os.listdir(location_of_lib+'/cell/'+cell_name+'/'+first_keyword+'/'):
                    os.mkdir(will_new_directory)

    return 0




def get_pin_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage']
    
    for cell in os.listdir(location_of_lib+'/cell/'):

        if cell.endswith('.txt'):
            continue

        if 'pin' not in os.listdir(location_of_lib+'/cell/'+cell):
            continue
        
        for pin_txt in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
            if not pin_txt.endswith('.txt'):
                continue

            target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin_txt
            target_directory=target_text.split('.txt')[0]

            with open(target_text,'r') as fw:
                lines=fw.readlines()
            fw.close()

            for parsing_keyword in checking_group:
                previous_etc_start_idx=list()
                previous_etc_end_idx=list()
                for previous_keyword in checking_group:
                    temp_etc_start_idx=list()
                    temp_etc_end_idx=list()
                    if previous_keyword==parsing_keyword:
                        break
                    
                    location_of_temp=target_directory+'/'+previous_keyword+'_index.json'
                    if previous_keyword+'_index.json' in os.listdir(target_directory):
                        
                        with open(location_of_temp,'r') as fw:
                            temp_dict=json.load(fw)
                        fw.close()
                        temp_etc_start_idx=temp_dict[previous_keyword+'_start_idx']
                        temp_etc_end_idx=temp_dict[previous_keyword+'_end_idx']

                        previous_etc_start_idx.extend(temp_etc_start_idx)
                        previous_etc_end_idx.extend(temp_etc_end_idx)

                previous_etc_start_idx.sort()
                previous_etc_end_idx.sort()

                start_idx_list=list()
                end_idx_list=list()

                checking_idx=-1
                for idx in range(len(lines)):
                    if len(previous_etc_start_idx)!=0:
                        check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
                        checking_idx=check_out[1]
                        if check_out[0]=='not_pass':
                            continue
                    if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
                        start_idx_list.append(idx) #### n개의 parsing_keyword가 시작하는 문장의 인덱스 번호
                        end_idx_list.append(counting_function(idx,lines)) #### n개의 parsing_keyword가 끝나는 문장의 인덱스 번호

                if len(start_idx_list)!=0:
                    idx_info={parsing_keyword+'_start_idx':start_idx_list,parsing_keyword+'_end_idx':end_idx_list}
                    
                    with open(target_directory+'/'+parsing_keyword+'_index.json','w') as fw:
                        json.dump(idx_info,fw,indent=4)
                    fw.close()

    return 0










def get_timing_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'

    text_keyword='timing'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt'):
            continue
        
        if 'pin_index.json' not in os.listdir(location_of_cell+cell):
            continue

        
        for pin_name in os.listdir(location_of_cell+cell+'/pin/'):
            if pin_name.endswith('.txt'):
                continue
        
            if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                continue

        
            previous_txt_location=location_of_cell+cell+'/pin/'+pin_name+'.txt'
            with open(previous_txt_location,'r') as fw:
                lines=fw.readlines()
            fw.close()

            with open(location_of_cell+cell+'/pin/'+pin_name+'/'+text_keyword+'_index.json','r') as fw:
                temp_dict=json.load(fw)
            fw.close()

            start_idx=temp_dict[text_keyword+'_start_idx']
            end_idx=temp_dict[text_keyword+'_end_idx']

            if text_keyword not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                os.mkdir(location_of_cell+cell+'/pin/'+pin_name+'/'+text_keyword)
            
            for idx in range(len(start_idx)):
                name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
                if name_directory=='':
                    name_directory=text_keyword+'_'+str(idx)

                for jdx in range(end_idx[idx]-start_idx[idx]+1):
                    if jdx==0:
                        with open(location_of_cell+cell+'/pin/'+pin_name+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                            fw.write(lines[start_idx[idx]+jdx])
                        fw.close()
                    else:
                        with open(location_of_cell+cell+'/pin/'+pin_name+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                            fw.write(lines[start_idx[idx]+jdx])
                        fw.close()

    return 0










#### parsing한 각각의 timing의 내용에 대한 하위 디렉토리 생성
def get_timing_directory(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    first_keyword='timing'

    for cell_name in os.listdir(location_of_lib+'/cell/'):
        if cell_name.endswith('.txt'):
            continue
        
        if 'pin_index.json' not in os.listdir(location_of_lib+'/cell/'+cell_name):
            continue

        for pin in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'):
            if pin.endswith('.txt'):
                continue

            if first_keyword+'_index.json' not in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'+pin):
                continue

            for timingth in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'+pin+'/timing/'):
                if timingth.endswith('.txt'):
                    continue
                if timingth.split('.txt')[0] not in os.listdir(location_of_lib+'/cell/'+cell_name+'/pin/'+pin+'/timing/'):
                    os.mkdir(location_of_lib+'/cell/'+cell_name+'/pin/'+pin+'/timing/'+timingth.split('.txt')[0])


    return 0






def get_timing_idx(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_group=['cell_rise','rise_transition','cell_fall','fall_transition','ccsn_first_stage','ccsn_last_stage',\
                    'output_current_rise','receiver_capacitance1_rise', 'receiver_capacitance2_rise',\
                    'output_current_fall','receiver_capacitance1_fall','receiver_capacitance2_fall',\
                    'rise_constraint','fall_constraint']
    
    for cell in os.listdir(location_of_lib+'/cell/'):

        if cell.endswith('.txt'):
            continue

        if 'pin' not in os.listdir(location_of_lib+'/cell/'+cell):
            continue
        
        for pin in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'):
            
            if pin.endswith('.txt'):
                continue
            
            if 'timing' not in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/'):
                continue

            for timingth in os.listdir(location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing'):
                if not timingth.endswith('.txt'):
                    continue

                target_text=location_of_lib+'/cell/'+cell+'/pin/'+pin+'/timing/'+timingth
                target_directory=target_text.split('.txt')[0]

                with open(target_text,'r') as fw:
                    lines=fw.readlines()
                fw.close()

                for parsing_keyword in checking_group:
                    previous_etc_start_idx=list()
                    previous_etc_end_idx=list()
                    for previous_keyword in checking_group:
                        temp_etc_start_idx=list()
                        temp_etc_end_idx=list()
                        if previous_keyword==parsing_keyword:
                            break
                        
                        location_of_temp=target_directory+'/'+previous_keyword+'_index.json'
                        if previous_keyword+'_index.json' in os.listdir(target_directory):
                            
                            with open(location_of_temp,'r') as fw:
                                temp_dict=json.load(fw)
                            fw.close()
                            temp_etc_start_idx=temp_dict[previous_keyword+'_start_idx']
                            temp_etc_end_idx=temp_dict[previous_keyword+'_end_idx']

                            previous_etc_start_idx.extend(temp_etc_start_idx)
                            previous_etc_end_idx.extend(temp_etc_end_idx)

                    previous_etc_start_idx.sort()
                    previous_etc_end_idx.sort()

                    start_idx_list=list()
                    end_idx_list=list()

                    checking_idx=-1
                    for idx in range(len(lines)):
                        if len(previous_etc_start_idx)!=0:
                            check_out=except_lines(previous_etc_start_idx,previous_etc_end_idx,idx,checking_idx)
                            checking_idx=check_out[1]
                            if check_out[0]=='not_pass':
                                continue
                        if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
                            start_idx_list.append(idx) #### n개의 parsing_keyword가 시작하는 문장의 인덱스 번호
                            end_idx_list.append(counting_function(idx,lines)) #### n개의 parsing_keyword가 끝나는 문장의 인덱스 번호

                    if len(start_idx_list)!=0:
                        idx_info={parsing_keyword+'_start_idx':start_idx_list,parsing_keyword+'_end_idx':end_idx_list}
                        
                        with open(target_directory+'/'+parsing_keyword+'_index.json','w') as fw:
                            json.dump(idx_info,fw,indent=4)
                        fw.close()

    return 0






def get_cell_rise_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'

    text_keyword='cell_rise'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt'):
            continue

        if 'pin_index.json' not in os.listdir(location_of_cell+cell):
            continue

        for pin_name in os.listdir(location_of_cell+cell+'/pin/'):
            if pin_name.endswith('.txt'):
                continue
        
            if 'timing_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                continue

            for timingth in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'):
                if timingth.endswith('.txt'):
                    continue
                if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth):
                    continue


                #print(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json')

        
                previous_txt_location=location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                with open(previous_txt_location,'r') as fw:
                    lines=fw.readlines()
                fw.close()

                with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json','r') as fw:
                    temp_dict=json.load(fw)
                fw.close()

                start_idx=temp_dict[text_keyword+'_start_idx']
                end_idx=temp_dict[text_keyword+'_end_idx']

                if text_keyword not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'):
                    os.mkdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword)
                
                for idx in range(len(start_idx)):
                    name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
                    if name_directory=='':
                        name_directory=text_keyword+'_'+str(idx)

                    for jdx in range(end_idx[idx]-start_idx[idx]+1):
                        if jdx==0:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()
                        else:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()

    return 0










def get_cell_fall_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'

    text_keyword='cell_fall'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt'):
            continue

        if 'pin_index.json' not in os.listdir(location_of_cell+cell):
            continue

        for pin_name in os.listdir(location_of_cell+cell+'/pin/'):
            if pin_name.endswith('.txt'):
                continue
        
            if 'timing_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                continue

            for timingth in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'):
                if timingth.endswith('.txt'):
                    continue
                if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth):
                    continue


                #print(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json')

        
                previous_txt_location=location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                with open(previous_txt_location,'r') as fw:
                    lines=fw.readlines()
                fw.close()

                with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json','r') as fw:
                    temp_dict=json.load(fw)
                fw.close()

                start_idx=temp_dict[text_keyword+'_start_idx']
                end_idx=temp_dict[text_keyword+'_end_idx']

                if text_keyword not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'):
                    os.mkdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword)
                
                for idx in range(len(start_idx)):
                    name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
                    if name_directory=='':
                        name_directory=text_keyword+'_'+str(idx)

                    for jdx in range(end_idx[idx]-start_idx[idx]+1):
                        if jdx==0:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()
                        else:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()

    return 0




def get_rise_transition_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'

    text_keyword='rise_transition'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt'):
            continue

        if 'pin_index.json' not in os.listdir(location_of_cell+cell):
            continue

        for pin_name in os.listdir(location_of_cell+cell+'/pin/'):
            if pin_name.endswith('.txt'):
                continue
        
            if 'timing_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                continue

            for timingth in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'):
                if timingth.endswith('.txt'):
                    continue
                if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth):
                    continue


                #print(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json')

        
                previous_txt_location=location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                with open(previous_txt_location,'r') as fw:
                    lines=fw.readlines()
                fw.close()

                with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json','r') as fw:
                    temp_dict=json.load(fw)
                fw.close()

                start_idx=temp_dict[text_keyword+'_start_idx']
                end_idx=temp_dict[text_keyword+'_end_idx']

                if text_keyword not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'):
                    os.mkdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword)
                
                for idx in range(len(start_idx)):
                    name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
                    if name_directory=='':
                        name_directory=text_keyword+'_'+str(idx)

                    for jdx in range(end_idx[idx]-start_idx[idx]+1):
                        if jdx==0:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()
                        else:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()

    return 0




def get_fall_transition_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_cell=address.split('.lib')[0]+'/cell/'

    text_keyword='fall_transition'
    for cell in (os.listdir(location_of_cell)):
        if cell.endswith('.txt'):
            continue

        if 'pin_index.json' not in os.listdir(location_of_cell+cell):
            continue

        for pin_name in os.listdir(location_of_cell+cell+'/pin/'):
            if pin_name.endswith('.txt'):
                continue
        
            if 'timing_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/'):
                continue

            for timingth in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'):
                if timingth.endswith('.txt'):
                    continue
                if text_keyword+'_index.json' not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth):
                    continue


                #print(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json')

        
                previous_txt_location=location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'.txt'
                with open(previous_txt_location,'r') as fw:
                    lines=fw.readlines()
                fw.close()

                with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'_index.json','r') as fw:
                    temp_dict=json.load(fw)
                fw.close()

                start_idx=temp_dict[text_keyword+'_start_idx']
                end_idx=temp_dict[text_keyword+'_end_idx']

                if text_keyword not in os.listdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'):
                    os.mkdir(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword)
                
                for idx in range(len(start_idx)):
                    name_directory=lines[start_idx[idx]].split(text_keyword)[1].split('(')[1].split(')')[0].strip()
                    if name_directory=='':
                        name_directory=text_keyword+'_'+str(idx)

                    for jdx in range(end_idx[idx]-start_idx[idx]+1):
                        if jdx==0:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','w')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()
                        else:
                            with open(location_of_cell+cell+'/pin/'+pin_name+'/timing/'+timingth+'/'+text_keyword+'/'+name_directory+'.txt','a')as fw:
                                fw.write(lines[start_idx[idx]+jdx])
                            fw.close()

    return 0



















################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################




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
    if sys.argv[1]=='999':
        checking_lib(lib_address)






    if checking=='tcbn40lpbwp12tm1plvttc_ccs.lib':
        print('tpgmlwns1!!!')



    #### 초기 lib파일에 대한 디렉토리 생성
    elif sys.argv[1]=='0':
        get_lib_directory(lib_address)

    #### 구간 정보 뽑기 : ['cell','lu_table_template','type','operating_conditions','power_lut_template','output_current_template','pg_current_template',
                        # 'wire_load','wire_load_selection','input_voltage','output_voltage']
    elif sys.argv[1]=='1':
        get_lib_idx(lib_address)
    
    #### 원하는 구간 정보를 txt로 저장 : cell
    elif sys.argv[1]=='2':
        get_cell_txt(lib_address)
    
    #### 구간 정보들 외의 정보들을 주석을 예외처리해서 first_info.json으로 저장
    ### if sys.argv[1]=='3':
    ###   get_cell_info_sentence(lib_address)










    #### cell에 대한 디렉토리 생성
    elif sys.argv[1]=='3':
        get_cell_directory(lib_address)
    
    #### 구간정보 parsing : ['test_cell', 'leakage_current', 'intrinsic_parasitic',
                        # 'pg_pin', 'statetable', 'leakage_power', 'dynamic_current', 'bus', 'memory',
                        #   'pin', 'ff', 'latch']
    elif sys.argv[1]=='4':
        get_cell_idx(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : pin
    elif sys.argv[1]=='5':
        get_pin_txt(lib_address)










    #### pin에 대한 디렉토리 생성
    elif sys.argv[1]=='6':
        get_pin_directory(lib_address)

    #### 구간정보 parsing : ['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage']
    elif sys.argv[1]=='7':
        get_pin_idx(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : timing
    elif sys.argv[1]=='8':
        get_timing_txt(lib_address)










    #### timing에 대한 디렉토리 생성
    elif sys.argv[1]=='9':
        get_timing_directory(lib_address)

    #### 구간정보 parsing : ['timing', 'internal_power', 'receiver_capacitance', 'ccsn_first_stage', 'ccsn_last_stage']
    elif sys.argv[1]=='10':
        get_timing_idx(lib_address)

    #### 원하는 구간 정보를 txt로 저장 : cell_rise, cell_fall, rise_transition, fall_transition
    elif sys.argv[1]=='11':
        get_cell_rise_txt(lib_address)
        get_cell_fall_txt(lib_address)
        get_rise_transition_txt(lib_address)
        get_fall_transition_txt(lib_address)


    #print('end',time.time()-start)
    #print()