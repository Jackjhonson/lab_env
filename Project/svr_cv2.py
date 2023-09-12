from math import sqrt
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
import numpy as np
import pandas as pd
import joblib
import random
import json
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import argparse

def get_scale_h(datapath):
    d = pd.read_csv(datapath)
    n_row = d.shape[0]
    n_col = d.shape[1]
    x = []
    y = []
    train_num = 0
    for i in range(n_row):
        t_temp = str(d.iloc[i,1])[0:4]
        if int(t_temp) < 2020:
            train_num += 1
        x_temp = []
        for j in range(3,n_col):
            x_temp.append(float(d.iloc[i,j]))
        x.append(x_temp)
        y.append(float(d.iloc[i,2]))
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs[0:train_num], xs[train_num:], y[0:train_num], y[train_num:]

def get_scale_h2(datapath):
    d = pd.read_csv(datapath)
    n_row = d.shape[0]
    n_col = d.shape[1]
    train_num = 0
    for i in range(n_row):
        t_temp = str(d.iloc[i,1])[0:4]
        if int(t_temp) < 2020:
            train_num += 1
        else:
            break
    x = d.iloc[:,3:]
    y = d.iloc[:,2]
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs[0:train_num], xs[train_num:], y[0:train_num], y[train_num:]

def train_cv(vector, label, p_C, p_gamma, cv_folder, score_dict):
    # 划分数据集
    all_index = [i for i in range(len(label))]
    test_sum = (int) (len(all_index)/cv_folder)
    data_index = []
    for i in range(cv_folder):
        if i == cv_folder-1:
            data_index.append(all_index)
        else:
            temp = random.sample(all_index,test_sum)
            data_index.append(temp)
            all_index = remove_from_list(all_index,temp)
    all_score = []
    # 训练，测试模型
    for i in range(cv_folder):
        one_test_vector = []
        one_test_label = []
        one_train_vector = []
        one_train_label = []
        for j in range(len(label)):
            if j in data_index[i]:
                one_test_vector.append(vector[j])
                one_test_label.append(label[j])
            else:
                one_train_vector.append(vector[j])
                one_train_label.append(label[j])
        clf = svm.SVR(C=p_C, gamma=p_gamma, kernel='rbf')
        clf.fit(one_train_vector,one_train_label)
        one_score = clf.score(one_test_vector,one_test_label)
        all_score.append(one_score)
    # 计算平均值
    average_score = sum(all_score) / len(all_score)
    score_dict[(p_C,p_gamma)] = average_score

def remove_from_list(l1, l2):
    all_index = []
    for i in l1:
        if i not in l2:
            all_index.append(i)
    return all_index

def get_best_para(train_x, train_y, parametersFilePath):
    # 候选参数设置
    C_para = [2 ** 3, 2 ** 5, 2 ** 7, 2 ** 9]
    gamma_para = [2 ** -7, 2 ** -9, 2 ** -11]
    cv_folder = 5
    # 设置进程池
    process_pool = multiprocessing.Pool(6)
    # 参数字典
    score_dict = multiprocessing.Manager().dict()
    # 设置共享数据
    vector = multiprocessing.Manager().list(train_x)
    label = multiprocessing.Manager().list(train_y)
    # 多进程交叉验证
    for C_temp in C_para:
        for gamma_temp in gamma_para:
            process_pool.apply_async(train_cv, args=(vector, label, C_temp, gamma_temp, cv_folder, score_dict,))
    process_pool.close()
    process_pool.join()
    # 寻找最佳参数
    max_score = max(zip(score_dict.values(), score_dict.keys()))
    max_C = max_score[1][0]
    max_gamma = max_score[1][1]
    # 记录最佳参数
    fw = open(parametersFilePath,'w')
    fw.write('C: '+str(max_C)+'\n')
    fw.write('gamma: '+str(max_gamma))
    fw.close()
    return max_C, max_gamma

def svr_train(train_x, train_y, p_C, p_gamma, modelFilePath):
    # 训练
    clf = svm.SVR(C=p_C, gamma=p_gamma, kernel='rbf')
    clf.fit(train_x,train_y)
    # 存储模型
    joblib.dump(clf, modelFilePath)

def svr_test(modelFilePath, test_x, test_y, testResultPath, predResultPath):
    # 加载模型
    model = joblib.load(modelFilePath)
    # 使用模型预测标签
    pred = model.predict(test_x)
    pred_list = pred.tolist()
    fw_pred = open(predResultPath,'w')
    json.dump(pred_list,fw_pred)
    MSE,RMSE,MAE = calculate_evaluation(test_y, pred)
    # 写入文件
    fw = open(testResultPath, 'w')
    fw.write("MSE: "+str(MSE)+"\t|\t"+"RMSE: "+str(RMSE)+"\t|\t"+"MAE: "+str(MAE))
    fw_pred.close()
    fw.close()
    return MSE,RMSE,MAE

def calculate_evaluation(label, pred):
    label = label.tolist()
    sum = len(label)
    MSE = 0
    MAE = 0
    for i in range(sum):
        f = pred[i]
        y = label[i]
        MSE += (f-y)*(f-y)
        MAE += abs(f-y)
    MSE_r = MSE / sum
    RMSE_r = sqrt(MSE_r)
    MAE_r = MAE / sum
    return MSE_r, RMSE_r, MAE_r

