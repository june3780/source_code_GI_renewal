import json
import copy
import time

def get_module_dict(wherethemodule): #verilog file parsing
    # macro_list: 해당 verilog에 사용되는 macro id들의 집합
    macro_list=['spsram_hd_256x23m4m','spsram_hd_2048x32m4s','spsram_hd_256x22m4m','sprf_hs_128x38m2s'\
    ,'TS1N40LPB1024X32M4FWBA','TS1N40LPB2048X36M4FWBA','TS1N40LPB256X23M4FWBA','TS1N40LPB128X63M4FWBA'\
    ,'TS1N40LPB256X12M4FWBA','TS1N40LPB512X23M4FWBA','TS1N40LPB1024X128M4FWBA','TS1N40LPB2048X32M4FWBA'\
    ,'TS1N40LPB256X22M4FWBA']



    # verilog 파일 읽기
    with open(wherethemodule,'r') as fw:
        module_str=fw.readlines()
    fw.close()



    # 'module-endmodule'을 기준으로 module_list 각 module의 문장들을 합쳐서 저장
    module_list=['']
    for ivalue in module_str:
        # verilog 파일에서의 주석처리
        if ivalue.strip().startswith('//'):
            continue
        # module_list의 마지막 인덱스에 module의 문장을 붙여서 최신화
        if module_list[-1]=='':
            module_list[-1]=ivalue.strip()
        else:
            module_list[-1]=module_list[-1]+' '+ivalue.strip()
        # endmodule이 나올 경우, module_list에 새로운 인덱스 추가
        if ivalue.replace('\n','').strip().endswith('endmodule'):
            module_list.append('')
    # 마지막 module의 endmodule에 의한 아무 내용 없는 인덱스 제거
    del module_list[-1]


    cc=int()
    # module_list의 각 module을 parsing하여 module_dict에 각 module의 내용 저장, assign에 대한 내용을 assign_dict에 저장
    module_dict=dict()
    assign_dict=dict()
    # 각 module에 접근 module_list에는 module에 대한 내용이 하나의 문장으로 합쳐져 있는 상태
    for ivalue in module_list:
        cc=cc+1
        module_name=str()
        # 각 module들의 문장을 ';'을 기준으로 나눠서 temp_str에 각 문장들을 저장
        temp_str=ivalue.split(';')
        for kvalue in temp_str:
            # 각 문장들의 첫 단어들을 통해 분류하여 module 내용을 저장, 현재 함수가 처리한 첫 단어들의 경우 : [module, input, output, wire, assign, endmodule]
            # 나머지의 경우들을 components_cell 혹은 macro, 또는 submodule로 간주한다.

            # 첫 단어가 module인 경우: module_dict에 module의 id를 추가
            if kvalue.strip().startswith('module '):
                module_name=kvalue.split(' ')[1]
                module_dict.update({module_name:{}})

            # 첫 단어가 input인 경우: 해당 module에 input 이라는 key를 추가, input에 해당 net을 추가, multi-input을 가질경우 각 요소들을 나눠 input에 해당 net들을 추가
            elif kvalue.strip().startswith('input '):
                if 'input' not in module_dict[module_name]:
                    module_dict[module_name].update(({'input':[]}))
                # multi-input일 경우
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 input에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for jvalue in temp_list:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['input'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif large_idx<small_idx:
                            for jvalue in temp_list:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['input'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['input'].append(jvalue+'['+str(large_idx)+']')
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 input에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx-tdx)+']')

                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['input'].append(jvalue+'['+str(large_idx)+']')
                # multi-input이 아닌 경우(단일 비트의 input)
                else:
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('input ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['input'].append(jvalue)
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('input ')[1].replace(';','').strip()
                        module_dict[module_name]['input'].append(jvalue)

            # 첫 단어가 output인 경우: 해당 module에 output 이라는 key를 추가, output에 해당 net을 추가, multi-output을 가질경우 각 요소들을 나눠 output에 해당 net들을 추가
            elif kvalue.strip().startswith('output '):
                if 'output' not in module_dict[module_name]:
                    module_dict[module_name].update(({'output':[]}))
                # multi-output일 경우
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 output에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for jvalue in temp_list:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['output'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for jvalue in temp_list:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['output'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['output'].append(jvalue+'['+str(large_idx)+']')
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 output에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['output'].append(jvalue+'['+str(large_idx)+']')
                # multi-output이 아닌 경우(단일 비트의 output)
                else:
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('output ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['output'].append(jvalue)
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('output ')[1].replace(';','').strip()
                        module_dict[module_name]['output'].append(jvalue)

            # 첫 단어가 wire인 경우: 해당 module에 wire 이라는 key를 추가, wire에 해당 net을 추가, multi-wire을 가질경우 각 요소들을 나눠 wire에 해당 net들을 추가
            elif kvalue.strip().startswith('wire '):
                if 'wire' not in module_dict[module_name]:
                    module_dict[module_name].update(({'wire':[]}))
                # multi-wire일 경우
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 wire에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for jvalue in temp_list:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for jvalue in temp_list:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx)+']')
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        # multi에 정의된 두 숫자의 3가지 경우에 따라 wire에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx)+']')
                # multi-wire이 아닌 경우(단일 비트의 wire)
                else:
                    # 정의된 net이 여러 개인 경우
                    if ',' in kvalue:
                        temp_list=kvalue.split('wire ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['wire'].append(jvalue)
                    # 정의된 net이 하나인 경우
                    else:
                        jvalue=kvalue.split('wire ')[1].replace(';','').strip()
                        module_dict[module_name]['wire'].append(jvalue)

            # 첫 단어가 assign인 경우: 해당 module을 assign_dict에 추가하고, assign A=B;를 {A:B}라는 딕셔너리로 바꾼 후 해당 module에 추가
            elif kvalue.strip().startswith('assign '):
                # 해당 moudule을 assign_dict에 추가
                if module_name not in assign_dict:
                    assign_dict.update({module_name:dict()})
                # temp_output: A에 해당하는 net
                temp_output=kvalue.split('assign')[1].split('=')[0].strip()
                # temp_value: B에 해당하는 net
                temp_value=kvalue.split('assign')[1].split('=')[1].strip()
                assign_dict[module_name].update({temp_output:temp_value})

            # 첫 단어가 module인 경우: 다음 인덱스로 넘어간다.
            elif kvalue.strip().startswith('endmodule'):
                continue

            # 첫 단어가 처리되는 단어에 포함되지 않을 경우, standard_cell 혹은 macro나 submodule로 간주한다.
            else:
                # component_or_module: standard_cell 혹은 macro나 submodule
                component_or_module=kvalue.strip().split(' ')[0].strip()
                # list_of_line: 해당 component_or_module이 가지는 port와 그에 연결된 net
                list_of_line=' '.join(kvalue.strip().split(' ')[2:])
                # module_dict에 해당 module에 component_or_module 추가 (해당 component_or_module의 이름을 저장한다, 'id'에 standard_cell이나 macro의 'id' 혹은 submodule의 module의 'id'로 추가)
                module_dict[module_name].update({kvalue.strip().split(' ')[1].strip():{'id':component_or_module}})
                # 해당 component_or_module에 대한 port와 그에 연결된 net 추가
                module_dict[module_name][kvalue.strip().split(' ')[1].strip()].update({'ports':{}})
                for tvalue in list_of_line.split('.'):
                    if '(' not in tvalue or ')' not in tvalue:
                        continue
                    module_dict[module_name][kvalue.strip().split(' ')[1].strip()]['ports'].update({tvalue.split('(')[0].strip():tvalue.split('(')[1].strip().split(')')[0].strip()})


    top_module=str()
    # 모든 module의 id를 module_list에 저장
    module_list=list(module_dict.keys())
    # 각 module에 추가한 standard_cell 혹은 macro나 submodule인 요소들을 components_counts에 standard_cell과 macro들을, module_counts에 submodule을 저장하여 해당 module에 추가
    for ivalue in module_dict:
        # 각 module에 components_counts와 module_counts 추가
        module_dict[ivalue].update({'components_counts':{}})
        module_dict[ivalue].update({'module_counts':{}})
        # 각 module마다 components_counts와 module_counts로 나누기
        for kvalue in module_dict[ivalue]:
            # module의 standard_cell 혹은 macro나 submodule인 요소들만 접근
            if kvalue!='input' and kvalue!='output' and kvalue!='wire' and kvalue!='components_counts' and kvalue!='module_counts':
                # 해당 요소의 id가 module_dict에 선언된 module에 포함이 안될 경우
                if module_dict[ivalue][kvalue]['id'] not in module_dict:
                    module_dict[ivalue]['components_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})
                # 해당 요소의 id가 module_dict에 선언된 module 중 하나일 경우
                else:
                    module_dict[ivalue]['module_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})
                    # top_module을 찾기 위해 안쓰인 module을 제외한 module들을 module_list에서 제거한다.
                    if module_dict[ivalue][kvalue]['id'] in module_list:
                        module_list.remove(module_dict[ivalue][kvalue]['id'])
    # 한번도 submodule로 쓰인 적 없는 module이 top_module이다.
    top_module=module_list[0]
    print(top_module)

    
    # assign이 있는 module에 예외 처리
    for ivalue in assign_dict:
        # {A:B}인 딕셔너리가 assign_dict[ivalue]에 있다. ex) kvalue: A, assign_dict[kvalue]: B
        for kvalue in assign_dict[ivalue]:
            # assign에 의해 wire와 input, 혹은 wire와 output에 동시에 정의된 net의 wire를 지워준다.
            if kvalue in module_dict[ivalue]['wire']:
                module_dict[ivalue]['wire'].remove(kvalue)
            if assign_dict[ivalue][kvalue] in module_dict[ivalue]['wire']:
                module_dict[ivalue]['wire'].remove(assign_dict[ivalue][kvalue])
            # assign을 가지는 특수한 module을 submodule로 갖는 module 탐색
            for rvalue in module_dict:
                for tvalue in module_dict[rvalue]['module_counts']:
                    # rvalue: assign을 가지는 module을 submodule로 가지는 module
                    # tvalue: rvalue 의 submodule 중 하나로 assign을 가지는 module
                    if ivalue==module_dict[rvalue]['module_counts'][tvalue]:
                        # assign_A_assign_B 와 assign_B_assign_A 라는 임의의 component를 rvalue인 moudule에 추가해준다.

                        # assign_A_assign_B의 id는 assign_A이다.
                        # assign_A_assign_B의 port는 'A' 하나이며, submodule의 A에 연결된 net과 같은 net을 assign_A_assign_B의 'A' port에 연결한다.
                        if 'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue] not in module_dict[rvalue]['components_counts']:
                            module_dict[rvalue]['components_counts'].update({'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]:str()})
                        module_dict[rvalue]['components_counts']['assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]]='assign_'+kvalue
                        if 'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue] not in module_dict[rvalue]:
                            module_dict[rvalue].update({'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]:dict()})
                        module_dict[rvalue]['assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]].update({'id':'assign_'+kvalue,'ports':{'A':module_dict[rvalue][tvalue]['ports'][kvalue]}})
                        # assign_B_assign_A의 id는 assign_B이다.
                        # assign_B_assign_A의 port는 'A' 하나이며, submodule의 B에 연결된 net과 같은 net을 assign_B_assign_A의 'A' port에 연결한다.
                        if 'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue not in module_dict[rvalue]['components_counts']:
                            module_dict[rvalue]['components_counts'].update({'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue:str()})
                        module_dict[rvalue]['components_counts']['assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue]='assign_'+assign_dict[ivalue][kvalue]
                        if 'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue not in module_dict[rvalue]:
                            module_dict[rvalue].update({'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue:dict()})
                        module_dict[rvalue]['assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue].update({'id':'assign_'+assign_dict[ivalue][kvalue],'ports':{'A':module_dict[rvalue][tvalue]['ports'][assign_dict[ivalue][kvalue]]}})



    # module에 있는 macro와 submodule에 쓰이는 array_port들과 연결된 array_net들을 각 port와 net이 대응하도록 분리
    for ivalue in module_dict:
        array_input=list()
        array_output=list()
        array_wire=list()
        # 하나의 module의 input들중에 같은 이름을 가지고 인덱스(배열값)만 다른 input들을 array_input에 이름만 저장
        for kvalue in module_dict[ivalue]['input']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_input:
                    array_input.append(kvalue.split('[')[0])
        # 하나의 module의 output들중에 같은 이름을 가지고 인덱스(배열값)만 다른 output들을 array_output에 이름만 저장
        for kvalue in module_dict[ivalue]['output']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_output:
                    array_output.append(kvalue.split('[')[0])
        # 하나의 module의 wire들중에 같은 이름을 가지고 인덱스(배열값)만 다른 wire들을 array_wire에 이름만 저장
        if 'wire' in module_dict[ivalue]:
            for kvalue in module_dict[ivalue]['wire']:
                if '[' in kvalue:
                    if kvalue.split('[')[0] not in array_wire:
                        array_wire.append(kvalue.split('[')[0])
        # 하나의 macro와 submodule을 탐색
        for kvalue in module_dict[ivalue]:

            # macro 혹은 submodule이 아닌 경우 continue
            if kvalue=='input' or kvalue=='output' or kvalue=='wire' or kvalue=='module_counts' or kvalue=='components_counts':
                continue
            elif module_dict[ivalue][kvalue]['id'] not in macro_list and kvalue in module_dict[ivalue]['components_counts']:
                continue
            
            # macro 혹은 submodule인 경우
            else:
                # 각 port별로 array 판별 및 분리
                temp_ports_list=copy.deepcopy(module_dict[ivalue][kvalue]['ports'])
                # new_ports_list: port key에 새로 저장할 port 딕셔너리
                new_ports_list=dict()
                for tvalue in temp_ports_list:
                    # '{_}' 결합 연산자로 묶여있지 않는 경우
                    temple_list=list()
                    if '{' not in temp_ports_list[tvalue]:
                        # 기존의 port가 연결된 net이 array_input, array_output, array_wire에 없을 경우: 1. '[number1:number2]'배열의 net 2. 단일 비트인 net
                        if temp_ports_list[tvalue] not in array_input\
                            and temp_ports_list[tvalue] not in array_output\
                            and temp_ports_list[tvalue] not in array_wire:
                            # 1. '[number1:number2]'배열의 net의 경우 => 해당 port에 배열 형태의 net을 분리하여 list 자료형으로 temple_list에 저장
                            if ':' in temp_ports_list[tvalue]:
                                large_idx=int(temp_ports_list[tvalue].split(']')[0].split(':')[0].split('[')[1])
                                small_idx=int(temp_ports_list[tvalue].split(']')[0].split(':')[1])
                                if large_idx>small_idx:
                                    for jdx in range(large_idx-small_idx+1):
                                        temple_list.append(temp_ports_list[tvalue].split('[')[0]+'['+str(large_idx-jdx)+']')
                                elif small_idx>large_idx:
                                    for jdx in range(small_idx-large_idx+1):
                                        temple_list.append(temp_ports_list[tvalue].split('[')[0]+'['+str(large_idx+jdx)+']')
                                else:
                                    temple_list.append(temp_ports_list[tvalue].split('[')[0])
                                temp_ports_list[tvalue]=temple_list
                            # 2. 단일 비트인 net의 경우 => 해당 net을 크기가 1인 list 자료형으로 temple_list에 저장
                            else:
                                temp_ports_list[tvalue]=[temp_ports_list[tvalue]]
                        # 기존의 port가 연결된 net이 array_input에 있을 경우
                        elif temp_ports_list[tvalue] in array_input:
                            
                            for jvalue in module_dict[ivalue]['input']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list
                        # 기존의 port가 연결된 net이 array_output에 있을 경우
                        elif temp_ports_list[tvalue] in array_output:
                            for jvalue in module_dict[ivalue]['output']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list
                        # 기존의 port가 연결된 net이 array_wire에 있을 경우
                        else:
                            if temp_ports_list[tvalue] in array_wire:
                                for jvalue in module_dict[ivalue]['wire']:
                                    if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                        temple_list.append(jvalue)
                                temp_ports_list[tvalue]=temple_list
                    # '{_}' 결합 연산자로 묶여있는 경우
                    else:
                        # '{}'의 안을 ','를 기준으로 쪼개어 just_ports에 list 자료형으로 저장
                        just_ports=temp_ports_list[tvalue].replace('{','').replace('}','').split(', ')
                        # just_ports에 있는 각 요소들을 판단 : '[]'이 있는 배열의 형태의 net인 경우, array_input 혹은 array_output 혹은 array_wire에 포함된 net인 경우, 단일 비트인 경우
                        for jvalue in just_ports:
                            temp_component=jvalue.strip()
                            # '[]'이 있는 배열의 형태의 net인 경우
                            if ':' in temp_component:
                                large_idx=int(temp_component.split(']')[0].split(':')[0].split('[')[1])
                                small_idx=int(temp_component.split(']')[0].split(':')[1])
                                if large_idx>small_idx:
                                    for fdx in range(large_idx-small_idx+1):
                                        temple_list.append(temp_component.split('[')[0]+'['+str(large_idx-fdx)+']')
                                elif small_idx>large_idx:
                                    for fdx in range(small_idx-large_idx+1):
                                        temple_list.append(temp_component.split('[')[0]+'['+str(large_idx+fdx)+']')
                            # array_input에 포함된 net인 경우
                            elif temp_component in array_input:
                                for fvalue in module_dict[ivalue]['input']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            # array_output에 포함된 net인 경우
                            elif temp_component in array_output:
                                for fvalue in module_dict[ivalue]['output']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            # array_wire에 포함된 net인 경우
                            elif temp_component in array_wire:
                                for fvalue in module_dict[ivalue]['wire']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            # 단일 비트인 경우
                            else:
                                temple_list.append(temp_component)
                        temp_ports_list[tvalue]=temple_list

                    # ivalue가 macro의 경우와 submodule인 경우로 나누어 각 경우마다 정의된 port를 연결된 net들의 group에 일대일 대응이 되도록 port를 쪼갠 후 해당 ivalue의 새로운 port의 정보를 new_ports_list에 저장
                    # ivalue의 id가 macro인 경우: 함수 macro_ports를 사용
                    if kvalue in module_dict[ivalue]['components_counts']:
                        new_ports_list.update(macro_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue]))
                    # ivalue의 id가 또다른 module인 경우: 함수 module_ports를 사용
                    else:
                        new_ports_list.update(module_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue],module_dict))
                # macro와 submodule의 array_port들을 하나씩 분리하여 최신화
                module_dict[ivalue][kvalue]['ports']=new_ports_list

#################################### 여기서부터 주석 시작

    '''print('@#@#@#@###@##@#@#@##@#@#')
    for ivalue in module_dict:
        temp_output=dict()
        for kvalue in module_dict[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='wire' and kvalue!='components_counts' and kvalue !='module_counts':
                for tvalue in module_dict[ivalue][kvalue]['ports']:
                    if module_dict[ivalue][kvalue]['ports'][tvalue] in module_dict[ivalue]['output']:
                        if module_dict[ivalue][kvalue]['ports'][tvalue] not in temp_output:
                            temp_output.update({module_dict[ivalue][kvalue]['ports'][tvalue]:list()})
                        temp_output[module_dict[ivalue][kvalue]['ports'][tvalue]].append(kvalue+' '+tvalue)
        for kvalue in temp_output:
            if '['in kvalue:
                continue
            if len(temp_output[kvalue])>1:
                print(ivalue)
                print(kvalue)
                print(temp_output[kvalue])
                print()'''
    return [module_dict,top_module]





def module_ports(id,port_name,port_list,All):

    new_ports_compo=dict()
    array_input=list()
    array_output=list()
    array_wire=list()

    for ivalue in All[id]['input']:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_input:
                array_input.append(ivalue.split('[')[0])

    for ivalue in All[id]['output']:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_output:
                array_output.append(ivalue.split('[')[0])

    if 'wire' in All[id]:
        for ivalue in All[id]['wire']:
            if '[' in ivalue:
                if ivalue.split('[')[0] not in array_wire:
                    array_wire.append(ivalue.split('[')[0])

    temp_array_list=list()
    if port_name not in array_input and port_name not in array_output and port_name not in array_wire:
        new_ports_compo.update({port_name:port_list[0]})
        return new_ports_compo

    elif port_name in array_input:
        for ivalue in All[id]['input']:
            if ivalue.startswith(port_name+'['):
                temp_array_list.append(ivalue)

    elif port_name in array_output:
        for ivalue in All[id]['output']:
            if ivalue.startswith(port_name+'['):
                temp_array_list.append(ivalue)

    elif port_name in array_wire:
        for ivalue in All[id]['wire']:
            if ivalue.startswith(port_name+'['):
                temp_array_list.append(ivalue)
    else:
        print('Error : the port not in definition')


    for idx in range(len(temp_array_list)):
        new_ports_compo.update({temp_array_list[idx]:port_list[idx]})

    return new_ports_compo





   
def macro_ports(id,port_name,port_list):
    ### lef 파일에서 단일 포트가 배열로 정의 되지 않는다면 => ###    ### 삭제하기 !!
    new_ports_compo=dict()

    if id=='spsram_hd_256x23m4m':
        if port_name=='RTSEL' or port_name=='WTSEL':
            num=2
        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            num=23
        elif port_name=='A' or port_name=='AM':
            num=8
        else:
            num=1

    elif id=='spsram_hd_2048x32m4s':
        if port_name=='RTSEL' or port_name=='WTSEL':
            num=2
        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            num=32
        elif port_name=='A' or port_name=='AM':
            num=11
        else:
            num=1

    elif id=='spsram_hd_256x22m4m':
        if port_name=='RTSEL' or port_name=='WTSEL':
            num=2
        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            num=22
        elif port_name=='A' or port_name=='AM':
            num=8
        else:
            num=1

    elif id=='sprf_hs_128x38m2s':
        if port_name=='TSEL':
            num=2
        elif port_name=='Q' or port_name=='BWEB' or port_name=='D':
            num=38
        elif port_name=='A':
            num=7
        else:
            num=1
     
    elif id=='TS1N40LPB1024X32M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=10
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=32
        else:
            num=1
    
    elif id=='TS1N40LPB2048X36M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=11
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=36
        else:
            num=1

    elif id=='TS1N40LPB256X23M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=8
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=23
        else:
            num=1

    elif id=='TS1N40LPB128X63M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=7
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=63
        else:
            num=1

    elif id=='TS1N40LPB256X12M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=8
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=12
        else:
            num=1 

    elif id=='TS1N40LPB512X23M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=9
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=23
        else:
            num=1 

    elif id=='TS1N40LPB1024X128M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=10
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=128
        else:
            num=1 
        
    elif id=='TS1N40LPB2048X32M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=11
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=32
        else:
            num=1 

    elif id=='TS1N40LPB256X22M4FWBA':
        if port_name=='AM' or port_name=='A':
            num=8
        elif port_name=='BWEBM' or port_name=='BWEB' or port_name=='DM' or port_name=='D' or port_name=='Q':
            num=22
        else:
            num=1 


    if num!=1:
        for idx in range(num):
            new_ports_compo.update({port_name+'['+str(num-1-idx)+']':port_list[idx]})
    else:
        new_ports_compo.update({port_name:port_list[0]})
        
    return new_ports_compo








def get_add_mod(All,upper_module,info):
    
    for ivalue in info[All[upper_module]['module']]['module_counts']:
        temp_id=info[All[upper_module]['module']][ivalue]['id']
        All.update({upper_module+'/'+ivalue:{'info':info[temp_id],'module':temp_id}})
        get_add_mod(All,upper_module+'/'+ivalue,info)

    return All




def checking_list_func(All,ivalue,toptop):
    temp_list=ivalue.split('/')
    temp_preview=str()
    for idx in range(len(temp_list)):
        if idx==0:
            if temp_list[idx] not in All[toptop]:
                print('Error : '+temp_list[idx]+' not in topmodule')
            else:
                temp_preview=All[toptop][temp_list[idx]]['id']
        else:
            if temp_list[idx] not in All[temp_preview]:
                print('Error : '+temp_list[idx]+' not in '+temp_preview)
            else:
                temp_preview=All[temp_preview][temp_list[idx]]['id']
    return 0




def get_tree(All,diff):
    top_module=All[1]
    All=All[0]

    all_tree=dict()
    treeAll=dict()
    for ivalue in All[top_module]['module_counts']:
        temp_id=All[top_module][ivalue]['id']
        treeAll.update({ivalue:{'info':All[temp_id],'module':temp_id}})
        all_tree=get_add_mod(treeAll,ivalue,All)

    list_tree_keys=list(all_tree.keys())
    for ivalue in list_tree_keys:
        checking_list_func(All,ivalue,top_module)
    
    for ivalue in all_tree:
        all_tree[ivalue].update({'submodule':{}})
        for kvalue in All[all_tree[ivalue]['module']]['module_counts']:
            all_tree[ivalue]['submodule'].update({kvalue:All[all_tree[ivalue]['module']][kvalue]['id']})

    components_list_with_ports=list()
    codict=dict()
    only_components=list()
    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            only_components.append(ivalue+'/'+kvalue)
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:
                components_list_with_ports.append(ivalue+'/'+kvalue+' '+tvalue)
                codict.update({ivalue+'/'+kvalue+' '+tvalue:all_tree[ivalue]['info'][kvalue]['id']})
    for ivalue in All[top_module]['components_counts']:
        only_components.append(ivalue)
        for kvalue in All[top_module][ivalue]['ports']:
            components_list_with_ports.append(ivalue+' '+kvalue)
            codict.update({ivalue+' '+kvalue:All[top_module][ivalue]['id']})


    will_del=list()
    for ivalue in components_list_with_ports:
        if ivalue.split('/')[-1].startswith('assign_') and '_assign_' in ivalue and ivalue.split(' ')[1]=='A':
            will_del.append(ivalue)
    for ivalue in will_del:
        components_list_with_ports.remove(ivalue)

    will_del=list()
    for ivalue in only_components:
        if ivalue.split('/')[-1].startswith('assign_') and '_assign_' in ivalue:
            will_del.append(ivalue)
    for ivalue in will_del:
        only_components.remove(ivalue)


    print(len(components_list_with_ports))
    print(len(only_components))
    print()

    net_group=dict()
    debt_group=dict()
    

    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:

                if all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b0':
                    if 'constant0' not in net_group:
                        net_group.update({'constant0':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant0']:
                        net_group['constant0'].append(ivalue+'/'+kvalue+' '+tvalue)

                elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b1':
                    if 'constant1' not in net_group:
                        net_group.update({'constant1':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant1']:
                        net_group['constant1'].append(ivalue+'/'+kvalue+' '+tvalue)


    temp_all_tree=copy.deepcopy(all_tree)
    #print(all_tree['u_l2cc/pl310_present_u_pl310_top']['info'])

    ccc=int()
    while True:
        counting=int()
        ccc=ccc+1
        will_del=list()

        #print(ccc)
        #print(json.dumps(debt_group,indent=4))
        #print()

        temp_debt_dict=dict()

        for ivalue in debt_group:
            tempports=ivalue.split('/')[-1]
            tempsub=ivalue.split('/')[-2]
            current_mod=ivalue.split('/'+tempsub+'/'+tempports)[0]

            if ivalue==current_mod:
                temp_debt_dict.update({ivalue:debt_group[ivalue]})

        for ivalue in debt_group:
            tempports=ivalue.split('/')[-1]
            tempsub=ivalue.split('/')[-2]
            current_mod=ivalue.split('/'+tempsub+'/'+tempports)[0]

            if ivalue==current_mod:
                continue
            
            if tempports not in all_tree[current_mod]['info'][tempsub]['ports']:
                submodule_id=all_tree[current_mod]['submodule'][tempsub]
                if tempports in All[submodule_id]['output']:
                    if ivalue not in net_group:
                        net_group.update({ivalue:list()})
                    for rvalue in debt_group[ivalue]:
                        net_group[ivalue].append(rvalue)
                    continue

            if 'wire' in all_tree[current_mod]['info']:
                #print(ivalue) 문제가 되는 ivalue= u_l2cc/pl310_present_u_pl310_top/TAGCLKOUT
                if all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['wire']:
                    if current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports] not in net_group:
                        net_group.update({current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]:list()})
                    for kvalue in debt_group[ivalue]:
                        if kvalue not in net_group[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]]:
                            net_group[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]].append(kvalue)
            
            if all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['input'] or all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['output']:
                if current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports] not in temp_debt_dict:

                    temp_debt_dict.update({current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]:list()})
                for kvalue in debt_group[ivalue]:
                    if kvalue not in temp_debt_dict[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]]:
                        temp_debt_dict[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]].append(kvalue)
                
            elif all_tree[current_mod]['info'][tempsub]['ports'][tempports]=='1\'b0':
                if 'constant0' not in net_group:
                    net_group.update({'constant0':list()})
                for kvalue in debt_group[ivalue]:
                    if kvalue not in net_group['constant0']:
                        net_group['constant0'].append(kvalue)

            elif all_tree[current_mod]['info'][tempsub]['ports'][tempports]=='1\'b1':
                if 'constant1' not in net_group:
                    net_group.update({'constant1':list()})
                for kvalue in debt_group[ivalue]:
                    if kvalue not in net_group['constant1']:
                        net_group['constant1'].append(kvalue)
            

        debt_group=copy.deepcopy(temp_debt_dict)

        for ivalue in all_tree:
            if len(all_tree[ivalue]['submodule'])==0 and '/' in ivalue:
                counting=counting+1
                will_del.append(ivalue)
                for kvalue in all_tree[ivalue]['info']['components_counts']:
                    for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:

                        if 'wire' in all_tree[ivalue]['info']:

                            if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['wire']:
                                if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in net_group:
                                    net_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                                
                                net_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)


                        if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['input'] or all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['output']:
                            if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in debt_group:
                                debt_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                            debt_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)
                        
                        elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b0':
                            if 'constant0' not in net_group:
                                net_group.update({'constant0':list()})
                            if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant0']:
                                net_group['constant0'].append(ivalue+'/'+kvalue+' '+tvalue)

                        elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b1':
                            if 'constant1' not in net_group:
                                net_group.update({'constant1':list()})
                            if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant1']:
                                net_group['constant1'].append(ivalue+'/'+kvalue+' '+tvalue)
        
        for ivalue in will_del:
            del all_tree[ivalue]
            del all_tree[ivalue.split('/'+ivalue.split('/')[-1])[0]]['submodule'][ivalue.split('/')[-1]]

        if counting==0:
            break

######################## top module의 sub module 처리
    
    temp_debt_dict=dict()
    for ivalue in debt_group:
        if 'wire' in all_tree[ivalue.split('/')[0]]['info']:
            if ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['wire']:
                if ivalue not in net_group:
                    net_group.update({ivalue:list()})
                net_group[ivalue].extend(debt_group[ivalue])
        
        if ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['input'] or ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['output']:
            if ivalue not in temp_debt_dict:
                temp_debt_dict.update({ivalue:debt_group[ivalue]})
            temp_debt_dict[ivalue].extend(debt_group[ivalue])
        
    debt_group=temp_debt_dict

    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:
                if 'wire' in all_tree[ivalue]['info']:
                    if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['wire']:
                        if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in net_group:
                            net_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                        net_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)
                
                if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['input'] or all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['output']:
                    if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in debt_group:
                        debt_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                    debt_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)

                elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b0':
                    if 'constant0' not in net_group:
                        net_group.update({'constant0':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant0']:
                        net_group['constant0'].append(ivalue+'/'+kvalue+' '+tvalue)

                elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b1':
                    if 'constant1' not in net_group:
                        net_group.update({'constant1':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant1']:
                        net_group['constant1'].append(ivalue+'/'+kvalue+' '+tvalue)


######################## top module 처리
    for ivalue in debt_group:

        if 'wire' in All[top_module]:
            if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['wire']:
                if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] not in net_group:
                    net_group.update({All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]:list()})
                
                for kvalue in debt_group[ivalue]:
                    if kvalue not in net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]]:
                        net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]].append(kvalue)

        if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['input'] or All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['output']:
            if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] not in net_group:
                net_group.update({All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]:list()})

            for kvalue in debt_group[ivalue]:
                if kvalue not in net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]]:
                    net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]].append(kvalue)


    for ivalue in All[top_module]['components_counts']:
        for kvalue in All[top_module][ivalue]['ports']:

            if All[top_module][ivalue]['ports'][kvalue]=='1\'b0':
                if 'constant0' not in net_group:
                    net_group.update({'constant0':list()})
                if ivalue+' '+kvalue not in net_group['constant0']:
                    net_group['constant0'].append(ivalue+' '+kvalue)
                continue

            elif All[top_module][ivalue]['ports'][kvalue]=='1\'b1':
                if 'constant1' not in net_group:
                    net_group.update({'constant1':list()})
                if ivalue+' '+kvalue not in net_group['constant1']:
                    net_group['constant1'].append(ivalue+' '+kvalue)
                continue

            if All[top_module][ivalue]['ports'][kvalue] not in net_group:
                net_group.update({All[top_module][ivalue]['ports'][kvalue]:list()})
            net_group[All[top_module][ivalue]['ports'][kvalue]].append(ivalue+' '+kvalue)


