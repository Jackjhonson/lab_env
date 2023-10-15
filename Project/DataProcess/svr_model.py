from math import sqrt
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
import numpy as np
import pandas as pd
import joblib
import random
import json

def get_scale():
    d = pd.read_csv('/home/zcx/python/project/data/svr_model/pingwang_day.csv')
    n_row = d.shape[0]
    n_col = d.shape[1]
    x = []
    y = []
    for i in range(n_row-1):
        x_temp = []
        for j in range(3,n_col):
            x_temp.append(float(d.iloc[i,j]))
        x.append(x_temp)
        y.append(float(d.iloc[i,2]))
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs, y

def get_scale2():
    d = pd.read_csv('/home/zcx/python/project/data/svr_model/PingwangDaily_Revise.csv')
    n_row = d.shape[0]
    n_col = d.shape[1]
    x = []
    y = []
    for i in range(n_row-1):
        x_temp = []
        for j in range(0,n_col-3):
            x_temp.append(float(d.iloc[i,j]))
        x.append(x_temp)
        y.append(float(d.iloc[i,359]))
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs, y

def get_scale_ignore():
    d = pd.read_csv('/home/zcx/python/project/data/svr_model/pingwang_day.csv')
    n_row = d.shape[0]
    n_col = d.shape[1]
    x = []
    y = []
    ignore_factor = [34,35, 69,70, 104,105, 139,140, 174,175, 209,210, 244,145, 279,280, 314,315, 349,350]
    for i in range(n_row-1):
        x_temp = []
        for j in range(3,n_col):
            if j in ignore_factor:
                continue
            x_temp.append(float(d.iloc[i,j]))
        x.append(x_temp)
        y.append(float(d.iloc[i,2]))
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs, y

def get_train_test_json(x, y):
    x = x.tolist()
    n_row = len(x)
    train_x = []
    train_y = []
    test_x = []
    test_y = []
    train_sum = 1224
    for i in range(n_row):
        if i < train_sum:
            train_x.append(x[i][:])
            train_y.append(y[i])
        else:
            test_x.append(x[i][:])
            test_y.append(y[i])
    fw_train_x = open('/home/zcx/python/project/data/svr_model/pingwang_train_x4.csv','w')
    fw_train_y = open('/home/zcx/python/project/data/svr_model/pingwang_train_y4.csv','w')
    fw_test_x = open('/home/zcx/python/project/data/svr_model/pingwang_test_x4.csv','w')
    fw_test_y = open('/home/zcx/python/project/data/svr_model/pingwang_test_y4.csv','w')
    json.dump(train_x,fw_train_x)
    json.dump(train_y,fw_train_y)
    json.dump(test_x,fw_test_x)
    json.dump(test_y,fw_test_y)

def svr_training(trainFilePath_x, trainFilePath_y, modelFilePath, parametersFilePath):
    # 读取文件
    fw_x = open(trainFilePath_x,'r')
    fw_y = open(trainFilePath_y,'r')
    vector = json.load(fw_x)
    label = json.load(fw_y)
    # 参数选择范围
    parameters = [
        {
            'C': [2 ** -5, 2 ** -3, 2 ** -1, 2 ** 1, 2 ** 3, 2 ** 5, 2 ** 7, 2 ** 9, 2 ** 11, 2 ** 13, 2 ** 15],
            'gamma': [2 ** 3, 2 ** 1, 2 ** -1, 2 ** -3, 2 ** -5, 2 ** -7, 2 ** -9, 2 ** -11, 2 ** -13, 2 ** -15],
            'kernel': ['rbf'],
            'epsilon': [0.01]
        }
    ]
    # 网格搜索交叉验证，找到最佳参数
    searchPara = GridSearchCV(svm.SVR(),parameters,cv=10,n_jobs=8)
    searchPara.fit(vector,label)
    # 使用最佳参数训练
    parameters_dict = searchPara.best_params_
    clf = svm.SVR(C=parameters_dict['C'], gamma=parameters_dict['gamma'], kernel=parameters_dict['kernel'])
    clf.fit(vector,label)
    # 存储模型
    joblib.dump(clf, modelFilePath)
    # 存储最佳参数,用于交叉验证
    np.save(parametersFilePath, searchPara.best_params_)

