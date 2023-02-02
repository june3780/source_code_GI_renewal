import json
import os
import copy
import time

import sys



#### lib 파일에서 cell 이름별로 파일을 나눈다.
def get_cell_list(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    parsing_keyword='cell'

    with open(address,'r') as fw:
        lines=fw.readlines()
    fw.close()
    
    cell_start_idx_list=list()
    cell_end_idx_list=list()
    for idx in range(len(lines)):
        #### cell의 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
        if lines[idx].strip().startswith(parsing_keyword) and lines[idx].split(parsing_keyword)[1].strip().startswith('('):
            cell_start_idx_list.append(idx) #### n개의 cell의 시작하는 문장의 인덱스 번호
            cell_end_idx_list.append(counting_function(idx,lines)) #### n개의 cell의 끝나는 문장의 인덱스 번호
    

    for idx in range(len(cell_start_idx_list)):
        #### n번째 cell의 내용을 가벼운 용량의 txt파일로 바꿔주어 pasing에 부담을 줄인다.
        #### cell_name : n번째 cell의 이름
        cell_name=lines[cell_start_idx_list[idx]].replace('\n','').split('cell')[1].split('(')[1].split(')')[0].strip()
        #### lib 파일이 위치한 디렉토리에 해당 파일과 이름이 같은 디렉토리 생성
        if address.split('/')[-1].split('.lib')[0] not in os.listdir(address.split(address.split('/')[-1])[0]):
            os.mkdir(location_of_lib)
        #### cell 마다 lib 디렉토리 안에 cell의 이름대로 디렉토리를 생성
        if cell_name not in os.listdir(location_of_lib):
            os.mkdir(location_of_lib+'/'+cell_name)
        
        #### cell의 내용들을 txt 파일로 각 cell의 디렉토리에 저장
        for kdx in range(cell_end_idx_list[idx]-cell_start_idx_list[idx]+1):
            if kdx==0:
                with open(location_of_lib+'/'+cell_name+'/cell.txt','w') as fw:
                    fw.write(lines[cell_start_idx_list[idx]+kdx])
                fw.close()
            else:
                with open(location_of_lib+'/'+cell_name+'/cell.txt','a') as fw:
                    fw.write(lines[cell_start_idx_list[idx]+kdx])
                fw.close()
        
    #### cell이외의 내용을 parsing할 때 참고할 각 cell들의 시작 인덱스 정보를 저장
    cell_info={'cell_start_idx':cell_start_idx_list,'cell_end_idx':cell_end_idx_list}
    with open(location_of_lib+'/cell_index.json','w') as fw:
        json.dump(cell_info,fw,indent=4)
    fw.close()

    return 0




#### 각 cell의 pin 내용을 parsing하기 전에 각 cell의 기타 정보들에 대한 인덱스를 저장
def get_frist_etc_list(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]

    #### pin 보다 먼저 확인해야할 다른 특성들 : checking_first
    checking_first=['leakage_current', 'intrinsic_parasitic', 'pg_pin', 'statetable', 'leakage_power', 'test_cell', 'dynamic_current', 'bus', 'memory']

    for jvalue in checking_first:
        checking_keyword=jvalue

        for ivalue in os.listdir(location_of_lib):
            #### cell에 대한 디렉토리만 접근한다.
            if ivalue.endswith('.json') or ivalue.endswith('.txt'):
                continue
            #### cell 이외의 정보가 들어있는 디렉토리인 lib_nickname+'_not_cell_info'는 continue로 처리
            if ivalue=='not_cell_info':
                continue

            #### 해당 cell의 cell.txt의 위치 : temp_cell_text_address
            temp_cell_text_address=location_of_lib+'/'+ivalue+'/cell.txt'
            with open(temp_cell_text_address,'r') as fw:
                lines=fw.readlines()
            fw.close()

            etc_start_idx_list=list()
            etc_end_idx_list=list()

            for kdx in range(len(lines)):
                #### cell의 각 특성에 대한 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
                if lines[kdx].replace('\n','').strip().startswith(checking_keyword) and lines[kdx].replace('\n','').split(checking_keyword)[1].strip().startswith('('):
                    etc_start_idx_list.append(kdx)
                    etc_end_idx_list.append(counting_function(kdx,lines))
            
            #### 해당 특성에 대한 내용이 있을 경우 해당 인덱스 번호들을 저장한다.
            if len(etc_start_idx_list)!=0:
                etc_info={checking_keyword+'_start_idx':etc_start_idx_list,checking_keyword+'_end_idx':etc_end_idx_list}
                with open(location_of_lib+'/'+ivalue+'/'+checking_keyword+'_index.json','w') as fw:
                    json.dump(etc_info,fw,indent=4)
                fw.close()

    return 0




#### 각 cell의 pin 내용을 parsing하고, 해당 정보들에 대한 인덱스를 저장
def get_second_etc_list(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]

    #### pin 보다 먼저 확인해야할 다른 특성들 : checking_first
    checking_first=['leakage_current', 'intrinsic_parasitic', 'pg_pin', 'statetable', 'leakage_power', 'test_cell', 'dynamic_current', 'bus', 'memory']
    #### pin과 같이 파악할 특성들 : checking_second
    checking_second=['pin', 'ff', 'latch']

    for jvalue in checking_second:
        checking_keyword=jvalue

        for ivalue in os.listdir(location_of_lib):
            #### cell에 대한 디렉토리만 접근한다.
            if ivalue.endswith('.json') or ivalue.endswith('.txt'):
                continue
            #### cell 이외의 정보가 들어있는 디렉토리인 'not_cell_info'는 continue로 처리
            if ivalue=='not_cell_info':
                continue

            #### 해당 cell의 cell.txt의 위치 : temp_cell_text_address
            temp_cell_text_address=location_of_lib+'/'+ivalue+'/cell.txt'
            with open(temp_cell_text_address,'r') as fw:
                lines=fw.readlines()
            fw.close()

            etc_start_idx_list=list()
            etc_end_idx_list=list()

            checking_other_start_idx=list()
            checking_other_end_idx=list()

            #### 먼저 parsing하였던 다른 특성들의 시작 인덱스와 마지막 인덱스를 각각 checking_other_start_idx과 checking_other_end_idx에 저장
            for kvalue in os.listdir(location_of_lib+'/'+ivalue):
                if kvalue.endswith('.json') and  kvalue!=checking_keyword+'_index.json' and kvalue.split('_index.json')[0] in checking_first:
                    with open(location_of_lib+'/'+ivalue+'/'+kvalue,'r') as fw:
                        temp_dict=json.load(fw)
                    fw.close()
                    checking_other_start_idx.extend(temp_dict[kvalue.split('_index.json')[0]+'_start_idx'])
                    checking_other_end_idx.extend(temp_dict[kvalue.split('_index.json')[0]+'_end_idx'])
            checking_other_start_idx.sort()
            checking_other_end_idx.sort()

            tt=int()
            checking_idx=-1
            for kdx in range(len(lines)):
                #### kdx가 get_frist_etc_list에서 parsing한 내용의 인덱스에 포함되면 continue로 예외처리한다.
                if len(checking_other_start_idx)!=0:
                    check_out=except_lines(checking_other_start_idx,checking_other_end_idx,kdx,checking_idx)
                    checking_idx=check_out[1]
                    if check_out[0]=='not_pass':
                        continue
                
                #### cell의 각 특성에 대한 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
                if lines[kdx].replace('\n','').strip().startswith(checking_keyword) and lines[kdx].replace('\n','').split(checking_keyword)[1].strip().startswith('('):
                    etc_start_idx_list.append(kdx)
                    etc_end_idx_list.append(counting_function(kdx,lines))
                    
            #### 해당 특성에 대한 내용이 있을 경우 해당 인덱스 번호들을 저장한다.
            if len(etc_start_idx_list)!=0:
                etc_info={checking_keyword+'_start_idx':etc_start_idx_list,checking_keyword+'_end_idx':etc_end_idx_list}
                with open(location_of_lib+'/'+ivalue+'/'+checking_keyword+'_index.json','w') as fw:
                    json.dump(etc_info,fw,indent=4)
                fw.close()
            
    return 0




def get_cell_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_first=['leakage_current', 'intrinsic_parasitic', 'pg_pin', 'statetable', 'leakage_power', 'test_cell', 'dynamic_current', 'bus', 'memory', 'pin', 'ff', 'latch']

    for ivalue in os.listdir(location_of_lib):
        #### cell에 대한 디렉토리만 접근한다.
        if ivalue.endswith('.json') or ivalue.endswith('.txt'):
            continue
        #### cell 이외의 정보가 들어있는 디렉토리인 'not_cell_info'는 continue로 처리
        if ivalue=='not_cell_info':
            continue

        #### 해당 cell의 cell.txt의 위치 : temp_cell_text_address
        temp_cell_text_address=location_of_lib+'/'+ivalue+'/cell.txt'
        with open(temp_cell_text_address,'r') as fw:
            lines=fw.readlines()
        fw.close()

        checking_other_start_idx=list()
        checking_other_end_idx=list()

        #### 먼저 parsing하였던 다른 특성들의 시작 인덱스와 마지막 인덱스를 각각 checking_other_start_idx과 checking_other_end_idx에 저장
        for kvalue in os.listdir(location_of_lib+'/'+ivalue):
            if kvalue.endswith('.json') and kvalue.split('_index.json')[0] in checking_first:
                with open(location_of_lib+'/'+ivalue+'/'+kvalue,'r') as fw:
                    temp_dict=json.load(fw)
                fw.close()
                checking_other_start_idx.extend(temp_dict[kvalue.split('_index.json')[0]+'_start_idx'])
                checking_other_end_idx.extend(temp_dict[kvalue.split('_index.json')[0]+'_end_idx'])
        checking_other_start_idx.sort()
        checking_other_end_idx.sort()

        tt=int()
        checking_idx=-1
        temp_lines=list()
        for kdx in range(len(lines)):
            #### kdx가 get_frist_etc_list에서 parsing한 내용의 인덱스에 포함되면 continue로 예외처리한다.
            if len(checking_other_start_idx)!=0:
                check_out=except_lines(checking_other_start_idx,checking_other_end_idx,kdx,checking_idx)
                checking_idx=check_out[1]
                if check_out[0]=='not_pass':
                    continue
                #### 구간을 가지는 정보를 제외한 cell에 대한 정보들을 temp_lines에 저장
                temp_lines.append(lines[kdx])
            else:
                print('tpgmwlns1!')
                temp_lines.append(lines[kdx])
        
        new_lines=['']
        for idx in range(len(temp_lines)):
            #### temp_lines에 주석으로 처리될 때마다 new_lines에 저장
            new_lines[-1]=new_lines[-1]+'\n'+temp_lines[idx].replace('\n','')
            if '*/' in temp_lines[idx]:
                new_lines.append('')

        real_lines=list()
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

        #### 주석이 없고, 구간에 대한 정보를 제외한 cell의 정보를 cell_info.txt에 저장
        for idx in range(len(real_lines)):
            if idx==0:
                with open(location_of_lib+'/'+ivalue+'/cell_info.txt','w') as fw:
                    fw.write(real_lines[idx]+'\n')
                fw.close()
            else:
                with open(location_of_lib+'/'+ivalue+'/cell_info.txt','a') as fw:
                    fw.write(real_lines[idx]+'\n')
                fw.close()
    return 0






#### cell의 구간을 가지는 정보를 제외한, 한 문장으로 표현되는 정보들을 nldm_lib_origin.json에 저장
def checking_index_in_cell(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    checking_sentence=['area', 'interface_timing', 'dont_use', 'dont_touch', 'map_only', 'drive_strength', 'cell_leakage_power', 'clock_gating_integrated_cell', 'cell_footprint']

    cell_origin_dict=dict()
    for ivalue in os.listdir(location_of_lib):
        #### cell에 대한 디렉토리만 접근한다.
        if ivalue.endswith('.json') or ivalue.endswith('.txt'):
            continue
        #### cell 이외의 정보가 들어있는 디렉토리인 'not_cell_info'는 continue로 처리
        if ivalue=='not_cell_info':
            continue
        
        if ivalue not in cell_origin_dict:
            cell_origin_dict.update({ivalue:{'cell_info':dict(),'input':dict(),'output':dict()}})
        #### 해당 cell의 cell.txt의 위치 : temp_cell_text_address
        temp_cell_text_address=location_of_lib+'/'+ivalue+'/cell_info.txt'
        with open(temp_cell_text_address,'r') as fw:
            lines=fw.readlines()
        fw.close()

        for kdx in range(len(lines)):
            #### cell의 이름을 나타내는 문자일 경우 continue로 처리
            if lines[kdx].strip().startswith('cell') and lines[kdx].split('cell')[1].strip().startswith('(') and \
            lines[kdx].split('cell')[1].strip().split('(')[1].startswith(ivalue) and lines[kdx].split('cell')[1].strip().split('(')[1].strip().split(ivalue)[1].strip().startswith(')'):
                continue
            #### cell의 내용이 끝났음을 알리는 문장일 경우 continue로 처리
            if lines[kdx].strip().startswith('}'):
                continue
            
            #### 해당 문장의 내용이 parsing하는 checking_sentence에 있다면 cell_origin_dict에 저장
            checking_lines=str()
            for rvalue in checking_sentence:
                if lines[kdx].strip().startswith(rvalue) and lines[kdx].split(rvalue)[1].strip().startswith(':') and lines[kdx].replace('\n','').strip().endswith(';'):
                    cell_origin_dict[ivalue]['cell_info'].update({rvalue:lines[kdx].split(':')[1].split(';')[0].strip()})
                    checking_lines='continue'
                    break

            #### 해당 문장이 checking_sentence에 있다면 continue로 처리
            if checking_lines=='continue':
                continue
            
            #### 해당 문장이 checking_sentence에 없다면 놓친 정보이므로 화면에 출력
            print('MISSING THE INFORMATION OF THE CELL :',ivalue,lines[kdx].replace('\n',''))
    
    #### nldm_lib_origin.json에 cell의 정보들을 저장
    with open(location_of_lib+'/nldm_lib_origin.json','w') as fw:
        json.dump(cell_origin_dict,fw,indent=4)
    fw.close()

    return 0







#### lib 디렉토리에 있는 각각의 cell의 pin 정보를 parsing, pin 디렉토리를 따로 만들어 저장한다.
def get_pin_list(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]

    for ivalue in os.listdir(location_of_lib):
        #### cell에 대한 디렉토리만 접근한다.
        if ivalue.endswith('.json') or ivalue.endswith('.txt'):
            continue
        #### cell 이외의 정보가 들어있는 디렉토리인 'not_cell_info'는 continue로 처리
        if ivalue=='not_cell_info':
            continue
        #### pin이 있는 cell에 대한 디렉토리만 접근한다.
        if 'pin_index.json' not in os.listdir(location_of_lib+'/'+ivalue):
            continue

        #### 해당 cell의 cell.txt의 위치 : temp_cell_text_address
        temp_cell_text_address=location_of_lib+'/'+ivalue+'/cell.txt'
        with open(temp_cell_text_address,'r') as fw:
            lines=fw.readlines()
        fw.close()
        
        #### 각 pin의 내용이 시작하는 인덱스와 끝나는 인덱스를 가져와서 분석
        with open(location_of_lib+'/'+ivalue+'/pin_index.json','r') as fw:
            temp_dict=json.load(fw)
        fw.close()
        pin_start_idx_list=temp_dict['pin_start_idx']
        pin_end_idx_list=temp_dict['pin_end_idx']

        for kdx in range(len(pin_start_idx_list)):
            #### n번째 pin의 내용을 가벼운 용량의 txt파일로 바꿔주어 pasing에 부담을 줄인다.
            #### pin_name : cell에서 n번째 cell의 이름
            pin_name=lines[pin_start_idx_list[kdx]].replace('\n','').split('pin')[1].split('(')[1].split(')')[0].strip()
            #### 각 pin의 내용을 해당 cell에 'pin_'+pin_name으로 새 디렉토리 생성 후 내용을 저장
            if 'pin_'+pin_name not in os.listdir(location_of_lib+'/'+ivalue):
                os.mkdir(location_of_lib+'/'+ivalue+'/pin_'+pin_name)

            for rdx in range(pin_end_idx_list[kdx]-pin_start_idx_list[kdx]+1):
                if rdx==0:
                    with open(location_of_lib+'/'+ivalue+'/pin_'+pin_name+'/pin.txt','w') as fw:
                        fw.write(lines[pin_start_idx_list[kdx]+rdx])
                    fw.close()
                else:
                    with open(location_of_lib+'/'+ivalue+'/pin_'+pin_name+'/pin.txt','a') as fw:
                        fw.write(lines[pin_start_idx_list[kdx]+rdx])
                    fw.close()
    
    return 0





#### 각 cell에 있는 pin에 대한 정보들을 parsing하여 저장
def get_pin_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]

    with open(location_of_lib+'/nldm_lib_origin.json','r') as fw:
        pins_info=json.load(fw)
    fw.close()

    for ivalue in os.listdir(location_of_lib):
        #### cell에 대한 디렉토리만 접근한다.
        if ivalue.endswith('.json') or ivalue.endswith('.txt'):
            continue
        #### cell 이외의 정보가 들어있는 디렉토리인 lib_nickname+'_not_cell_info'는 continue로 처리
        if ivalue==lib_nickname+'_not_cell_info':
            continue
        #### pin이 있는 cell에 대한 디렉토리만 접근한다.
        if 'pin_index.json' not in os.listdir(location_of_lib+'/'+ivalue):
            continue
        
        #print(ivalue)
        if ivalue not in pins_info:
            pins_info.update({ivalue:{'input':dict(),'output':dict()}})
        #### 각 pin의 디렉토리에 접근
        for kvalue in os.listdir(location_of_lib+'/'+ivalue):
            if kvalue.startswith('pin_'):
                #### 디렉토리가 아닌 파일의 경우 continue로 처리
                if kvalue.endswith('.json') or kvalue.endswith('.txt'):
                    continue
                
                #### 해당 pin의 내용이 있는 txt 파일을 lines에 저장
                with open(location_of_lib+'/'+ivalue+'/'+kvalue+'/pin.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()

                direction=str()
                for rdx in range(len(lines)):
                    if lines[rdx].strip().startswith('direction'):
                        direction=lines[rdx].split(':')[1].split(';')[0].strip()
                
                #### direction이 input이나 output이 아닌경우 continue로 처리
                if direction!='input' and direction!='output':
                    continue
                pins_info[ivalue][direction].update({kvalue.split('_')[1]:dict()})

    #### input과 output을 따로 parsing

    for cell_name in pins_info:
        #### input pin parsing
        for input_pin in pins_info[cell_name]['input']:
            #### 해당 pin의 내용 parsing
            with open (location_of_lib+'/'+cell_name+'/pin_'+input_pin+'/pin.txt' ,'r') as fw:
                lines=fw.readlines()
            fw.close()

            #### input의 구간을 가지는 특성들
            checking_first=['timing','internal_power','ccsn_first_stage','receiver_capacitance']
            #### timing, internal_power, ccsn_first_stage, receiver_capacitance에 대한 구간의 시작하는 인덱스와 끝나는 인덱스를 각 list에 저장
            #### 구간을 가지는 keyword마다 index를 저장
            for jvalue in checking_first:
                checking_keyword=jvalue

                etc_start_idx_list=list()
                etc_end_idx_list=list()

                for qdx in range(len(lines)):
                    #### pin의 각 특성에 대한 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
                    if lines[qdx].replace('\n','').strip().startswith(checking_keyword) and lines[qdx].replace('\n','').split(checking_keyword)[1].strip().startswith('('):
                        etc_start_idx_list.append(qdx)
                        etc_end_idx_list.append(counting_function(qdx,lines))
                
                #### 해당 특성에 대한 내용이 있을 경우 해당 인덱스 번호들을 저장한다.
                if len(etc_start_idx_list)!=0:
                    etc_info={checking_keyword+'_start_idx':etc_start_idx_list,checking_keyword+'_end_idx':etc_end_idx_list}
                    with open(location_of_lib+'/'+cell_name+'/pin_'+input_pin+'/'+checking_keyword+'_index.json','w') as fw:
                        json.dump(etc_info,fw,indent=4)
                    fw.close()
            
            
            checking_sentence=['fall_capacitance','rise_capacitance','capacitance','nextstate_type','clock','max_transition']
            #### fall_capacitance, rise_capacitance, capacitance, nextstate_type, clock, max_transition을 parsing하여 저장
            #### capacitance값은 있지만, fall_capacitance나 rise_capacitance값이 없을 경우 capacitance값으로 대체하여 저장, capacitance값을 저장하기 위한 temp_capacitance 변수 생성


            checking_other_start_idx=list()
            checking_other_end_idx=list()
            #### 먼저 parsing하였던 다른 특성들의 시작 인덱스와 마지막 인덱스를 각각 checking_other_start_idx과 checking_other_end_idx에 저장
            for jvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+input_pin):
                if jvalue.endswith('.json') and jvalue.split('_index.json')[0] in checking_first:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+input_pin+'/'+jvalue,'r') as fw:
                        temp_dict=json.load(fw)
                    fw.close()
                    checking_other_start_idx.extend(temp_dict[jvalue.split('_index.json')[0]+'_start_idx'])
                    checking_other_end_idx.extend(temp_dict[jvalue.split('_index.json')[0]+'_end_idx'])
            checking_other_start_idx.sort()
            checking_other_end_idx.sort()

            checking_idx=-1
            ##temp_capacitance=str()
            bre=str()
            temp_lines=list()
            for qdx in range(len(lines)):
                if len(checking_other_start_idx)!=0:
                    check_out=except_lines(checking_other_start_idx,checking_other_end_idx,qdx,checking_idx)
                    checking_idx=check_out[1]
                    if check_out[0]=='not_pass':
                        continue
                    #### 구간을 가지는 정보를 제외한 cell에 대한 정보들을 temp_lines에 저장
                    temp_lines.append(lines[qdx])
                else:
                    temp_lines.append(lines[qdx])


            real_lines=get_lines_uncomment(temp_lines)

            #### 주석이 없고, 구간에 대한 정보를 제외한 cell의 정보를 cell_info.txt에 저장
            for idx in range(len(real_lines)):
                if idx==0:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+input_pin+'/pin_info.txt','w') as fw:
                        fw.write(real_lines[idx]+'\n')
                    fw.close()
                else:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+input_pin+'/pin_info.txt','a') as fw:
                        fw.write(real_lines[idx]+'\n')
                    fw.close()

        
        


            '''#### fall_capacitance, rise_capacitance, capacitance, nextstate_type, clock, max_transition을 parsing
                if lines[qdx].strip().startswith('fall_capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['input'][input_pin].update({'fall_capacitance':lines[qdx].split(':')[1].split(';')[0].strip()})
    
                elif lines[qdx].strip().startswith('rise_capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['input'][input_pin].update({'rise_capacitance':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('capacitance') and lines[qdx].strip().endswith(';'):
                    temp_capacitance=lines[qdx].split(':')[1].split(';')[0].strip()

                elif lines[qdx].strip().startswith('nextstate_type') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['input'][input_pin].update({'nextstate_type':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('clock') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['input'][input_pin].update({'clock':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('max_transition') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['input'][input_pin].update({'max_transition':lines[qdx].split(':')[1].split(';')[0].strip()})

            #### fall_capacitance가 없다면 capacitance값을 fall_capacitance에 저장                
            if 'fall_capacitance' not in pins_info[cell_name]['input'][input_pin]:
                pins_info[cell_name]['input'][input_pin].update({'fall_capacitance':temp_capacitance})
                
            #### rise_capacitance가 없다면 capacitance값을 rise_capacitance에 저장        
            if 'rise_capacitance' not in pins_info[cell_name]['input'][input_pin]:
                pins_info[cell_name]['input'][input_pin].update({'rise_capacitance':temp_capacitance})'''
            



        #### output pin parsing
        for output_pin in pins_info[cell_name]['output']:
            #### 해당 pin의 내용 parsing
            with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/pin.txt' ,'r') as fw:
                lines=fw.readlines()
            fw.close()

            checking_first=['timing','internal_power','ccsn_last_stage','receiver_capacitance']
            #### timing, internal_power, ccsn_last_stage, receiver_capacitance에 대한 구간의 시작하는 인덱스와 끝나는 인덱스를 각 list에 저장

            #### 구간을 가지는 keyword마다 index를 저장
            for jvalue in checking_first:
                checking_keyword=jvalue

                etc_start_idx_list=list()
                etc_end_idx_list=list()

                for qdx in range(len(lines)):
                    #### pin의 각 특성에 대한 내용이 시작하고 끝나는 문장의 인덱스 번호를 각각 start와 end에 리스트로 저장
                    if lines[qdx].replace('\n','').strip().startswith(checking_keyword) and lines[qdx].replace('\n','').split(checking_keyword)[1].strip().startswith('('):
                        etc_start_idx_list.append(qdx)
                        etc_end_idx_list.append(counting_function(qdx,lines))

                #### 해당 특성에 대한 내용이 있을 경우 해당 인덱스 번호들을 저장한다.
                if len(etc_start_idx_list)!=0:
                    etc_info={checking_keyword+'_start_idx':etc_start_idx_list,checking_keyword+'_end_idx':etc_end_idx_list}
                    with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+checking_keyword+'_index.json','w') as fw:
                        json.dump(etc_info,fw,indent=4)
                    fw.close()

            checking_sentence=['max_capacitance','fall_capacitance','rise_capacitance','capacitance',\
                'power_down_function','state_function','function','three_state',\
                'related_ground_pin','related_power_pin','clock_gate_out_pin','driver_type']

            #### max_capacitance, fall_capacitance, rise_capacitance, capacitance,
            #### power_down_function, state_function, function, three_state,
            #### related_ground_pin, related_power_pin, clock_gate_out_pin, driver_type을 parsing하여 저장


            checking_other_start_idx=list()
            checking_other_end_idx=list()
            #### 먼저 parsing하였던 다른 특성들의 시작 인덱스와 마지막 인덱스를 각각 checking_other_start_idx과 checking_other_end_idx에 저장
            for jvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                if jvalue.endswith('.json') and jvalue.split('_index.json')[0] in checking_first:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+jvalue,'r') as fw:
                        temp_dict=json.load(fw)
                    fw.close()
                    checking_other_start_idx.extend(temp_dict[jvalue.split('_index.json')[0]+'_start_idx'])
                    checking_other_end_idx.extend(temp_dict[jvalue.split('_index.json')[0]+'_end_idx'])
            checking_other_start_idx.sort()
            checking_other_end_idx.sort()

            checking_idx=-1
            ##temp_capacitance=str()
            temp_lines=list()
            for qdx in range(len(lines)):
                if len(checking_other_start_idx)!=0:
                    check_out=except_lines(checking_other_start_idx,checking_other_end_idx,qdx,checking_idx)
                    checking_idx=check_out[1]
                    if check_out[0]=='not_pass':
                        continue
                    #### 구간을 가지는 정보를 제외한 cell에 대한 정보들을 temp_lines에 저장
                    temp_lines.append(lines[qdx])
                else:
                    temp_lines.append(lines[qdx])

            real_lines=get_lines_uncomment(temp_lines)

            #### 주석이 없고, 구간에 대한 정보를 제외한 cell의 정보를 cell_info.txt에 저장
            for idx in range(len(real_lines)):
                if idx==0:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/pin_info.txt','w') as fw:
                        fw.write(real_lines[idx]+'\n')
                    fw.close()
                else:
                    with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/pin_info.txt','a') as fw:
                        fw.write(real_lines[idx]+'\n')
                    fw.close()
        


        '''for qdx in range(len(lines)):
                if lines[qdx].strip().startswith('fall_capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'fall_capacitance':float(lines[qdx].split(':')[1].split(';')[0].strip())})

                elif lines[qdx].strip().startswith('rise_capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'rise_capacitance':float(lines[qdx].split(':')[1].split(';')[0].strip())})

                elif lines[qdx].strip().startswith('max_capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'max_capacitance':float(lines[qdx].split(':')[1].split(';')[0].strip())})

                elif lines[qdx].strip().startswith('capacitance') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'capacitance':float(lines[qdx].split(':')[1].split(';')[0].strip())})

                elif lines[qdx].strip().startswith('power_down_function') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'power_down_function':lines[qdx].split('\"')[1].strip()})

                elif lines[qdx].strip().startswith('state_function') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'state_function':lines[qdx].split('\"')[1].strip()})

                elif lines[qdx].strip().startswith('function') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'function':lines[qdx].split('\"')[1].strip()})

                elif lines[qdx].strip().startswith('three_state') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'three_state':lines[qdx].split('\"')[1].strip()})

                elif lines[qdx].strip().startswith('related_ground_pin') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'related_ground_pin':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('related_power_pin') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'related_power_pin':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('clock_gate_out_pin') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'clock_gate_out_pin':lines[qdx].split(':')[1].split(';')[0].strip()})

                elif lines[qdx].strip().startswith('driver_type') and lines[qdx].strip().endswith(';'):
                    pins_info[cell_name]['output'][output_pin].update({'driver_type':lines[qdx].split(':')[1].split(';')[0].strip()})'''





    #### timing에 대한 정보가 없는 lib의 내용을 요약한 json파일 저장 : nldm_lib_first.json
    '''with open(location_of_lib+'/nldm_lib_first.json','w') as fw:
        json.dump(pins_info,fw,indent=4)
    fw.close()'''
    return 0





