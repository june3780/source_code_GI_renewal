


def get_cal():


    capa=float(0.05472)
    refer=float()
    time_list=[0.1407, 0.1628, 0.1917, 0.2789, 0.3265, 0.3668, 0.3838, 0.3976, 0.4374, 0.4624, 0.4761]
    value_list=[-0.0101703, -0.0249316, -0.0615269, -0.226528, -0.301911, -0.324454, -0.314276, -0.283473, -0.115110, -0.0466234, -0.140532]
    all_value_all=float()
    if value_list[0]>0:
        all_value_all=value_list[0]*(1/2)*time_list[0]
    else:
        all_value_all=value_list[0]*(1/2)*time_list[0]*(-1)
    for idx in range(len(time_list)-1):
        tempflow=float()
        if value_list[idx]>0 and value_list[idx+1]>0:
            if value_list[idx]<value_list[idx+1]:
                tempflow=((value_list[idx+1]-value_list[idx])*(time_list[idx+1]-time_list[idx])*(1/2))+(value_list[idx]*(time_list[idx+1]-time_list[idx]))
            else:
                tempflow=((value_list[idx]-value_list[idx+1])*(time_list[idx+1]-time_list[idx])*(1/2))+(value_list[idx+1]*(time_list[idx+1]-time_list[idx]))

        elif value_list[idx]<0 and value_list[idx+1]<0:
            tempidx=value_list[idx]*(-1)
            tempidxplus=value_list[idx+1]*(-1)
            if tempidx<tempidxplus:
                tempflow=((tempidxplus-tempidx)*(time_list[idx+1]-time_list[idx])*(1/2))+(tempidx*(time_list[idx+1]-time_list[idx]))
            else:
                tempflow=((tempidx-tempidxplus)*(time_list[idx+1]-time_list[idx])*(1/2))+(tempidxplus*(time_list[idx+1]-time_list[idx]))
        all_value_all=all_value_all+tempflow
    all_value_all=all_value_all/capa
    print(all_value_all)


if __name__ == "__main__":
    get_cal()