def svr_testing(modelFilePath, testFilePath_x, testFilePath_y, testResultPath):
    # 加载模型
    model = joblib.load(modelFilePath)
    # 读取文件
    fw_x = open(testFilePath_x,'r')
    fw_y = open(testFilePath_y,'r')
    vector = json.load(fw_x)
    label = json.load(fw_y)
    # 使用模型预测标签
    pred = model.predict(vector)
    pred_list = pred.tolist()
    fw_pred = open('/home/zcx/python/project/data/svr_model/day_data/result/predictResult4.json','w')
    json.dump(pred_list,fw_pred)
    MSE,RMSE,MAE = calculate_evaluation(label, pred)
    # 写入文件
    fw = open(testResultPath, 'w')
    fw.write("MSE: "+str(MSE)+"\t|\t"+"RMSE: "+str(RMSE)+"\t|\t"+"MAE: "+str(MAE))
    return MSE,RMSE,MAE

def svr_validating(trainFilePath_x, trainFilePath_y, parametersFilePath, validationFilePath):
    # 读取文件
    fw_x = open(trainFilePath_x,'r')
    fw_y = open(trainFilePath_y,'r')
    vector = json.load(fw_x)
    label = json.load(fw_y)
    # 读取参数
    parameters_dict = np.load(parametersFilePath, allow_pickle=True).item()
    # 定义写入文件
    fw = open(validationFilePath, 'w')
    # 10次10折交叉验证,即100个结果
    for i in range(0, 100):
        vector_train, label_train, vector_test, label_test = get_random_validation_data(vector, label)
        # 定义模型
        clf = svm.SVR(C=parameters_dict['C'], gamma=parameters_dict['gamma'], kernel=parameters_dict['kernel'], epsilon=parameters_dict['epsilon'])
        # 模型训练
        clf.fit(vector_train, label_train)
        # 模型预测
        pred = clf.predict(vector_test)
        # 计算accuracy
        MSE,RMSE,MAE = calculate_evaluation(label_test, pred)
        # 写入文件
        fw.write("MSE: "+str(MSE)+"\t|\t"+"RMSE: "+str(RMSE)+"\t|\t"+"MAE: "+str(MAE)+"\n")

# 获取交叉验证的数据
def get_random_validation_data(vector,label):
    # 获取随机数
    random_index = []
    one_sum = int(len(label) / 5)
    while True:
        r_index = random.randint(0, len(label)-1)
        if not random_index.__contains__(r_index):
            random_index.append(r_index)
        if len(random_index) == one_sum:
            break
    # 根据随机数划分数据集
    vector_train = []
    label_train = []
    vector_test = []
    label_test = []
    for i in range(0, len(label)):
        if random_index.__contains__(i):
            vector_test.append(vector[i])
            label_test.append(label[i])
        else:
            vector_train.append(vector[i])
            label_train.append(label[i])
    return vector_train, label_train, vector_test, label_test

# 计算MSE，RMSE，MAE
def calculate_evaluation(label, pred):
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

def overall_for():
    trainFilePath_x = "/home/zcx/python/project/data/svr_model/pingwang_train_x4.csv"
    trainFilePath_y = "/home/zcx/python/project/data/svr_model/pingwang_train_y4.csv"
    modelFilePath = "/home/zcx/python/project/data/svr_model/day_data/model/model4.pkl"
    parametersFilePath = "/home/zcx/python/project/data/svr_model/day_data/model/parameters4.npy"
    testFilePath_x = "/home/zcx/python/project/data/svr_model/pingwang_test_x4.csv"
    testFilePath_y = "/home/zcx/python/project/data/svr_model/pingwang_test_y4.csv"
    testResultPath = "/home/zcx/python/project/data/svr_model/day_data/result/testResult4.txt"
    validationFilePath = "/home/zcx/python/project/data/svr_model/day_data/result/validation4.txt"
    # # 训练模型
    svr_training(trainFilePath_x, trainFilePath_y, modelFilePath, parametersFilePath)
    # # 测试模型
    MSE,RMSE,MAE = svr_testing(modelFilePath, testFilePath_x, testFilePath_y, testResultPath)
    # # 交叉验证
    svr_validating(trainFilePath_x, trainFilePath_y, parametersFilePath, validationFilePath)

    get_DC_QR(modelFilePath, testFilePath_x, testFilePath_y, testResultPath)

