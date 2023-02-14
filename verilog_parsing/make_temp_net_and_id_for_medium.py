import os
import json
import shutil




def get_temp_net(origin):
    with open(origin,'r') as fw:
        origin_net=json.load(fw)
    fw.close()

    temp_net=dict()
    for ivalue in origin_net:
        temp_net.update({ivalue:list()})
        temp_net[ivalue]=origin_net[ivalue]['cell_list']

    with open('../../data/easy/easy/temp_net.json','w') as fw:
        json.dump(temp_net,fw,indent=4)
    fw.close()
    print('../../data/easy/easy/temp_net.json')
    #print(json.dumps(temp_net,indent=4))


    return 0


def get_temp_id(origin):
    shutil.copy(origin,'../../data/easy/easy/temp_id.json')
    return 0


def get_lef_united(lef_address,lef_list):
    tt=int()
    temp_list=list()
    for ivalue in lef_list:
        leflef=lef_address+ivalue
        #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
        where_the_lef=leflef.split('.lef')[0]
        #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
        the_lef=where_the_lef.split('/')[-1]
        upper_directory=leflef.split('/'+the_lef+'.lef')[0]

        '''#### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
        if the_lef not in os.listdir(upper_directory):
            os.mkdir(upper_directory+'/'+the_lef)'''

        #### 해당 lef 파일 열기
        with open(leflef,'r') as fw:
            fines=fw.readlines()
        fw.close()

        #### macro인 성분들이 시작하는 인덱스와 끝나는 인덱스를 각각 macro_start_idx와 macro_end_idx에 저장
        macro_start_idx=list()
        macro_end_idx=list()
        for idx in range(len(fines)):
            if fines[idx].strip().startswith('MACRO') and fines[idx].split('MACRO')[1].startswith(' '):
                macro_start_idx.append(idx)
                #### 해당 macro의 내용이 끝나는 인덱스를 get_end_idx로 저장
                macro_end_idx.append(get_end_idx(idx,fines))

        for idx in range(len(macro_start_idx)):
            for jdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
                temp_list.append(fines[macro_start_idx[idx]+jdx])
        temp_list.append('\n')

    for idx in range(len(temp_list)):
        if idx==0:
            with open ('../../data/easy/easy.lef','w') as fw:
                fw.write(temp_list[idx])
            fw.close()
        else:
            with open ('../../data/easy/easy.lef','a') as fw:
                fw.write(temp_list[idx])
            fw.close()

    return 0


#### lef 파일에서 macro인 id를 parsing하여 해당 lef 파일의 위치에 하위 디렉토리 생성 후 저장
def get_macro_from_lef(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]

    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    #### 해당 lef 파일 열기
    with open(leflef,'r') as fw:
        fines=fw.readlines()
    fw.close()

    #### macro인 성분들이 시작하는 인덱스와 끝나는 인덱스를 각각 macro_start_idx와 macro_end_idx에 저장
    macro_start_idx=list()
    macro_end_idx=list()
    for idx in range(len(fines)):
        if fines[idx].strip().startswith('MACRO') and fines[idx].split('MACRO')[1].startswith(' '):
            macro_start_idx.append(idx)
            #### 해당 macro의 내용이 끝나는 인덱스를 get_end_idx로 저장
            macro_end_idx.append(get_end_idx(idx,fines))

    '''#### 각 macro들 중 CLASS가 BLOCK으로 쓰여진 macro들을 MACRO_list에 저장
    MACRO_list=list()
    for idx in range(len(macro_start_idx)):
        temp_macro_name=fines[macro_start_idx[idx]].split('MACRO')[1].replace('\n','').strip()

        for kdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
            if fines[kdx+macro_start_idx[idx]].strip().startswith('CLASS') and fines[kdx+macro_start_idx[idx]].split('CLASS')[1].startswith(' '):
                #### 해당 macro의 CLASS가 BLOCK으로 쓰여있는 경우
                if fines[kdx+macro_start_idx[idx]].split('CLASS')[1].strip().startswith('BLOCK') and fines[kdx+macro_start_idx[idx]].split('BLOCK')[1].replace('\n','').strip()==';':
                   MACRO_list.append(temp_macro_name)
                   break

    #### MACRO_list를 lef_macro_list.json파일로 저장
    with open(upper_directory+'/'+the_lef+'/lef_macro_list.json','w') as fw:
        json.dump(MACRO_list,fw,indent=4)
    fw.close()'''
    
    return 0


#### 임의의 macro가 시작하는 인덱스를 통해 끝나는 인덱스를 반환하는 함수
def get_end_idx(start_idx,lines):
    #### 해당 macro의 내용이 시작할 때, 해당 macro의 이름 : start_macro_name
    start_macro_name=lines[start_idx].split('MACRO')[1].replace('\n','').strip()
    #### 해당 macro가 끝났을 때의 인덱스의 내용 : end_macro_name
    end_macro_name='END '+start_macro_name
    #### lef 파일에서 임의의 macro가 끝나는 인덱스의 내용을 만났을 때, 해당 인덱스를 반환
    for idx in range(len(lines)):
        if lines[idx].replace('\n','').strip()==end_macro_name:
            return idx




if __name__=="__main__":
    ivalue='easy'
    origin_net='../../data/easy/net_list_easy.json'
    origin_id='../../data/easy/checking_id_components_modified.json'
    origin_address='../../data/easy/'
    lef_list=['DMY_TCD_H_20100305.lef','DMY_TCD_V_20100305.lef','TS1N40LPB128X63M4FWBA.lef','TS1N40LPB256X12M4FWBA.lef','TS1N40LPB256X22M4FWBA.lef','TS1N40LPB256X23M4FWBA.lef'\
        ,'TS1N40LPB512X23M4FWBA.lef','TS1N40LPB1024X32M4FWBA.lef','TS1N40LPB1024X128M4FWBA.lef','TS1N40LPB2048X32M4FWBA.lef','TS1N40LPB2048X36M4FWBA.lef']
    lef_list=['sprf_hs_128x38m2s.lef','spsram_hd_256x22m4m.lef','spsram_hd_256x23m4m.lef','spsram_hd_2048x32m4s.lef']
    get_temp_net(origin_net)
    get_temp_id(origin_id)
    get_lef_united(origin_address,lef_list)
