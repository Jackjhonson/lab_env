from math import sqrt
from sklearn import svm
from sklearn.datasets import load_diabetes
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# diabetes = load_diabetes()

# X = diabetes.data
# y = diabetes.target

# X = X.tolist()
# y = y.tolist()

# for i in range(len(X)):
#     X[i].append(y[i])

# dat = pd.DataFrame(data=X)
# dat.to_csv('/home/zcx/python/project/data/data_for_java/diabetes.csv')

def get_scale_data(datapath):
    d = pd.read_csv(datapath)
    n_row = d.shape[0]
    train_num = int(n_row * 0.8)
    x = d.iloc[:,1:11]
    y = d.iloc[:,11]
    scaler = MinMaxScaler()
    xs = scaler.fit_transform(x)
    return xs[0:train_num], xs[train_num:], y[0:train_num], y[train_num:]

def svr(train_x, test_x, train_y, test_y):
    # 训练
    model = svm.SVR(C=100, gamma=0.01, kernel='rbf')
    model.fit(train_x,train_y)
    # 预测
    pred = model.predict(test_x)
    pred_list = pred.tolist()
    MSE,RMSE,MAE = calculate_evaluation(test_y, pred)
    print(RMSE)

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

if __name__ == '__main__':
    train_x, test_x, train_y, test_y = get_scale_data('/home/zcx/python/project/data/diabetes.csv')
    svr(train_x, test_x, train_y, test_y)