def get_DC_QR(modelFilePath, testFilePath_x, testFilePath_y, testResultPath):
    # 加载模型
    model = joblib.load(modelFilePath)
    # 读取文件
    fw_x = open(testFilePath_x,'r')
    fw_y = open(testFilePath_y,'r')
    vector = json.load(fw_x)
    label = json.load(fw_y)
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
    print("DC: "+str(DC)+" | QR: "+str(QR))

def get_para():
    para = np.load('/home/zcx/python/project/data/svr_model/day_data/model/parameters2.npy',allow_pickle=True)
    print(para)

def get_RMSE():
    fr = open('/home/zcx/python/project/data/svr_model/day_data/result/validation.txt','r')
    fw = open('/home/zcx/python/project/data/svr_model/day_data/result/rmse.txt','w')
    for l in fr:
        temp = l.split("|")
        rmse_temp = temp[1].strip().split(":")
        fw.write(str(rmse_temp[1].strip())+"\n")
    fw.close()

def get_all_data(x, y):
    x = x.tolist()
    n_row = len(x)
    train_x = []
    train_y = []
    for i in range(n_row):
        train_x.append(x[i][:])
        train_y.append(y[i])
    fw_train_x = open('/home/zcx/python/project/data/svr_model/pingwang_all_x3.csv','w')
    fw_train_y = open('/home/zcx/python/project/data/svr_model/pingwang_all_y3.csv','w')
    json.dump(train_x,fw_train_x)
    json.dump(train_y,fw_train_y)

def svr_test_all(modelFilePath, testFilePath_x, testFilePath_y, testResultPath):
    # 加载模型
    model = joblib.load(modelFilePath)
    # 读取文件
    fw_x = open(testFilePath_x,'r')
    fw_y = open(testFilePath_y,'r')
    vector = json.load(fw_x)
    label = json.load(fw_y)
    # 使用模型预测标签
    pred = model.predict(vector)
    pred_list = pred.tolist()
    fw_pred = open('/home/zcx/python/project/data/svr_model/day_data/result/predict_all3.json','w')
    json.dump(pred_list,fw_pred)

def get_all_test_result():
    modelFilePath = "/home/zcx/python/project/data/svr_model/day_data/model/model3.pkl"
    testFilePath_x = "/home/zcx/python/project/data/svr_model/pingwang_all_x3.csv"
    testFilePath_y = "/home/zcx/python/project/data/svr_model/pingwang_all_y3.csv"
    testResultPath = "/home/zcx/python/project/data/svr_model/day_data/result/testResult3.txt"
    
    svr_test_all(modelFilePath, testFilePath_x, testFilePath_y, testResultPath)

def write_txt():
    fr = open('/home/zcx/python/project/data/svr_model/day_data/result/predict_all3.json','r')
    fw = open('/home/zcx/python/project/data/svr_model/day_data/result/predict_all3.txt','w')
    s = json.load(fr)
    for l in s:
        fw.write(str(l)+"\n")
    fw.close()

if __name__ == "__main__":
    # x,y = get_scale()
    # x,y = get_scale_ignore()
    # x,y = get_scale2()
    # get_train_test_json(x, y)
    # get_all_data(x, y)
    overall_for()
    # get_para()
    # get_scale()
    # get_RMSE()
    # get_all_test_result()
    # write_txt()