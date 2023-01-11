import json



def get_all_process(vfile):
    f=open(vfile,'r')
    all=f.readlines()
    f.close()
    
    module_list=list()
    for idx in range(len(all)):
        if all[idx].strip().startswith('module'):
            module_list.append(all[idx])
        else:
            if len(module_list)!=0:
                module_list[-1]=module_list[-1]+all[idx]
            else:
                continue
    
    print(len(module_list))
    print()
    module_dict=dict()
    '''for ivalue in module_list:
        module_dict.update({ivalue.split('module ')[1].split(' ')[0]:})'''
    for idx in range(len(module_list)):
        ivalue=module_list[idx]
        module_dict.update({ivalue.split('module ')[1].split(' ')[0]:ivalue.split('module ')[1].split(ivalue.split('module ')[1].split(' ')[0])[1].split('endmodule')[0]})

    for kdx,kvalue in enumerate(module_dict):
        print(kdx)
        temp_one_list=['']
        for jdx in range(len(module_dict[kvalue].split('\n'))):
            jvalue=module_dict[kvalue].split('\n')[jdx].strip()
            temp_one_list[-1]=temp_one_list[-1]+jvalue
            if jvalue.endswith(';'):
                temp_one_list.append('')
            #print(jdx,module_dict[kvalue].split('\n')[jdx])
            #if module_dict[kvalue].split('\n')[jdx]=='':
            #    print(jdx)
            #print(module_dict[kvalue].split('\n')[jdx])
        del temp_one_list[-1]
        for jdx in range(len(temp_one_list)):
            if jdx ==0:
                continue
            if temp_one_list[jdx].split(' ')[0]=='input' and '[' in temp_one_list[jdx]:
                temptemp=temp_one_list[jdx]
                if len(temptemp.split(' '))!=3:
                    print(temp_one_list[jdx])
                    
            elif temp_one_list[jdx].split(' ')[0]=='output':
                continue
                print(temp_one_list[jdx])
            elif temp_one_list[jdx].split(' ')[0]=='wire':
                continue
                print(temp_one_list[jdx])
                continue
            else:
                continue
        print()
        #print(jdx)

    return 0


def get_db(dbfile):
    return 0


if __name__ == "__main__":
    verilog_address='../data/20221219/NETLIST/CORTEXA5INTEGRATIONCS.mapped_incr.v'
    verilog_address

    db_address='../data/20221219/DB/TS1N40LPB128X63M4FWBA_tt1p1v25c.db'
    get_all_process(verilog_address)
    get_db(db_address)