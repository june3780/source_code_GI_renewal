import json
import numpy as np
from scipy.stats import norm



def get_distance_with_macro(defdef,leflef,text):

    def_unit=float()
    die_position=list()

    with open(leflef,'r') as fw:
        fines=fw.readlines()
    fw.close()

    macro_start_idx=list()
    macro_end_idx=list()
    for idx in range(len(fines)):
        if fines[idx].strip().startswith('MACRO') and fines[idx].split('MACRO')[1].startswith(' '):
            macro_start_idx.append(idx)
            macro_end_idx.append(get_end_idx(idx,fines))
        



    MACRO_dict=dict()
    for idx in range(len(macro_start_idx)):
        temp_macro_name=fines[macro_start_idx[idx]].split('MACRO')[1].replace('\n','').strip()

        for kdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
            if fines[kdx+macro_start_idx[idx]].strip().startswith('CLASS') and fines[kdx+macro_start_idx[idx]].split('CLASS')[1].startswith(' '):
                if fines[kdx+macro_start_idx[idx]].split('CLASS')[1].strip().startswith('BLOCK') and fines[kdx+macro_start_idx[idx]].split('BLOCK')[1].replace('\n','').strip()==';':
                   MACRO_dict.update({temp_macro_name:list()})
                   continue

        if temp_macro_name in MACRO_dict:
            for kdx in range(macro_end_idx[idx]-macro_start_idx[idx]+1):
                MACRO_dict[temp_macro_name].append(fines[kdx+macro_start_idx[idx]].replace('\n',''))
    lef_temp_dict=get_pin_info(MACRO_dict)



    with open(defdef,'r') as fw:
        lines=fw.readlines()
    fw.close()

    start_cell_idx=int()
    end_cell_idx=int()
    start_pin_idx=int()
    end_pin_idx=int()
    diearea=str()
    for idx in range(len(lines)):

        if lines[idx].strip().startswith('COMPONENTS') and lines[idx].split('COMPONENTS')[1].startswith(' '):
            start_cell_idx=idx
        elif lines[idx].strip().startswith('END COMPONENTS'):
            end_cell_idx=idx
        
        elif lines[idx].strip().startswith('PINS') and lines[idx].split('PINS')[1].startswith(' '):
            start_pin_idx=idx
        elif lines[idx].strip().startswith('END PINS'):
            end_pin_idx=idx
    
        elif lines[idx].strip().startswith('DIEAREA'):
            diearea=lines[idx].split('DIEAREA')[1].split(';')[0].strip()

        elif lines[idx].strip().startswith('UNITS DISTANCE MICRONS'):
            def_unit=float(lines[idx].split('UNITS DISTANCE MICRONS')[1].split(';')[0].strip())
        
        
    
    first_die=diearea.split('(')[1].split(')')[0].strip().split(' ')
    second_die=diearea.split('(')[-1].split(')')[0].strip().split(' ')

    die_position.append([float(first_die[0]),float(first_die[1])])
    die_position.append([float(second_die[0]),float(second_die[1])])


    new_lines=['']
    for idx in range(end_cell_idx-start_cell_idx+1):
        new_lines[-1]=new_lines[-1]+' '+lines[idx+start_cell_idx+1].replace('\n','').strip()

        if lines[idx+start_cell_idx+1].replace('\n','').strip().endswith(';'):
            new_lines.append('')
    del new_lines[-1]

    cell_dict=get_def_components(new_lines)


    '''new_lines=['']
    for idx in range(end_pin_idx-start_pin_idx+1):
        new_lines[-1]=new_lines[-1]+' '+lines[idx+start_pin_idx+1].replace('\n','').strip()

        if lines[idx+start_pin_idx+1].replace('\n','').strip().endswith(';'):
            new_lines.append('')
    del new_lines[-1]

    ext_pins_dict=get_ext_pins(new_lines)'''



    macro_cells=list()
    for ivalue in cell_dict:
        if cell_dict[ivalue]['id'] in lef_temp_dict and 'pin' in lef_temp_dict[cell_dict[ivalue]['id']]:
            macro_cells.append(ivalue)

    each_macro_position=dict()
    for ivalue in macro_cells:
        each_macro_position.update({ivalue:[float(cell_dict[ivalue]['position'].split(' ')[0].strip()),float(cell_dict[ivalue]['position'].split(' ')[1].strip())]})

    with open('temp_macro_position.json','w') as fw:
        json.dump(each_macro_position,fw,indent=4)
    fw.close()
    
    with open('temp_macro_position.json','r') as fw:
        each_macro_position=json.load(fw)
    fw.close()

    with open(text,'r') as fw:
        lines=fw.readlines()
    fw.close()
    ttt=float()
    for ivalue in lines:
        one_macro=ivalue.replace('\n','').split('_and_')[0].strip()
        two_macro=ivalue.replace('\n','').split('_and_')[1].split('_distance_')[0].strip()
        distance=abs(each_macro_position[one_macro][0]-each_macro_position[two_macro][0])+\
            abs(each_macro_position[one_macro][1]-each_macro_position[two_macro][1])
        ttt=ttt+distance
    
    ttt=ttt/len(lines)
    print()
    print(ttt)

    #print(json.dumps(cell_dict,indent=4))




    return 0







