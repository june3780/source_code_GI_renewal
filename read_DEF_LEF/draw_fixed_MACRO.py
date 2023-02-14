import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import copy
import os
import sys
import json

def get_def(defdef,leflef,checking_number):
    lef_unit=float()
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
        
        elif fines[idx].strip().startswith('DATABASE MICRONS') and fines[idx].split('DATABASE MICRONS')[1].startswith(' '):
            lef_unit=float(fines[idx].split('DATABASE MICRONS')[1].split(';')[0].strip())


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
    position_of_macro=get_each_position(lef_temp_dict)





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


    new_lines=['']
    for idx in range(end_pin_idx-start_pin_idx+1):
        new_lines[-1]=new_lines[-1]+' '+lines[idx+start_pin_idx+1].replace('\n','').strip()

        if lines[idx+start_pin_idx+1].replace('\n','').strip().endswith(';'):
            new_lines.append('')
    del new_lines[-1]

    ext_pins_dict=get_ext_pins(new_lines)





    get_real_position(cell_dict,ext_pins_dict,position_of_macro,def_unit,die_position,checking_number)
    
    return 0



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




def get_real_position(cell,ext_pin,leflef,def_unit,die_area,saving):
    che=''
    overlapping_list=list()
    die_area=[[die_area[0][0]/def_unit,die_area[0][1]/def_unit],[die_area[1][0]/def_unit,die_area[1][1]/def_unit]]
    def_unit=float(def_unit)
    temp_dict=dict()
    for ivalue in cell:
        if cell[ivalue]['id'] in leflef:
            temp_dict.update({ivalue:dict()})
            cell_position=[float(cell[ivalue]['position'].split(' ')[0].strip())/def_unit,float(cell[ivalue]['position'].split(' ')[1].strip())/def_unit]
            real_macro_position=[[leflef[cell[ivalue]['id']]['MACRO_position'][0][0]+cell_position[0],leflef[cell[ivalue]['id']]['MACRO_position'][0][1]+cell_position[1]],\
                [leflef[cell[ivalue]['id']]['MACRO_position'][1][0]+cell_position[0],leflef[cell[ivalue]['id']]['MACRO_position'][1][1]+cell_position[1]]]
            temp_dict[ivalue].update({'macro_position':real_macro_position})
            temp_dict[ivalue].update({'orientation':cell[ivalue]['orientation']})

            if 'pin' in leflef[cell[ivalue]['id']]:
                overlapping_list.append(ivalue)

                temp_dict[ivalue].update({'pin':dict()})
                for kvalue in leflef[cell[ivalue]['id']]['pin']:
                    temp_pin_position=[[leflef[cell[ivalue]['id']]['pin'][kvalue]['PIN_position'][0][0]+real_macro_position[0][0],\
                                        leflef[cell[ivalue]['id']]['pin'][kvalue]['PIN_position'][0][1]+real_macro_position[0][1]],\
                                        [leflef[cell[ivalue]['id']]['pin'][kvalue]['PIN_position'][1][0]+real_macro_position[0][0],\
                                        leflef[cell[ivalue]['id']]['pin'][kvalue]['PIN_position'][1][1]+real_macro_position[0][1]]]
                    temp_dict[ivalue]['pin'].update({kvalue:{'pin_position':temp_pin_position}})
                    temp_dict[ivalue]['pin'][kvalue].update({'layer':leflef[cell[ivalue]['id']]['pin'][kvalue]['layer']})


    real_overlapped_list=dict()
    sticky_list=dict()
    for idx in range(len(overlapping_list)):
        for kdx in range(len(overlapping_list)):
            if idx==kdx:
                continue
            
            chenumber=checking_overlapping(temp_dict[overlapping_list[idx]]['macro_position'],temp_dict[overlapping_list[kdx]]['macro_position'])

            if chenumber==0:
                real_overlapped_list.update({overlapping_list[idx]:str()})
                real_overlapped_list.update({overlapping_list[kdx]:str()})

            elif chenumber==1:
                sticky_list.update({overlapping_list[idx]:str()})
                sticky_list.update({overlapping_list[kdx]:str()})
            

    only_sticky_list=copy.deepcopy(sticky_list)
    for ivalue in sticky_list:
        if ivalue not in real_overlapped_list:
            for kvalue in sticky_list:
                if kvalue==ivalue:
                    continue
                if kvalue not in real_overlapped_list:
                    chenumber=checking_overlapping(temp_dict[ivalue]['macro_position'],temp_dict[kvalue]['macro_position'])
                    if chenumber==1:
                        if ivalue in only_sticky_list:
                            del only_sticky_list[ivalue]
                        if kvalue in only_sticky_list:
                            del only_sticky_list[kvalue]



    x_list=list()
    y_list=list()
    special_x=list()
    special_y=list()
    special_pins=['p691917','p691918','p691919','p691920']
    for ivalue in ext_pin:
        if ivalue in special_pins:
            special_x.append(ext_pin[ivalue]['ext_pin_location'][0]/def_unit)
            special_y.append(ext_pin[ivalue]['ext_pin_location'][1]/def_unit)
        x_list.append(ext_pin[ivalue]['ext_pin_location'][0]/def_unit)
        y_list.append(ext_pin[ivalue]['ext_pin_location'][1]/def_unit)




    X=np.array([die_area[0][0],die_area[1][0]])
    Y=np.array([die_area[0][1],die_area[1][1]])
    plt.plot(X,Y,color='None')
    plt.scatter(x_list,y_list,color='blue',s=1)
    plt.scatter(special_x,special_y,color='black',s=4)

    for kdx in range(len(special_pins)):
        plt.text(special_x[kdx],special_y[kdx],special_pins[kdx].replace('p6919',''),size=4)

    shp=patches.Rectangle((die_area[0][0], die_area[0][1]), die_area[1][0]-die_area[0][0], die_area[1][1]-die_area[0][1], color='green', fill=False, linewidth=0.5)
    plt.gca().add_patch(shp)


    for ivalue in temp_dict:
        if 'pin' in temp_dict[ivalue]:
            if ivalue in sticky_list and ivalue not in real_overlapped_list and ivalue not in only_sticky_list:
                
                temp_origin=temp_dict[ivalue]['macro_position'][0]
                temp_width=temp_dict[ivalue]['macro_position'][1][0]-temp_origin[0]
                temp_height=temp_dict[ivalue]['macro_position'][1][1]-temp_origin[1]

                shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width, temp_height, color='black', fill=False, linewidth=0.5)
                if ivalue=='o680451':
                    plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)
                plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)
                
                plt.gca().add_patch(shp)

                for kvalue in temp_dict[ivalue]['pin']:
                    ### layer_checking(temp_dict[ivalue]['pin'][kvalue]['layer'],saving)
                    ### if che=='':
                    ###    print(temp_dict[ivalue]['pin'][kvalue]['layer'])
                    ###    che='che'
                    temp_origin=temp_dict[ivalue]['pin'][kvalue]['pin_position'][0]
                    temp_width=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][0]-temp_origin[0]
                    temp_height=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][1]-temp_origin[1]

                    shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width,temp_height, color='red', fill=True, linewidth=0.5)
                    plt.gca().add_patch(shp)


    plt.title(saving+'_temp_without_no_pins_macro_only_zsticky')
    plt.savefig(os.getcwd()+'/'+saving+'/'+saving+'_temp_without_no_pins_macro_only_zsticky.png',dpi=1000)


    for ivalue in temp_dict:
        if 'pin' in temp_dict[ivalue]:
            if ivalue in only_sticky_list and ivalue not in real_overlapped_list:
                
                temp_origin=temp_dict[ivalue]['macro_position'][0]
                temp_width=temp_dict[ivalue]['macro_position'][1][0]-temp_origin[0]
                temp_height=temp_dict[ivalue]['macro_position'][1][1]-temp_origin[1]

                shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width, temp_height, color='black', fill=False, linewidth=0.5)
                plt.gca().add_patch(shp)
                
                if ivalue=='o680451':
                    plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)
                plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)

                for kvalue in temp_dict[ivalue]['pin']:
                    ### layer_checking(temp_dict[ivalue]['pin'][kvalue]['layer'],saving)
                    ### if che=='':
                    ###    print(temp_dict[ivalue]['pin'][kvalue]['layer'])
                    ###    che='che'
                    temp_origin=temp_dict[ivalue]['pin'][kvalue]['pin_position'][0]
                    temp_width=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][0]-temp_origin[0]
                    temp_height=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][1]-temp_origin[1]

                    shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width,temp_height, color='red', fill=True, linewidth=0.5)
                    plt.gca().add_patch(shp)

    plt.title(saving+'_temp_without_no_pins_macro_only_sticky')
    plt.savefig(os.getcwd()+'/'+saving+'/'+saving+'_temp_without_no_pins_macro_only_sticky.png',dpi=1000)

    #plt.savefig(saving+'.png',dpi=1000)


    overlapped_id=dict()
    for ivalue in temp_dict:
        if 'pin' in temp_dict[ivalue]:
            if ivalue in real_overlapped_list:
                overlapped_id.update({cell[ivalue]['id']:str()})
                temp_origin=temp_dict[ivalue]['macro_position'][0]
                temp_width=temp_dict[ivalue]['macro_position'][1][0]-temp_origin[0]
                temp_height=temp_dict[ivalue]['macro_position'][1][1]-temp_origin[1]

                shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width, temp_height, color='black', fill=False, linewidth=0.5)
                plt.gca().add_patch(shp)
                
                if ivalue=='o680451':
                    plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)
                plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)

                for kvalue in temp_dict[ivalue]['pin']:
                    ### layer_checking(temp_dict[ivalue]['pin'][kvalue]['layer'],saving)
                    ### if che=='':
                    ###    print(temp_dict[ivalue]['pin'][kvalue]['layer'])
                    ###    che='che'
                    temp_origin=temp_dict[ivalue]['pin'][kvalue]['pin_position'][0]
                    temp_width=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][0]-temp_origin[0]
                    temp_height=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][1]-temp_origin[1]

                    shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width,temp_height, color='red', fill=True, linewidth=0.5)
                    plt.gca().add_patch(shp)


    plt.title(saving+'_temp_without_no_pins_macro_only_overlapped')
    plt.savefig(os.getcwd()+'/'+saving+'/'+saving+'_temp_without_no_pins_macro_only_overlapped.png',dpi=1000)





    for ivalue in temp_dict:
        if 'pin' in temp_dict[ivalue]:
            if ivalue not in real_overlapped_list:
                temp_origin=temp_dict[ivalue]['macro_position'][0]
                temp_width=temp_dict[ivalue]['macro_position'][1][0]-temp_origin[0]
                temp_height=temp_dict[ivalue]['macro_position'][1][1]-temp_origin[1]

                shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width, temp_height, color='black', fill=False, linewidth=0.5)
                plt.gca().add_patch(shp)
                
                if ivalue=='o680451':
                    plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)
                plt.text((temp_origin[0]+temp_dict[ivalue]['macro_position'][1][0])/2, (temp_origin[1]+temp_dict[ivalue]['macro_position'][1][1])/2,ivalue.replace('o680',''),size=4)

                for kvalue in temp_dict[ivalue]['pin']:
                    ### layer_checking(temp_dict[ivalue]['pin'][kvalue]['layer'],saving)
                    ### if che=='':
                    ###    print(temp_dict[ivalue]['pin'][kvalue]['layer'])
                    ###    che='che'
                    temp_origin=temp_dict[ivalue]['pin'][kvalue]['pin_position'][0]
                    temp_width=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][0]-temp_origin[0]
                    temp_height=temp_dict[ivalue]['pin'][kvalue]['pin_position'][1][1]-temp_origin[1]

                    shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width,temp_height, color='red', fill=True, linewidth=0.5)
                    plt.gca().add_patch(shp)

    plt.title(saving+'_temp_without_no_pins_macro')
    plt.savefig(os.getcwd()+'/'+saving+'/'+saving+'_temp_without_no_pins_macro.png',dpi=1000)

    for ivalue in temp_dict:
        if 'pin' not in temp_dict[ivalue]:
            
            temp_origin=temp_dict[ivalue]['macro_position'][0]
            temp_width=temp_dict[ivalue]['macro_position'][1][0]-temp_origin[0]
            temp_height=temp_dict[ivalue]['macro_position'][1][1]-temp_origin[1]

            shp=patches.Rectangle((temp_origin[0], temp_origin[1]), temp_width, temp_height, color='black', fill=False, linewidth=0.5)
            plt.gca().add_patch(shp)

    plt.title(saving+'_temp_with_all_macro')
    plt.savefig(os.getcwd()+'/'+saving+'/'+saving+'_temp_with_all_macro.png',dpi=1000)
    #plt.savefig(saving+'_with_all_macro.png',dpi=1000)
    plt.clf()


    return temp_dict





