import json
import pickle
import sys
import copy


def get_module_dict():
    wherethemodule='../data/easy/easy.v'
    with open(wherethemodule,'r') as fw:
        module_str=fw.readlines()
    fw.close()

    module_list=['']
    for ivalue in module_str:
        if module_list[-1]=='':
            module_list[-1]=ivalue.strip()
        else:
            module_list[-1]=module_list[-1]+' '+ivalue.strip()
        if ivalue.replace('\n','').strip().endswith('endmodule'):
            module_list.append('')
    del module_list[-1]

    module_dict=dict()
    for ivalue in module_list:
        module_name=str()
        temp_str=ivalue.split(';')
        for kvalue in temp_str:
            if 'module ' in kvalue and 'endmodule' not in kvalue:
                module_name=kvalue.split(' ')[1]
                module_dict.update({module_name:{}})
            elif 'input ' in kvalue:
                if 'input' not in module_dict[module_name]:
                    module_dict[module_name].update(({'input':[]}))
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(small_idx+tdx)+']')

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        for tdx in range(large_idx-small_idx+1):
                            module_dict[module_name]['input'].append(jvalue+'['+str(small_idx+tdx)+']')
                else:
                    if ',' in kvalue:
                        temp_list=kvalue.split('input ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['input'].append(jvalue)
                    
                    else:
                        jvalue=kvalue.split('input ')[1].replace(';','').strip()
                        module_dict[module_name]['input'].append(jvalue)

            elif 'output' in kvalue:
                if 'output' not in module_dict[module_name]:
                    module_dict[module_name].update(({'output':[]}))
                
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(small_idx+tdx)+']')

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        for tdx in range(large_idx-small_idx+1):
                            module_dict[module_name]['output'].append(jvalue+'['+str(small_idx+tdx)+']')

                else:
                    if ',' in kvalue:
                        temp_list=kvalue.split('output ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['output'].append(jvalue)
                    
                    else:
                        jvalue=kvalue.split('output ')[1].replace(';','').strip()
                        module_dict[module_name]['output'].append(jvalue)

            elif 'endmodule' not in kvalue and 'input' not in kvalue and 'wire' not in kvalue and 'output' not in kvalue:
                component_or_module=kvalue.strip().split(' ')[0].strip()
                list_of_line=' '.join(kvalue.strip().split(' ')[2:])
                module_dict[module_name].update({kvalue.strip().split(' ')[1].strip():{'id':component_or_module}})
                module_dict[module_name][kvalue.strip().split(' ')[1].strip()].update({'ports':{}})

                for tvalue in list_of_line.split('.'):
                    if '(' not in tvalue or ')' not in tvalue:
                        continue
                    module_dict[module_name][kvalue.strip().split(' ')[1].strip()]['ports'].update({tvalue.split('(')[0].strip():tvalue.split('(')[1].strip().split(')')[0].strip()})



    return module_dict




def get_tree(All):
    who_is_top=list()
    for ivalue in All:
        who_is_top.append(ivalue)
        All[ivalue].update({'components_counts':{}})
        All[ivalue].update({'module_counts':{}})
        kkkqqq=int()
        for kvalue in All[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='components_counts' and kvalue!='module_counts':
                if All[ivalue][kvalue]['id'] not in All:
                    All[ivalue]['components_counts'].update({kvalue:All[ivalue][kvalue]['id']})
                else:
                    All[ivalue]['module_counts'].update({kvalue:All[ivalue][kvalue]['id']})



    for ivalue in All:
        for kvalue in All[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='components_counts' and kvalue!='module_counts':
                if All[ivalue][kvalue]['id'] in who_is_top:
                    who_is_top.remove(All[ivalue][kvalue]['id'])

    copy_who_is_top=copy.deepcopy(who_is_top[0])
    who_is_top=[]
    for ivalue in All[copy_who_is_top]['module_counts']:
        if ivalue not in who_is_top:
            who_is_top.append(ivalue)

    parent=copy_who_is_top

    while True:
        will_add_list=list()
        will_del_list=list()
        for ivalue in who_is_top:

            for kvalue in All[ivalue.split('/')[-1]]['module_counts']:
                    will_add_list.append(ivalue+'/'+kvalue)

            if len(All[ivalue.split('/')[-1]]['module_counts'])!=0:
                will_del_list.append(ivalue)


        if len(will_add_list)==0:
            break
        
        for ivalue in will_del_list:
            who_is_top.remove(ivalue)
        
        who_is_top.extend(will_add_list)

    each_stage=dict()
    max_stage=int()
    for ivalue in who_is_top:
        count_stage=len(ivalue.split('/'))
        each_stage.update({ivalue:count_stage})
        if max_stage<count_stage:
            max_stage=count_stage

    current_stage=max_stage

    temp_dict=dict()
    while True:
        will_del_list=list()
        will_add_list=list()
        for ivalue in who_is_top:
            if len(ivalue.split('/'))==current_stage:
                if str(current_stage) not in temp_dict:
                    temp_dict.update({str(current_stage):int()})
                temp_dict[str(current_stage)]=temp_dict[str(current_stage)]+len(All[ivalue.split('/')[-1]]['components_counts'])
                will_del_list.append(ivalue)
                
                if ivalue.split('/'+ivalue.split('/')[-1])[0] not in will_add_list:
                    will_add_list.append(ivalue.split('/'+ivalue.split('/')[-1])[0])

        for ivalue in will_del_list:
            who_is_top.remove(ivalue)

        for ivalue in will_add_list:
            if ivalue not in who_is_top:
                who_is_top.append(ivalue)

        current_stage=current_stage-1
        if current_stage==0:
            break
    print(len(All[who_is_top[0]]['module_counts']))
    print(temp_dict)

    



    return 0



if __name__=="__main__":
    
    if sys.argv[1]==str(0):
        kkk=get_module_dict()
        with open('temp_temp.pickle','wb') as fw:
            pickle.dump(kkk,fw)
        fw.close()

    elif sys.argv[1]==str(1):
        with open('temp_temp.pickle','rb') as fw:
            kkk=pickle.load(fw)
        fw.close()
        mmm=get_tree(kkk)