def get_DC_QR(modelFilePath, vector, label, DCResultPath):
    label = label.tolist()
    # 加载模型
    model = joblib.load(modelFilePath)
    # 使用模型预测标签
    pred = model.predict(vector)
    pred_list = pred.tolist()
    aY = 0
    for i in range(len(label)):
        aY += label[i]
    aY = aY / len(label)
    sum1 = 0
    sum2 = 0
    summ = 0
    for i in range(len(label)):
        sum1 += (pred_list[i]-label[i])*(pred_list[i]-label[i])
        sum2 += (pred_list[i]-aY)*(pred_list[i]-aY)
        temp = abs(pred_list[i]-label[i]) / label[i]
        if temp <= 0.2:
            summ += 1
    DC = 1 - (sum1/sum2)
    QR = summ / len(label)
    fw = open(DCResultPath,'w')
    fw.write("DC: "+str(DC)+" | QR: "+str(QR) + "\n")
    fw.close()

def overall_for(train_x, test_x, train_y, test_y, file_index):
    modelFilePath = "/home/zcx/python/project/data/pingwang_svr_model/model/model_"+str(file_index)+".pkl"
    parametersFilePath = "/home/zcx/python/project/data/pingwang_svr_model/model/parameters_"+str(file_index)+".txt"
    testResultPath = "/home/zcx/python/project/data/pingwang_svr_model/result/testResult_"+str(file_index)+".txt"
    predResultPath = "/home/zcx/python/project/data/pingwang_svr_model/result/predictResult_"+str(file_index)+".json"
    DCResultPath = "/home/zcx/python/project/data/pingwang_svr_model/result/DCResult_"+str(file_index)+".txt"
    # 网格搜索参数
    p_C, p_gamma = get_best_para(train_x, train_y, parametersFilePath)
    # 训练模型
    svr_train(train_x, train_y, p_C, p_gamma, modelFilePath)
    # 测试模型
    MSE,RMSE,MAE = svr_test(modelFilePath, test_x, test_y, testResultPath, predResultPath)

    get_DC_QR(modelFilePath, test_x, test_y, DCResultPath)

def train_svr():
    # for i in range(2,73):
    #     train_x, test_x, train_y, test_y = get_scale_h('/home/zcx/python/project/data/pingwang_data/train_data/平望时频训练数据（t+'+str(i)+'）.csv')
    #     overall_for(train_x, test_x, train_y, test_y, 'h(t+'+str(i)+')')
    i = 2    
    train_x, test_x, train_y, test_y = get_scale_h('/home/zcx/python/project/data/pingwang_data/train_data/平望时频训练数据（t+'+str(i)+'）.csv')
    overall_for(train_x, test_x, train_y, test_y, 'h(t+'+str(i)+')')

def train_svr2(i):
    # for i in range(64,72):
    train_x, test_x, train_y, test_y = get_scale_h2('/home/zcx/python/project/data/pingwang_data/train_data/平望时频训练数据（t+'+str(i)+'）.csv')
    overall_for(train_x, test_x, train_y, test_y, 'h(t+'+str(i)+')')

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', type=int, help = 'time')

    return parser

def get_all_para():
    # para = np.load('/home/zcx/python/project/data/pingwang_svr_model/model/parameters_d(t+3).npy',allow_pickle=True)
    # print(para)

    fw = open('/home/zcx/python/project/data/pingwang_svr_model/all/all_h_para.txt','w')
    for i in range(1,73):
        fr = open('/home/zcx/python/project/data/pingwang_svr_model/model/parameters_h(t+'+str(i)+').txt','r')
        g_c = []
        for line in fr:
            temp = line.split(':')
            g_c.append(temp[1].strip())
        fw.write(g_c[1]+'，'+g_c[0]+'\n')
    fw.close()

def get_all_rmse():
    fw = open('/home/zcx/python/project/data/pingwang_svr_model/all/all_h_rmse.txt','w')
    for i in range(1,73):
        fr = open('/home/zcx/python/project/data/pingwang_svr_model/result/testResult_h(t+'+str(i)+').txt','r')
        for line in fr:
            temp1 = line.split('|')
            temp2 = temp1[1].strip().split(':')
        fw.write(temp2[1].strip()+'\n')
    fw.close()

def get_all_DC():
    fw = open('/home/zcx/python/project/data/pingwang_svr_model/all/all_h_DC.txt','w')
    for i in range(1,73):
        fr = open('/home/zcx/python/project/data/pingwang_svr_model/result/DCResult_h(t+'+str(i)+').txt','r')
        for line in fr:
            temp1 = line.split('|')
            temp2 = temp1[0].strip().split(':')
        fw.write(temp2[1].strip()+'\n')
    fw.close()

def get_all_QR():
    fw = open('/home/zcx/python/project/data/pingwang_svr_model/all/all_h_QR.txt','w')
    for i in range(1,73):
        fr = open('/home/zcx/python/project/data/pingwang_svr_model/result/DCResult_h(t+'+str(i)+').txt','r')
        for line in fr:
            temp1 = line.split('|')
            temp2 = temp1[1].strip().split(':')
        fw.write(temp2[1].strip()+'\n')
    fw.close()

if __name__ == '__main__':
    # start = time.time()
    # train_svr()
    # end = time.time()
    # print(end-start)

    # parser = args()
    # args = parser.parse_args()
    # t = args.time
    # train_svr2(t)

    # get_all_para()
    # get_all_rmse()
    get_all_DC()
    get_all_QR()