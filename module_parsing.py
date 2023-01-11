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
                module_dict[module_name].update(({'input':[]}))
                module_dict[module_name].update(({'output':[]}))
                module_dict[module_name].update(({'wire':[]}))

            elif 'input ' in kvalue:
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])

                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            if large_idx>small_idx:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['input'].append(jvalue+'['+str(large_idx-tdx)+']')
                            elif large_idx<small_idx:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['input'].append(jvalue+'['+str(large_idx+tdx)+']')
                            else:
                                if large_idx==0:
                                    module_dict[module_name]['input'].append(jvalue+'['+str(0)+']')
                                else:
                                    print(kvalue,'Error : define_error')
        
                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif large_idx<small_idx:
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['input'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            if large_idx==0:
                                print(kvalue)
                                module_dict[module_name]['input'].append(jvalue+'['+str(0)+']')
                            else:
                                print(kvalue,'Error : define_error')
                else:
                    if ',' in kvalue:
                        temp_list=kvalue.split('input ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['input'].append(jvalue)
                    
                    else:
                        jvalue=kvalue.split('input ')[1].replace(';','').strip()
                        module_dict[module_name]['input'].append(jvalue)

            elif 'output' in kvalue:
                if '[' in kvalue:
                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])

                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            if large_idx>small_idx:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['output'].append(jvalue+'['+str(large_idx-tdx)+']')
                            elif large_idx<small_idx:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['output'].append(jvalue+'['+str(large_idx+tdx)+']')
                            else:
                                if large_idx==0:
                                    module_dict[module_name]['output'].append(jvalue+'['+str(0)+']')
                                else:
                                    print(kvalue,'Error : define_error')

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif large_idx<small_idx:
                            
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['output'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            if large_idx==0:
                                print(kvalue)
                                module_dict[module_name]['output'].append(jvalue+'['+str(0)+']')
                            else:
                                print(kvalue,'Error : define_error')

                else:
                    if ',' in kvalue:
                        temp_list=kvalue.split('output ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['output'].append(jvalue)
                    
                    else:
                        jvalue=kvalue.split('output ')[1].replace(';','').strip()
                        module_dict[module_name]['output'].append(jvalue)

            elif 'wire' in kvalue:
                if '[' in kvalue:

                    small_idx=int(kvalue.split(']')[0].split(':')[1])
                    large_idx=int(kvalue.split(']')[0].split(':')[0].split('[')[1])
                    if ',' in kvalue:
                        temp_list=kvalue.split('] ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            if large_idx>small_idx:
                                for tdx in range(large_idx-small_idx+1):
                                    module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx-tdx)+']')
                            elif large_idx<small_idx:
                                for tdx in range(small_idx-large_idx+1):
                                    module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx+tdx)+']')   
                            else:
                                if large_idx==0:
                                    module_dict[module_name]['wire'].append(jvalue+'['+str(0)+']')
                                else:
                                    print(kvalue,'Error : define_error')

                    else:
                        jvalue=kvalue.split('] ')[1].replace(';','').strip()
                        if large_idx>small_idx:
                            for tdx in range(large_idx-small_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx-tdx)+']')
                        elif large_idx<small_idx:
                            print(kvalue)
                            for tdx in range(small_idx-large_idx+1):
                                module_dict[module_name]['wire'].append(jvalue+'['+str(large_idx+tdx)+']')
                        else:
                            if large_idx==0:
                                module_dict[module_name]['wire'].append(jvalue+'['+str(0)+']')
                            else:
                                print(kvalue,'Error : define_error')

                else:
                    if ',' in kvalue:
                        temp_list=kvalue.split('wire ')[1].replace(';','').strip().split(', ')
                        for jvalue in temp_list:
                            module_dict[module_name]['wire'].append(jvalue)
                    
                    else:
                        jvalue=kvalue.split('wire ')[1].replace(';','').strip()
                        module_dict[module_name]['wire'].append(jvalue)


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
            if kvalue!='input' and kvalue!='output' and kvalue!='components_counts' and kvalue!='module_counts' and kvalue!='wire':
                if All[ivalue][kvalue]['id'] not in All:
                    All[ivalue]['components_counts'].update({kvalue:All[ivalue][kvalue]['id']})
                else:
                    All[ivalue]['module_counts'].update({kvalue:All[ivalue][kvalue]['id']})

    '''for ivalue in All:
        for kvalue in All[ivalue]['components_counts']:
            if 'BTB_mem' in kvalue:
                print(kvalue)
                print(len(All[ivalue][kvalue]['ports']))
                print()'''

    for ivalue in All:
        for kvalue in All[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue!='components_counts' and kvalue!='module_counts' and kvalue!='wire':
                if All[ivalue][kvalue]['id'] in who_is_top:
                    who_is_top.remove(All[ivalue][kvalue]['id'])
    
    temp_first_list=list()
    module_first_list=list()
    for ivalue in All[who_is_top[0]]['module_counts']:
        temp_first_list.append(ivalue)
        module_first_list.append(All[who_is_top[0]]['module_counts'][ivalue])



    while True:
        will_add_list_module=list()
        will_del_list_module=list()
        will_add_list_name=list()
        will_del_list_name=list()
        tempkk=int()
        for idx in range(len(temp_first_list)):
            temp_module=module_first_list[idx].split('/')[-1]
            #temp_name=temp_first_list[idx].split('/')[-1]
            
            if len(All[temp_module]['module_counts'])==0:
                tempkk=tempkk+1
            else:
                if temp_first_list[idx] not in will_del_list_name:
                    will_del_list_name.append(temp_first_list[idx])
                    will_del_list_module.append(module_first_list[idx])
                
                for kvalue in All[temp_module]['module_counts']:
                    if temp_first_list[idx]+'/'+kvalue not in will_add_list_name:
                        will_add_list_name.append(temp_first_list[idx]+'/'+kvalue)
                        will_add_list_module.append(module_first_list[idx]+'/'+All[temp_module]['module_counts'][kvalue])

        if len(will_del_list_name)!=0:
            for idx in range(len(will_del_list_name)):
                if will_del_list_name[idx] in temp_first_list:
                    temp_first_list.remove(will_del_list_name[idx])
                    module_first_list.remove(will_del_list_module[idx])

        if len(will_add_list_name)!=0:
            temp_first_list.extend(will_add_list_name)
            module_first_list.extend(will_add_list_module)
        if tempkk==len(temp_first_list):
            break

    max_stage=int()
    for ivalue in temp_first_list:
        count_stage=len(ivalue.split('/'))
        if max_stage<count_stage:
            max_stage=count_stage

    current_stage=max_stage
    exp_name_list=copy.deepcopy(temp_first_list)
    exp_module_list=copy.deepcopy(module_first_list)

    counting=dict()
    while True:
        temp_del_list=list()
        temp_add_list=list()
        temp_del_molist=list()
        temp_add_molist=list()
        std_macro=int()
        no_child=int()
        for idx in range(len(exp_name_list)):
            if len(exp_name_list[idx].split('/'))==1:
                no_child=no_child+1
                continue

            if len(exp_name_list[idx].split('/'))==current_stage:
                if exp_name_list[idx] not in temp_del_list:
                    temp_del_list.append(exp_name_list[idx])
                    temp_del_molist.append(exp_module_list[idx])

                if exp_name_list[idx].split('/'+exp_name_list[idx].split('/')[-1])[0] not in temp_add_list:
                    temp_add_list.append(exp_name_list[idx].split('/'+exp_name_list[idx].split('/')[-1])[0])
                    temp_add_molist.append(exp_module_list[idx].split('/'+exp_module_list[idx].split('/')[-1])[0])
                
                std_macro=std_macro+len(All[exp_module_list[idx].split('/')[-1]]['components_counts'])

        for idx in range(len(temp_del_list)):
            exp_name_list.remove(temp_del_list[idx])
            exp_module_list.remove(temp_del_molist[idx])
        
        for idx in range(len(temp_add_list)):
            exp_name_list.append(temp_add_list[idx])
            exp_module_list.append(temp_add_molist[idx])

        if no_child==len(exp_name_list):
            rrr=int()
            for idx in range(len(exp_name_list)):
                rrr=rrr+len(All[exp_module_list[idx]]['components_counts'])
            counting.update({'1':rrr})
            break

        counting.update({str(current_stage):std_macro})
        current_stage=current_stage-1
        
    print(counting)
    print('tpgmlwns1!')
    print()


    for ivalue in All:
        for kvalue in All[ivalue]:
            if kvalue !='input' and kvalue != 'output' and kvalue !='components_counts' and kvalue !='wire' and kvalue !='module_counts':
                if All[ivalue][kvalue]['id']=='spsram_hd_2048x32m4s' or All[ivalue][kvalue]['id']=='sprf_hs_128x38m2s'\
                    or All[ivalue][kvalue]['id']=='spsram_hd_256x23m4m' or All[ivalue][kvalue]['id']=='spsram_hd_256x22m4m':

                    All[ivalue][kvalue]['ports']=get_macro_port(All[ivalue]['input'],All[ivalue]['output'],All[ivalue]['wire'],All[ivalue][kvalue]['ports'],All[ivalue][kvalue]['id'])
                    
                elif kvalue in All[ivalue]['components_counts']:
                    for jvalue in All[ivalue][kvalue]['ports']:
                        All[ivalue][kvalue]['ports'][jvalue]=[All[ivalue][kvalue]['ports'][jvalue]]
                        

                else:
                    All[ivalue][kvalue]['ports']=get_module_port(All[ivalue]['input'],All[ivalue]['output'],All[ivalue]['wire'],All[ivalue][kvalue]['ports'],All[ivalue][kvalue]['id'],All)


    print()
    print('############################################################################################')
    print('############################################################################################')
    print('############################################################################################')
    print()

    current_stage=max_stage
    exp_name_list=copy.deepcopy(temp_first_list)
    exp_module_list=copy.deepcopy(module_first_list)

    print(len(All['d25_core_top']['input']),len(All['d25_core_top']['output']))
    print()
    wire_debt=dict()
    wire_net=dict()
    chch=str()
    while True:
        temp_del_list=list()
        temp_add_list=list()
        temp_del_molist=list()
        temp_add_molist=list()

        no_child=int()

        for idx in range(len(exp_name_list)):
            #print(exp_name_list[idx],'###################',exp_name_list[idx].split('/')[-1],current_stage)
            if len(exp_name_list[idx].split('/'))==1:
                no_child=no_child+1
                continue

            if len(exp_name_list[idx].split('/'))==current_stage:
                #print(exp_name_list[idx],'##',exp_name_list[idx].split('/')[-1],current_stage)
                if exp_name_list[idx] not in temp_del_list:
                    temp_del_list.append(exp_name_list[idx])
                    temp_del_molist.append(exp_module_list[idx])

                if exp_name_list[idx].split('/'+exp_name_list[idx].split('/')[-1])[0] not in temp_add_list:
                    temp_add_list.append(exp_name_list[idx].split('/'+exp_name_list[idx].split('/')[-1])[0])
                    temp_add_molist.append(exp_module_list[idx].split('/'+exp_module_list[idx].split('/')[-1])[0])




                current_mod=exp_module_list[idx].split('/')[-1]

                for ivalue in All[current_mod]['wire']:
                        wire_net.update({exp_name_list[idx]+'/'+ivalue:[]})


                for ivalue in All[current_mod]['components_counts']:
                    for kvalue in All[current_mod][ivalue]['ports']:
                        if exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0] in wire_net:
                            wire_net[exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0]].append(exp_name_list[idx]+'/'+ivalue+' '+All[current_mod][ivalue]['id']+'/'+kvalue)

                for ivalue in All[current_mod]['module_counts']:
                    for kvalue in All[current_mod][ivalue]['ports']:
                        if exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0] in wire_net:
                            wire_net[exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0]].extend(wire_debt[exp_name_list[idx]+'/'+ivalue+'/'+kvalue])
                            del wire_debt[exp_name_list[idx]+'/'+ivalue+'/'+kvalue]



                for ivalue in All[current_mod]['input']:
                    wire_debt.update({exp_name_list[idx]+'/'+ivalue:[]})
                
                for ivalue in All[current_mod]['output']:
                    wire_debt.update({exp_name_list[idx]+'/'+ivalue:[]})

                for ivalue in All[current_mod]['components_counts']:
                    for kvalue in All[current_mod][ivalue]['ports']:
                        if exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0] in wire_debt:
                            wire_debt[exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0]].append(exp_name_list[idx]+'/'+ivalue+' '+All[current_mod][ivalue]['id']+'/'+kvalue)

                for ivalue in All[current_mod]['module_counts']:
                    for kvalue in All[current_mod][ivalue]['ports']:
                        if exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0] in wire_debt:
                            wire_debt[exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0]].extend(wire_debt[exp_name_list[idx]+'/'+ivalue+'/'+kvalue])
                            del wire_debt[exp_name_list[idx]+'/'+ivalue+'/'+kvalue]
                            #print(exp_name_list[idx]+'/'+All[current_mod][ivalue]['ports'][kvalue][0])



                #print()
                #print(exp_name_list[idx])
        #print()
        '''if current_stage==5:
            break'''


        if chch=='con':
            break

        for idx in range(len(temp_del_list)):
            exp_name_list.remove(temp_del_list[idx])
            exp_module_list.remove(temp_del_molist[idx])
        
        for idx in range(len(temp_add_list)):
            exp_name_list.append(temp_add_list[idx])
            exp_module_list.append(temp_add_molist[idx])

        if no_child==len(exp_name_list):
            chch='con'
        current_stage=current_stage-1




    temp_del=list()
    for ivalue in wire_debt:
        if len(wire_debt[ivalue])==0:
            temp_del.append(ivalue)
    for ivalue in temp_del:
        del wire_debt[ivalue]
    #print(json.dumps(wire_net,indent=4))
    print(len(wire_net))
    con=int()
    for ivalue in wire_net:
        con=con+len(wire_net[ivalue])
    print(con)
    print()

    temp_temp=list()
    for ivalue in wire_debt:
        temp_slash_count=[]
        for kvalue in wire_debt[ivalue]:
            temp_slash_count.append(len(kvalue.split('/')))

        for kdx in range(len(temp_slash_count)):
            for jdx in range(len(temp_slash_count)):
                if temp_slash_count[kdx]!=temp_slash_count[jdx]:
                    if ivalue not in temp_temp:
                        temp_temp.append(ivalue)

    for ivalue in temp_temp:
        print(wire_debt[ivalue][0])
        #print(json.dumps(wire_debt[ivalue],indent=4))
    print()
    id_list=[]
    for ivalue in All:
        for kvalue in All[ivalue]:
            if kvalue!='input' and kvalue!='output' and kvalue !='wire' and kvalue !='components_counts' and kvalue !='module_counts' and kvalue not in All[ivalue]['module_counts']:
                if All[ivalue][kvalue]['id'] not in id_list:
                    id_list.append(All[ivalue][kvalue]['id'])
    print(id_list)
    return 0




