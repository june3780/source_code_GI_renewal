import json
import os


#### superblue에 있는 macro의 location을 구한다.
def get_location(defdef):
    #### 해당 verilog 파일의 파일명: where_the_def+'.v'
    where_the_def=defdef.split('.def')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_def
    the_def=where_the_def.split('/')[-1]
    upper_directory=defdef.split('/'+the_def+'.def')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_def not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_def)

    with open(defdef,'r') as fw:
        lines=fw.readlines()
    fw.close()

    with open(upper_directory+'/'+the_def+'/pins_macro_with_ports.json','r') as fw:
        checking_group=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_def+'/macro_width_height.json','r') as fw:
        size_of_macro=json.load(fw)
    fw.close()
    with open(upper_directory+'/'+the_def+'/temp_id.json','r') as fw:
        component_id=json.load(fw)
    fw.close()

    new_lines=['']
    for ivalue in lines:
        new_lines[-1]=new_lines[-1]+' '+ivalue.replace('\n','').strip()
        if ivalue.replace('\n','').strip().endswith(';'):
            new_lines.append('')

    die_area=str()
    macro_location_list=dict()
    for ivalue in new_lines:
        if '-' in ivalue:
            if ivalue.split('-')[1].strip().split(' ')[0].strip() in checking_group['macro']:
                if 'UNPLACED' in ivalue:
                    continue
                elif 'PLACED' in ivalue:
                    macro_location_list.update({ivalue.split('-')[1].strip().split(' ')[0].strip():{'x_point':float(ivalue.split('PLACED')[1].split('(')[1].split(')')[0].strip().split(' ')[0]),\
                        'y_point':float(ivalue.split('PLACED')[1].split('(')[1].split(')')[0].strip().split(' ')[1])}})
                elif 'FIXED' in ivalue:
                    macro_location_list.update({ivalue.split('-')[1].strip().split(' ')[0].strip():{'x_point':float(ivalue.split('FIXED')[1].split('(')[1].split(')')[0].strip().split(' ')[0]),\
                        'y_point':float(ivalue.split('FIXED')[1].split('(')[1].split(')')[0].strip().split(' ')[1])}})
        elif 'DIEAREA' in ivalue:
            die_area=ivalue.split('DIEAREA')[1].split(';')[0].strip()
        
    
        

    saving_lines=list()
    for ivalue in macro_location_list:
        macro_location_list[ivalue]['x_point']=macro_location_list[ivalue]['x_point']+1000*size_of_macro[component_id[ivalue]]['width']/2
        macro_location_list[ivalue]['y_point']=macro_location_list[ivalue]['y_point']+1000*size_of_macro[component_id[ivalue]]['height']/2
        saving_lines.append(ivalue+' '+str(macro_location_list[ivalue]['x_point'])+' '+str(macro_location_list[ivalue]['y_point']))


    with open(upper_directory+'/'+the_def+'/die_area.txt','w') as fw:
        fw.write(die_area+'\n')
    fw.close()

    for idx in range(len(saving_lines)):
        if idx==0:
            with open(upper_directory+'/'+the_def+'/temp_macro_location.txt','w') as fw:
                fw.write(saving_lines[idx]+'\n')
            fw.close()
        else:
            with open(upper_directory+'/'+the_def+'/temp_macro_location.txt','a') as fw:
                fw.write(saving_lines[idx]+'\n')
            fw.close()

    return 0


if __name__=="__main__":
    superblue=['easy','superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD']
    for ivalue in superblue:
    #ivalue='superblue16_ISPD'
        checking_def='../../data/'
        checking_def=checking_def+ivalue+'/'+ivalue+'.def'
        get_location(checking_def)
        break