def get_pin_info(macro):

    temp_dict=dict()
    for ivalue in macro:
        temp_dict.update({ivalue:dict()})
        pin_start_idx=list()
        pin_end_idx=list()
        for kdx in range(len(macro[ivalue])):
            '''if macro[ivalue][kdx].strip().startswith('ORIGIN') and macro[ivalue][kdx].split('ORIGIN')[1].startswith(' '):
                temp_dict[ivalue].update({'ORIGIN':macro[ivalue][kdx].split('ORIGIN')[1].split(';')[0].strip().split(' ')})
            elif macro[ivalue][kdx].strip().startswith('SIZE') and macro[ivalue][kdx].split('SIZE')[1].startswith(' '):
                temp_dict[ivalue].update({'width':float(macro[ivalue][kdx].split('SIZE')[1].strip().split(' ')[0]),'height':float(macro[ivalue][kdx].split('BY')[1].split(';')[0].strip())})
            else:'''
            if macro[ivalue][kdx].strip().startswith('PIN') and macro[ivalue][kdx].split('PIN')[1].startswith(' '):
                    pin_start_idx.append(kdx)
                    pin_name=macro[ivalue][kdx].split('PIN')[1].strip()
                    for jdx in range(len(macro[ivalue])):
                        if jdx<kdx:
                            continue
                        if macro[ivalue][jdx].strip()=='END '+pin_name:
                            pin_end_idx.append(jdx)
                            break


        for kdx in range(len(pin_start_idx)):
            pin_name=macro[ivalue][pin_start_idx[kdx]].split('PIN')[1].strip()
            if 'pin' not in temp_dict[ivalue]:
                temp_dict[ivalue].update({'pin':dict()})
            temp_dict[ivalue]['pin'].update({pin_name:dict()})
            
            start_port_idx=list()
            end_port_idx=list()

            for jdx in range(pin_end_idx[kdx]-pin_start_idx[kdx]+1):
                temp_line=macro[ivalue][pin_start_idx[kdx]+jdx]
                
                #print(temp_line)
                if temp_line.strip().startswith('PORT') and temp_line.strip().endswith('PORT'):
                    start_port_idx.append(pin_start_idx[kdx]+jdx)
                    for udx in range(pin_end_idx[kdx]-pin_start_idx[kdx]+1):
                        if udx<jdx:
                            continue
                        if macro[ivalue][pin_start_idx[kdx]+udx].strip().startswith('END'):
                            end_port_idx.append(pin_start_idx[kdx]+udx)
                            break


            '''for rdx in range(len(start_port_idx)):
                for jdx in range(end_port_idx[rdx]-start_port_idx[rdx]+1):
                    if macro[ivalue][start_port_idx[rdx]+jdx].strip().startswith('RECT') and macro[ivalue][start_port_idx[rdx]+jdx].split('RECT')[1].startswith(' '):
                        if 'RECT' not in temp_dict[ivalue]['pin'][pin_name]:
                            temp_dict[ivalue]['pin'][pin_name].update({'RECT':list()})
                        temp_dict[ivalue]['pin'][pin_name]['RECT'].append(macro[ivalue][start_port_idx[rdx]+jdx].split('RECT')[1].split(';')[0].strip().split(' '))

                    if macro[ivalue][start_port_idx[rdx]+jdx].strip().startswith('LAYER') and macro[ivalue][start_port_idx[rdx]+jdx].split('LAYER')[1].startswith(' '):
                        if 'layer' not in temp_dict[ivalue]['pin'][pin_name]:
                            temp_dict[ivalue]['pin'][pin_name].update({'layer':str()})
                        temp_dict[ivalue]['pin'][pin_name]['layer']=macro[ivalue][start_port_idx[rdx]+jdx].split('LAYER')[1].split(';')[0].strip()'''

    return temp_dict