#### 각 cell에 있는 output_pin에 대한 정보들 중, timing에 대한 정보들을 parsing하여 저장
def get_timing_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    with open(location_of_lib+'/nldm_lib_first.json','r') as fw:
        pins_info=json.load(fw)
    fw.close()

    for cell_name in pins_info:
        for output_pin in pins_info[cell_name]['output']:
            #print(output_pin)
            #### timing의 정보만 있는 output_pin에만 접근
            if 'timing_index.json' not in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                continue
            
            #### 해당 output_pin의 내용 parsing
            with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/pin.txt' ,'r') as fw:
                lines=fw.readlines()
            fw.close()

            #### 해당 output_pin에서 timing이 시작하는 인덱스와 끝나는 인덱스 불러오기
            with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/timing_index.json','r') as fw:
                temp_dict=json.load(fw)
            start_timing_idx=temp_dict['timing_start_idx']
            end_timing_idx=temp_dict['timing_end_idx']

            #### timing에 대한 각각의 case들을 timing_n 이라는 디렉토리를 만들어서 내용을 저장
            if len(start_timing_idx)!=0:
                for idx in range(len(start_timing_idx)):
                    if 'timing_'+str(idx) not in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                        os.mkdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/timing_'+str(idx))

                    for kdx in range(end_timing_idx[idx]-start_timing_idx[idx]+1):
                        if kdx==0:
                            with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/timing_'+str(idx)+'/timing.txt','w') as fw:
                                fw.write(lines[start_timing_idx[idx]+kdx])
                            fw.close()
                        else:
                            with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/timing_'+str(idx)+'/timing.txt','a') as fw:
                                fw.write(lines[start_timing_idx[idx]+kdx])
                            fw.close()

    return 0







