import json


def get_compare():
    with open('checking_net_components.json','r') as fw:
    #with open('checking_net_components_no_constant_group.json','r') as fw:
        net_all=json.load(fw)
    fw.close()
    with open('components_list_with_ports.json','r') as fw:
        should_all=json.load(fw)
    fw.close()

    should_all.sort()
    net_all.sort()



    print(len(should_all))
    print(len(net_all))

    for idx in range(len(should_all)):
        if should_all[idx]!=net_all[idx]:
            print(idx, should_all[idx],net_all[idx])
            print()

    '''for idx in range(len(net_all)):
        should_all.remove(net_all[idx])
        if idx==250000:
            print(250000)
        elif idx==500000:
            print(500000)
        elif idx==750000:
            print(750000)
        elif idx==1000000:
            print(1000000)
        elif idx==1250000:
            print(1250000)
        elif idx==1500000:
            print(1500000)
        elif idx==1750000:
            print(1750000)
        elif idx==2000000:
            print(2000000)
        elif idx==2250000:
            print(2250000)
    print()
    
    print(len(should_all))
    with open('should_be_there_constant_case_not_included.json','w') as fw:
        json.dump(should_all,fw,indent=4)
    fw.close()'''

    return 0




if __name__=="__main__":
    get_compare()