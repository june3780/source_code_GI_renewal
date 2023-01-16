import json



def parsing_lib(lib):
    with open(lib,'r') as fw:
        lines=fw.readlines()
    fw.close()
    cell_list=[[]]
    
    for ivalue in lines:
        
        if ivalue.replace('\n','').strip().startswith('cell ('):
            cell_list.append([])
        elif 'cell (' in ivalue:
            print(ivalue)
        cell_list[-1].append(ivalue.replace('\n','').strip())
        
    print(len(cell_list))



    return 0



if __name__=="__main__":
    lib='../data/20221219/LIB/tcbn40lpbwp12tm1plvttc_ccs.lib'
    parsing_lib(lib)