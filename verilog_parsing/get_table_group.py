import pandas as pd
import json
import os
import copy

def get_wvalue_group(leflef):
    #### 해당 verilog 파일의 파일명: where_the_lef+'.v'
    where_the_lef=leflef.split('.lef')[0]
    #### id와 net정보를 저장할 새 디렉토리 : upper_directory+'/'+the_lef
    the_lef=where_the_lef.split('/')[-1]
    upper_directory=leflef.split('/'+the_lef+'.lef')[0]
    #### 해당 lef 파일의 위치에 하위 디렉토리가 없을 경우 생성
    if the_lef not in os.listdir(upper_directory):
        os.mkdir(upper_directory+'/'+the_lef)

    W_df=pd.read_csv(upper_directory+'/'+the_lef+'/'+the_lef+'W_df.csv',sep='\t',index_col=0)

    temp_dict=dict()
    temp_group_dict=dict()
    macro_connected_weight=list()
    for idx in range(len(W_df.columns)):
        temp_dict.update({str(list(W_df.columns)[idx]):dict()})
        
        for kdx in range(len(W_df.columns)):
            temp_dict[str(list(W_df.columns)[idx])].update({str(list(W_df.columns)[kdx]):list(W_df[list(W_df.columns)[idx]])[kdx]})

    indexing_list=list()
    for idx,ivalue in enumerate(temp_dict):
        indexing_list.append(str(idx+1)+' '+ivalue)
        #print(str(idx)+' '+ivalue)
        for kdx, kvalue in enumerate(temp_dict):
            if temp_dict[ivalue][kvalue]<=float(1):
                continue

            if idx>=kdx:
                continue
            
            macro_connected_weight.append(str(idx+1)+' '+str(kdx+1)+' '+str(temp_dict[ivalue][kvalue]))
            #print(str(idx)+' '+str(kdx)+' '+str(temp_dict[ivalue][kvalue]))
    
    max_number=int()
    for ivalue in macro_connected_weight:
        num1=ivalue.split(' ')[0]
        num2=ivalue.split(' ')[1]
        if max_number<int(num1):
            max_number=int(num1)
        if max_number<int(num2):
            max_number=int(num2)
    macro_connected_weight.append(str(max_number)+' '+str(max_number)+' '+str(0))

    for idx in range(len(macro_connected_weight)):
        if idx==0:
            with open(upper_directory+'/'+the_lef+'/'+the_lef+'_W_value_about_macro.txt','w') as fw:
                fw.write(macro_connected_weight[idx]+'\n')
            fw.close()
        else:
            with open(upper_directory+'/'+the_lef+'/'+the_lef+'_W_value_about_macro.txt','a') as fw:
                fw.write(macro_connected_weight[idx]+'\n')
            fw.close()


    if the_lef.startswith('easy') or the_lef.startswith('medium'):
        print(the_lef,'tpgmlwns1!')

    else:
        for idx in range(len(indexing_list)):
            if idx==0:
                with open(upper_directory+'/'+the_lef+'/'+the_lef+'_index_number_written_by_jun.txt','w') as fw:
                    fw.write(macro_connected_weight[idx]+'\n')
                fw.close()
            else:
                with open(upper_directory+'/'+the_lef+'/'+the_lef+'_index_number_written_by_jun.txt','a') as fw:
                    fw.write(macro_connected_weight[idx]+'\n')
                fw.close()

        #for kvalue in temp_dict[ivalue]:









    '''group_dict=dict()
    tt=int()
    for ivalue in temp_group_dict:
        if len(temp_group_dict[ivalue])==1:
            continue

        one_str=str()
        for kvalue in temp_group_dict[ivalue]:
            for rvalue in group_dict:
                if kvalue in group_dict[rvalue]:
                    group_dict[rvalue]=list(set(group_dict[rvalue])|set(temp_group_dict[ivalue]))
                    one_str='one'
                    break
        
        if one_str!='one':
            group_dict.update({'group_'+str(tt):copy.deepcopy(temp_group_dict[ivalue])})
            tt=tt+1



    while_str=''
    while while_str=='continue':
        temple_dict=dict()
        for idx,ivalue in enumerate(temple_dict):
            for kdx,kvalue in enumerate(temple_dict):
                if idx>=kdx:
                    continue
                
                if len(set(group_dict[ivalue])&set(group_dict[kvalue]))>0:
                    while_str='continue'
                    temple_dict.update({ivalue:list(set(group_dict[ivalue])|set(group_dict[kvalue]))})
                
                else:
                    temple_dict.update({ivalue:group_dict[ivalue]})
        
        will_del=list()
        for idx,ivalue in enumerate(temple_dict):
            for kdx,kvalue in enumerate(temple_dict):
                if idx>=kdx:
                    continue

                if set(temple_dict[ivalue])==set(temple_dict[kvalue]):
                    will_del.append(ivalue)
        will_del=list(set(will_del))

        for ivalue in will_del:
            del temple_dict[ivalue]
        
        group_dict=copy.deepcopy(temple_dict)

    for ivalue in group_dict:
        temp_list=list()
        for kvalue in group_dict[ivalue]:
            temp_list.append(int(kvalue))
        
        temp_list.sort()
        group_dict[ivalue]=list()
        for kvalue in temp_list:
            group_dict[ivalue].append(str(kvalue))
    print(group_dict)'''
        #print(ivalue, group_dict[ivalue])


    '''temp_checking_dict=dict()
    #while temp_checking_dict!=temp_group_dict:
    count=copy.deepcopy(len(temp_group_dict))
    for rdx in range(count):
        new_dict=dict()
        temp_checking_dict=copy.deepcopy(temp_group_dict)
        for ivalue in temp_group_dict:
            if len(temp_group_dict[ivalue])==1:
                continue
            if ivalue not in temp_group_dict[ivalue]:
                continue
            intersection_set=set(copy.deepcopy(temp_group_dict[ivalue]))
            intersection_set=intersection_set&set(list(temp_group_dict.keys()))
            break_str=str()
            for kvalue in temp_group_dict[ivalue]:
                if kvalue in temp_group_dict:
                    intersection_set=set(temp_group_dict[ivalue])&set(temp_group_dict[kvalue])
                    if ivalue not in temp_group_dict[kvalue]:
                        break_str='break'
                        break
                else:
                    intersection_set.discard(kvalue)


            if len(intersection_set)==1:
                continue
            for kvalue in intersection_set:
                if kvalue not in temp_group_dict:
                    break_str='break'
                    break
            if break_str=='break':
                continue

            intersection_set=list(intersection_set)
            intersection_set.sort()
            new_dict.update({ivalue:intersection_set})
        temp_group_dict=copy.deepcopy(new_dict)
    

    for ivalue in temp_group_dict:
        break_str=str()
        #print(temp_group_dict[ivalue])
        for kvalue in temp_group_dict[ivalue]:
            if temp_group_dict[ivalue]!=temp_group_dict[kvalue]:
                break_str='break'
                #print(ivalue,temp_group_dict[ivalue])
        #print(ivalue, temp_group_dict[ivalue])
        if break_str=='break':
            print(ivalue,temp_group_dict[ivalue])'''



    return 0


if __name__=="__main__":
    #superblue=['superblue16_ISPD','superblue1','superblue3','superblue4','superblue5','superblue7','superblue10','superblue16','superblue18','superblue11_ISPD','superblue12_ISPD','medium_e1','medium_e2','medium','easy']
    #superblue=['superblue11_ISPD']
    #superblue=['medium_e1','medium_e2','medium','easy']
    #superblue=['easy']
    #superblue=['medium_e2']
    #superblue=['easy']
    #superblue=['superblue3']
    superblue=[ 'medium' ]
    ivalue=''
    #ivalue='medium'
    #ivalue='easy'
    #ivalue='toy'
    for ivalue in superblue:
        checking_def='../../data/'
        checking_lef='../../data/'
        checking_def=checking_def+ivalue+'/'+ivalue+'.def'
        checking_lef=checking_lef+ivalue+'/'+ivalue+'.lef'



        print(ivalue)
        get_wvalue_group(checking_lef)
        print()
        #break
        

