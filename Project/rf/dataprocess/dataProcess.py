import numpy as np
from numpy import array
import pandas as pd
from pandas import DataFrame

# split a multivariate sequence into samples
def split_sequences(sequences, n_steps_in, n_steps_out):
	X, y = list(), list()
	for i in range(len(sequences)-1):#遍历4511次
		# find the end of this pattern
		end_ix = i + n_steps_in #0+45, 1+45, 2+45...
		out_end_ix = end_ix + n_steps_out-1 #0+45+1-1, 1+45+1-1, 2+45+1-1
		# check if we are beyond the dataset
		if out_end_ix > len(sequences)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequences[i:end_ix, :-1], sequences[out_end_ix:out_end_ix+1, -1]
		seq_x = seq_x.flatten()
		seq_y = seq_y.flatten()
		# print(seq_y.shape)
		extra = sequences[end_ix:out_end_ix+1, 2:31]
		# print(extra.shape)
		# extra[:,0:1] = 0
		# extra[:,22:25] = 0
		extra = extra.flatten()
		seq_x = np.concatenate([seq_x,extra], axis=0)
		# print(seq_x.shape)
        #seq_x = [0:0+45,:-1],[1:1+45,:-1],...
        #seq_y = [0+45:0+45+1-1+1,-1],[1+45:1+45+1-1+1,-1],...
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

df = pd.read_excel('/home/lzy/lab/Project/TaihuData/taihunew.xlsx')

in_cols = ['Z', 'Q', 'DRP(63001000)', 'DRP(63203000)', 'DRP(63204401)',
       'DRP(63204450)', 'DRP(63204600)', 'DRP(63204650)', 'DRP(63204800)',
       'DRP(63204850)', 'DRP(63205350)', 'DRP(63300800)', 'DRP(63301150)',
       'DRP(63301600)', 'DRP(63303400)', 'DRP(63303600)', 'DRP(63304400)',
       'DRP(63304800)', 'DRP(63305200)', 'DRP(63305800)', 'DRP(63307200)',
       'DRP(63307800)', 'DRP(63309200)', 'DRP(63309600)', 'DRP(63310400)',
       'DRP(63310600)', 'DRP(63320600)', 'DRP(63403200)', 'DRP(63403500)',
       'DRP(63403600)', 'DRP(63404900)', 'TGTQ', 'TDZ']
out_cols = ['Z']

# choose a number of time steps
n_steps_in = 240

for n_steps_out in range(1,73):
    print(str(n_steps_out)+'开始运行')
    j=0
    dataset_low = np.empty((df[out_cols[j]].values.shape[0],0))
    print(dataset_low.shape)
    for i in range(len(in_cols)):
        dataset_low = np.append(dataset_low, df[in_cols[i]].values.reshape(df[in_cols[i]].values.shape[0],1), axis=1)
    dataset_low = np.append(dataset_low, df[out_cols[j]].values.reshape(df[out_cols[j]].values.shape[0],1), axis=1)
    print(dataset_low.shape)
    dataset_low = pd.DataFrame(dataset_low)
    dataset_low = dataset_low.values

    X, y = split_sequences(dataset_low, n_steps_in, n_steps_out)
    print(X.shape)
    print(y.shape)
    int(len(X[1]))
    y = pd.DataFrame(y).rename(columns={0:int(len(X[1]))})

    TM = df['TM'].iloc[n_steps_in+n_steps_out-1:].reset_index(drop=True)

    Xy = pd.concat([TM,pd.DataFrame(X),pd.DataFrame(y)],axis=1)
    Xy.shape

    start = Xy.iloc[:,0].iloc[0]
    end = Xy.iloc[:,0].iloc[-1]
    t_index = pd.date_range(start=start, end=end, freq='H')
    full_time = pd.DataFrame(t_index, columns=['TM'])

    five = full_time['TM'][full_time['TM'].dt.month == 5]
    six = full_time['TM'][full_time['TM'].dt.month == 6]
    seven = full_time['TM'][full_time['TM'].dt.month == 7]
    eight = full_time['TM'][full_time['TM'].dt.month == 8]
    nine = full_time['TM'][full_time['TM'].dt.month == 9]
    flow_time = pd.concat([five,six,seven,eight,nine]).reset_index(drop=True,name='TM')

    flow_time = pd.DataFrame(flow_time).sort_values('TM')
    flow_time

    complete = Xy.merge(flow_time,how='right',sort=True)
    complete.shape

    filename= '/home/lzy/lab_env/Project/平望日频时频/处理/PingwangHourly'+str(n_steps_out)+'.csv'
    complete.to_csv(filename)
    print(str(n_steps_out)+'运行完毕')


