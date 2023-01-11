








def get_cell_footprint():
    lib_f='../data/20221219/LIB/tcbn40lpbwp12tm1plvttc_ccs.lib'

    with open(lib_f,'r') as fw:
        module_str=fw.readlines()
    fw.close()

    temp_dict=dict()
    temp_list=list()
    function_list=list()
    for idx in range(len(module_str)):
        if module_str[idx].replace('\n','').strip().startswith('* Design : '):
            temp_dict.update({module_str[idx].replace('\n','').strip():idx})
        if module_str[idx].replace('\n','').strip().startswith('cell_footprint :'):
            temp_list.append({module_str[idx].replace('\n','').strip():idx})
        if module_str[idx].replace('\n','').strip().startswith('function :'):
            function_list.append({module_str[idx].replace('\n','').strip():idx})
    

    print(len(temp_dict))
    print(len(temp_list))
    print(len(function_list))
    return 0


if __name__=="__main__":
    get_cell_footprint()