#### 각 cell에 있는 output_pin의 timing에 대한 정보들의 시작하는 인덱스와 끝나는 인덱스를 저장
def get_timing_detail_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    with open(location_of_lib+'/nldm_lib_first.json','r') as fw:
        pins_info=json.load(fw)
    fw.close()

    #### 구간을 가지는 정보들을 먼저 parsing하여 각각 시작하는 인덱스와 끝나는 인덱스를 저장
    characteristic_list=['cell_rise','rise_transition','cell_fall','fall_transition','ccsn_first_stage','ccsn_last_stage',\
        'output_current_rise','receiver_capacitance1_rise', 'receiver_capacitance2_rise','output_current_fall','receiver_capacitance1_fall','receiver_capacitance2_fall']

    for cell_name in pins_info:
        for output_pin in pins_info[cell_name]['output']:

            #### timing의 정보만 있는 output_pin에만 접근
            if 'timing_index.json' not in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                continue
            for kvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                #### output_pin의 내용 중 timing에 대한 정보가 아닌 경우 continue로 처리
                if not kvalue.startswith('timing_'):
                    continue
                #### 디랙토리가 아닌 파일명의 경우 continue로 처리
                if kvalue.endswith('.json') or kvalue.endswith('.txt'):
                    continue

                with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/timing.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()

                #### 구간을 가지는 정보들의 keyword : characteristic_list[qdx]
                for qdx in range(len(characteristic_list)):
                    start_etc_list=list()
                    end_etc_list=list()
                    
                    #### 구간이 시작하는 인덱스를 start_etc_list에 저장, 구간이 끝나는 인덱스를 end_etc_list에 저장
                    for jdx in range(len(lines)):
                        if lines[jdx].strip().startswith(characteristic_list[qdx]) and lines[jdx].split(characteristic_list[qdx])[1].strip().startswith('('):
                            start_etc_list.append(jdx)
                            end_etc_list.append(counting_function(jdx,lines))

                    #### 해당 keyword의 정보가 output_pin에 있다면 인덱스를 json파일로 저장
                    if len(start_etc_list)!=0:
                        temp_dict={characteristic_list[qdx]+'_start_idx':start_etc_list,characteristic_list[qdx]+'_end_idx':end_etc_list}
                        with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/'+characteristic_list[qdx]+'_index.json','w') as fw:
                            json.dump(temp_dict,fw,indent=4)

    return 0





