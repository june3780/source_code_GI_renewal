import os
import time





def be_parsing():
    lib_list=['example1_slow.lib', 'example1_typ.lib','example1_fast.lib',
    'superblue1_Late.lib', 'superblue1_Early.lib', 'superblue3_Late.lib', 'superblue3_Early.lib',
    'superblue4_Late.lib', 'superblue4_Early.lib', 'superblue5_Late.lib', 'superblue5_Early.lib',
    'superblue7_Late.lib', 'superblue7_Early.lib', 'superblue10_Late.lib', 'superblue10_Early.lib',
    'superblue16_Late.lib', 'superblue16_Early.lib', 'superblue18_Late.lib', 'superblue18_Early.lib', 
    'tcbn40lpbwp12tm1ptc_ccs.lib', 'tcbn40lpbwp12tm1plvttc_ccs.lib',
    'TS1N40LPB2048X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB4096X32M8MWBA_tt1p1v25c.lib',
    'TS1N40LPB1024X128M4FWBA_tt1p1v25c.lib', 'TS1N40LPB2048X36M4FWBA_tt1p1v25c.lib',
    'TS1N40LPB1024X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB256X22M4FWBA_tt1p1v25c.lib',
    'TS1N40LPB512X23M4FWBA_tt1p1v25c.lib', 'TS1N40LPB256X12M4FWBA_tt1p1v25c.lib',
    'TS1N40LPB512X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB128X63M4FWBA_tt1p1v25c.lib',
    'TS1N40LPB256X23M4FWBA_tt1p1v25c.lib']


    '''lib_list=['TS1N40LPB2048X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB4096X32M8MWBA_tt1p1v25c.lib',\
    'TS1N40LPB1024X128M4FWBA_tt1p1v25c.lib', 'TS1N40LPB2048X36M4FWBA_tt1p1v25c.lib',\
    'TS1N40LPB1024X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB256X22M4FWBA_tt1p1v25c.lib',\
    'TS1N40LPB512X23M4FWBA_tt1p1v25c.lib', 'TS1N40LPB256X12M4FWBA_tt1p1v25c.lib',\
    'TS1N40LPB512X32M4FWBA_tt1p1v25c.lib', 'TS1N40LPB128X63M4FWBA_tt1p1v25c.lib',\
    'TS1N40LPB256X23M4FWBA_tt1p1v25c.lib']'''


    for idx in range(len(lib_list)):
        #print('checking=\''+lib_list[idx]+'\'')
        '''for kdx in range(9):
            start=time.time()
            print(str(kdx)+' '+lib_list[idx])
            os.system('python3 lib_parsing_final.py '+str(kdx)+' '+lib_list[idx])
            print('end',time.time()-start)
            print()'''



    for idx in range(len(lib_list)):
        #print('checking=\''+lib_list[idx]+'\'')
            start=time.time()
            print(str(6)+' '+lib_list[idx])
            os.system('python3 lib_parsing_final.py '+str(6)+' '+lib_list[idx])
            print('end',time.time()-start)
            #print()
            

    return 0

if __name__=="__main__":

    be_parsing()