def get_module_port(in_list,out_list,wire_list,origin_ports,name_module,all):
    
    array_in=[]
    array_out=[]
    array_wire=[]
    for ivalue in in_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_in:
                array_in.append(ivalue.split('[')[0])

    for ivalue in out_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_out:
                array_out.append(ivalue.split('[')[0])

    for ivalue in wire_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_wire:
                array_wire.append(ivalue.split('[')[0])

    for ivalue in origin_ports: ### ivalue는 port 이름
        temp_list=list()
        if '{' in origin_ports[ivalue]: ### origin_ports[ivalue]는 ivalue port 의 구성요소들
            origin_ports[ivalue]=origin_ports[ivalue].replace('{','').replace('}','')
        origin_ports[ivalue]=origin_ports[ivalue].strip().split(', ')

        for kvalue in origin_ports[ivalue]: ### kvalue 는 k번째 구성요소
            if '[' in kvalue and ':' in kvalue:
                large_idx=int(kvalue.split(':')[0].split('[')[1])
                small_idx=int(kvalue.split(':')[1].split(']')[0])
                if large_idx>small_idx:
                    for tdx in range(large_idx-small_idx+1):
                        temp_list.append(kvalue.split('[')[0]+'['+str(large_idx-tdx)+']')
                elif large_idx<small_idx:
                    for tdx in range(large_idx-small_idx+1):
                        temp_list.append(kvalue.split('[')[0]+'['+str(large_idx+tdx)+']')
                else:
                    if large_idx==0:
                        temp_list.append(kvalue.split('[')[0])
                    else:
                        print(name_module,'Error : define_error')
            elif '[' in kvalue:
                temp_list.append(kvalue)
            elif kvalue in in_list or kvalue in out_list or kvalue in wire_list:
                temp_list.append(kvalue)
            else:
                if kvalue in array_in:
                    for tvalue in in_list:
                        if tvalue.startswith(kvalue+'['):
                            temp_list.append(tvalue)
                
                elif kvalue in array_out:
                    for tvalue in out_list:
                        if tvalue.startswith(kvalue+'['):
                            temp_list.append(tvalue)

                elif kvalue in array_wire:
                    for tvalue in wire_list:
                        if tvalue.startswith(kvalue+'['):
                            temp_list.append(tvalue)

                elif "\'b" in kvalue:
                    temp_list.append(kvalue)
                
                else:
                    print('Error : not defined ports are used')
        origin_ports[ivalue]=temp_list
    

    array_in=[]
    array_out=[]
    array_wire=[]
    for ivalue in all[name_module]['input']:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_in:
                array_in.append(ivalue.split('[')[0])

    for ivalue in all[name_module]['output']:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_out:
                array_out.append(ivalue.split('[')[0])

    for ivalue in all[name_module]['wire']:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_wire:
                array_wire.append(ivalue.split('[')[0])

    will_new_mod=dict()
    for ivalue in origin_ports:
        if len(origin_ports[ivalue])==1:
            if ivalue in array_out or ivalue in array_in or ivalue in array_wire:
                will_new_mod.update({ivalue+'[0]':origin_ports[ivalue]})
            else:
                will_new_mod.update({ivalue:origin_ports[ivalue]})
        else:
            list_temp=list()
            
            if ivalue in array_in:
                for kdx in range(len(all[name_module]['input'])):
                    if all[name_module]['input'][kdx].startswith(ivalue+'['):
                        list_temp.append(all[name_module]['input'][kdx])

            elif ivalue in array_out:
                for kdx in range(len(all[name_module]['output'])):
                    if all[name_module]['output'][kdx].startswith(ivalue+'['):
                        list_temp.append(all[name_module]['output'][kdx])

            elif ivalue in array_wire:
                for kdx in range(len(all[name_module]['wire'])):
                    if all[name_module]['wire'][kdx].startswith(ivalue+'['):
                        list_temp.append(all[name_module]['wire'][kdx])

            for kdx in range(len(list_temp)):
                will_new_mod.update({list_temp[kdx]:[origin_ports[ivalue][kdx]]})



    ports_life=dict()

    for ivalue in all[name_module]['input']:
        ports_life.update({ivalue:1})
    for ivalue in all[name_module]['output']:
        ports_life.update({ivalue:1})
    for ivalue in all[name_module]['wire']:
        ports_life.update({ivalue:1})



    for ivalue in will_new_mod:
        if len(will_new_mod[ivalue])!=ports_life[ivalue]:
            print('Error : lack of ports')

    return will_new_mod









