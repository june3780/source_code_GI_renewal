import json
import copy
import time
import sys
import os

def get_module_dict(wherethemodule): #verilog file parsing
    #### 해당 verilog 파일의 파일명: where_the_v+'.v'
    where_the_v=wherethemodule.split('.v')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_v
    the_v=where_the_v.split('/')[-1]
    upper_directory=wherethemodule.split('/'+the_v+'.v')[0]

    #### 해당 verilog 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_v not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_v)

    #### macro_list: 해당 verilog에 사용되는 macro id들의 집합, 새로운 macro가 있을 경우 update해야한다.
    macro_list=['spsram_hd_256x23m4m','spsram_hd_2048x32m4s','spsram_hd_256x22m4m','sprf_hs_128x38m2s'\
    ,'TS1N40LPB1024X32M4FWBA','TS1N40LPB2048X36M4FWBA','TS1N40LPB256X23M4FWBA','TS1N40LPB128X63M4FWBA'\
    ,'TS1N40LPB256X12M4FWBA','TS1N40LPB512X23M4FWBA','TS1N40LPB1024X128M4FWBA','TS1N40LPB2048X32M4FWBA'\
    ,'TS1N40LPB256X22M4FWBA','spsram_hd_16384x32m32']

    #### verilog 파일 읽기
    with open(wherethemodule,'r') as fw:
        module_str=fw.readlines()
    fw.close()

    #### 'module-endmodule'을 기준으로 module_list 각 module의 문장들을 합쳐서 저장
    module_list=['']
    for ivalue in module_str:
        #### verilog 파일에서의 주석처리
        if ivalue.strip().startswith('//'):
            continue
        #### module_list의 마지막 인덱스에 module의 문장을 붙여서 최신화
        if module_list[-1]=='':
            module_list[-1]=ivalue.strip()
        else:
            module_list[-1]=module_list[-1]+' '+ivalue.strip()
        #### endmodule이 나올 경우, module_list에 새로운 인덱스 추가
        if ivalue.replace('\n','').strip().endswith('endmodule'):
            module_list.append('')
    #### 마지막 module의 endmodule에 의한 아무 내용 없는 인덱스 제거
    del module_list[-1]


    cc=int()
    #### module_list의 각 module을 parsing하여 module_dict에 각 module의 내용 저장, assign에 대한 내용을 assign_dict에 저장
    module_dict=dict()
    assign_dict=dict()
    #### 각 module에 접근 module_list에는 module에 대한 내용이 하나의 문장으로 합쳐져 있는 상태
    for ivalue in module_list:
        cc=cc+1
        module_name=str()
        #### 각 module들의 문장을 ';'을 기준으로 나눠서 temp_str에 각 문장들을 저장
        temp_str=ivalue.split(';')
        for kvalue in temp_str:
            #### 각 문장들의 첫 단어들을 통해 분류하여 module 내용을 저장, 현재 함수가 처리한 첫 단어들의 경우 : [module, input, output, wire, assign, endmodule]
            #### 나머지의 경우들을 components_cell 혹은 macro, 또는 submodule로 간주한다.

            #### 첫 단어가 module인 경우: module_dict에 module의 id를 추가
            if kvalue.strip().startswith('module '):
                module_name=kvalue.split(' ')[1]
                module_dict.update({module_name:{}})

            #### 첫 단어가 input인 경우: 해당 module에 input 이라는 key를 추가, input에 해당 net을 추가, multi-input을 가질경우 각 요소들을 나눠 input에 해당 net들을 추가
            elif kvalue.strip().startswith('input '):
                module_dict=get_module_net(module_dict,module_name,kvalue,'input')

            #### 첫 단어가 output인 경우: 해당 module에 output 이라는 key를 추가, output에 해당 net을 추가, multi-output을 가질경우 각 요소들을 나눠 output에 해당 net들을 추가
            elif kvalue.strip().startswith('output '):
                module_dict=get_module_net(module_dict,module_name,kvalue,'output')


            #### 첫 단어가 wire인 경우: 해당 module에 wire 이라는 key를 추가, wire에 해당 net을 추가, multi-wire을 가질경우 각 요소들을 나눠 wire에 해당 net들을 추가
            elif kvalue.strip().startswith('wire '):
                module_dict=get_module_net(module_dict,module_name,kvalue,'wire')


            #### 첫 단어가 assign인 경우: 해당 module을 assign_dict에 추가하고, assign A=B;를 {A:B}라는 딕셔너리로 바꾼 후 해당 module에 추가
            elif kvalue.strip().startswith('assign '):
                # 해당 moudule을 assign_dict에 추가
                if module_name not in assign_dict:
                    assign_dict.update({module_name:dict()})
                # temp_output: A에 해당하는 net
                temp_output=kvalue.split('assign')[1].split('=')[0].strip()
                # temp_value: B에 해당하는 net
                temp_value=kvalue.split('assign')[1].split('=')[1].strip()
                assign_dict[module_name].update({temp_output:temp_value})

            #### 첫 단어가 module인 경우: 다음 인덱스로 넘어간다.
            elif kvalue.strip().startswith('endmodule'):
                continue

            #### 첫 단어가 처리되는 단어에 포함되지 않을 경우, standard_cell 혹은 macro나 submodule로 간주한다.
            else:
                #### component_or_module: standard_cell 혹은 macro나 submodule
                component_or_module=kvalue.strip().split(' ')[0].strip()
                #### list_of_line: 해당 component_or_module이 가지는 port와 그에 연결된 net
                list_of_line=' '.join(kvalue.strip().split(' ')[2:])
                #### module_dict에 해당 module에 component_or_module 추가 (해당 component_or_module의 이름을 저장한다, 'id'에 standard_cell이나 macro의 'id' 혹은 submodule의 module의 'id'로 추가)
                temp_name=kvalue.strip().split(' ')[1].strip()
                module_dict[module_name].update({temp_name:{'id':component_or_module}})
                #### 해당 component_or_module에 대한 port와 그에 연결된 net 추가
                module_dict[module_name][temp_name].update({'ports':{}})
                for tvalue in list_of_line.split('.'):
                    if '(' in tvalue and ')' in tvalue:
                        module_dict[module_name][temp_name]['ports'].update({tvalue.split('(')[0].strip():tvalue.split('(')[1].strip().split(')')[0].strip()})


    top_module=str()
    #### 모든 module의 id를 module_list에 저장
    module_list=list(module_dict.keys())
    #### 각 module에 추가한 standard_cell 혹은 macro나 submodule인 요소들을 components_counts에 standard_cell과 macro들을, module_counts에 submodule을 저장하여 해당 module에 추가
    for ivalue in module_dict:
        #### 각 module에 components_counts와 module_counts 추가
        module_dict[ivalue].update({'components_counts':{}})
        module_dict[ivalue].update({'module_counts':{}})
        #### 각 module마다 components_counts와 module_counts로 나누기
        for kvalue in module_dict[ivalue]:
            #### module의 standard_cell 혹은 macro나 submodule인 요소들만 접근
            if kvalue!='input' and kvalue!='output' and kvalue!='wire' and kvalue!='components_counts' and kvalue!='module_counts':
                #### 해당 요소의 id가 module_dict에 선언된 module에 포함이 안될 경우
                if module_dict[ivalue][kvalue]['id'] not in module_dict:
                    module_dict[ivalue]['components_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})
                #### 해당 요소의 id가 module_dict에 선언된 module 중 하나일 경우
                else:
                    module_dict[ivalue]['module_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})
                    #### top_module을 찾기 위해 안쓰인 module을 제외한 module들을 module_list에서 제거한다.
                    if module_dict[ivalue][kvalue]['id'] in module_list:
                        module_list.remove(module_dict[ivalue][kvalue]['id'])
    #### 한번도 submodule로 쓰인 적 없는 module이 top_module이다.
    top_module=module_list[0]
    #### 해당 verlog에서의 top_module출력
    print(top_module)


    #### assign이 있는 module에 예외 처리
    for ivalue in assign_dict:
        #### {A:B}인 딕셔너리가 assign_dict[ivalue]에 있다. ex) kvalue: A, assign_dict[kvalue]: B
        for kvalue in assign_dict[ivalue]:
            #### assign에 의해 wire와 input, 혹은 wire와 output에 동시에 정의된 net의 wire를 지워준다.
            if kvalue in module_dict[ivalue]['wire']:
                module_dict[ivalue]['wire'].remove(kvalue)
            if assign_dict[ivalue][kvalue] in module_dict[ivalue]['wire']:
                module_dict[ivalue]['wire'].remove(assign_dict[ivalue][kvalue])
            #### assign을 가지는 특수한 module을 submodule로 갖는 module 탐색
            for rvalue in module_dict:
                for tvalue in module_dict[rvalue]['module_counts']:
                    #### rvalue: assign을 가지는 module을 submodule로 가지는 module
                    #### tvalue: rvalue 의 submodule 중 하나로 assign을 가지는 module
                    if ivalue==module_dict[rvalue]['module_counts'][tvalue]:
                        #### assign_A_assign_B 와 assign_B_assign_A 라는 임의의 component를 rvalue인 moudule에 추가해준다.

                        #### assign_A_assign_B의 id는 assign_A이다.
                        #### assign_A_assign_B의 port는 'A' 하나이며, submodule의 A에 연결된 net과 같은 net을 assign_A_assign_B의 'A' port에 연결한다.
                        if 'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue] not in module_dict[rvalue]['components_counts']:
                            module_dict[rvalue]['components_counts'].update({'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]:str()})
                        module_dict[rvalue]['components_counts']['assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]]='assign_'+kvalue
                        if 'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue] not in module_dict[rvalue]:
                            module_dict[rvalue].update({'assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]:dict()})
                        module_dict[rvalue]['assign_'+kvalue+'_assign_'+assign_dict[ivalue][kvalue]].update({'id':'assign_'+kvalue,'ports':{'A':module_dict[rvalue][tvalue]['ports'][kvalue]}})
                        #### assign_B_assign_A의 id는 assign_B이다.
                        #### assign_B_assign_A의 port는 'A' 하나이며, submodule의 B에 연결된 net과 같은 net을 assign_B_assign_A의 'A' port에 연결한다.
                        if 'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue not in module_dict[rvalue]['components_counts']:
                            module_dict[rvalue]['components_counts'].update({'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue:str()})
                        module_dict[rvalue]['components_counts']['assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue]='assign_'+assign_dict[ivalue][kvalue]
                        if 'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue not in module_dict[rvalue]:
                            module_dict[rvalue].update({'assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue:dict()})
                        module_dict[rvalue]['assign_'+assign_dict[ivalue][kvalue]+'_assign_'+kvalue].update({'id':'assign_'+assign_dict[ivalue][kvalue],'ports':{'A':module_dict[rvalue][tvalue]['ports'][assign_dict[ivalue][kvalue]]}})



    #### module에 있는 macro와 submodule에 쓰이는 array_port들과 연결된 array_net들을 각 port와 net이 대응하도록 분리
    for ivalue in module_dict:
        array_input=list()
        array_output=list()
        array_wire=list()
        #### 하나의 module의 input들중에 같은 이름을 가지고 인덱스(배열값)만 다른 input들을 array_input에 이름만 저장
        for kvalue in module_dict[ivalue]['input']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_input:
                    array_input.append(kvalue.split('[')[0])
        #### 하나의 module의 output들중에 같은 이름을 가지고 인덱스(배열값)만 다른 output들을 array_output에 이름만 저장
        for kvalue in module_dict[ivalue]['output']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_output:
                    array_output.append(kvalue.split('[')[0])
        #### 하나의 module의 wire들중에 같은 이름을 가지고 인덱스(배열값)만 다른 wire들을 array_wire에 이름만 저장
        if 'wire' in module_dict[ivalue]:
            for kvalue in module_dict[ivalue]['wire']:
                if '[' in kvalue:
                    if kvalue.split('[')[0] not in array_wire:
                        array_wire.append(kvalue.split('[')[0])
        #### 하나의 macro와 submodule을 탐색
        for kvalue in module_dict[ivalue]:

            #### macro 혹은 submodule이 아닌 경우 continue
            if kvalue=='input' or kvalue=='output' or kvalue=='wire' or kvalue=='module_counts' or kvalue=='components_counts':
                continue
            elif module_dict[ivalue][kvalue]['id'] not in macro_list and kvalue in module_dict[ivalue]['components_counts']:
                continue
            
            #### macro 혹은 submodule인 경우
            else:
                #### 각 port별로 array 판별 및 분리
                temp_ports_list=copy.deepcopy(module_dict[ivalue][kvalue]['ports'])
                #### new_ports_list: port key에 새로 저장할 port 딕셔너리
                new_ports_list=dict()
                for tvalue in temp_ports_list:
                    #### '{_}' 결합 연산자로 묶여있지 않는 경우
                    temple_list=list()
                    if '{' not in temp_ports_list[tvalue]:
                        #### 기존의 port가 연결된 net이 array_input, array_output, array_wire에 없을 경우: 1. '[number1:number2]'배열의 net 2. 단일 비트인 net
                        if temp_ports_list[tvalue] not in array_input\
                            and temp_ports_list[tvalue] not in array_output\
                            and temp_ports_list[tvalue] not in array_wire:
                            #### 1. '[number1:number2]'배열의 net의 경우 => 해당 port에 배열 형태의 net을 분리하여 list 자료형으로 temple_list에 저장
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
                            #### 2. 단일 비트인 net의 경우 => 해당 net을 크기가 1인 list 자료형으로 temple_list에 저장
                            else:
                                temp_ports_list[tvalue]=[temp_ports_list[tvalue]]
                        #### 기존의 port가 연결된 net이 array_input에 있을 경우
                        elif temp_ports_list[tvalue] in array_input:
                            
                            for jvalue in module_dict[ivalue]['input']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list
                        #### 기존의 port가 연결된 net이 array_output에 있을 경우
                        elif temp_ports_list[tvalue] in array_output:
                            for jvalue in module_dict[ivalue]['output']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list
                        #### 기존의 port가 연결된 net이 array_wire에 있을 경우
                        else:
                            if temp_ports_list[tvalue] in array_wire:
                                for jvalue in module_dict[ivalue]['wire']:
                                    if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                        temple_list.append(jvalue)
                                temp_ports_list[tvalue]=temple_list
                    #### '{_}' 결합 연산자로 묶여있는 경우
                    else:
                        #### '{}'의 안을 ','를 기준으로 쪼개어 just_ports에 list 자료형으로 저장
                        just_ports=temp_ports_list[tvalue].replace('{','').replace('}','').split(', ')
                        #### just_ports에 있는 각 요소들을 판단 : '[]'이 있는 배열의 형태의 net인 경우, array_input 혹은 array_output 혹은 array_wire에 포함된 net인 경우, 단일 비트인 경우
                        for jvalue in just_ports:
                            temp_component=jvalue.strip()
                            #### '[]'이 있는 배열의 형태의 net인 경우
                            if ':' in temp_component:
                                large_idx=int(temp_component.split(']')[0].split(':')[0].split('[')[1])
                                small_idx=int(temp_component.split(']')[0].split(':')[1])
                                if large_idx>small_idx:
                                    for fdx in range(large_idx-small_idx+1):
                                        temple_list.append(temp_component.split('[')[0]+'['+str(large_idx-fdx)+']')
                                elif small_idx>large_idx:
                                    for fdx in range(small_idx-large_idx+1):
                                        temple_list.append(temp_component.split('[')[0]+'['+str(large_idx+fdx)+']')
                            #### array_input에 포함된 net인 경우
                            elif temp_component in array_input:
                                for fvalue in module_dict[ivalue]['input']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            #### array_output에 포함된 net인 경우
                            elif temp_component in array_output:
                                for fvalue in module_dict[ivalue]['output']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            #### array_wire에 포함된 net인 경우
                            elif temp_component in array_wire:
                                for fvalue in module_dict[ivalue]['wire']:
                                    if fvalue.startswith(temp_component+'['):
                                        temple_list.append(fvalue)
                            #### 단일 비트인 경우
                            else:
                                temple_list.append(temp_component)
                        temp_ports_list[tvalue]=temple_list

                    #### ivalue가 macro의 경우와 submodule인 경우로 나누어 각 경우마다 정의된 port를 연결된 net들의 group에 일대일 대응이 되도록 port를 쪼갠 후 해당 ivalue의 새로운 port의 정보를 new_ports_list에 저장
                    #### ivalue의 id가 macro인 경우: 함수 macro_ports를 사용
                    if kvalue in module_dict[ivalue]['components_counts']:
                        new_ports_list.update(macro_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue]))
                    #### ivalue의 id가 또다른 module인 경우: 함수 module_ports를 사용
                    else:
                        new_ports_list.update(module_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue],module_dict))
                #### macro와 submodule의 array_port들을 하나씩 분리하여 최신화
                module_dict[ivalue][kvalue]['ports']=new_ports_list


    return [module_dict,top_module]



#### 해당 net_type이 단일 비트인 경우, 멸티 비트인 경우에 따라 해당 cell의 각 port의 net정보를 update
def get_module_net(All_module,module_name,line,net_type):

    if net_type not in All_module[module_name]:
        All_module[module_name].update(({net_type:[]}))
    #### multi-net_type일 경우
    if '[' in line:
        small_idx=int(line.split(']')[0].split(':')[1])
        large_idx=int(line.split(']')[0].split(':')[0].split('[')[1])
        #### 정의된 net이 여러 개인 경우
        if ',' in line:
            temp_list=line.split('] ')[1].replace(';','').strip().split(', ')
            #### multi에 정의된 두 숫자의 3가지 경우에 따라 net_type에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
            if large_idx>small_idx:
                for jvalue in temp_list:
                    for tdx in range(large_idx-small_idx+1):
                        All_module[module_name][net_type].append(jvalue+'['+str(large_idx-tdx)+']')
            elif large_idx<small_idx:
                for jvalue in temp_list:
                    for tdx in range(small_idx-large_idx+1):
                        All_module[module_name][net_type].append(jvalue+'['+str(large_idx+tdx)+']')
            else:
                All_module[module_name][net_type].append(jvalue+'['+str(large_idx)+']')
        #### 정의된 net이 하나인 경우
        else:
            jvalue=line.split('] ')[1].replace(';','').strip()
            #### multi에 정의된 두 숫자의 3가지 경우에 따라 net_type에 추가하는 순서가 다르다. : 앞의 숫자가 더 큰 경우, 뒤의 숫자가 더 큰 경우, 두 숫자가 같은 경우
            if large_idx>small_idx:
                for tdx in range(large_idx-small_idx+1):
                    All_module[module_name][net_type].append(jvalue+'['+str(large_idx-tdx)+']')

            elif small_idx>large_idx:
                for tdx in range(small_idx-large_idx+1):
                    All_module[module_name][net_type].append(jvalue+'['+str(large_idx+tdx)+']')
            else:
                All_module[module_name][net_type].append(jvalue+'['+str(large_idx)+']')
    #### multi-net_type이 아닌 경우(단일 비트의 net_type)
    else:
        #### 정의된 net이 여러 개인 경우
        if ',' in line:
            temp_list=line.split(net_type+' ')[1].replace(';','').strip().split(', ')
            for jvalue in temp_list:
                All_module[module_name][net_type].append(jvalue)
        #### 정의된 net이 하나인 경우
        else:
            jvalue=line.split(net_type+' ')[1].replace(';','').strip()
            All_module[module_name][net_type].append(jvalue)

    return All_module









#### 해당 submodule의 연결된 net을 최신화, 멀티비트를 가진 경우 쪼개서 저장
def module_ports(id,port_name,port_list,All):

    new_ports_compo=dict()
    array_input=list()
    array_output=list()
    array_wire=list()

    for ivalue in All[id]['input']:
        #### 해당 submodule이 멀티비트의 input을 가질 경우
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_input:
                array_input.append(ivalue.split('[')[0])

    
    for ivalue in All[id]['output']:
        #### 해당 submodule이 멀티비트의 output을 가질 경우
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_output:
                array_output.append(ivalue.split('[')[0])

    
    if 'wire' in All[id]:
        for ivalue in All[id]['wire']:
            #### 해당 submodule이 멀티비트의 wire을 가질 경우
            if '[' in ivalue:
                if ivalue.split('[')[0] not in array_wire:
                    array_wire.append(ivalue.split('[')[0])

    temp_array_list=list()
    #### 확인하는 port가 단일비트를 가질 경우 port_list의 첫번째 비트로 최신화 후 함수 리턴
    if port_name not in array_input and port_name not in array_output and port_name not in array_wire:
        new_ports_compo.update({port_name:port_list[0]})
        return new_ports_compo

    #### 확인하는 port가 멀티비트를 가질 경우: input, output, wire의 경우
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

    #### 멀티비트의 경우 해당 port 또한 여러 개로 쪼개서 최신화 후 함수 리턴
    for idx in range(len(temp_array_list)):
        new_ports_compo.update({temp_array_list[idx]:port_list[idx]})

    return new_ports_compo





#### 해당 id가 get_module_dict의 macro_list에 포함된 macro의 경우 해당 macro의 pin을 따라 쪼개서 저장 (해당 macro를 설명하는 lef파일이나 lib파일을 통해 최신화 필수)!!
def macro_ports(id,port_name,port_list):
    #### 해당하는 macro의 pin의 정보에 따라 비트 수를 정한다. num==해당 port의 비트수
    new_ports_compo=dict()

    if id=='spsram_hd_16384x32m32':
        if port_name=='D' or port_name=='BWEN' or port_name=='Q':
            num=32
        elif port_name=='A':
            num=14
        else:
            num=1

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


    #### 해당 port가 단일 비트가 아닐 경우 num만큼 port를 쪼개서 저장 (num-1부터 0까지)
    if num!=1:
        for idx in range(num):
            new_ports_compo.update({port_name+'['+str(num-1-idx)+']':port_list[idx]})

    #### 해당 port가 단일 비트일 경우
    else:
        new_ports_compo.update({port_name:port_list[0]})
        
    return new_ports_compo





#### 해당 verilog의 net과 components들의 id에 대한 정보를 저장하는 함수
def get_tree(All,diff):
    #### 해당 verilog 파일의 파일명: where_the_v+'.v'
    where_the_v=diff.split('.v')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_v
    the_v=where_the_v.split('/')[-1]
    upper_directory=diff.split('/'+the_v+'.v')[0]

    #### 해당 verilog 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_v not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_v)

    top_module=All[1]
    All=All[0]

    all_tree=dict()
    treeAll=dict()

    #### submodule의 경우 module/submodule의 구조로 all_tree에 각각의 submodule을 저장(모든 module을 요소로 갖는 all_tree 생성)
    for ivalue in All[top_module]['module_counts']:
        temp_id=All[top_module][ivalue]['id']
        treeAll.update({ivalue:{'info':All[temp_id],'module':temp_id}})
        #### ivalue에 대해 get_add_mod실행 (submodule이 있을 경우 all_tree에 저장)
        all_tree=get_add_mod(treeAll,ivalue,All)

    list_tree_keys=list(all_tree.keys())
    #### all_tree에 있는 모든 요소들의 각 모듈의 네이밍이 상위 모듈과 하위 모듈의 관계를 갖는지 확인
    for ivalue in list_tree_keys:
        checking_list_func(All,ivalue,top_module)
    
    #### all_tree의 각 모듈마다 가지는 submodule을 최신화, submodule이 각각 가지는 module이름도 최신화한다.
    for ivalue in all_tree:
        all_tree[ivalue].update({'submodule':{}})
        for kvalue in All[all_tree[ivalue]['module']]['module_counts']:
            all_tree[ivalue]['submodule'].update({kvalue:All[all_tree[ivalue]['module']][kvalue]['id']})


    components_list_with_ports=list()
    only_components=list()

    #### components_list_with_ports라는 리스트에 all_tree에 저장된 각각의 모듈의 components들과 해당 components의 ports들을 저장한다.
    #### only_components에는 사용하는 components들을 저장한다.
    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            only_components.append(ivalue+'/'+kvalue)
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:
                components_list_with_ports.append(ivalue+'/'+kvalue+' '+tvalue)
    
    #### top_module에 대해서도 components_list_with_ports와 only_components에 해당 components의 정보를 저장한다.
    for ivalue in All[top_module]['components_counts']:
        only_components.append(ivalue)
        for kvalue in All[top_module][ivalue]['ports']:
            components_list_with_ports.append(ivalue+' '+kvalue)


    will_del=list()
    #### components_list_with_ports에서 실제로는 존재하지 않는 assign의 소자에 대해 지운다.
    for ivalue in components_list_with_ports:
        if ivalue.split('/')[-1].startswith('assign_') and '_assign_' in ivalue and ivalue.split(' ')[1]=='A':
            will_del.append(ivalue)
    for ivalue in will_del:
        components_list_with_ports.remove(ivalue)

    will_del=list()
    #### only_components에서 실제로는 존재하지 않는 assign의 소자에 대해 지운다.
    for ivalue in only_components:
        if ivalue.split('/')[-1].startswith('assign_') and '_assign_' in ivalue:
            will_del.append(ivalue)
    for ivalue in will_del:
        only_components.remove(ivalue)



    #### 실제 net을 구하여 저장할 딕셔너리 선언
    #### debt_group은 임의의 모듈A가 또 다른 모듈B의 하위모듈일 경우, A에서의 external net인 input과 output에 대한 net을 debt_group에 저장시켜서 후에 모듈 B의 net을 확인할 때 debt_group을 참고하여 모듈 B의 net을 구한다.
    net_group=dict()
    debt_group=dict()
    
    #### 어떠한 모듈의 component의 port가 상수 1\b0 혹은 1\b1에 연결될 경우, 각각 constant0와 constant1이라는 임의의 net을 선언하고 해당 net의 요소로 저장
    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:

                #### 어떠한 모듈의 component의 port가 상수 1\b0에 연결될 경우
                if all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b0':
                    if 'constant0' not in net_group:
                        net_group.update({'constant0':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant0']:
                        net_group['constant0'].append(ivalue+'/'+kvalue+' '+tvalue)

                #### 어떠한 모듈의 component의 port가 상수 1\b1에 연결될 경우
                elif all_tree[ivalue]['info'][kvalue]['ports'][tvalue]=='1\'b1':
                    if 'constant1' not in net_group:
                        net_group.update({'constant1':list()})
                    if ivalue+'/'+kvalue+' '+tvalue not in net_group['constant1']:
                        net_group['constant1'].append(ivalue+'/'+kvalue+' '+tvalue)



    temp_all_tree=copy.deepcopy(all_tree)

    #### top_module과 top_module의 submodule들을 제외한 module에 대해서 처리하는 동안 반복문 실행
    while True:
        counting=int()
        will_del=list()
        temp_debt_dict=dict()

        #### parsing이 끝난 module들의 input net과 output net에 존재하는 component들을 처리_1
        for ivalue in debt_group:
            tempports=ivalue.split('/')[-1]
            tempsub=ivalue.split('/')[-2]
            current_mod=ivalue.split('/'+tempsub+'/'+tempports)[0]
            #### ivalue가 current_mod와 같은 경우 : 해당 input_net과 output_net은 top_mododule의 submodule이기에 temp_debt_dict에 해당 내용을 추가
            if ivalue==current_mod:
                temp_debt_dict.update({ivalue:debt_group[ivalue]})

        #### parsing이 끝난 module들의 input net과 output net에 존재하는 component들을 처리_2
        for ivalue in debt_group:
            tempports=ivalue.split('/')[-1]
            tempsub=ivalue.split('/')[-2]
            current_mod=ivalue.split('/'+tempsub+'/'+tempports)[0]

            #### ivalue가 current_mod와 같은 경우 : 해당 input_net과 output_net은 top_mododule의 submodule이기에 continue로 처리
            if ivalue==current_mod:
                continue
            
            #### ivalue의 tempports가 하위 모듈에서는 쓰이지만 current_module에선 명시되지 않은 경우 따로 net_group에 추가해준다.
            if tempports not in all_tree[current_mod]['info'][tempsub]['ports']:
                submodule_id=all_tree[current_mod]['submodule'][tempsub]
                if tempports in All[submodule_id]['output'] or tempports in All[submodule_id]['input']:
                    if ivalue not in net_group:
                        net_group.update({ivalue:list()})
                    for rvalue in debt_group[ivalue]:
                        net_group[ivalue].append(rvalue)
                    continue

            #### current_mod에 'wire'key가 있을 경우 고려한다.
            if 'wire' in all_tree[current_mod]['info']:
                #### 해당 current_mod에 존재하는 wire_net 중 해당 ivalue 의 tempports에 연결된 wire가 있을 경우 net_group에 추가한다.
                if all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['wire']:
                    if current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports] not in net_group:
                        net_group.update({current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]:list()})
                    for kvalue in debt_group[ivalue]:
                        if kvalue not in net_group[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]]:
                            net_group[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]].append(kvalue)
            
            #### 해당 ivalue의 tempport가 상위 module인 current_mod에 input_net이나 output_net에 연결된 경우 temp_debt_dict에 추가한다.
            if all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['input'] or all_tree[current_mod]['info'][tempsub]['ports'][tempports] in all_tree[current_mod]['info']['output']:
                if current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports] not in temp_debt_dict:
                    temp_debt_dict.update({current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]:list()})
                for kvalue in debt_group[ivalue]:
                    if kvalue not in temp_debt_dict[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]]:
                        temp_debt_dict[current_mod+'/'+all_tree[current_mod]['info'][tempsub]['ports'][tempports]].append(kvalue)
            
            #### 해당 ivalue의 tempport가 상위 module인 current_mod에서 상수와 연결되는 경우, net_group의 constant0 혹은 constant1에 해당 tempport를 추가
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
            
        #### debt_group을 temp_debt_dict로 최신화
        debt_group=copy.deepcopy(temp_debt_dict)

        #### all_tree에서 submodule이 없는 module만 취급하여 해당 module에서의 wire_net은 net_group에 추가, input_net과 output_net은 debt_group에 추가한 후,
        #### 해당 module을 submodule로 갖는 상위 module들의 submodule_list에서 해당 module을 삭제한 후, 해당 module을 all_tree에서 삭제한다. (top_module과 top_module의 submodule들은 고려하지 않는다.)
        for ivalue in all_tree:
            #### ivalue 가 top_module혹은 top_module의 submodule이 아닌 경우 진행, counting: 반복문을 수행하는 ivalue의 갯수
            if len(all_tree[ivalue]['submodule'])==0 and '/' in ivalue:
                counting=counting+1
                #### all_tree에서 삭제할 ivalue 를 will_del이라는 list에 추가한다.
                will_del.append(ivalue)
                for kvalue in all_tree[ivalue]['info']['components_counts']:
                    for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:

                        #### 해당 ivalue의 임의의 component의 임의의 port가 wire_net에 연결된 경우, net_group에 해당 ivalue의 component와 port를 추가
                        if 'wire' in all_tree[ivalue]['info']:
                            if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['wire']:
                                if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in net_group:
                                    net_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                                net_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)

                        #### 해당 ivalue의 임의의 component의 임의의 port가 input_net 혹은 output_net에 연결된 경우, debt_group에 해당 ivalue의 component와 port를 추가
                        if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['input'] or all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['output']:
                            if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in debt_group:
                                debt_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                            debt_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)
                        
                        #### 해당 ivalue의 임의의 component의 임의의 port가 상수에 연결된 경우 net_group의 constant0 혹은 constant1에 추가
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
        
        #### 분석이 끝난, 현재 all_tree에서 submodule이 없는 module들을 all_tree에서 제거하고,submodule의 리스트에 해당 module을 가지는 특정 상위 module의 submodule의 리스트에 해당 module을 제거
        for ivalue in will_del:
            del all_tree[ivalue]
            del all_tree[ivalue.split('/'+ivalue.split('/')[-1])[0]]['submodule'][ivalue.split('/')[-1]]

        #### all_tree에 top_module의 submodule을 제외한 다른 module이 존재하지 않을 경우 break을 통해 while문을 벗어난다.
        if counting==0:
            break

######################## top module의 sub module 처리
    

    temp_debt_dict=dict()
    #### top_module의 submodule들 중 임의의 module애 대해서 debt_group의 ivalue 가 해당 module의 wire_net에 연결되는 경우, net_group에 추가, input_net이나 output_net에 연결된 경우 temp_debt_dict에 추가
    for ivalue in debt_group:
        #### wire_net에 해당 ivalue가 연결된 경우 net_group에 해당 ivalue의 원소들을 추가
        if 'wire' in all_tree[ivalue.split('/')[0]]['info']:
            if ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['wire']:
                if ivalue not in net_group:
                    net_group.update({ivalue:list()})
                net_group[ivalue].extend(debt_group[ivalue])
        
        #### input_net이나 output_net에 해당 ivalue가 연결된 경우 temp_debt_dict에 해당 ivalue의 원소들을 추가
        if ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['input'] or ivalue.split('/')[-1] in all_tree[ivalue.split('/')[0]]['info']['output']:
            if ivalue not in temp_debt_dict:
                temp_debt_dict.update({ivalue:debt_group[ivalue]})
            temp_debt_dict[ivalue].extend(debt_group[ivalue])
    
    #### debt_group을 temp_debt_dict로 최신화
    debt_group=copy.deepcopy(temp_debt_dict)

    #### top_module의 submodule에 대한 분석
    for ivalue in all_tree:
        for kvalue in all_tree[ivalue]['info']['components_counts']:
            for tvalue in all_tree[ivalue]['info'][kvalue]['ports']:
                #### 임의의 top_module의 submodule의 임의의 component의 port가 wire_net에 연결된 경우, net_group에 해당 ivalue의 component와 port를 추가
                if 'wire' in all_tree[ivalue]['info']:
                    if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['wire']:
                        if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in net_group:
                            net_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                        net_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)
                
                #### 임의의 top_module의 submodule의 임의의 component의 port가 input_net 혹은 output_net에 연결된 경우, debt_group에 해당 ivalue의 component와 port를 추가
                if all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['input'] or all_tree[ivalue]['info'][kvalue]['ports'][tvalue] in all_tree[ivalue]['info']['output']:
                    if ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue] not in debt_group:
                        debt_group.update({ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]:list()})
                    debt_group[ivalue+'/'+all_tree[ivalue]['info'][kvalue]['ports'][tvalue]].append(ivalue+'/'+kvalue+' '+tvalue)


                #### 해당 ivalue의 임의의 component의 임의의 port가 상수에 연결된 경우 net_group의 constant0 혹은 constant1에 추가
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
    #### debt_group이 top_module의 wire_net에 연결된 경우 net_group에 추가, input_net 혹은 output_net에 연결된 경우, 해당 net의 이름으로 net_group에 추가
    for ivalue in debt_group:
        #### debt_group에서 해당 ivalue가 wire_net에 연결된 경우, net_group에 추가
        if 'wire' in All[top_module]:
            if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['wire']:
                if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] not in net_group:
                    net_group.update({All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]:list()})
                
                for kvalue in debt_group[ivalue]:
                    if kvalue not in net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]]:
                        net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]].append(kvalue)

        #### debt_group에서 해당 ivalue가 input_net 혹은 output_net에 연결된 경우, net_group에 추가
        if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['input'] or All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] in All[top_module]['output']:
            if All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]] not in net_group:
                net_group.update({All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]:list()})

            for kvalue in debt_group[ivalue]:
                if kvalue not in net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]]:
                    net_group[All[top_module][ivalue.split('/')[0]]['ports'][ivalue.split('/')[1]]].append(kvalue)

    #### top_module에 있는 component들을 처리
    for ivalue in All[top_module]['components_counts']:
        for kvalue in All[top_module][ivalue]['ports']:
            if 'hart_id' in kvalue:
                print(kvalue)

            #### 임의의 component의 port가 상수값에 연결된 경우 net_group의 constant0 혹은 constant1에 component와 port를 추가
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
            
            #### 임의의 component의 port가 연결된 net이 net_group에 없다면 해당 net을 net_group에 추가한 후, 해당 net에 해당 component의 port를 추가
            if All[top_module][ivalue]['ports'][kvalue] not in net_group:
                net_group.update({All[top_module][ivalue]['ports'][kvalue]:list()})
            net_group[All[top_module][ivalue]['ports'][kvalue]].append(ivalue+' '+kvalue)


