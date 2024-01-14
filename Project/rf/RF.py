import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from pprint import pprint
from sklearn import metrics
from openpyxl import load_workbook
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV

def main():
    for i in range(1,4):

        print('PingwangDaily+'+str(i)+'start')
        #读取数据
        flood=pd.read_csv('/home/lzy/lab_env/Project/平望日频时频/处理/PingwangDaily+'+str(i)+'.csv',index_col=0) 
        flood=flood.iloc[:,1:]
        flood.shape

        #进行数据归一化
        from sklearn import preprocessing
        min_max_scaler = preprocessing.MinMaxScaler()
        flood_scal=min_max_scaler.fit_transform(flood)
        flood_df = pd.DataFrame(flood_scal, columns=flood.columns)
        X=flood_df.iloc[:,:-1]
        y=flood_df.iloc[:,-1]
        print(X.shape)
        print(y)

        #构造训练集测试集 
        y=pd.DataFrame(y.values,columns=['target'])
        x=X
        input_size=len(x.iloc[1,:])
        cut=458#取最后cut=458天为测试集
        X_train, X_test=x.iloc[:-cut],x.iloc[-cut:]#列表的切片操作
        y_train, y_test=y.iloc[:-cut],y.iloc[-cut:]
        X_train,X_test,y_train,y_test=X_train.values,X_test.values,y_train.values,y_test.values
        x.iloc[:-cut]
        print(X_train.shape)#通过输出训练集测试集的大小来判断数据格式正确。
        print(X_test.shape)
        print(y_train.shape)
        print(y_test.shape)

        # Search optimal hyperparameter
        n_estimators_range=[int(x) for x in np.linspace(start=50,stop=500,num=10)]
        # max_features_range=['auto','sqrt']
        max_depth_range=[int(x) for x in np.linspace(10,410,num=9)]
        max_depth_range.append(None)
        min_samples_split_range=[int(x) for x in np.linspace(start=2,stop=10,num=9)]
        min_samples_leaf_range=[int(x) for x in np.linspace(start=2,stop=10,num=9)]
        # bootstrap_range=[True,False]

        random_forest_hp_range2={'n_estimators':n_estimators_range,
                                # 'max_features':max_features_range,
                                'max_depth':max_depth_range,
                                'min_samples_split':min_samples_split_range,
                                'min_samples_leaf':min_samples_leaf_range
                                # 'bootstrap':bootstrap_range
                                }
        print(random_forest_hp_range2)

        from sklearn.ensemble import RandomForestRegressor

        random_forest_model_test_2_base=RandomForestRegressor()
        random_forest_model_test_2_random=GridSearchCV(estimator=random_forest_model_test_2_base,
                                                        param_grid=random_forest_hp_range2,
                                                        n_jobs=10,
                                                        cv=10,
                                                        verbose=0)
        random_forest_model_test_2_random.fit(X_train,y_train)

        best_hp_now_2=random_forest_model_test_2_random.best_params_
        print(best_hp_now_2)

        # Build RF regression model with optimal hyperparameters

        random_forest_model_final=random_forest_model_test_2_random.best_estimator_

        # Predict test set data

        random_forest_predict=random_forest_model_test_2_random.predict(X_test)
        random_forest_error=random_forest_predict-y_test
        random_forest_predict.reshape(-1, 1).shape

        scaler_new = preprocessing.MinMaxScaler()
        scaler_new.min_, scaler_new.scale_ = min_max_scaler.min_[0], min_max_scaler.scale_[0]

        train_result=random_forest_model_test_2_random.predict(X_train)
        train_result = scaler_new.inverse_transform(train_result.reshape(-1, 1))
        train_label = scaler_new.inverse_transform(y_train)
        train_data = pd.concat([pd.DataFrame(train_result),pd.DataFrame(train_label)],axis=1)
        train_data.columns = ['predict','origin']

        train_data.to_csv('/home/lzy/lab_env/Project/平望日频时频/训练/PingwangDailytrain+'+str(i)+'.csv')

        test_result = scaler_new.inverse_transform(random_forest_predict.reshape(-1, 1))
        test_label = scaler_new.inverse_transform(y_test)
        test_data = pd.concat([pd.DataFrame(test_result),pd.DataFrame(test_label)],axis=1)
        test_data.columns = ['predict','origin']

        test_data.to_csv('/home/lzy/lab_env/Project/平望日频时频/训练/PingwangDailytest+'+str(i)+'.csv')

        # Verify the accuracy
        random_forest_R2=metrics.r2_score(test_label,test_result)
        random_forest_RMSE=metrics.mean_squared_error(test_label,test_result)**0.5
        s = 'PingwangDailytest+'+str(i)+'\'s RMSE is {0}., R2 is {1}.'.format(random_forest_RMSE, random_forest_R2)
        f = open (r'/home/lzy/lab_env/Project/平望日频时频/训练/result.txt','a')
        print (s,file = f)
        f.close()

        print('PingwangDaily+'+str(i)+'finish')


if __name__ == '__main__':
    main()