def get_end_idx(start_idx,lines):
    start_macro_name=lines[start_idx].split('MACRO')[1].replace('\n','').strip()
    end_macro_name='END '+start_macro_name
    for idx in range(len(lines)):
        if lines[idx].replace('\n','').strip()==end_macro_name:
            return idx



def get_def_components(components_list):
    temp_dict=dict()
    for ivalue in components_list:
        components_name=ivalue.split('-')[1].strip().split(' ')[0]
        components_id=ivalue.split('-')[1].strip().split(' ')[1]
        components_location=str()
        if 'UNPLACED' in ivalue:
            continue
        elif 'FIXED' in ivalue:
            components_location=ivalue.split('FIXED')[1].split('(')[1].split(')')[0].strip()
        elif 'PLACED' in ivalue:
            components_location=ivalue.split('PLACED')[1].split('(')[1].split(')')[0].strip()
        components_ori=ivalue.split(components_location)[1].split(')')[1].split(';')[0].strip()
        temp_dict.update({components_name:dict()})
        temp_dict[components_name].update({'id':components_id,'position':components_location,'orientation':components_ori})

    return temp_dict




def get_ext_pins(line):
    temp_dict=dict()
    for ivalue in line:
        temp_components_list=ivalue.split('+')
        ext_pin_name=temp_components_list[0].split('-')[1].strip()
        ext_pin_location=list()
        ext_pin_orientation=str()
        for kdx in range(len(temp_components_list)):
            if ('PLACED' in temp_components_list[kdx] or 'FIXED' in temp_components_list[kdx]) and 'UNPLACED' not in  temp_components_list[kdx]:
                ext_pin_temp_location=temp_components_list[kdx].split('(')[1].split(')')[0].strip()
                ext_pin_location.append(float(ext_pin_temp_location.split(' ')[0]))
                ext_pin_location.append(float(ext_pin_temp_location.split(' ')[1]))
                ext_pin_orientation=temp_components_list[kdx].split(')')[1].strip()
        
        if ext_pin_name not in temp_dict:
            temp_dict.update({ext_pin_name:dict()})
        temp_dict[ext_pin_name].update({'ext_pin_location':ext_pin_location,'orientation':ext_pin_orientation})

    return temp_dict