#### 각 output_pin이 가지는 timing의 여러 case들의 nldm table을 parsing한다.
def get_nldm_table_and_pin_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]

    with open(location_of_lib+'/nldm_lib_first.json','r') as fw:
        pins_info=json.load(fw)
    fw.close()
    nldm_lib_second=copy.deepcopy(pins_info)

    #### 함수 get_timing_detail_info에서 저장한 구간을 가지는 정보들의 키워드 집합
    characteristic_list=['cell_rise','rise_transition','cell_fall','fall_transition','ccsn_first_stage','ccsn_last_stage',\
        'output_current_rise','receiver_capacitance1_rise', 'receiver_capacitance2_rise','output_current_fall','receiver_capacitance1_fall','receiver_capacitance2_fall']

    for cell_name in pins_info:
        for output_pin in pins_info[cell_name]['output']:
            #### timing의 정보만 있는 output_pin에만 접근

            #### timing에 대한 정보가 없는 output_pin의 경우 continue로 처리
            if 'timing_index.json' not in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                continue

            for kvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                #### output_pin의 내용 중 timing에 대한 정보가 아닌 경우 continue로 처리
                if not kvalue.startswith('timing_'):
                    continue
                #### 디랙토리가 아닌 파일명의 경우 continue로 처리
                if kvalue.endswith('.json') or kvalue.endswith('.txt'):
                    continue

                #### lines에 timing에 대한 정보 저장
                with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/timing.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()

                #### 구간을 가지는 정보들을 제외하기 위해, 해당 정보들의 각 구간들을 etc_start_list와 etc_end_list에 저장
                etc_start_list=list()
                etc_end_list=list()


                for qvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue):
                    if qvalue.endswith('.json') and qvalue.split('_index.json')[0] in characteristic_list:
                        with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/'+qvalue,'r') as fw:
                            temp_dict=json.load(fw)
                        fw.close()
                        etc_start_list.extend(temp_dict[qvalue.split('_index.json')[0]+'_start_idx'])
                        etc_end_list.extend(temp_dict[qvalue.split('_index.json')[0]+'_end_idx'])
                
                #### 구간을 가지는 모든 정보들의 집합
                etc_start_list.sort()
                etc_end_list.sort()


                checking_idx=-1
                addition_dict=dict()
                for qdx in range(len(lines)):

                    #### timing의 정보 중 구간을 가지는 정보가 있을 경우 제외한다.
                    if len(etc_start_list)!=0:
                        check_out=except_lines(etc_start_list,etc_end_list,qdx,checking_idx)
                        checking_idx=check_out[1]
                        #### 탐색중인 인덱스가 구간을 가지는 정보의 구간에 포함될 경우 continue로 처리
                        if check_out[0]=='not_pass':
                            continue
                    
                    #### 구간이 아닌 정보들의 경우 nldm_lib_second에 추가한다. : related_pin, sdf_cond, timing_sense, timing_type, when
                    if lines[qdx].strip().startswith('related_pin') and lines[qdx].split('related_pin')[1].strip().startswith(':'):
                        addition_dict.update({'related_pin':lines[qdx].split('\"')[1]})

                    elif lines[qdx].strip().startswith('sdf_cond') and lines[qdx].split('sdf_cond')[1].strip().startswith(':'):
                        addition_dict.update({'sdf_cond':lines[qdx].split('\"')[1]})
                        
                    elif lines[qdx].strip().startswith('timing_sense') and lines[qdx].split('timing_sense')[1].strip().startswith(':'):
                        addition_dict.update({'timing_sense':lines[qdx].split(':')[1].split(';')[0].strip()})

                    elif lines[qdx].strip().startswith('timing_type') and lines[qdx].split('timing_type')[1].strip().startswith(':'):
                        addition_dict.update({'timing_type':lines[qdx].split(':')[1].split(';')[0].strip()})
                        
                    elif lines[qdx].strip().startswith('when') and lines[qdx].split('when')[1].strip().startswith(':'):
                        addition_dict.update({'when':lines[qdx].split('\"')[1]})

                if len(addition_dict)!=0:
                    if 'timing' not in nldm_lib_second[cell_name]['output'][output_pin]:
                        nldm_lib_second[cell_name]['output'][output_pin].update({'timing':dict()})
                    nldm_lib_second[cell_name]['output'][output_pin]['timing'].update({'case_'+kvalue.split('timing_')[1]:addition_dict})
            
            #### timing의 정보가 없는 output_pin은 continue로 처리
            if 'timing' not in nldm_lib_second[cell_name]['output'][output_pin]:
                continue

            for kvalue in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin):
                #### output_pin의 내용 중 timing에 대한 정보가 아닌 경우 continue로 처리
                if not kvalue.startswith('timing_'):
                    continue
                #### 디랙토리가 아닌 파일명의 경우 continue로 처리
                if kvalue.endswith('.json') or kvalue.endswith('.txt'):
                    continue

                #### 해당 output_pin의 여러 case들 중 n번째 case의 대한 내용을 lines에 저장
                with open(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/timing.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()

                #### 해당 case에서 rise한 경우가 있을 때
                if 'cell_rise_index.json' in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue) and \
                    'rise_transition_index.json' in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue):

                    #### cell_rise의 delay의 정보
                    with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/cell_rise_index.json','r') as fw:
                        temp_cell_rise=json.load(fw)
                    fw.close()
                    
                    #### cell_rise의 transition의 정보
                    with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/rise_transition_index.json','r') as fw:
                        temp_rise_transition=json.load(fw)
                    fw.close()

                    start_cell_rise=temp_cell_rise['cell_rise_start_idx']
                    end_cell_rise=temp_cell_rise['cell_rise_end_idx']
                    start_rise_transition=temp_rise_transition['rise_transition_start_idx']
                    end_rise_transition=temp_rise_transition['rise_transition_end_idx']

                    #### 함수 get_temporary_nldm_table을 통해 해당 nldm의 template id와 index 및 value를 parsing하여 해당 case에 저장
                    template_id_with_index_and_value_cell_rise=get_temporary_nldm_table(start_cell_rise,end_cell_rise,lines,'cell_rise')
                    template_id_cell_rise=template_id_with_index_and_value_cell_rise[0]
                    cell_rise_lines=template_id_with_index_and_value_cell_rise[1]

                    template_id_with_index_and_value_rise_transition=get_temporary_nldm_table(start_rise_transition,end_rise_transition,lines,'rise_transition')
                    template_id_rise_transition=template_id_with_index_and_value_rise_transition[0]
                    rise_transition_lines=template_id_with_index_and_value_rise_transition[1]

                    #### 해당 case에 rise추가
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]].update({'rise':dict()})
                    #### 해당 case에 cell_rise의 template id와 정보 저장
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['rise'].update({'template_id_cell_rise':template_id_cell_rise})
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['rise'].update({'cell_rise_lines':cell_rise_lines})
                    #### 해당 case에 rise_transition의 template id와 정보 저장
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['rise'].update({'template_id_rise_transition':template_id_rise_transition})
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['rise'].update({'rise_transition_lines':rise_transition_lines})                    

    
                #### 해당 case에서 fall한 경우가 있을 때
                if 'cell_fall_index.json' in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue) and \
                    'fall_transition_index.json' in os.listdir(location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue):
                
                    with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/cell_fall_index.json','r') as fw:
                        temp_cell_fall=json.load(fw)
                    fw.close()

                    with open (location_of_lib+'/'+cell_name+'/pin_'+output_pin+'/'+kvalue+'/fall_transition_index.json','r') as fw:
                        temp_fall_transition=json.load(fw)
                    fw.close()

                    start_cell_fall=temp_cell_fall['cell_fall_start_idx']
                    end_cell_fall=temp_cell_fall['cell_fall_end_idx']
                    start_fall_transition=temp_fall_transition['fall_transition_start_idx']
                    end_fall_transition=temp_fall_transition['fall_transition_end_idx']

                    #### 함수 get_temporary_nldm_table을 통해 해당 nldm의 template id와 index 및 value를 parsing하여 해당 case에 저장
                    template_id_with_index_and_value_cell_fall=get_temporary_nldm_table(start_cell_fall,end_cell_fall,lines,'cell_fall')
                    template_id_cell_fall=template_id_with_index_and_value_cell_fall[0]
                    cell_fall_lines=template_id_with_index_and_value_cell_fall[1]

                    template_id_with_index_and_value_fall_transition=get_temporary_nldm_table(start_fall_transition,end_fall_transition,lines,'fall_transition')
                    template_id_fall_transition=template_id_with_index_and_value_fall_transition[0]
                    fall_transition_lines=template_id_with_index_and_value_fall_transition[1]

                    #### 해당 case에 fall추가
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]].update({'fall':dict()})
                    #### 해당 case에 cell_fall의 template id와 정보 저장
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['fall'].update({'template_id_cell_fall':template_id_cell_fall})
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['fall'].update({'cell_fall_lines':cell_fall_lines})
                    #### 해당 case에 fall_transition의 template id와 정보 저장
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['fall'].update({'template_id_fall_transition':template_id_fall_transition})
                    nldm_lib_second[cell_name]['output'][output_pin]['timing']['case_'+kvalue.split('timing_')[1]]['fall'].update({'fall_transition_lines':fall_transition_lines})   

    #### nldm table을 parsing하여 그 내용을 저장한 nldm_lib_second을 json파일로 저장
    with open(location_of_lib+'/nldm_lib_second.json','w') as fw:
        json.dump(nldm_lib_second,fw,indent=4)
    fw.close()

    return 0