######################## assign 처리
    assign_temp=dict()
    #### net_group에 임의의 net에 특정 component가 'assign_'으로 시작하고 '_assign_'이라는 문자열을 가지며, 해당 port가 'A'인 net을 assign_temp에 추가한다.
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:
            if kvalue.split('/')[-1].startswith('assign_') and '_assign_' in kvalue.split('/')[-1] and kvalue.split(' ')[1]=='A':
                assign_temp.update({kvalue.split(' ')[0]:ivalue})

    checking_list=dict()
    #### checking_list에 assign으로 정의 되었던 net이 쓰인 module과 해당 module에서 assign구문에 사용된 net들과 assign이 어떻게 묶였는지에 대한 딕셔너리 생성
    for ivalue in assign_temp:
        temp_assign=ivalue.split('/')[-1]
        #### assign_temp에서의 ivalue에 assign의 좌변을 first_assign, 우변을 second_assign으로 취급
        first_assign=temp_assign.split('_assign_')[0].split('assign_')[1]
        second_assign=temp_assign.split('_assign_')[1]
        #### 해당 assign구문이 쓰인 module을 checking_list에 추가
        if ivalue.split(ivalue.split('/')[-1])[0] not in checking_list:
            checking_list.update({ivalue.split(ivalue.split('/')[-1])[0]:dict({'wires':list(),'groups':list()})})
        #### first_assign과 second_assign이 checking_list의 해당 module의 wire에 존재하지 않을 경우 first_assign 혹은 second_assign을 추가
        if first_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(first_assign)
        if second_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(second_assign)
        #### checking_list에서 해당 module의 group에 [first_assign,second_assign]을 추가
        checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['groups'].append([first_assign,second_assign])


    sum_assign=dict()
    #### checking_list을 참고하여 checking_list에 있는 module의 group들중, 합집합을 가지는 group을 합쳐서 sum_assign에 저장
    for ivalue in checking_list:
        if ivalue not in sum_assign:
            sum_assign.update({ivalue:list()})

        #### set_list에 해당 ivalue의 group에 있는 리스트들을 set으로 취급하여 세팅
        set_list=list()
        for idx in range(len(checking_list[ivalue]['groups'])):
            set_list.append(set(checking_list[ivalue]['groups'][idx]))
        #### set으로 합집합이 만들어지지 않는 경우가 될때까지 while문 실행
        while True:
            #### 새로 업데이트할 new_set_list 초기화
            new_set_list=list()
            #### 한번이라도 checking_break이 continue가 되면 while문을 다시 반복한다.
            checking_break=str()
            for idx in range(len(set_list)):
                for kdx in range(len(set_list)):
                    if kdx<=idx:
                        continue
                    #### 하나의 set과 다른 set이 합집합을 만드는 경우가 있을 경우 checking_break는 continue가 되고, new_set_list에 합집합을 만들어서 저장
                    if len(set_list[idx]&set_list[kdx])!=0:
                        checking_break='continue'
                        new_set_list.append(set_list[idx]|set_list[kdx])
            #### 합집합이 만들어지는 경우가 없을 경우 break으로 while문을 나간다.
            if checking_break=='':
                break
            set_list=copy.deepcopy(new_set_list)
        #### set_list에 있는 집합을 list로 해당 ivalue에 대해 저장
        for idx in range(len(set_list)):
            sum_assign[ivalue].append(list(set_list[idx]))

    #### assign 구문이 쓰인 모듈에 대해서 존재하는 assign들의 group중에 assign_temp에 저장된 net들을 group_assign으로 하나의 그룹에 모아준다.
    #### group_assign초기화 : assign구문이 쓰인 모듈에 존재하는 assign집합의 수만큼 해당 module에 빈 리스트를 추가한다.
    group_assign=dict()
    for ivalue in sum_assign:
        group_assign.update({ivalue:list()})
        for tdx in range(len(sum_assign[ivalue])):
            group_assign[ivalue].append([])

    #### kvalue모듈에서 assign구문으로 합쳐진 tdx번째 그룹에 해당하는 net들을 group_assign에 모아준다.
    for ivalue in assign_temp:
        for kvalue in sum_assign:
            for tdx in range(len(sum_assign[kvalue])):
                #### kvalue 모듈에 tdx번째 assign 집합에 해당 net이 포함되면 group_assign에 kvalue 모듈의 tdx번째 리스트에 추가한다.
                if ivalue.split(ivalue.split('/')[-1])[0]==kvalue and ivalue.split('/')[-1].split('_assign_')[0].split('assign_')[1] in sum_assign[kvalue][tdx] \
                    and ivalue.split('/')[-1].split('_assign_')[1].split(' ')[0] in sum_assign[kvalue][tdx]:
                    group_assign[kvalue][tdx].append(assign_temp[ivalue])


    net_group_assign=dict()
    #### group_assign에 저장된 하나의 그룹을 이루는 net들이 가지는 원소들을 net_group_assign에 모두 저장 assign_group_+temp_number로 해당 그룹명을 바꾼다.
    for ivalue in group_assign:
        net_group_assign.update({ivalue:dict()})

        temp_number=int()
        for tdx in range(len(group_assign[ivalue])):
            name_of_assign='assign_group_'+str(temp_number)
            temp_number=temp_number+1
            
            for kdx in range(len(group_assign[ivalue][tdx])):
                #### 만약 해당 그룹에 top_module의 net이 있으면 그룹명을 해당 net으로 바꾼다.
                if '/' not in group_assign[ivalue][tdx][kdx]:
                    name_of_assign=group_assign[ivalue][tdx][kdx]
                    temp_number=temp_number-1
            net_group_assign[ivalue].update({name_of_assign:[]})

            #### 해당 그룹명에 각 net이 가지는 원소들을 해당 그룹에 추가
            for kdx in range(len(group_assign[ivalue][tdx])):
                for rvalue in net_group[group_assign[ivalue][tdx][kdx]]:
                    if rvalue not in net_group_assign[ivalue][name_of_assign]:
                        net_group_assign[ivalue][name_of_assign].append(rvalue)


    will_add_net=dict()
    #### net_group에 더할 will_add_net을 만든다.
    for ivalue in net_group_assign:
        for kvalue in net_group_assign[ivalue]:
            #### kvalue module의 임의의 assign 그룹명이 assign_group_으로 시작할 경우 해당 module 이름 + assign_group_ + temp_number로 저장
            if kvalue.startswith('assign_group_'):
                will_add_net.update({ivalue+kvalue:net_group_assign[ivalue][kvalue]})
            #### 아닐 경우 해당 그룹명 그대로 저장
            else:
                will_add_net.update({kvalue:net_group_assign[ivalue][kvalue]})

    #### will_add_net의 각 net의 원소들 중 marking을 위해 존재했던 assign_A_assign_B A 라는 가상의 component와 port를 지워준다.
    for ivalue in will_add_net:
        will_del_list=list()
        for kvalue in will_add_net[ivalue]:
            if kvalue.split('/')[-1].split(' ')[1]=='A' and kvalue.split('/')[-1].startswith('assign_') and '_assign_' in kvalue.split('/')[-1]:
                will_del_list.append(kvalue)
        for kvalue in will_del_list:
            will_add_net[ivalue].remove(kvalue)
    
    #### group_assign에 저장되어 있던 net들은 net_group에서 지운다.
    for ivalue in group_assign:
        for kdx in range(len(group_assign[ivalue])):
            for tdx in range(len(group_assign[ivalue][kdx])):
                del net_group[group_assign[ivalue][kdx][tdx]]

    real_net_group=copy.deepcopy(net_group)
    temp_matching_net=copy.deepcopy(net_group)
    #### net_group에 will_add_net을 추가함으로서 assign 구문에 의해 합쳐지는 집합들을 net_group에 최신화
    for idx,ivalue in enumerate(will_add_net):
        #### net_group에는 assignModule에 idx번째 net을 추가
        net_group.update({'assignModule'+str(idx):will_add_net[ivalue]})
        real_net_group.update({ivalue:will_add_net[ivalue]})
        temp_matching_net.update({ivalue:'assignModule'+str(idx)})