def temp_func(text):
    with open('temp_macro_position.json','r') as fw:
        each_macro_position=json.load(fw)
    fw.close()

    with open(text,'r') as fw:
        lines=fw.readlines()
    fw.close()

    average_of_distance=dict()
    for ivalue in each_macro_position:
        dist=list()
        for kvalue in each_macro_position:
            if ivalue==kvalue:
                continue
            dist.append(abs(each_macro_position[ivalue][0]-each_macro_position[kvalue][0])+\
            abs(each_macro_position[ivalue][1]-each_macro_position[kvalue][1]))

        average_of_distance.update({ivalue:{'average':np.mean(dist),'std':np.std(dist),'dist_group':dist}})


    tt=int()
    for ivalue in lines:
        one_macro=ivalue.replace('\n','').split('_and_')[0].strip()
        two_macro=ivalue.replace('\n','').split('_and_')[1].split('_distance_')[0].strip()
        distance=abs(each_macro_position[one_macro][0]-each_macro_position[two_macro][0])+\
            abs(each_macro_position[one_macro][1]-each_macro_position[two_macro][1])
        
        mu1=average_of_distance[one_macro]['average']
        S1=average_of_distance[one_macro]['std']

        zstat1=(distance-mu1)/S1
        p1=norm.cdf(zstat1)
        

        mu2=average_of_distance[two_macro]['average']
        S2=average_of_distance[two_macro]['std']

        zstat2=(distance-mu2)/S2
        p2=norm.cdf(zstat2)

        ttt=int()
        max_distance=float()
        for rvalue in average_of_distance[one_macro]['dist_group']:
            if max_distance<rvalue:
                max_distance=rvalue
            if rvalue>distance:
                ttt=ttt+1

        min_distance=max_distance
        for rvalue in average_of_distance[one_macro]['dist_group']:
            if min_distance>rvalue:
                min_distance=rvalue
        
        one_macro_close=str()
        for jvalue in each_macro_position:
            if abs(each_macro_position[one_macro][0]-each_macro_position[jvalue][0])+\
            abs(each_macro_position[one_macro][1]-each_macro_position[jvalue][1])==min_distance:
                one_macro_close=jvalue

        qqq=int()
        for rvalue in average_of_distance[two_macro]['dist_group']:
            if rvalue>distance:
                qqq=qqq+1


        max_distance=float()
        for rvalue in average_of_distance[two_macro]['dist_group']:
            if max_distance<rvalue:
                max_distance=rvalue


        min_distance=max_distance
        for rvalue in average_of_distance[two_macro]['dist_group']:
            if min_distance>rvalue:
                min_distance=rvalue
        
        two_macro_close=str()
        for jvalue in each_macro_position:
            if abs(each_macro_position[two_macro][0]-each_macro_position[jvalue][0])+\
            abs(each_macro_position[two_macro][1]-each_macro_position[jvalue][1])==min_distance:
                two_macro_close=jvalue

        if tt==0:
            with open('temp_result.txt','w') as fw:
                fw.write(one_macro+' | '+two_macro+' | ranking : '+str(len(each_macro_position)-ttt-1)+' '+str(len(each_macro_position)-qqq-1)+' | shortest '+one_macro_close+' '+two_macro_close+' \n')    
            fw.close()
            tt=1

        else:
            with open('temp_result.txt','a') as fw:
                fw.write(one_macro+' | '+two_macro+' | ranking : '+str(len(each_macro_position)-ttt-1)+' '+str(len(each_macro_position)-qqq-1)+' | shortest '+one_macro_close+' '+two_macro_close+' \n')    
            fw.close()


        #print(round(p1*100,3),'% |',round(p2*100,3),'% |')
        #print()

    return 0


if __name__=="__main__":

    superblue=['superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD']
    #superblue=['superblue11_ISPD','superblue12_ISPD','superblue16_ISPD']
    for ivalue in superblue:
        checking_def='../../data/'
        checking_lef='../../data/'
        checking_def=checking_def+ivalue+'/'+ivalue+'.def'
        checking_lef=checking_lef+ivalue+'/'+ivalue+'.lef'
        print(ivalue)


        temp_func(checking_lef.split(ivalue+'.lef')[0]+'calc_distance.txt')
        #get_distance_with_macro(checking_def,checking_lef,checking_lef.split(ivalue+'.lef')[0]+'calc_distance.txt')
        print()
        break