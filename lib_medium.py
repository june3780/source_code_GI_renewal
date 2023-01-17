import json
import os
import sys

def parsing_lib(libb):
    with open(libb,'r') as fw:
        lines=fw.readlines()
    fw.close()
    cell_list=[[]]
    

    for ivalue in lines:
        if ivalue.replace('\n','').strip().startswith('cell ('):
            cell_list.append([])
        cell_list[-1].append(ivalue.replace('\n',''))


    for idx in range(len(cell_list)):
        if idx==0:
            continue
        cell_dir=libb.split('.lib')[0]+'/'+cell_list[idx][0].split('cell (')[1].split(')')[0]
        if cell_list[idx][0].split('cell (')[1].split(')')[0] not in os.listdir(libb.split('.lib')[0]):
            os.mkdir(cell_dir)
        for kdx in range(len(cell_list[idx])):
            if kdx==0:
                with open(cell_dir+'/naive.txt','w') as fw:
                    fw.write(cell_list[idx][kdx]+'\n')
                fw.close()
            else:
                if idx==len(cell_list)-1 and kdx==len(cell_list[idx])-1:
                    break
                with open(cell_dir+'/naive.txt','a') as fw:
                    fw.write(cell_list[idx][kdx]+'\n')
                fw.close()

        ##@print(idx,cell_list[idx][0].split('cell (')[1].split(')')[0])
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



def checking_lines_start_end(start_idx,end_idx):
    force='no'
    for idx in range(len(start_idx)):
        if idx==len(start_idx)-1:
            break
        if end_idx[idx]+1!=start_idx[idx+1]:
            force='force'
            break

    return force



def each_file_directory_info(libb,chekcing,first_or_not):
    checking_str=str()
    if chekcing!='leakage_current_intrinsic_parasitic':

        if chekcing=='pin':
            checking_str='pin('

        elif chekcing=='leakage_power':
            checking_str='leakage_power ('
            
        elif chekcing=='dynamic_current':
            checking_str='dynamic_current ('
        
        elif chekcing=='pg_pin':
            checking_str='pg_pin ('
        
        elif chekcing=='test_cell':
            checking_str='test_cell ('
        
        elif chekcing=='statetable':
            checking_str='statetable ('

        elif chekcing=='ff':
            checking_str='ff ('

        elif chekcing=='latch':
            checking_str='latch ('

    list_of_cell=os.listdir(libb.split('.lib')[0])
    force_break='no'
    for idx in range(len(list_of_cell)):
            force_break='no'
            temp_txt=str()
            if first_or_not==str(1):
                temp_txt=libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/naive.txt'
            else:
                temp_txt=libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt'
        #if list_of_cell[idx]=='AN2D0BWP12TM1PLVT':
        #if idx==0:
            start_lines=list()
            end_lines=list()

            with open(temp_txt,'r') as fw:
                lines=fw.readlines()
            fw.close()
            for kdx in range(len(lines)):
                lines[kdx]=lines[kdx].replace('\n','')

            if chekcing=='leakage_current_intrinsic_parasitic':
                for kdx in range(len(lines)):
                    if lines[kdx].strip().startswith('leakage_current (') or lines[kdx].strip().startswith('intrinsic_parasitic ('):
                        start_lines.append(kdx)
            else:
                for kdx in range(len(lines)):
                    if lines[kdx].strip().startswith(checking_str):
                        start_lines.append(kdx)

            if len(start_lines)==0:
                for kdx in range(len(lines)):
                    if kdx==0:
                        with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt','w') as fw:
                            fw.write(lines[kdx]+'\n')
                        fw.close()
                    else:
                        if lines[kdx].strip().startswith('/*'):
                            break
                        else:
                            with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt','a') as fw:
                                fw.write(lines[kdx]+'\n')
                            fw.close()
                ##@print(idx,list_of_cell[idx],'continue')
                continue

            for kdx in range(len(start_lines)):
                    end_lines.append(counting_function(start_lines[kdx],lines))

            force_break=checking_lines_start_end(start_lines,end_lines)

            if force_break=='force':
                print(idx,list_of_cell[idx],'break')
                break

            else:
                if chekcing not in os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]):
                    os.mkdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+chekcing)

                for kdx in range(len(lines[start_lines[0]:end_lines[-1]+1])):
                    if kdx==0:
                        with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+chekcing+'/naive.txt','w') as fw:
                            fw.write(lines[start_lines[0]+kdx]+'\n')
                        fw.close()
                    else:
                        if lines[start_lines[0]+kdx].strip().startswith('/*'):
                            break
                        else:
                            with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/'+chekcing+'/naive.txt','a') as fw:
                                fw.write(lines[start_lines[0]+kdx]+'\n')
                            fw.close()

                for kdx in range(end_lines[-1]-start_lines[0]+1):
                    del lines[end_lines[-1]-kdx]

                for kdx in range(len(lines)):
                    if kdx==0:
                        with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt','w') as fw:
                            fw.write(lines[kdx]+'\n')
                        fw.close()
                    else:
                        if lines[kdx].strip().startswith('/*'):
                            break
                        else:
                            with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt','a') as fw:
                                fw.write(lines[kdx]+'\n')
                            fw.close()

            ##@print(idx,list_of_cell[idx])

    return 0



