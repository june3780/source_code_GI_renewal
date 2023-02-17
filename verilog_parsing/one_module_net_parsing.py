import json
import os

def get_superblue_netlist(v_add):
    #### 해당 verilog 파일의 파일명: where_the_verilog+'.v'
    where_the_verilog=v_add.split('.v')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_verilog
    the_verilog=where_the_verilog.split('/')[-1]
    upper_directory=v_add.split('/'+the_verilog+'.v')[0]


    if the_verilog not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_verilog)


    #### 해당 superblue def 불러오기
    with open(v_add,'r') as fw:
        lines=fw.readlines()
    fw.close()

    #### 주석을 제외하고 ';'을 기준으로 각 문자열을 new_lines에 저장
    new_lines=['']
    for idx in range(len(lines)):
        #### 주석의 경우 continue로 처리
        if lines[idx].strip().startswith('//'):
            continue
        #### 주석 이외의 문장은 new_lines의 마지막 요소인 문자열에 이어 붙여서 new_lines의 마지막 요소 업데이트
        new_lines[-1]=(new_lines[-1]+' '+lines[idx].replace('\n','').strip()).strip()
        #### 해당 문자열이 ';'로 끝날 경우 new_lines에 새로운 요소를 공백인 문자열로 추가
        if lines[idx].replace('\n','').strip().endswith(';'):
            new_lines.append('')

    net_all=dict()
    component_id=dict()
    assign_list=list()
    input_list=list()
    output_list=list()


    #### new_lines에 각 net과 components들을 가리키는 딕션너리 생성
    #### net_all : 각 input, output 혹은 wire가 어떤 components의 pin과 연결되어 있는지 net별로 값 저장
    #### components_id : 각 components들의 standard_cell id나 macro_id를 저장
    #### input_list : external_input pin들의 집합을 저장
    #### output_list : external_output pin들의 집합을 저장

    for idx in range(len(new_lines)):

        #### assign 구문의 경우 assign_list에 해당 문자열을 추가 후 continue로 처리
        if  new_lines[idx].startswith('assign '):
            #### 좌변의 net과 우변의 net을 하나의 list에 묶어서 저장
            left_net=new_lines[idx].split('assign')[1].split('=')[0].strip()
            right_net=new_lines[idx].split('=')[1].split(';')[0].strip()
            assign_list.append([left_net,right_net])
            continue

        #### input_external_pin일 경우 input_list에 저장
        if new_lines[idx].startswith('input '):
            input_list.append(new_lines[idx].split(' ')[1].split(';')[0].strip())
        
        #### output_external_pin일 경우 input_list에 저장
        elif new_lines[idx].startswith('output '):
            output_list.append(new_lines[idx].split(' ')[1].split(';')[0].strip())


    for idx in range(len(new_lines)):

        #### idx번째 new_lines 문자열이 wire, input, output, module, endmodule, assign로 시작할 때, continue로 처리
        if  new_lines[idx].startswith('assign ') or new_lines[idx].startswith('wire ') or new_lines[idx].startswith('input ') or new_lines[idx].startswith('output ') or new_lines[idx].startswith('module ') or new_lines[idx].startswith('endmodule'):
            continue

        #### idx 번째 문자열의 id : temp_id
        temp_id=new_lines[idx].split(' ')[0]
        #### idx 번째 문자열의 name : temp_name
        temp_name=new_lines[idx].split(' ')[1]

        #### 해당 components의 port들이 어떤 net으로 연결되어있는지 확인
        port_and_net=new_lines[idx].split(temp_id+' '+temp_name)[1].split('.')
        for kvalue in port_and_net:
            #### 해당 components의 port와 해당 port가 연결된 net을 표현하는 구간
            if '(' in kvalue and ')' in kvalue:
                #### 괄호 안의 net : temp_net
                temp_net=kvalue.split(')')[0].split('(')[1].strip()
                #### temp_net 이 net_all에 없을 경우 업데이트
                if temp_net not in net_all:
                    net_all.update({temp_net:list()})
                #### components_id+' '+components_port를 하나의 요소로 취급하여 연결되는 temp_net의 list에 추가
                net_all[temp_net].append(temp_name+' '+kvalue.split('(')[0].strip())

                #### 해당 net이 input_external_pin일 경우
                if temp_net in input_list:
                    if 'PIN '+temp_net not in net_all[temp_net]:
                        net_all[temp_net].append('PIN '+temp_net)

                #### 해당 net이 output_external_pin일 경우
                elif temp_net in output_list:
                    if 'PIN '+temp_net not in net_all[temp_net]:
                        net_all[temp_net].append('PIN '+temp_net)

        #### 해당 components의 id를 component_id에 저장
        component_id.update({temp_name.split('(')[0].strip():temp_id})





    #### assign구문 처리 : 좌변의 net을 우변의 net_all의 net에 extend로 처리 assign 구문을 처리하면 삭제하여, assign에 관련된 데이터가 없을 때까지 while문 진행
    while len(assign_list)!=0:
        will_del=list()
        for idx in range(len(assign_list)):
            
            #### idx번째 assign항의 우변이 net_all에 없을 경우 업데이트
            if assign_list[idx][1] not in net_all:
                net_all.update({assign_list[idx][1]:list()})
            
            #### idx번째 좌변이 net_all에 있을 경우
            if assign_list[idx][0] not in net_all[assign_list[idx][1]]:
                #### net_all에 좌변에 대한 net이 있을 경우
                if assign_list[idx][0] in net_all:
                    net_all[assign_list[idx][1]].extend(net_all[assign_list[idx][0]])
                    #### 좌변의 net은 net_all에서 삭제
                    del net_all[assign_list[idx][0]]

                #### net_all에 좌변에 대한 net이 없을 경우
                else:
                    #### 해당 좌변이 input_external_pin일 경우
                    if assign_list[idx][0] in input_list:
                        net_all[assign_list[idx][1]].append('PIN '+temp_net)
                    #### 해당 좌변이 output_external_pin일 경우
                    elif assign_list[idx][0] in output_list:
                        net_all[assign_list[idx][1]].append('PIN '+temp_net)
            #### assign에 idx를 추가
            will_del.append(idx)

            #### idx번째 assign에서의 좌변의 net이 다른 (kdx번째)assign항의 우변의 net일 경우 kdx번째 assign의 우변의 net을 idx번째 assign의 우변의 net으로 변경
            for kdx in range(len(assign_list)):
                if idx==kdx:
                    continue
                if assign_list[idx][0]==assign_list[kdx][1]:
                    assign_list[kdx][1]=assign_list[idx][1]

        #### will_del에 요소들은 처리된 assign항들을 삭제할 인덱스가 들어있다.
        will_del.reverse()
        for idx in will_del:
            del assign_list[idx]
    


    with open(upper_directory+'/'+the_verilog+'/temp_net.json','w') as fw:
        json.dump(net_all,fw,indent=4)
    fw.close()

    with open(upper_directory+'/'+the_verilog+'/temp_id.json','w') as fw:
        json.dump(component_id,fw,indent=4)
    fw.close()

    return 0



if __name__=="__main__":

    #### superblue의 경우 module이 하나인 verilog 이므로 다르게 parsing하였다.
    listlist=['16_ISPD','1','3','4','5','7','10','16','18']
    listlist=['11_ISPD','12_ISPD','16_ISPD']
    for number in listlist:
        superblue='../../data/'
        chekcing='superblue'+number
        superblue=superblue+chekcing+'/'+chekcing+'.v'

        get_superblue_netlist(superblue)
        print(number)