########################################################################################################################################################################## assign 처리
    assign_temp=dict()
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:
            if kvalue.split('/')[-1].startswith('assign_') and '_assign_' in kvalue.split('/')[-1] and kvalue.split(' ')[1]=='A':
                assign_temp.update({kvalue.split(' ')[0]:ivalue})

    checking_list=dict()
    for ivalue in assign_temp:
        temp_assign=ivalue.split('/')[-1]
        first_assign=temp_assign.split('_assign_')[0].split('assign_')[1]
        second_assign=temp_assign.split('_assign_')[1]
        if ivalue.split(ivalue.split('/')[-1])[0] not in checking_list:
            checking_list.update({ivalue.split(ivalue.split('/')[-1])[0]:dict({'wires':list(),'groups':list()})})
        if first_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(first_assign)
        if second_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(second_assign)
        checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['groups'].append([first_assign,second_assign])



    sum_assign=dict()
    for ivalue in checking_list:
        previous_wire_counts=int()
        will_exterminate_group=list()
        will_add_wire_groups=list()
        will_delete_group=list()
        while len(checking_list[ivalue]['wires'])!=0:
            che='che'
            if len(will_add_wire_groups)!=0:
                sum_assign[ivalue].extend([will_add_wire_groups])

            for kvalue in will_exterminate_group:
                if kvalue in checking_list[ivalue]['wires']:
                    checking_list[ivalue]['wires'].remove(kvalue)
            
            for kvalue in will_delete_group:
                if kvalue in checking_list[ivalue]['groups']:
                    checking_list[ivalue]['groups'].remove(kvalue)
            

            if ivalue not in sum_assign:
                sum_assign.update({ivalue:list()})
            will_exterminate_group=list()
            will_add_wire_groups=list()
            for kdx in range(len(checking_list[ivalue]['groups'])):
                if len(sum_assign[ivalue])==0:
                    sum_assign[ivalue].append(checking_list[ivalue]['groups'][kdx])
                    will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                    will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                    will_delete_group.append(checking_list[ivalue]['groups'][kdx])

                else:
                    for tdx in range(len(sum_assign[ivalue])):
                        if checking_list[ivalue]['groups'][kdx][0] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][1] not in sum_assign[ivalue][tdx]:
                            che='ehc'
                            sum_assign[ivalue][tdx].append(checking_list[ivalue]['groups'][kdx][1])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        elif checking_list[ivalue]['groups'][kdx][1] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][0] not in sum_assign[ivalue][tdx]:
                            che='ehc'
                            sum_assign[ivalue][tdx].append(checking_list[ivalue]['groups'][kdx][0])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        elif checking_list[ivalue]['groups'][kdx][0] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][1] in sum_assign[ivalue][tdx]:
                            che='ehc'
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        else:
                            if len(checking_list[ivalue]['wires'])!=previous_wire_counts:
                                che='ehc'
                                continue

                    if che=='che':
                                will_add_wire_groups=[checking_list[ivalue]['groups'][kdx][0],checking_list[ivalue]['groups'][kdx][1]]
                                will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                                will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                                will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                                break

            previous_wire_counts=len(checking_list[ivalue]['wires'])

    
    group_assign=dict()
    for ivalue in sum_assign:
        group_assign.update({ivalue:list()})
        for tdx in range(len(sum_assign[ivalue])):
            group_assign[ivalue].append([])

    for ivalue in assign_temp:
        for kvalue in sum_assign:
            for tdx in range(len(sum_assign[kvalue])):
                if ivalue.split(ivalue.split('/')[-1])[0]==kvalue and ivalue.split('/')[-1].split('_assign_')[0].split('assign_')[1] in sum_assign[kvalue][tdx] \
                    and ivalue.split('/')[-1].split('_assign_')[1].split(' ')[0] in sum_assign[kvalue][tdx]:
                    group_assign[kvalue][tdx].append(assign_temp[ivalue])

    net_group_assign=dict()
    for ivalue in group_assign:
        net_group_assign.update({ivalue:dict()})

        temp_number=int()
        for tdx in range(len(group_assign[ivalue])):
            name_of_assign='assign_group_'+str(temp_number)
            temp_number=temp_number+1
            
            for kdx in range(len(group_assign[ivalue][tdx])):
                if '/' not in group_assign[ivalue][tdx][kdx]:
                    name_of_assign=group_assign[ivalue][tdx][kdx]
                    temp_number=temp_number-1
            net_group_assign[ivalue].update({name_of_assign:[]})

            for kdx in range(len(group_assign[ivalue][tdx])):
                for rvalue in net_group[group_assign[ivalue][tdx][kdx]]:
                    if rvalue not in net_group_assign[ivalue][name_of_assign]:
                        net_group_assign[ivalue][name_of_assign].append(rvalue)

    will_add_net=dict()
    for ivalue in net_group_assign:
        for kvalue in net_group_assign[ivalue]:
            if kvalue.startswith('assign_group_'):
                will_add_net.update({ivalue+kvalue:net_group_assign[ivalue][kvalue]})
            else:
                will_add_net.update({kvalue:net_group_assign[ivalue][kvalue]})

    for ivalue in will_add_net:
        will_del_list=list()
        for kvalue in will_add_net[ivalue]:
            if kvalue.split('/')[-1].split(' ')[1]=='A' and kvalue.split('/')[-1].startswith('assign_') and '_assign_' in kvalue.split('/')[-1]:
                will_del_list.append(kvalue)
        for kvalue in will_del_list:
            will_add_net[ivalue].remove(kvalue)
    
    for ivalue in group_assign:
        for kdx in range(len(group_assign[ivalue])):
            for tdx in range(len(group_assign[ivalue][kdx])):
                del net_group[group_assign[ivalue][kdx][tdx]]

    real_net_group=copy.deepcopy(net_group)
    for idx,ivalue in enumerate(will_add_net):
        net_group.update({'assignModule'+str(idx):will_add_net[ivalue]})
        real_net_group.update({ivalue:will_add_net[ivalue]})

    

