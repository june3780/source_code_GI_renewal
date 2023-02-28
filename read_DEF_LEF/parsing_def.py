import json
import sys





def get_def_components(defdef,from_02):

    temp_def=defdef.split('/')
    directory_of_def=str()
    for idx in range(len(temp_def)):
        if idx==len(temp_def)-1:
            continue
        directory_of_def=directory_of_def+temp_def[idx]+'/'

    def_name=defdef.split('/')[-1].split('.def')[0]


    with open(defdef,'r') as fw:
        lines=fw.readlines()
    fw.close()


    components_idx=dict()
    pin_idx=dict()
    net_idx=dict()

    for idx in range(len(lines)):
        if lines[idx].strip().startswith('COMPONENTS'):
            components_idx.update({'start_idx':idx})

        elif lines[idx].strip().startswith('END') and lines[idx].split('END')[1].strip().startswith('COMPONENTS'):
            components_idx.update({'end_idx':idx})

        elif lines[idx].strip().startswith('PINS'):
            pin_idx.update({'start_idx':idx})

        elif lines[idx].strip().startswith('END') and lines[idx].split('END')[1].strip().startswith('PINS'):
            pin_idx.update({'end_idx':idx})

        elif lines[idx].strip().startswith('NETS'):
            net_idx.update({'start_idx':idx})

        elif lines[idx].strip().startswith('END') and lines[idx].split('END')[1].strip().startswith('NETS'):
            net_idx.update({'end_idx':idx})
            
    
    components_lines=get_lines_by_idx(components_idx,lines)
    
    components_list=list()
    for ivalue in components_lines:
        if ivalue.strip().endswith(';'):
            if ivalue.strip().startswith('COMPONENTS'):
                continue
            components_list.append(ivalue.split('-')[1].strip().split(' ')[0])


    pins_list=list()
    pins_lines=get_lines_by_idx(pin_idx,lines)
    for ivalue in pins_lines:
        if ivalue.strip().endswith(';'):
            if ivalue.strip().startswith('PINS'):
                continue
            pins_list.append(ivalue.split('-')[1].strip().split(' ')[0])


    nets_lines=get_lines_by_idx(net_idx,lines)
    net_dict=dict()
    for ivalue in nets_lines:
        if ivalue.strip().endswith(';'):
            if ivalue.strip().startswith('NETS'):
                continue
            net_name=ivalue.split('-')[1].strip().split(' ')[0]
            net_dict.update({net_name:list()})
            temp_net_compo=ivalue.split('(')
            for kvalue in temp_net_compo:
                if ')' in kvalue:
                    net_dict[net_name].append(kvalue.split(')')[0].strip())

    with open(from_02,'r') as fw:
        origin_net=json.load(fw)
    fw.close()
    #print(json.dumps(origin_net,indent=4))


    not_in_parsing_verilog=list()
    for ivalue in net_dict:
        if ivalue not in origin_net:
            not_in_parsing_verilog.append(ivalue)
        else:
            for kvalue in net_dict[ivalue]:
                if kvalue not in origin_net[ivalue]:
                    print(kvalue)
    
    print('not_in_parsing_verilog_net :',not_in_parsing_verilog)
    return 0






def get_lines_by_idx(index_dict,line):
    temp_lines=['']
    for idx in range(len(line)):
        if idx<index_dict['start_idx'] or idx>index_dict['end_idx']:
            continue
        temp_lines[-1]=temp_lines[-1]+' '+line[idx].replace('\n','')
        if line[idx].replace('\n','').strip().endswith(';'):
            temp_lines.append('')
        

    return temp_lines









if __name__=="__main__":
    def_address='../../data/easy/'
    def_address=def_address+'floorplan.def'
    
    parsing_from_verilog='../../temp_data/verilog/easy/nets_from_02.json'
    checking_components_and_pin='../../temp_data/verilog/easy/checking_id_components.json'
    if sys.argv[1]=='0':
        get_def_components(def_address,parsing_from_verilog,checking_components_and_pin)