def checking_each_cell_left_right(libb):
    list_of_cell=os.listdir(libb.split('.lib')[0])
    for idx in range(len(list_of_cell)):
            temp_txt=str()
            temp_txt=libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt'

            with open(temp_txt,'r') as fw:
                lines=fw.readlines()
            fw.close()

            left=int()
            right=int()

            for ivalue in lines:
                if '{' in ivalue:
                    left=left+1
                if '}' in ivalue:
                    right=right+1
            if left==1 and right==1:
                ##@print(idx,list_of_cell[idx],'continue')
                continue
            else:
                print(idx,list_of_cell[idx],'break')
                break
        
    return 0





def checking_cell_info(libb):
    list_of_cell=os.listdir(libb.split('.lib')[0])
    for idx in range(len(list_of_cell)):
            temp_txt=str()
            temp_txt=libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/temp_naive.txt'

            if 'temp_naive.txt' not in os.listdir(libb.split('.lib')[0]+'/'+list_of_cell[idx]):
                ##@print(idx,list_of_cell[idx],'continue')
                continue

            with open(temp_txt,'r') as fw:
                lines=fw.readlines()
            fw.close()

            for kdx in range(len(lines)):
                lines[kdx]=lines[kdx].replace('\n','')
            

            area=float()
            cell_leakage_power=float()
            cell_footprint=str()
            dont_use=str()
            dont_touch=str()
            clock_gating_integrated_cell=str()

            temp_lines=list()

            for kdx in range(len(lines)):

                if lines[kdx].strip().startswith('area : '):
                    area=float(lines[kdx].split('area : ')[1].replace(';','').strip())

                elif lines[kdx].strip().startswith('cell_footprint : '):
                    cell_footprint=lines[kdx].strip().split('cell_footprint : ')[1].replace(';','').strip()

                elif lines[kdx].strip().startswith('dont_use : '):
                    dont_use=lines[kdx].strip().split('dont_use : ')[1].replace(';','').strip()

                elif lines[kdx].strip().startswith('dont_touch : '):
                    dont_touch=lines[kdx].strip().split('dont_touch : ')[1].replace(';','').strip()

                elif lines[kdx].strip().startswith('clock_gating_integrated_cell : '):
                    clock_gating_integrated_cell=lines[kdx].strip().split('clock_gating_integrated_cell : ')[1].replace(';','').strip()

                elif lines[kdx].strip().startswith('cell_leakage_power : '):
                    cell_leakage_power=float(lines[kdx].strip().split('cell_leakage_power : ')[1].replace(';','').strip())

                elif kdx==0:
                    if  'cell ('+list_of_cell[idx]+') {'==lines[kdx].strip():
                        continue
                    else:
                        print(list_of_cell[idx],'break')
                        break
                
                elif kdx==len(lines)-1:
                    if '}'==lines[kdx].strip():
                        continue
                    else:
                        print(list_of_cell[idx],'break')
                        break

                else:
                    temp_lines.append(lines[kdx])

            if len(temp_lines)==0:
                with open(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/info.txt','w') as fw:
                    fw.write('area : '+str(area)+'\n')
                    fw.write('cell_leakage_power : '+str(cell_leakage_power)+'\n')
                    fw.write('cell_footprint : '+cell_footprint+'\n')
                    fw.write('dont_use : '+dont_use+'\n')
                    fw.write('dont_touch : '+dont_touch+'\n')
                    fw.write('clock_gating_integrated_cell : '+clock_gating_integrated_cell+'\n')
                fw.close()
                os.remove(temp_txt)
                os.remove(libb.split('.lib')[0]+'/'+list_of_cell[idx]+'/naive.txt')
                ##@print(idx,list_of_cell[idx])
                continue
            
            print(list_of_cell[idx],'break')
            break

    return 0




if __name__=="__main__":
    lib='../data/20221219/LIB/tcbn40lpbwp12tm1ptc_ccs.lib'
    check=str()
    if sys.argv[1]==str(0):
        parsing_lib(lib)
    else:
        if int(sys.argv[1])<10:
            if sys.argv[1]==str(1):
                check='dynamic_current'

            elif sys.argv[1]==str(2):
                check='pin'

            elif sys.argv[1]==str(3):
                check='leakage_power'

            elif sys.argv[1]==str(4):
                check='leakage_current_intrinsic_parasitic'

            elif sys.argv[1]==str(5):
                check='pg_pin'

            elif sys.argv[1]==str(6):
                check='test_cell'

            elif sys.argv[1]==str(7):
                check='statetable'

            elif sys.argv[1]==str(8):
                check='ff'

            elif sys.argv[1]==str(9):
                check='latch'

            each_file_directory_info(lib,check,sys.argv[1])
        
        else:
            if sys.argv[1]==str(10):
                checking_each_cell_left_right(lib)
            else:
                checking_cell_info(lib)
    print(sys.argv)