def get_template_txt(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]

    #### template를 비교할 dictionary : pin_info
    with open(location_of_lib+'/nldm_lib_second.json','r') as fw:
        pin_info=json.load(fw)
    fw.close()

    #### cell들의 시작하는 인덱스와 끝나는 인덱스의 집합 : cell_group
    with open(location_of_lib+'/cell_index.json','r') as fw:
        cell_group=json.load(fw)
    fw.close()
    cell_start_idx=cell_group['cell_start_idx']
    cell_end_idx=cell_group['cell_end_idx']
    
    with open(address,'r') as fw:
        lines=fw.readlines()
    fw.close()

    cell_start_idx.sort()
    cell_end_idx.sort()


    except_cell=list()
    checking_idx=-1
    for idx in range(len(lines)):
        #### lib파일에서 cell대한 인덱스를 탐색중일 경우 제외한다.
        if len(cell_start_idx)!=0:
            check_out=except_lines(cell_start_idx,cell_end_idx,idx,checking_idx)
            checking_idx=check_out[1]
            #### 탐색중인 인덱스가 구간을 가지는 정보의 구간에 포함될 경우 continue로 처리
            if check_out[0]=='not_pass':
                continue
        
        except_cell.append(lines[idx])
        

################# 여기서부터 주석 수정
    new_lines=['']
    for idx in range(len(except_cell)):

        new_lines[-1]=new_lines[-1]+'\n'+except_cell[idx].replace('\n','')
        if '*/' in except_cell[idx]:
            new_lines.append('')

    real_lines=list()
    for idx in range(len(new_lines)):
        if '*/' in new_lines[idx]:
            new_lines[idx]=new_lines[idx].split('/*')[0]+new_lines[idx].split('*/')[1]
        if new_lines[idx].strip()=='':
            continue
        for kdx in range(len(new_lines[idx].split('\n'))):
            if new_lines[idx].split('\n')[kdx].strip()=='':
                continue
            real_lines.append(new_lines[idx].split('\n')[kdx])


    if 'not_cell_info' not in os.listdir(location_of_lib):
        os.mkdir(location_of_lib+'/not_cell_info')
    
    for idx in range(len(real_lines)):
        if idx==0:
            with open(location_of_lib+'/not_cell_info/text.txt','w') as fw:
                fw.write(real_lines[idx]+'\n')
            fw.close()
        else:
            with open(location_of_lib+'/not_cell_info/text.txt','a') as fw:
                fw.write(real_lines[idx]+'\n')
            fw.close()

    return 0