def checking_overlapping(dot1,dot2):
    con=int()
    if dot1[1][1]<dot2[0][1] or dot1[0][1]>dot2[1][1]:
        con=2
    elif dot1[1][0]<dot2[0][0] or dot1[0][0]>dot2[1][0]:
        con=2
    
    if con==0:
        if dot1[1][0]==dot2[0][0] or dot1[0][0]==dot2[1][0] or dot1[1][1]==dot2[0][1] or dot1[0][1]==dot2[1][1]:
            con=1

    return con












def layer_checking(layer,def_test):
    if def_test=='superblue1' or def_test=='superblue3' or def_test=='superblue4' or def_test=='superblue5' \
        or def_test=='superblue7' or def_test=='superblue10' or def_test=='superblue16' or def_test=='superblue18':
        if layer!='metal4':
            print(layer)
    
    elif def_test=='superblue11_ISPD' or def_test=='superblue11_ISPD' or def_test=='superblue11_ISPD':
        if layer!='metal5':
            print(layer)
        


    return 0






def get_each_position(lef_dict):
    temp_dict=dict()
    for ivalue in lef_dict:
        if 'ORIGIN' in lef_dict[ivalue] and 'width' in lef_dict[ivalue] and 'height' in lef_dict[ivalue]:
            if ivalue not in temp_dict:
                temp_dict.update({ivalue:dict()})
            MACRO_position=list()
            MACRO_position.append([float(lef_dict[ivalue]['ORIGIN'][0]),float(lef_dict[ivalue]['ORIGIN'][1])])
            temp_position=[float(lef_dict[ivalue]['width']),float(lef_dict[ivalue]['height'])]
            temp_position[0]=temp_position[0]+MACRO_position[0][0]
            temp_position[1]=temp_position[1]+MACRO_position[0][1]
            MACRO_position.append(temp_position)
            temp_dict[ivalue].update({'MACRO_position':MACRO_position})

    for ivalue in lef_dict:
        if 'pin' in lef_dict[ivalue]:
            for kvalue in lef_dict[ivalue]['pin']:
                if 'pin' not in temp_dict[ivalue]:
                    temp_dict[ivalue].update({'pin':dict()})
                temp_dict[ivalue]['pin'].update({kvalue:dict()})
                pin_position_1=[float(lef_dict[ivalue]['pin'][kvalue]['RECT'][0][0]),float(lef_dict[ivalue]['pin'][kvalue]['RECT'][0][1])]
                pin_position_2=[float(lef_dict[ivalue]['pin'][kvalue]['RECT'][0][2]),float(lef_dict[ivalue]['pin'][kvalue]['RECT'][0][3])]
                pin_position_1=[pin_position_1[0]+temp_dict[ivalue]['MACRO_position'][0][0],pin_position_1[1]+temp_dict[ivalue]['MACRO_position'][0][1]]
                pin_position_2=[pin_position_2[0]+temp_dict[ivalue]['MACRO_position'][0][0],pin_position_2[1]+temp_dict[ivalue]['MACRO_position'][0][1]]
                total_position=[pin_position_1,pin_position_2]
                temp_dict[ivalue]['pin'][kvalue].update({'PIN_position':total_position,'layer':lef_dict[ivalue]['pin'][kvalue]['layer']})
                

    return temp_dict








