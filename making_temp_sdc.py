import pandas as pd





def get_sdc(file):
    with open(file,'r') as fw:
        info=fw.readlines()
    fw.close()

    temp_info=['']
    for ivalue in info:

        temp_line=ivalue.replace('\n','').strip()
        temp_info[-1]=temp_info[-1]+temp_line.split(';')[0]

        if temp_line.endswith(';'):
            temp_info.append('')


    willchange=list()
    for ivalue in temp_info:
        if '[' in ivalue:
            willchange.append(ivalue)
    

    input_gro=list()
    output_gro=list()
    tttt=int()
    for ivalue in willchange:
        large_num=int(ivalue.split('[')[1].split(':')[0])
        small_num=int(ivalue.split(']')[0].split(':')[1])
        length_num=large_num-small_num+1
        if 'input' in ivalue:
            tttt=tttt+length_num
        temp_str=ivalue.split(' ')[0]+' '
        for idx in range(length_num):
            if idx !=length_num-1:
                temp_str=temp_str+ivalue.split(' ')[2]+'['+str(idx+small_num)+'], '
            else:
                temp_str=temp_str+ivalue.split(' ')[2]+'['+str(idx+small_num)+']'
    
        if ivalue in temp_info:
            temp_info.remove(ivalue)

        #print(temp_str)
        if temp_str.split(' ')[0]=='input':
            for kvalue in temp_str.split('input ')[1].split(', '):
                input_gro.append(kvalue)

        if temp_str.split(' ')[0]=='output':
            for kvalue in temp_str.split('output ')[1].split(', '):
                output_gro.append(kvalue)
    #print(tttt)
    del temp_info[-1]

    for idx in range(len(temp_info)):
        if 'input' in temp_info[idx]:
            for kvalue in input_gro:
                temp_info[idx]=temp_info[idx]+', '+kvalue

        elif 'output' in temp_info[idx]:
            for kvalue in output_gro:
                temp_info[idx]=temp_info[idx]+', '+kvalue

    if ' clk_i,' in temp_info[0]:
        temp_info[0]=temp_info[0].replace(' clk_i, ','')
    

    data=['# Synopsys Design Constraints Format','# Copyright © 2011, Synopsys, Inc. and others. All Rights reserved.','','# clock definition','create_clock -name mclk -period 0.0 [get_ports clk_i]','','#input delays']
    input_str=temp_info[0]
    input_str=input_str.replace('input','')
    ingro=input_str.split(',')
    for idx in range(len(ingro)):
        ingro[idx]=ingro[idx].strip()
        if ',' in ingro[idx]:
            ingro[idx]=ingro[idx].replace(',','')
        data.append('set_input_delay 0.0 [get_ports {'+ingro[idx]+'}] -clock mclk')

    data.append('')
    data.append('#output delays ')

    output_str=temp_info[1]
    output_str=output_str.replace('output ','')
    outgro=output_str.split(',')
    for idx in range(len(outgro)):
        outgro[idx]=outgro[idx].strip()
        if ',' in outgro[idx]:
            outgro[idx]=outgro[idx].replace(',','')
        data.append('set_output_delay 0.0 [get_ports {'+outgro[idx]+'}] -clock mclk')
    df1=pd.DataFrame(index=data)
    df1.to_csv('../data/20221219/LIB/temp.sdc',sep='\t')
    return 0











if __name__ == "__main__":
    verilog_address='../data/20221219/LIB/temp_sdc.txt'


    ##db_address='../data/20221219/DB/TS1N40LPB128X63M4FWBA_tt1p1v25c.db'
    get_sdc(verilog_address)