def get_each_template_info(address):
    #### 해당 lib 파일의 디렉토리 위치 : location_of_lib
    location_of_lib=address.split('.lib')[0]
    #### lib 파일의 이름명
    lib_nickname=location_of_lib.split('/')[-1]


    with open(address.split('/'+address.split('/')[-1])[0]+'/'+lib_nickname+'_not_cell_info/text.txt','r') as fw:
        lines=fw.readlines()
    fw.close()
    
    for idx in range(len(lines)):
        print(lines[idx].replace('\n',''))



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
    lib_address=lib_address+checking
    #print(checking)
    #print('start')
    #start=time.time()
    if sys.argv[1]=='0':
        get_cell_list(lib_address)
    

    elif sys.argv[1]=='1':
        get_frist_etc_list(lib_address)

    elif sys.argv[1]=='2':
        get_second_etc_list(lib_address)
    
    elif sys.argv[1]=='3':
        get_cell_info(lib_address)

    elif sys.argv[1]=='4':
        checking_index_in_cell(lib_address)


    elif sys.argv[1]=='5':
        get_pin_list(lib_address)
    
    elif sys.argv[1]=='6':
        get_pin_info(lib_address)

    elif sys.argv[1]=='12':
        checking_index_in_input_pin_and_output_pin(lib_address)



    elif sys.argv[1]=='7':
        get_timing_info(lib_address)

    elif sys.argv[1]=='8':
        get_timing_detail_info(lib_address)
    elif sys.argv[1]=='13':
        checking_index_in_timing_of_output_pin(lib_address)



    elif sys.argv[1]=='9':
        get_nldm_table_and_pin_info(lib_address)
    
    elif sys.argv[1]=='10':
        get_template_txt(lib_address)
    
    elif sys.argv[1]=='11':
        get_each_template_info(lib_address)

    #print('end',time.time()-start)
    #print()