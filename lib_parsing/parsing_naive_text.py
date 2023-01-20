import os
import json


def get_naive_txt(libb,checking):

    list_of_cell=os.listdir(libb.split('.lib')[0])
    check=str()
    if checking=='pin':
        check='pin('

    for idx in range(len(list_of_cell)):
        
        directory_and_info=os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx])
        lines=list()

        for kdx in range(len(directory_and_info)):
            if directory_and_info[kdx]==checking:
                with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+checking+'/naive.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()
        
        if len(lines)==0:
            print(list_of_cell[idx],'continue')
            print()
            continue

        for kdx in range(len(lines)):
            lines[kdx]=lines[kdx].replace('\n','')

        start_lines=list()
        end_lines=list()

        for kdx in range(len(lines)):
            if lines[kdx].strip().startswith(check):
                print(lines[kdx])
                

        print(list_of_cell[idx])
        print()


        if idx==0:
            break

    return 0



def get_info_txt(libb):
    list_break=[]
    list_of_cell=os.listdir(libb.split('.lib')[0])
    check=str()

    for idx in range(len(list_of_cell)):
        list_break.append(list_of_cell[idx].split('12TM1P')[0])
        foot=str('')
        
        directory_and_info=os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx])
        lines=list()

        if 'info.txt' in directory_and_info:
            with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/info.txt','r') as fw:
                lines=fw.readlines()
            fw.close()
        
        if len(lines)==0:
            print('##################################################################################################################',list_of_cell[idx],'continue')
            print()
            continue

        for kdx in range(len(lines)):
            lines[kdx]=lines[kdx].replace('\n','')

        start_lines=list()
        end_lines=list()

        for kdx in range(len(lines)):
                if lines[kdx].strip().startswith('cell_footprint : '):
                    foot='june'

                print(lines[kdx])
        if foot !='june':
            
            print('##################################################################################################################',idx,list_of_cell[idx],'break')
            print()
            #break

        print('##################################################################################################################',list_of_cell[idx])
        print()


        #if idx==0:
        #    break
    listcomponents=dict()
    with open('../../data/easy/easy.v','r') as fw:
        veril_easy=fw.readlines()
    fw.close()
    for idx in range(len(list_break)):
        for kvalue in veril_easy:
            if list_break[idx] in kvalue:
                listcomponents.update({list_break[idx]:str()})
                print(idx)
                break
    print()
    print(len(listcomponents))

    return 0


if __name__=="__main__":

    lib='../../data/20221219/LIB/tcbn40lpbwp12tm1ptc_ccs.lib'
    
    target='pin'##################################################### dynamic_current, pin, leakage_power, leakage_current_intrinsic_parasitic, pg_pin, test_cell, statetable, ff, latch
    target='info'##################################################### info (info.txt)
    if target!='info':
        get_naive_txt(lib,target)
    else:
        get_info_txt(lib)