######################## checking 영역

    #### net_group에 존재하는 모든 components들과 port의 쌍을 checking_net_components에 저장하고, component의 이름만 checking_net_components에 저장한다.
    checking_net_components=list()
    checking_only_components=dict()
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:

            checking_net_components.append(kvalue)
            checking_only_components.update({kvalue.split(' ')[0]:str('')})

    #### 만약 components_list_with_ports!=checking_net_components 이라면 몇 component들의 port들이 누락되었거나 더 많이 net에 쓰였다.
    if len(components_list_with_ports)>len(checking_net_components):
        print('Error : some components are not in net_group components_list_with_ports :',len(components_list_with_ports),'checking_net_components :',len(checking_net_components))
    elif len(components_list_with_ports)<len(checking_net_components):
        print('Error : some components are not in definiftion components_list_with_ports :',len(components_list_with_ports),'checking_net_components :',len(checking_net_components))
    elif set(components_list_with_ports)!=set(checking_net_components):
        print('Error : some_components are not in net_list or some_components in net_list which is not in verilog')

    #### 만약 only_components!=checking_only_components 이라면 몇 component들이 누락되었거나 더 많이 net에 쓰였다.
    if len(only_components)>len(checking_only_components):
        print('Error : some components are not in net_group only_components :',len(only_components),'checking_only_components :',len(checking_only_components))
    elif len(only_components)<len(checking_only_components):
        print('Error : some components are not in definiftion only_components :',len(only_components),'checking_only_components :',len(checking_only_components))
    elif set(only_components)!=set(checking_only_components):
        print('Error : some_components are not in net_list or some_components in net_list which is not in verilog')

    print(len(only_components))



    #### net_group에서 쓰인 components들의 id를 checking_only_components에 추가해준다. 만약 external_pin의 경우 PIN +pin_name:external_[direction]_PIN으로 추가해준다.
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:
            if '/' in kvalue:
                checking_only_components[kvalue.split(' ')[0]]=temp_all_tree[kvalue.split('/'+kvalue.split('/')[-1])[0]]['info'][kvalue.split('/')[-1].split(' ')[0]]['id']
            else:
                checking_only_components[kvalue.split(' ')[0]]=All[top_module][kvalue.split('/')[-1].split(' ')[0]]['id']
        
        #### PIN의 경우 top_module의 input_net이거나 output_net의 경우이다.
        if ivalue in All[top_module]['input']:
            net_group[ivalue].append('PIN '+ivalue)
            checking_only_components.update({'PIN '+ivalue:'external_input_PIN'})
        elif ivalue in All[top_module]['output']:
            net_group[ivalue].append('PIN '+ivalue)
            checking_only_components.update({'PIN '+ivalue:'external_output_PIN'})

    #### assign구문에 의해 만들어진 net에 PIN의 내용이 있을겅우에도 PIN에 대한 id를 추가해준다.
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

    #### 사용된 components들의 id에 대한 정보를 json파일로 저장한다.
    with open(upper_directory+'/'+the_v+'/checking_id_components.json','w') as fw:
        json.dump(checking_only_components,fw,indent=4)
    fw.close()


    #### 상위모듈들은 제거하여 각 module의 name이 아닌 module의 id를 각 components의 이름으로 갖는 딕셔너리 저장
    checking_id_components_modified=dict()
    #### 이름이 바뀌는 conponents들의 index확인용 딕션너리 : matching_dict
    matching_dict=dict()
    for ivalue in checking_only_components:
        #### 해당 component가 PIN일 경우 그대로 PIN의 이름으로 저장한다.
        if ivalue.startswith('PIN '):
            checking_id_components_modified.update({ivalue:checking_only_components[ivalue]})
            matching_dict.update({ivalue:ivalue})
        #### 해당 component가 PIN이 아닌 경우 해당 component가 선언된, 해당 component의 이름에서 가장 하위 module이 되는 module의 id와 component의 이름으로 저장한다.
        else:
            #### 해당 component의 이름 : temp_components
            temp_components=ivalue.split('/')[-1]
            #### '/'이 있다면 top_module의 component가 아니므로 가장 하위의 module을 찾는다.
            if  '/' in ivalue:
                templist=temp_module=ivalue.split('/'+temp_components)[0].split('/')
                #### 해당 component가 선언된, 해당 module의 id : temp_module
                temp_module=str()
                for kdx in range(len(templist)):
                    if kdx==0:
                        temp_module=All[top_module][templist[kdx]]['id']
                    else:
                        temp_module=All[temp_module][templist[kdx]]['id']
                #### 해당 temp_module+'/'+temp_components로 해당 component의 이름을 다르게 저장한다.
                checking_id_components_modified.update({temp_module+'/'+temp_components:checking_only_components[ivalue]})
                matching_dict.update({ivalue:temp_module+'/'+temp_components})
            #### top_module에서 선언된 component들은 top_module+'/'+temp_components로 해당 component의 이름을 다르게 저장한다.
            else:
                checking_id_components_modified.update({top_module+'/'+temp_components:checking_only_components[ivalue]})
                matching_dict.update({ivalue:top_module+'/'+temp_components})

    #### 이름이 바뀐 component들의 집합을 json파일로 저장
    with open(upper_directory+'/'+the_v+'/checking_id_components_modified.json','w') as fw:
        json.dump(checking_id_components_modified,fw,indent=4)
    fw.close()

    with open(upper_directory+'/'+the_v+'/matching_dict.json','w') as fw:
        json.dump(matching_dict,fw,indent=4)
    fw.close()
    #### real_net_group에서의 원소 중에 임의의 component가 외부 PIN일 경우, 해당 net에 외부 PIN을 저장한다.
    for ivalue in real_net_group:
        if ivalue in All[top_module]['input'] or ivalue in All[top_module]['output']:
            if 'PIN '+ivalue not in real_net_group[ivalue]:
                real_net_group[ivalue].append('PIN '+ivalue)

    #### 구한 net의 총 갯수를 화면에 출력
    print('net_counts :',len(net_group))
    
    #### net_group에서 쓰이는 net의 이름과 각 net의 원소들인 component들도 선언된 각 module의 id를 이름으로 갖는 딕셔너리 생성
    new_net_group=dict()
    for ivalue in net_group:
        #### conseq은 각 net의 새로운 이름이 된다. 해당 net이 온전히 선언되는 최하위 module의 id를 net이름으로 갖는다.
        conseq=str()
        #### '/'가 있을 경우 최하위 module을 찾아서 conseq에 저장
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
        #### '/'이 없을 경우 ivalue를 conseq에 저장
        else:
            conseq=ivalue
        #### new_net_group에 각각의 conseq을 저장
        new_net_group.update({conseq:list()})
        temp_matching_net[ivalue]=conseq

        for kvalue in net_group[ivalue]:
            #### 각 net의 구성요소들도 conseq과 마찬가지로 선언된 최하위의 module의 id+'/'+components_id+' '+port의 형태로 result로 저장
            result=str()
            #### '/'이 있을 경우 해당 component가 선언된 최하위 module을 찾아 result에 저장
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
            #### '/'이 없을 경우 result에 kvalue를 저장
            else:
                result=kvalue
            #### 각 result를 new_net_group의 conseq인 net에 추가
            new_net_group[conseq].append(result)
    print('ptmglwnsAWerer!!@!@')
    print(len(real_net_group))
    #### new_net_group에서의 net이름은 assignModule이지만 해당 net에 외부 PIN이 있을 경우, net의 이름을 해당 외부 PIN으로 바꿔준다.
    modified_group=dict()
    for ivalue in new_net_group:
        #### assignModule 혹은 constant0 혹은 constant1 혹은 top_module의 net인 경우
        if '/' not in ivalue:
            che=str()
            #### 해당 net에 PIN이 있다면 che는 'che'로 저장
            for kvalue in new_net_group[ivalue]:
                if 'PIN ' in kvalue:
                    che='che'
                    break
            #### 외부 PIN이 있을 경우 (assign그룹의 net이 아닌경우)
            if che=='che' and 'assignModule' not in ivalue:
                modified_group.update({'PIN '+ivalue:new_net_group[ivalue]})
                for temp_ivalue in temp_matching_net:
                    if temp_matching_net[temp_ivalue]==ivalue:
                        temp_matching_net[temp_ivalue]='PIN '+ivalue

            #### 외부 PIN이 없을 경우
            else:
                #### assignModule도 아니고, constant0와 constant1도 아니면 top_module의 wire_net이다.
                if 'assignModule' not in ivalue and ivalue!='constant0' and ivalue!='constant1':
                    for temp_ivalue in temp_matching_net:
                        if temp_matching_net[temp_ivalue]==ivalue:
                            temp_matching_net[temp_ivalue]=top_module+'/'+ivalue
                    modified_group.update({top_module+'/'+ivalue:new_net_group[ivalue]})
                #### assignModule의 경우와 constant0, constant1의 경우 그대로 저장한다.
                else:
                    modified_group.update({ivalue:new_net_group[ivalue]})
        #### '/'이 있을 경우 modified_group에 최하위 module과 해당 module에서의 id로 net을 저장한다.
        else:
            for temp_ivalue in temp_matching_net:
                if temp_matching_net[temp_ivalue]==ivalue:
                    temp_matching_net[temp_ivalue]=ivalue.split('/'+ivalue.split('/')[-1])[0].split('/')[-1]+'/'+ivalue.split('/')[-1]
            modified_group.update({ivalue.split('/'+ivalue.split('/')[-1])[0].split('/')[-1]+'/'+ivalue.split('/')[-1]:new_net_group[ivalue]})


    print(len(temp_matching_net))
    for ivalue in modified_group:
        temp=list()
        for kvalue in modified_group[ivalue]:
            if kvalue.startswith('PIN '):
                temp.append(kvalue)
            elif '/' not in kvalue:
                temp.append(top_module+'/'+kvalue)
            else:
                last_slash=kvalue.split('/')[-1]
                previous_slash=kvalue.split('/'+last_slash)[0].split('/')[-1]
                temp.append(previous_slash+'/'+last_slash)
        modified_group[ivalue]=temp

    return [modified_group,real_net_group]