def get_pin_info(macro):

    temp_dict=dict()
    for ivalue in macro:
        temp_dict.update({ivalue:dict()})
        pin_start_idx=list()
        pin_end_idx=list()
        for kdx in range(len(macro[ivalue])):
            if macro[ivalue][kdx].strip().startswith('ORIGIN') and macro[ivalue][kdx].split('ORIGIN')[1].startswith(' '):
                temp_dict[ivalue].update({'ORIGIN':macro[ivalue][kdx].split('ORIGIN')[1].split(';')[0].strip().split(' ')})
            elif macro[ivalue][kdx].strip().startswith('SIZE') and macro[ivalue][kdx].split('SIZE')[1].startswith(' '):
                temp_dict[ivalue].update({'width':float(macro[ivalue][kdx].split('SIZE')[1].strip().split(' ')[0]),'height':float(macro[ivalue][kdx].split('BY')[1].split(';')[0].strip())})
            else:
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


            for rdx in range(len(start_port_idx)):
                for jdx in range(end_port_idx[rdx]-start_port_idx[rdx]+1):
                    if macro[ivalue][start_port_idx[rdx]+jdx].strip().startswith('RECT') and macro[ivalue][start_port_idx[rdx]+jdx].split('RECT')[1].startswith(' '):
                        if 'RECT' not in temp_dict[ivalue]['pin'][pin_name]:
                            temp_dict[ivalue]['pin'][pin_name].update({'RECT':list()})
                        temp_dict[ivalue]['pin'][pin_name]['RECT'].append(macro[ivalue][start_port_idx[rdx]+jdx].split('RECT')[1].split(';')[0].strip().split(' '))

                    if macro[ivalue][start_port_idx[rdx]+jdx].strip().startswith('LAYER') and macro[ivalue][start_port_idx[rdx]+jdx].split('LAYER')[1].startswith(' '):
                        if 'layer' not in temp_dict[ivalue]['pin'][pin_name]:
                            temp_dict[ivalue]['pin'][pin_name].update({'layer':str()})
                        temp_dict[ivalue]['pin'][pin_name]['layer']=macro[ivalue][start_port_idx[rdx]+jdx].split('LAYER')[1].split(';')[0].strip()

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







if __name__=="__main__":

    superblue=['superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD']
    #superblue=['superblue11_ISPD','superblue12_ISPD','superblue16_ISPD']
    for ivalue in superblue:
        checking_def='../../data/'
        checking_lef='../../data/'
        checking_def=checking_def+ivalue+'/'+ivalue+'.def'
        checking_lef=checking_lef+ivalue+'/'+ivalue+'.lef'

        if ivalue not in os.listdir(os.getcwd()):
            os.mkdir(os.getcwd()+'/'+ivalue+'/')

        print(ivalue)
        get_def(checking_def,checking_lef,ivalue)
        print()
        break
