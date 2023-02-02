import json
import sys




def counting_nets(nets):
    print(len(nets))
    max_compo=int()
    for ivalue in nets:
        if max_compo<len(nets[ivalue]):
            max_compo=len(nets[ivalue])
    
    print(max_compo)
    for ivalue in nets:
        if len(nets[ivalue])==max_compo:
            print(ivalue)
    print('tpgmlwns!@!@!@\n\n\n')
    for ivalue in nets:
        if len(nets[ivalue])>1000:
            print(ivalue)

    return 0

if __name__=="__main__":


    difficulty=sys.argv[1]
    with open('../../data/'+difficulty+'/'+'nets_from_june.json','r') as fw:
        mmm=json.load(fw)
    fw.close()
    
    counting_nets(mmm)