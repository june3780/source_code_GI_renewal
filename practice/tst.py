import copy



def get_test():
    checking_list={'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/': \
        {'wires': ['ram_clk_o', 'clk_o', 'clk_ug_o', 'CLKIN', 'ic_clk_o', 'PERIPHCLK'], \
        'groups': [['ram_clk_o', 'clk_o'], ['clk_o', 'ram_clk_o'], ['clk_ug_o', 'CLKIN'], ['ic_clk_o', 'PERIPHCLK'], ['CLKIN', 'clk_ug_o'], ['PERIPHCLK', 'ic_clk_o']]}}
    sum_assign=dict()
    for ivalue in checking_list:
        if ivalue not in sum_assign:
            sum_assign.update({ivalue:list()})

        set_list=list()
        for idx in range(len(checking_list[ivalue]['groups'])):
            set_list.append(set(checking_list[ivalue]['groups'][idx]))
        
        while True:
            new_set_list=list()
            checking_break=str()
            for idx in range(len(set_list)):
                for kdx in range(len(set_list)):
                    if kdx<=idx:
                        continue
                    if len(set_list[idx]&set_list[kdx])!=0:
                        checking_break='continue'
                        new_set_list.append(set_list[idx]|set_list[kdx])
            
            if checking_break=='':
                break
            set_list=copy.deepcopy(new_set_list)

        print(set_list,'tpgmlwns!@#!@')
    result={'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/': [['clk_o', 'ram_clk_o'], ['clk_ug_o', 'CLKIN'], ['PERIPHCLK', 'ic_clk_o']]}
    result={'u_cpu/cortexa5mp_wrapper_u_cortexa5mp/u_ca5scu/u_ca5scu_noram/': [['ram_clk_o', 'clk_o'], ['clk_ug_o', 'CLKIN'], ['ic_clk_o', 'PERIPHCLK']]}
    return 0


if __name__=="__main__":
    get_test()