def get_macro_port(in_list,out_list,wire_list,origin_ports,name_macro):
    array_in=[]
    array_out=[]
    array_wire=[]

    for ivalue in in_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_in:
                array_in.append(ivalue.split('[')[0])

    for ivalue in out_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_out:
                array_out.append(ivalue.split('[')[0])

    for ivalue in wire_list:
        if '[' in ivalue:
            if ivalue.split('[')[0] not in array_wire:
                array_wire.append(ivalue.split('[')[0])

    #print(in_list)
    ports_life=dict()
    if name_macro=='spsram_hd_2048x32m4s':
        ports_life.update({'RTSEL':2,'WTSEL':2,'Q':32,'A':11,'AM':11,'BWEB':32,'BWEBM':32,'D':32\
            ,'DM':32,'PD':1,'AWT':1,'BIST':1,'CLK':1,'CEB':1,'CEBM':1,'WEB':1,'WEBM':1})
    elif name_macro=='sprf_hs_128x38m2s':
        ports_life.update({'TSEL':2,'Q':38,'A':7,'BWEB':38,'D':38,'RTSEL':1,'TURBO':1,'PD':1\
            ,'CLK':1,'CEB':1,'WEB':1})
    elif name_macro=='spsram_hd_256x23m4m':
        ports_life.update({'RTSEL':2,'WTSEL':2,'Q':23,'A':8,'AM':8,'BWEB':23,'BWEBM':23,'D':23\
            ,'DM':23,'PD':1,'AWT':1,'BIST':1,'CLK':1,'CEB':1,'CEBM':1,'WEB':1,'WEBM':1})
    elif name_macro=='spsram_hd_256x22m4m':
        ports_life.update({'RTSEL':2,'WTSEL':2,'Q':22,'A':8,'AM':8,'BWEB':22,'BWEBM':22,'D':22\
            ,'DM':22,'PD':1,'AWT':1,'BIST':1,'CLK':1,'CEB':1,'CEBM':1,'WEB':1,'WEBM':1})

    origin_ports_list=copy.deepcopy(origin_ports)
    for ivalue in ports_life:
        if '{' in origin_ports_list[ivalue]:
            origin_ports_list[ivalue]=origin_ports_list[ivalue].replace('{','').replace("}",'').strip()
        checking_list=origin_ports_list[ivalue].split(', ')
        will_be_new_list=[]
        
        for kvalue in checking_list:
            if '[' in kvalue and ':' in kvalue:
                small_idx=int(kvalue.split(']')[0].split(':')[1])
                large_idx=int(kvalue.split('[')[1].split(':')[0])
                temp_name=kvalue.split('[')[0]
                if large_idx>small_idx:
                    for tdx in range(large_idx-small_idx+1):
                        will_be_new_list.append(temp_name+'['+str(large_idx-tdx)+']')
                elif large_idx<small_idx:
                    for tdx in range(large_idx-small_idx+1):
                        will_be_new_list.append(temp_name+'['+str(large_idx+tdx)+']')
                else:
                    if large_idx==0:
                        will_be_new_list.append(temp_name)
                    else:
                        print(name_macro,'Error : define_error')
            elif kvalue in in_list or kvalue in out_list or kvalue in wire_list:
                will_be_new_list.append(kvalue)
            else:
                if kvalue in array_in:
                    for jvalue in in_list:
                        if jvalue.startswith(kvalue+'['):
                            will_be_new_list.append(jvalue)

                elif kvalue in array_out:
                    for jvalue in out_list:
                        if jvalue.startswith(kvalue+'['):
                            will_be_new_list.append(jvalue)

                elif kvalue in array_wire:
                    for jvalue in wire_list:
                        if jvalue.startswith(kvalue+'['):
                           will_be_new_list.append(jvalue)
                
                elif "\'b" in kvalue:
                    will_be_new_list.append(kvalue)
                
                else:
                    print('Error : not defined ports are used')
        origin_ports_list[ivalue]=will_be_new_list

        if len(will_be_new_list)!=ports_life[ivalue]:
            print('Error : lack of ports')

    return origin_ports_list



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
