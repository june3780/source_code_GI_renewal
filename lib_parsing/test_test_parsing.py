import json













def get_remark(address):
    with open(address,'r') as fw:
        lines=fw.readlines()
    fw.close()


    new_lines=['']
    for idx in range(len(lines)):
        print(lines[idx].replace('\n',''))

        new_lines[-1]=new_lines[-1]+'\n'+lines[idx].replace('\n','')
        if '*/' in lines[idx]:
            new_lines.append('')

    for idx in range(len(new_lines)):
        if '*/' in new_lines[idx]:
            new_lines[idx]=new_lines[idx].split('/*')[0]+new_lines[idx].split('*/')[1]
        if new_lines[idx].strip()=='':
            continue
        #print(new_lines[idx])



















    return 0

if __name__=="__main__":
    temp='test_parsing.txt'
    get_remark(temp)