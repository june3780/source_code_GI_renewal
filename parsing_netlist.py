import json
import pickle
import sys
import copy

def get_module_dict(wherethemodule):
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

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()

                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx-tdx)+']')

                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['input'].append(jvalue+'['+str(large_idx)+']')

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

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['output'].append(jvalue+'['+str(large_idx)+']')
                else:

                    if ',' in kvalue:
                        temp_list=kvalue.split('output ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['output'].append(jvalue)
                    else:
                        jvalue=kvalue.split('output ')[1].replace(';','').strip()
                        module_dict[module_name]['output'].append(jvalue)

            elif 'wire' in kvalue:
                if 'wire' not in module_dict[module_name]:
                    module_dict[module_name].update(({'wire':[]}))
                
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])

                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        
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

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif small_idx>large_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx)+']')
                else:

                    if ',' in kvalue:
                        temp_list=kvalue.split('wire ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['wire'].append(jvalue)
                    else:
                        jvalue=kvalue.split('wire ')[1].replace(';','').strip()
                        module_dict[module_name]['wire'].append(jvalue)

            elif 'assign' in kvalue:
                print(kvalue)



            elif 'endmodule' not in kvalue and 'input' not in kvalue and 'wire' not in kvalue and 'output' not in kvalue:
                component_or_module=kvalue.strip().split(' ')[0].strip()
                list_of_line=' '.join(kvalue.strip().split(' ')[2:])
                module_dict[module_name].update({kvalue.strip().split(' ')[1].strip():{'id':component_or_module}})
                module_dict[module_name][kvalue.strip().split(' ')[1].strip()].update({'ports':{}})

                for tvalue in list_of_line.split('.'):
                    if '(' not in tvalue or ')' not in tvalue:
                        continue
                    module_dict[module_name][kvalue.strip().split(' ')[1].strip()]['ports'].update({tvalue.split('(')[0].strip():tvalue.split('(')[1].strip().split(')')[0].strip()})




    for ivalue in module_dict:
        module_dict[ivalue].update({'components_counts':{}})
        module_dict[ivalue].update({'module_counts':{}})

        for kvalue in module_dict[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='wire' and kvalue!='components_counts' and kvalue!='module_counts':

                if module_dict[ivalue][kvalue]['id'] not in module_dict:
                    module_dict[ivalue]['components_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})

                else:
                    module_dict[ivalue]['module_counts'].update({kvalue:module_dict[ivalue][kvalue]['id']})


    for ivalue in module_dict:
        array_input=list()
        array_output=list()
        array_wire=list()

        for kvalue in module_dict[ivalue]['input']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_input:
                    array_input.append(kvalue.split('[')[0])
        
        for kvalue in module_dict[ivalue]['output']:
            if '[' in kvalue:
                if kvalue.split('[')[0] not in array_output:
                    array_output.append(kvalue.split('[')[0])

        if 'wire' in module_dict[ivalue]:
            for kvalue in module_dict[ivalue]['wire']:
                if '[' in kvalue:
                    if kvalue.split('[')[0] not in array_wire:
                        array_wire.append(kvalue.split('[')[0])

        for kvalue in module_dict[ivalue]:
            if kvalue=='input' or kvalue=='output' or kvalue=='wire' or kvalue=='module_counts' or kvalue=='components_counts':
                continue
            if module_dict[ivalue][kvalue]['id']!='spsram_hd_256x23m4m'\
                and module_dict[ivalue][kvalue]['id']!='spsram_hd_2048x32m4s'\
                and module_dict[ivalue][kvalue]['id']!='spsram_hd_256x22m4m'\
                and module_dict[ivalue][kvalue]['id']!='sprf_hs_128x38m2s'\
                and kvalue in module_dict[ivalue]['components_counts']:
                continue
                
            else:
                temp_ports_list=copy.deepcopy(module_dict[ivalue][kvalue]['ports'])
                new_ports_list=dict()
                for tvalue in temp_ports_list:
                    temple_list=list()

                    if '{' not in temp_ports_list[tvalue]:
                        if temp_ports_list[tvalue] not in array_input\
                            and temp_ports_list[tvalue] not in array_output\
                            and temp_ports_list[tvalue] not in array_wire:

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

                            else:
                                temp_ports_list[tvalue]=[temp_ports_list[tvalue]]

                        elif temp_ports_list[tvalue] in array_input:
                            
                            for jvalue in module_dict[ivalue]['input']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list

                        elif temp_ports_list[tvalue] in array_output:
                            for jvalue in module_dict[ivalue]['output']:
                                if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                    temple_list.append(jvalue)
                            temp_ports_list[tvalue]=temple_list

                        else:
                            if temp_ports_list[tvalue] in array_wire:
                                for jvalue in module_dict[ivalue]['wire']:
                                    if jvalue.startswith(temp_ports_list[tvalue]+'['):
                                        temple_list.append(jvalue)
                                temp_ports_list[tvalue]=temple_list

                    else:
                        just_ports=temp_ports_list[tvalue].replace('{','').replace('}','').split(', ')
                        new_temple_list=list()

                        for jvalue in just_ports:
                            temp_component=jvalue.strip()
                            if ':' in temp_component:
                                large_idx=int(temp_component.split(']')[0].split(':')[0].split('[')[1])
                                small_idx=int(temp_component.split(']')[0].split(':')[1])
                                if large_idx>small_idx:
                                    for fdx in range(large_idx-small_idx+1):
                                        new_temple_list.append(temp_component.split('[')[0]+'['+str(large_idx-fdx)+']')
                                elif small_idx>large_idx:
                                    for fdx in range(small_idx-large_idx+1):
                                        new_temple_list.append(temp_component.split('[')[0]+'['+str(large_idx+fdx)+']')

                            elif temp_component in array_input:
                                for fvalue in module_dict[ivalue]['input']:
                                    if fvalue.startswith(temp_component+'['):
                                        new_temple_list.append(fvalue)

                            elif temp_component in array_output:
                                for fvalue in module_dict[ivalue]['output']:
                                    if fvalue.startswith(temp_component+'['):
                                        new_temple_list.append(fvalue)
                            
                            elif temp_component in array_wire:
                                for fvalue in module_dict[ivalue]['wire']:
                                    if fvalue.startswith(temp_component+'['):
                                        new_temple_list.append(fvalue)
                            else:
                                new_temple_list.append(temp_component)

                        temp_ports_list[tvalue]=new_temple_list

                    if kvalue in module_dict[ivalue]['components_counts']:
                        new_ports_list.update(macro_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue]))

                    else:
                        new_ports_list.update(module_ports(module_dict[ivalue][kvalue]['id'],tvalue,temp_ports_list[tvalue],module_dict))

                module_dict[ivalue][kvalue]['ports']=new_ports_list



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


    return module_dict





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
    ### lef 파일에서 단일 포트가 배열로 정의 되지 않는다면 => ###  +'['+str(0-idx)+']'  ### 삭제하기 !!
    new_ports_compo=dict()

    if id=='spsram_hd_256x23m4m':

        if port_name=='RTSEL' or port_name=='WTSEL':
            for idx in range(2):
                new_ports_compo.update({port_name+'['+str(1-idx)+']':port_list[idx]})

        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            for idx in range(23):
                new_ports_compo.update({port_name+'['+str(22-idx)+']':port_list[idx]})
        
        elif port_name=='A' or port_name=='AM':
            for idx in range(8):
                new_ports_compo.update({port_name+'['+str(7-idx)+']':port_list[idx]})
        
        else:
            for idx in range(1):
                new_ports_compo.update({port_name+'['+str(0-idx)+']':port_list[idx]})


    elif id=='spsram_hd_2048x32m4s':

        if port_name=='RTSEL' or port_name=='WTSEL':
            for idx in range(2):
                new_ports_compo.update({port_name+'['+str(1-idx)+']':port_list[idx]})

        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            for idx in range(32):
                new_ports_compo.update({port_name+'['+str(31-idx)+']':port_list[idx]})
        
        elif port_name=='A' or port_name=='AM':
            for idx in range(11):
                new_ports_compo.update({port_name+'['+str(10-idx)+']':port_list[idx]})
        
        else:
            for idx in range(1):
                new_ports_compo.update({port_name+'['+str(0-idx)+']':port_list[idx]})


    elif id=='spsram_hd_256x22m4m':

        if port_name=='RTSEL' or port_name=='WTSEL':
            for idx in range(2):
                new_ports_compo.update({port_name+'['+str(1-idx)+']':port_list[idx]})

        elif port_name=='Q' or port_name=='BWEB' or port_name=='BWEBM' or port_name=='D' or port_name=='DM':
            for idx in range(22):
                new_ports_compo.update({port_name+'['+str(21-idx)+']':port_list[idx]})
        
        elif port_name=='A' or port_name=='AM':
            for idx in range(8):
                new_ports_compo.update({port_name+'['+str(7-idx)+']':port_list[idx]})
        
        else:
            for idx in range(1):
                new_ports_compo.update({port_name+'['+str(0-idx)+']':port_list[idx]})


    elif id=='sprf_hs_128x38m2s':
        if port_name=='TSEL':
            for idx in range(2):
                new_ports_compo.update({port_name+'['+str(1-idx)+']':port_list[idx]})

        elif port_name=='Q' or port_name=='BWEB' or port_name=='D':
            for idx in range(38):
                new_ports_compo.update({port_name+'['+str(37-idx)+']':port_list[idx]})
        
        elif port_name=='A':
            for idx in range(7):
                new_ports_compo.update({port_name+'['+str(6-idx)+']':port_list[idx]})
        
        else:
            for idx in range(1):
                new_ports_compo.update({port_name+'['+str(0-idx)+']':port_list[idx]})

    return new_ports_compo








def get_add_mod(All,upper_module,info):
    
    for ivalue in info[All[upper_module]['module']]['module_counts']:
        temp_id=info[All[upper_module]['module']][ivalue]['id']
        All.update({upper_module+'/'+ivalue:{'info':info[temp_id],'module':temp_id}})
        get_add_mod(All,upper_module+'/'+ivalue,info)

    return All




def checking_list(All,ivalue,toptop):
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




def get_tree(All):

    who_is_top=list()
    for ivalue in All:
        who_is_top.append(ivalue)

    for ivalue in All:
        for kvalue in All[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='wire' and kvalue!='components_counts' and kvalue!='module_counts':
                if All[ivalue][kvalue]['id'] in who_is_top:
                    who_is_top.remove(All[ivalue][kvalue]['id'])

    top_module=who_is_top[0]


    all_tree=dict()
    treeAll=dict()
    for ivalue in All[top_module]['module_counts']:
        temp_id=All[top_module][ivalue]['id']
        treeAll.update({ivalue:{'info':All[temp_id],'module':temp_id}})
        all_tree=get_add_mod(treeAll,ivalue,All)

    list_tree_keys=list(all_tree.keys())
    for ivalue in list_tree_keys:
        checking_list(All,ivalue,top_module)
    
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


    net_group=dict()
    debt_group=dict()

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

            if 'wire' in all_tree[current_mod]['info']:
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
            net_group[All[top_module][ivalue]['ports'][ivalue]].append(ivalue+' '+kvalue)
    

    print(len(components_list_with_ports))
    print(len(only_components))
    print()

    checking_net_components=list()
    checking_only_components=dict()
    for ivalue in net_group:
        for kvalue in net_group[ivalue]:
            checking_net_components.append(kvalue)

            checking_only_components.update({kvalue.split(' ')[0]:[]})
    checking_only_components=list(checking_only_components.keys())

    print(len(checking_net_components))
    print(len(checking_only_components))


    '''for idx in range(len(checking_net_components)):
        #print(idx,checking_net_components[idx])
        components_list_with_ports.remove(checking_net_components[idx])
    print('\n\n######################################################\n\n')
    print(components_list_with_ports)
    print(len(components_list_with_ports))'''
    #for ivalue in checking_net_components:
    #    print(ivalue)

    for ivalue in net_group:
        if ivalue in All[top_module]['input'] or ivalue in All[top_module]['output']:
            net_group[ivalue].append('PIN '+ivalue)

        '''if len(net_group[ivalue])==1:
            if '/' not in ivalue:
                if ivalue in All[top_module]['input'] or ivalue in All[top_module]['output']:
                    continue
                else:
                    print(ivalue,net_group[ivalue],'TTTTT')
            else:
                print(ivalue,net_group[ivalue])'''

    print()
    print(len(net_group))
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

            #print(conseq)
        




    return new_net_group




if __name__=="__main__":
    
    if sys.argv[1]==str(0):
        kkk=get_module_dict('../data/easy/easy.v')
        with open('temp_temp.pickle','wb') as fw:
            pickle.dump(kkk,fw)
        fw.close()

    elif sys.argv[1]==str(1):
        with open('temp_temp.pickle','rb') as fw:
            kkk=pickle.load(fw)
        fw.close()
        mmm=get_tree(kkk)
        with open('temp_module_nets.json','w') as fw:
            json.dump(mmm,fw,indent=4)
        fw.close()