########################################################################################################################################################################## checking 영역


    checking_net_components=list()
    checking_only_components=dict()
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:

            checking_net_components.append(kvalue)
            checking_only_components.update({kvalue.split(' ')[0]:str('tpmglwns1!@!@')})

    print(len(checking_net_components))
    print(len(checking_only_components))
    print()

    with open('../../data/'+diff+'/'+'checking_net_components.json','w') as fw:
        json.dump(checking_net_components,fw,indent=4)
    fw.close()
    with open('../../data/'+diff+'/'+'components_list_with_ports.json','w') as fw:
        json.dump(components_list_with_ports,fw,indent=4)
    fw.close()


    for ivalue in net_group:
        for kvalue in net_group[ivalue]:
            if '/' in kvalue:
                checking_only_components[kvalue.split(' ')[0]]=temp_all_tree[kvalue.split('/'+kvalue.split('/')[-1])[0]]['info'][kvalue.split('/')[-1].split(' ')[0]]['id']
            else:
                checking_only_components[kvalue.split(' ')[0]]=All[top_module][kvalue.split('/')[-1].split(' ')[0]]['id']
                
        if ivalue in All[top_module]['input']:
            net_group[ivalue].append('PIN '+ivalue)
            checking_only_components.update({'PIN '+ivalue:'external_input_PIN'})
        elif ivalue in All[top_module]['output']:
            net_group[ivalue].append('PIN '+ivalue)
            checking_only_components.update({'PIN '+ivalue:'external_output_PIN'})



    for idx,ivalue in enumerate(will_add_net):
        if ivalue in All[top_module]['input'] or ivalue in All[top_module]['output']:
            if 'PIN '+ivalue not in net_group['assignModule'+str(idx)]:
                net_group['assignModule'+str(idx)].append('PIN '+ivalue)
            if 'PIN '+ivalue not in real_net_group[ivalue]:
                real_net_group[ivalue].append('PIN '+ivalue)

            if ivalue in All[top_module]['input']:
                checking_only_components.update({'PIN '+ivalue:'external_input_PIN'})
            else:
                checking_only_components.update({'PIN '+ivalue:'external_output_PIN'})

    with open('../../data/'+diff+'/'+'checking_id_components.json','w') as fw:
        json.dump(checking_only_components,fw,indent=4)
    fw.close()


        #if len(net_group[ivalue])==1:
        #    if '/' not in ivalue:
        #        if ivalue in All[top_module]['input'] or ivalue in All[top_module]['output']:
        #            continue
        #        else:
        #            print(ivalue,net_group[ivalue],'TTTTT')
        #    else:
        #        print(ivalue,net_group[ivalue])


    print(len(net_group))
    print()
    new_net_group=dict()
    for ivalue in net_group:
        conseq=str()
        if '/' in ivalue:
            temp_nick=ivalue.split('/'+ivalue.split('/')[-1])[0].split('/')
            tempo=list()
            preview=str()
            for kdx in range(len(temp_nick)):
                if kdx==0:
                    tempo.append(All[top_module][temp_nick[kdx]]['id'])
                    preview=All[top_module][temp_nick[kdx]]['id']
                else:
                    tempo.append(All[preview][temp_nick[kdx]]['id'])
                    preview=All[preview][temp_nick[kdx]]['id']
            for kdx in range(len(tempo)):
                if kdx==0:
                    conseq=tempo[kdx]
                else:
                    conseq=conseq+'/'+tempo[kdx]
            conseq=conseq+'/'+ivalue.split('/')[-1]
        else:
            conseq=ivalue
        new_net_group.update({conseq:list()})

        for kvalue in net_group[ivalue]:
            result=str()
            if '/' in kvalue:
                temp_nick=kvalue.split('/'+kvalue.split('/')[-1])[0].split('/')
                tempo=list()
                preview=str()
                for kdx in range(len(temp_nick)):
                    if kdx==0:
                        tempo.append(All[top_module][temp_nick[kdx]]['id'])
                        preview=All[top_module][temp_nick[kdx]]['id']
                    else:
                        tempo.append(All[preview][temp_nick[kdx]]['id'])
                        preview=All[preview][temp_nick[kdx]]['id']
                for kdx in range(len(tempo)):
                    if kdx==0:
                        result=tempo[kdx]
                    else:
                        result=result+'/'+tempo[kdx]
                result=result+'/'+kvalue.split('/')[-1]
            else:
                result=kvalue
            new_net_group[conseq].append(result)


    jun=dict()
    for ivalue in new_net_group:
        if '/' not in ivalue:
            che=str()
            for kvalue in new_net_group[ivalue]:
                if 'PIN ' in kvalue:
                    che='che'
                    break
            if che=='che' and 'assignModule' not in ivalue:
                jun.update({'PIN '+ivalue:new_net_group[ivalue]})
            else:
                if 'assignModule' not in ivalue and ivalue!='constant0' and ivalue!='constant1':
                    jun.update({top_module+'/'+ivalue:new_net_group[ivalue]})
                else:
                    jun.update({ivalue:new_net_group[ivalue]})
        else:
            jun.update({ivalue.split('/'+ivalue.split('/')[-1])[0].split('/')[-1]+'/'+ivalue.split('/')[-1]:new_net_group[ivalue]})

    for ivalue in jun:
        temp=list()
        for kvalue in jun[ivalue]:
            if kvalue.startswith('PIN '):
                temp.append(kvalue)
            elif '/' not in kvalue:
                temp.append(top_module+'/'+kvalue)
            else:
                last_slash=kvalue.split('/')[-1]
                previous_slash=kvalue.split('/'+last_slash)[0].split('/')[-1]
                temp.append(previous_slash+'/'+last_slash)
        jun[ivalue]=temp

    return [jun,real_net_group]
    #return net_group





if __name__=="__main__":
    #get_tree(str())


    difficulty='medium' ##################### difficulty 는 easy 와 medium 두가지 경우가 있다.
    difficulty='easy'
    file='../../data/'+difficulty+'/'+difficulty+'.v'
    #file='../../data/easy/easy.v'
    start=time.time()

    kkk=get_module_dict(file)

    mmm=get_tree(kkk,difficulty)

    print('############')

    with open('../../data/'+difficulty+'/'+'nets_modified_by_june.json','w') as fw:
        json.dump(mmm[0],fw,indent=4)
    fw.close()
    with open('../../data/'+difficulty+'/'+'nets_from_june.json','w') as fw:
        json.dump(mmm[1],fw,indent=4)
    fw.close()

    print(time.time()-start)