#### submodule아 있을 경우 All에 최신화를 하여 모든 submodule에 대해 tree 구성
def get_add_mod(All,upper_module,info):
    
    for ivalue in info[All[upper_module]['module']]['module_counts']:
        temp_id=info[All[upper_module]['module']][ivalue]['id']
        All.update({upper_module+'/'+ivalue:{'info':info[temp_id],'module':temp_id}})
        #### submodule이 있을 경우, 각 submodule 마다 upper_module+'/'+submodule을 All에 저장
        get_add_mod(All,upper_module+'/'+ivalue,info)

    return All




def checking_list_func(All,ivalue,toptop):
    temp_list=ivalue.split('/')
    temp_preview=str()
    for idx in range(len(temp_list)):
        if idx==0:
            #### '/'을 기준으로 첫번째 모듈은 top_module의 하위 모듈이 아닐 경우
            if temp_list[idx] not in All[toptop]:
                print('Error : '+temp_list[idx]+' not in topmodule')
            #### '/'을 기준으로 첫번째 모듈은 top_module의 하위 모듈일 경우
            else:
                temp_preview=All[toptop][temp_list[idx]]['id']
        
        else:
            ####'/'을 기준으로 idx번째 모듈아 temp_preview모듈의 하위 모듈이 아닐 경우
            if temp_list[idx] not in All[temp_preview]:
                print('Error : '+temp_list[idx]+' not in '+temp_preview)
            ####'/'을 기준으로 idx번째 모듈아 temp_preview모듈의 하위 모듈알 경우
            else:
                temp_preview=All[temp_preview][temp_list[idx]]['id']
    return 0




if __name__=="__main__":
    #get_tree(str())


    difficulty='medium' ##################### difficulty 는 easy 와 medium 두가지 경우가 있다.
    difficulty='easy'
    difficulty=sys.argv[1]
    file='../../temp_data/verilog/'+difficulty+'.v'
    #file='../../data/easy/easy.v'
    start=time.time()

    kkk=get_module_dict(file)

    mmm=get_tree(kkk,file)

    #### 해당 verilog 파일의 파일명: where_the_v+'.v'
    where_the_v=file.split('.v')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_v
    the_v=where_the_v.split('/')[-1]
    upper_directory=file.split('/'+the_v+'.v')[0]
    #### 해당 verilog 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_v not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_v)

    with open(upper_directory+'/'+the_v+'/nets_modified_by_02.json','w') as fw:
        json.dump(mmm[0],fw,indent=4)
    fw.close()
    with open(upper_directory+'/'+the_v+'/nets_from_02.json','w') as fw:
        json.dump(mmm[1],fw,indent=4)
    fw.close()

    print(time.time()-start)
