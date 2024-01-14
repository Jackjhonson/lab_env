import pandas as pd
import numpy as np

def get_csv():
    # dx = pd.read_csv('/home/zcx/python/project/data/train_data (one data)/20221021X_value_pingwang.csv')
    # dy = pd.read_csv('/home/zcx/python/project/data/train_data (one data)/20221021y_value_pingwang.csv')

    # arr_x = np.array(dx)
    # lx = arr_x.tolist()
    # arr_y = np.array(dy)
    # ly = arr_y.tolist()

    # all_time = find_time("2012-01-01 00:00","2022-09-28 16:00")
    # new_X = []
    # sum_i = len(ly)
    # i = 0
    # while i < sum_i:
    #     tempx = lx[i][:]
    #     del tempx[0]
    #     tempy = ly[i][1]
    #     tempx.insert(0,tempy)
    #     tempx.insert(0,all_time[i])
    #     new_X.append(tempx)
    #     i += 1
    
    # head = get_csv_head()
    # df = pd.DataFrame(data=new_X,columns=head)
    # df.to_csv('/home/zcx/python/project/data/train_data (one data)/pingwang_training.csv')

    all_time = find_time("2012-01-01 00:00","2022-09-28 16:00")
    print(len(all_time))

def get_csv_head():
    head = ['T(t0)','Y(t10_Z)']

    rain_station = ['63001000','63203000','63204401','63204450','63204600','63204650','63204800','63204850','63205350','63300800','63301150','63301600','63303400','63303600','63304400','63304800','63305200','63305800','63307200','63307800','63309200','63309600','63310400','63310600','63320600','63403200','63403500','63403600','63404900']
    else_head = ['太浦闸_UPZ','太浦闸_DWZ','太浦闸_TGTQ','米市渡潮位_TDZ']
    rs_dyp = []
    for j in rain_station:
        temp = j+'_DYP'
        rs_dyp.append(temp)
    rs_dyp_temp = rs_dyp[:]
    rs_dyp.extend(else_head)
    day_head = ['Z','Q']
    day_head.extend(rs_dyp)
    day_step = ['t0','t1','t2','t3','t4','t5','t6','t7','t8','t9','t10']
    rain_head = []
    for i in day_step:
        if i == 't10':
            for j in rs_dyp_temp:
                temp = i+'_'+j
                rain_head.append(temp)
        else:
            for j in day_head:
                temp = i+'_'+j
                rain_head.append(temp)
    head.extend(rain_head)
    return head

def find_time(start_time, end_time):
    s_year, s_month, s_day, s_hour, s_minute = ana_time(start_time)
    e_year, e_month, e_day, e_hour, e_minute = ana_time(end_time)
    month31 = [1,3,5,7,8,10,12]
    month30 = [4,6,9,11]
    
    all_time = []
    while not (s_year==e_year and s_month==e_month and s_day==e_day and s_hour==e_hour and s_minute==e_minute):
        if s_hour == 8:
            merge_time_temp = merge_time(s_year, s_month, s_day, s_hour, s_minute)
            all_time.append(merge_time_temp)
        s_hour += 1
        # day进位
        if s_hour == 24:
            s_day += 1
            s_hour = 0
        # month进位
        if s_month in month30 and s_day == 31:
            s_day = 1
            s_month += 1
        elif s_month in month31 and s_day == 32:
            s_day = 1
            s_month += 1
        elif ((s_year%4==0 and s_year%100!=0) or (s_year%400==0)) and s_month == 2 and s_day == 30:
            s_day = 1
            s_month += 1
        elif (not ((s_year%4==0 and s_year%100!=0) or (s_year%400==0))) and s_month == 2 and s_day == 29:
            s_day = 1
            s_month += 1
        # year进位
        if s_month == 13:
            s_year += 1
            s_month = 1
    if e_hour == 8:
        merge_time_temp = merge_time(e_year, e_month, e_day, e_hour, e_minute)
        all_time.append(merge_time_temp)
    return all_time

def ana_time(time):
    dt = time.split(" ")
    d = dt[0].split("-")
    t = dt[1].split(":")
    year = int(d[0])
    month = int(d[1])
    day = int(d[2])
    hour = int(t[0])
    minute = int(t[1])
    return year, month, day, hour, minute

def merge_time(year, month, day, hour, minute):
    year = str(year)
    month = str(month)
    day = str(day)
    hour = str(hour)
    minute = str(minute)
    if len(month) == 1:
        month = "0"+month
    if len(day) == 1:
        day = "0"+day
    if len(hour) == 1:
        hour = "0"+hour
    if len(minute) == 1:
        minute = "0"+minute
    return year+"-"+month+"-"+day+" "+hour+":"+minute

if __name__ == "__main__":
    # get_csv_head()
    get_csv()