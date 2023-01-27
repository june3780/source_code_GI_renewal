import os
import json
import sys


def get_naive_txt(libb,checking):

    list_of_cell=os.listdir(libb.split('.lib')[0])
    check=str()
    if checking=='pin':
        check='pin('
    elif checking=='dynamic_current':
        check='dynamic_current ('

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
                start_lines.append(kdx)
                end_lines.append(counting_function(kdx,lines))
        

        for kdx in range(len(start_lines)):
            #for jdx in range(end_lines[kdx]-start_lines[kdx]):

            checking_number=start_lines[kdx]
            with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+checking+'/case_'+str(kdx)+'.txt','w') as fw:
                fw.write(lines[checking_number]+'\n')
            fw.close()

            while checking_number!=end_lines[kdx]:
                checking_number=checking_number+1
                with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+checking+'/case_'+str(kdx)+'.txt','a') as fw:
                    fw.write(lines[checking_number]+'\n')
                fw.close()

                

        print(list_of_cell[idx])
        print()


    return 0






def counting_function(start_number,lines):
    left=int()
    right=int()
    if  '{' in lines[start_number]:
        left=left+1
    if  '}' in lines[start_number]:
        right=right+1

    for idx in range(len(lines)-start_number-1):
        if '{' in lines[start_number+idx+1]:
            left=left+1
        if '}' in lines[start_number+idx+1]:
            right=right+1
        if left==right:
            return start_number+idx+1


            
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




def get_each_timing(libb):
    list_of_cell=os.listdir(libb.split('.lib')[0])
    check=str()

    che='che'
    for idx in range(len(list_of_cell)):
        if 'temp_function_groups' in list_of_cell[idx]:
            continue

        directory_and_info=os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx])

        if 'pin' not in directory_and_info:
            continue

        print(list_of_cell[idx])
        pins_list=os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/')
        #tt=int()
        for kdx in range(len(pins_list)):
            if pins_list[kdx].endswith('.txt'):
                continue
            if pins_list[kdx].startswith('output_'):
                list_of_output_dictionary=os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/'+pins_list[kdx])
                if 'timing.txt' not in list_of_output_dictionary:
                    continue

                #tt=tt+1
                
                with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/'+pins_list[kdx]+'/timing.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()

                timing_start_idx=list()
                timing_end_idx=list()
                for rdx in range(len(lines)):
                    if lines[rdx].strip().startswith('timing ('):
                        timing_start_idx.append(rdx)
                        timing_end_idx.append(counting_function(rdx,lines))

                if 'timing' not in os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/'+pins_list[kdx]):
                    os.mkdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/'+pins_list[kdx]+'/timing')

                for rdx in range(len(timing_start_idx)):
                    temp_cases=libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/'+pins_list[kdx]+'/timing/timing_case_'+str(rdx)+'.txt'
                    for qdx in range(timing_end_idx[rdx]-timing_start_idx[rdx]+1):
                        if qdx==0:
                            with open(temp_cases,'w') as fw:
                                fw.write(lines[qdx+timing_start_idx[rdx]])
                            fw.close()

                        else:
                            with open(temp_cases,'a') as fw:
                                fw.write(lines[qdx+timing_start_idx[rdx]])
                            fw.close()
                
                #tt=tt+1


                #print(list_of_cell[idx])
                #print(pins_list[kdx])

                
        #if tt>0:
        #    break

        if che=='break':
            print('breakkkkkkkkkkkkkkk')
            break

        #print()        
        '''for kdx in range(len(directory_and_info)):
                with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/pin/naive.txt','r') as fw:
                    lines=fw.readlines()
                fw.close()
        
        if len(lines)==0:
            print(list_of_cell[idx],'continue')
            print()
            continue

        for kdx in range(len(lines)):
            lines[kdx]=lines[kdx].replace('\n','')'''

    return 0



if __name__=="__main__":
    lib='../../data/20221219/LIB/tcbn40lpbwp12tm1ptc_ccs.lib'
    #lib='../../data/20221219/LIB/tcbn40lpbwp12tm1plvttc_ccs.lib'
    
    target='pin'##################################################### dynamic_current, pin, leakage_power, leakage_current_intrinsic_parasitic, pg_pin, test_cell, statetable, ff, latch
    #target='info'##################################################### info (info.txt)
    timing_target='timing'


    if sys.argv[1]=='0':
        if target!='info':
            get_naive_txt(lib,target)
        else:
            get_info_txt(lib)

    elif sys.argv[1]=='1':
        get_each_timing(lib)
