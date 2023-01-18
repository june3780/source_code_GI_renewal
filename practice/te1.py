import json


def test():
    june=dict()
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_ram_clk_o_assign_clk_o':'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/ram_clk'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_clk_o_assign_ram_clk_o':'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/clk'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_clk_ug_o_assign_CLKIN':'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/clk_ug'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_ic_clk_o_assign_PERIPHCLK':'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/ic_clk'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_CLKIN_assign_clk_ug_o':'clk_i'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_PERIPHCLK_assign_ic_clk_o':'periphclk_i'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_june1115_assign_PERIPHCLK':'aaa'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_june3780_assign_ram_clk_o':'aaa'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_june_assign_CLKIN':'aaa'})
    june.update({'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/assign_galaxy_assign_iphone':'bbb'})








































    checking_list=dict()
    for ivalue in june:
        temp_assign=ivalue.split('/')[-1]
        first_assign=temp_assign.split('_assign_')[0].split('assign_')[1]
        second_assign=temp_assign.split('_assign_')[1]
        if ivalue.split(ivalue.split('/')[-1])[0] not in checking_list:
            checking_list.update({ivalue.split(ivalue.split('/')[-1])[0]:dict({'wires':list(),'groups':list()})})
        if first_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(first_assign)
        if second_assign not in checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires']:
            checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['wires'].append(second_assign)
        checking_list[ivalue.split(ivalue.split('/')[-1])[0]]['groups'].append([first_assign,second_assign])



    sum_assign=dict()
    for ivalue in checking_list:
        previous_wire_counts=int()
        will_exterminate_group=list()
        will_add_wire_groups=list()
        will_delete_group=list()
        while len(checking_list[ivalue]['wires'])!=0:
            che='che'
            if len(will_add_wire_groups)!=0:
                sum_assign[ivalue].extend([will_add_wire_groups])

            for kvalue in will_exterminate_group:
                if kvalue in checking_list[ivalue]['wires']:
                    checking_list[ivalue]['wires'].remove(kvalue)
            
            for kvalue in will_delete_group:
                if kvalue in checking_list[ivalue]['groups']:
                    checking_list[ivalue]['groups'].remove(kvalue)
            

            if ivalue not in sum_assign:
                sum_assign.update({ivalue:list()})
            will_exterminate_group=list()
            will_add_wire_groups=list()
            for kdx in range(len(checking_list[ivalue]['groups'])):
                if len(sum_assign[ivalue])==0:
                    sum_assign[ivalue].append(checking_list[ivalue]['groups'][kdx])
                    will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                    will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                    will_delete_group.append(checking_list[ivalue]['groups'][kdx])

                else:
                    
                    for tdx in range(len(sum_assign[ivalue])):
                        if checking_list[ivalue]['groups'][kdx][0] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][1] not in sum_assign[ivalue][tdx]:
                            che='ehc'
                            sum_assign[ivalue][tdx].append(checking_list[ivalue]['groups'][kdx][1])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        elif checking_list[ivalue]['groups'][kdx][1] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][0] not in sum_assign[ivalue][tdx]:
                            che='ehc'
                            sum_assign[ivalue][tdx].append(checking_list[ivalue]['groups'][kdx][0])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        elif checking_list[ivalue]['groups'][kdx][0] in sum_assign[ivalue][tdx] and checking_list[ivalue]['groups'][kdx][1] in sum_assign[ivalue][tdx]:
                            che='ehc'
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                            will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                            will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                        else:
                            if len(checking_list[ivalue]['wires'])!=previous_wire_counts:
                                che='ehc'
                                continue
                    if che=='che':
                                will_add_wire_groups=[checking_list[ivalue]['groups'][kdx][0],checking_list[ivalue]['groups'][kdx][1]]
                                will_delete_group.append(checking_list[ivalue]['groups'][kdx])
                                will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][0])
                                will_exterminate_group.append(checking_list[ivalue]['groups'][kdx][1])
                                break

            previous_wire_counts=len(checking_list[ivalue]['wires'])


    print(sum_assign)
    print()


    open_temp=dict()
    with open('temp_assign_groups.json','r') as fw:
        open_temp=json.load(fw)
    fw.close()
    print('##############################################################################')
    for ivalue in open_temp:
        for kvalue in open_temp[ivalue]:
            print(ivalue,len(open_temp[ivalue][kvalue]))
    return 0

if __name__=="__main__":
    test()
