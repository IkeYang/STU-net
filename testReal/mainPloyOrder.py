import sys
import pickle
sys.path.append(r"c:\users\user\anaconda3\lib\site-packages")
sys.path.append(r"..")
import numpy as np
import random
import pandas as pd
import torch
import time
import matplotlib.pyplot as plt
from dataProcess.clearWithCoord import fliterData
from Unet.testPic import pipLineTestUnet
# from testReal.testBaseline import testDE
# from testReal.testBaseline import testSVR
from testReal.testBaseline import testSNN
from testReal.testBaseline import testSNN2
from testReal.testBaseline import testKNN
from testReal.testBaseline import testSpline
from baseline.testCurveModel import testCurveModel
from utlize import delSomeName
def MAPELoss(output, target):
    output=output.flatten()
    target=target.flatten()
    return np.mean(np.abs((target - output) / (target+1e-12)))
from sklearn.metrics import mean_squared_error,mean_absolute_error
def RMSE(output, target):
    output=output.flatten()
    target=target.flatten()
    return np.sqrt(mean_squared_error(output,target))
def MAE(output, target):
    output=output.flatten()
    target=target.flatten()
    return mean_absolute_error(output,target)
def reserveList(fL,l):
    f=[]
    for i in l:
        f.append(fL[i])
    return f
if __name__ == '__main__':
    # seq = ["ZMS4WT7", "LN43", "H1-10F", "ZMS1WT6", "ZMS1WT9",
    #        "JF-64", "LN62", "H1-06F", "H1-27F", "A1-05", "H1-13F",
    #        "LN51", "A1-14", "A1-10", "JF-50", "A1-11", "H1-03F", "ZMS1WT7", "H1-02F",
    #        "JF-78", "H1-16F", "ZMS4WT6", "H1-05F", "A1-07", "H1-29F", "A1-08", "ZMS4WT2", "ZMS4WT4",
    #        "A1-13", "H1-19F", "H1-07F", "H1-26F", "H1-08F", "A1-12", "H1-28F", "A2-25", "A2-30", "A1-09",
    #        "H1-09F", "ZMS4WT9", "LN35", "A2-23", "LN40", "ZMS4WT1", "H1-01F", "H1-31F", "ZMS1WT1", "A1-02", "LN41",
    #        "H1-17F", "ZMS1WT8", "LN42", "ZMS4WT3", "LN63", "H1-14F", "ZMS4WT8", "H1-32F", "H1-12F", "H1-11F", "LN54",
    #        "H1-04F", "H1-20F", "H1-24F", "ZMS1WT4", "A2-21", "ZMS1WT2", "ZMS1WT3", "H1-18F", "H1-15F", "JF-33", "A2-22",
    #        "A2-19", "H1-23F", "LN53", "H1-21F", "H1-22F", "A2-33"]
    def testOnce(cutdownX = True,xPer = 0.85 * 100):


        path = r"D:\YANG Luoxiao\Data\WPC\newRes"
        # path = r"D:\YANG Luoxiao\Data\WPC\newRes"
        with open(path, "rb") as f:
            newRes = pickle.load(f)
        data = newRes["data"]
        thresRes = newRes["thres"]

        timeCost=0
        ##test Unet
        delNameL = ['H1-30F','H1-25F', 'A1-02', 'LN49', ]
        delete = True

        if delete:
            compareRes = np.zeros([len(thresRes.keys()) - len(delNameL), 2, 3])

        else:
            compareRes = np.zeros([len(thresRes.keys()), 2, 3])

        bs = 20
        setLen = 4000
        epoch = 3
        ms = 0.8
        name='DEAndADE'
        for p in range(20,100):
            res = {}
            seq, rate, res1, res2, res3, (f1, f2, f3) = pipLineTestUnet(data, thresRes, epoch=3, ms=ms, name='DEAndADE',p=p,
                                                                        setLen=setLen, bs=bs, enhance=True, dev=10,
                                                                        testOnly=False, dataType='default', saveMiddle=False,cutdownX=cutdownX,xPer=xPer)
            # if cutdownX:
            #     with open('FuncUnetCTotal0-8' + str(xPer), 'wb') as f:
            #         pickle.dump((f1, f2, f3), f)
            # else:
            #     with open('FuncUnetTotal0-8', 'wb') as f:
            #         pickle.dump((f1, f2, f3), f)
            # return 0
            seq, l = delSomeName(seq, delNameL=delNameL, delete=delete)
            res['seq']=seq
            res['rate']=rate[l]
            res['methodOrder']=['Unet','KNN','SNN','DE','ADE','PLF4','PLF5','Spline']
            res['res']=np.zeros([len(res['methodOrder']),len(seq),3,3]) # method , wt, 3dataCleanType,2 metric rmse mape MAE
            f1Unet=reserveList(f1,l);f2Unet=reserveList(f2,l);f3Unet=reserveList(f3,l)
            f1KNN=[];f2KNN=[];f3KNN=[]
            f1SNN=[];f2SNN=[];f3SNN=[]
            f1DE=[];f2DE=[];f3DE=[]
            f1ADE=[];f2ADE=[];f3ADE=[]
            f1PLF4=[];f2PLF4=[];f3PLF4=[]
            f1PLF5=[];f2PLF5=[];f3PLF5=[]
            f1Spline=[];f2Spline=[];f3Spline=[]





            for i,k in enumerate(seq):

                data1, data2, data3, dT = fliterData(data[k], thresRes[k], trainTestSPlit=True,minmax=False,xcutDown=cutdownX,xpercentilep=xPer)
                #Unet
                res['res'][0,i,0,0]=RMSE(f1Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,0,1]=MAPELoss(f1Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,0,2]=MAE(f1Unet[i](dT[:,0]), dT[:,1])

                res['res'][0,i,1,0]=RMSE(f2Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,1,1]=MAPELoss(f2Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,1,2]=MAE(f2Unet[i](dT[:,0]), dT[:,1])

                res['res'][0,i,2,0]=RMSE(f3Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,2,1]=MAPELoss(f3Unet[i](dT[:,0]), dT[:,1])
                res['res'][0,i,2,2]=MAE(f3Unet[i](dT[:,0]), dT[:,1])
                # #KNN
                # x1P,_ = testKNN(data1, None, None, dT)
                # x2P,_ = testKNN(data2, None, None, dT)
                # x3P,_ = testKNN(data3, None, None, dT)
                # res['res'][1,i,0,0]=RMSE(x1P, dT[:,1])
                # res['res'][1,i,0,1]=MAPELoss(x1P, dT[:,1])
                # res['res'][1,i,0,2]=MAE(x1P, dT[:,1])
                #
                # res['res'][1,i,1,0]=RMSE(x2P, dT[:,1])
                # res['res'][1,i,1,1]=MAPELoss(x2P, dT[:,1])
                # res['res'][1,i,1,2]=MAE(x2P, dT[:,1])
                #
                # res['res'][1,i,2,0]=RMSE(x3P, dT[:,1])
                # res['res'][1,i,2,1]=MAPELoss(x3P, dT[:,1])
                # res['res'][1,i,2,2]=MAE(x3P, dT[:,1])
                # #SNN
                # x1P, _ = testSNN2(data1, None, None, dT,hidden=(50,50))
                # x2P, _ = testSNN2(data2, None, None, dT,hidden=(50,50))
                # x3P, _ = testSNN2(data3, None, None, dT,hidden=(50,50))
                # res['res'][2, i, 0, 0] = RMSE(x1P, dT[:, 1])
                # res['res'][2, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                # res['res'][2, i, 0, 2] = MAE(x1P, dT[:, 1])
                #
                # res['res'][2, i, 1, 0] = RMSE(x2P, dT[:, 1])
                # res['res'][2, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                # res['res'][2, i, 1, 2] = MAE(x2P, dT[:, 1])
                #
                # res['res'][2, i, 2, 0] = RMSE(x3P, dT[:, 1])
                # res['res'][2, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                # res['res'][2, i, 2, 2] = MAE(x3P, dT[:, 1])
                # #DE
                # x1P, _ = testCurveModel(dT,k,1,'DE')
                # x2P, _ = testCurveModel(dT,k,2,'DE')
                # x3P, _ = testCurveModel(dT,k,3,'DE')
                # res['res'][3, i, 0, 0] = RMSE(x1P, dT[:, 1])
                # res['res'][3, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                # res['res'][3, i, 0, 2] = MAE(x1P, dT[:, 1])
                #
                # res['res'][3, i, 1, 0] = RMSE(x2P, dT[:, 1])
                # res['res'][3, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                # res['res'][3, i, 1, 2] = MAE(x2P, dT[:, 1])
                #
                # res['res'][3, i, 2, 0] = RMSE(x3P, dT[:, 1])
                # res['res'][3, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                # res['res'][3, i, 2, 2] = MAE(x3P, dT[:, 1])
                #
                # # ADE
                # x1P, _ = testCurveModel(dT, k, 1, 'ADE')
                # x2P, _ = testCurveModel(dT, k, 2, 'ADE')
                # x3P, _ = testCurveModel(dT, k, 3, 'ADE')
                # res['res'][4, i, 0, 0] = RMSE(x1P, dT[:, 1])
                # res['res'][4, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                # res['res'][4, i, 0, 2] = MAE(x1P, dT[:, 1])
                #
                # res['res'][4, i, 1, 0] = RMSE(x2P, dT[:, 1])
                # res['res'][4, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                # res['res'][4, i, 1, 2] = MAE(x2P, dT[:, 1])
                #
                # res['res'][4, i, 2, 0] = RMSE(x3P, dT[:, 1])
                # res['res'][4, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                # res['res'][4, i, 2, 2] = MAE(x3P, dT[:, 1])
                #
                # # # PLF4
                # x1P, _ = testCurveModel(dT, k, 1, 'PLF4')
                # x2P, _ = testCurveModel(dT, k, 2, 'PLF4')
                # x3P, _ = testCurveModel(dT, k, 3, 'PLF4')
                # res['res'][5, i, 0, 0] = RMSE(x1P, dT[:, 1])
                # res['res'][5, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                # res['res'][5, i, 0, 2] = MAE(x1P, dT[:, 1])
                #
                # res['res'][5, i, 1, 0] = RMSE(x2P, dT[:, 1])
                # res['res'][5, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                # res['res'][5, i, 1, 2] = MAE(x2P, dT[:, 1])
                #
                # res['res'][5, i, 2, 0] = RMSE(x3P, dT[:, 1])
                # res['res'][5, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                # res['res'][5, i, 2, 2] = MAE(x3P, dT[:, 1])
                #
                # # # PLF5
                # x1P, _ = testCurveModel(dT, k, 1, 'PLF5')
                # x2P, _ = testCurveModel(dT, k, 2, 'PLF5')
                # x3P, _ = testCurveModel(dT, k, 3, 'PLF5')
                # res['res'][6, i, 0, 0] = RMSE(x1P, dT[:, 1])
                # res['res'][6, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                # res['res'][6, i, 0, 2] = MAE(x1P, dT[:, 1])
                #
                # res['res'][6, i, 1, 0] = RMSE(x2P, dT[:, 1])
                # res['res'][6, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                # res['res'][6, i, 1, 2] = MAE(x2P, dT[:, 1])
                #
                # res['res'][6, i, 2, 0] = RMSE(x3P, dT[:, 1])
                # res['res'][6, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                # res['res'][6, i, 2, 2] = MAE(x3P, dT[:, 1])

                #Spline
                time_start = time.time()
                x1P, _ = testSpline(data1, None, None, dT)
                x2P, _ = testSpline(data2, None, None, dT)
                x3P, _ = testSpline(data3, None, None, dT)

                res['res'][7, i, 0, 0] = RMSE(x1P, dT[:, 1])
                res['res'][7, i, 0, 1] = MAPELoss(x1P, dT[:, 1])
                res['res'][7, i, 0, 2] = MAE(x1P, dT[:, 1])

                res['res'][7, i, 1, 0] = RMSE(x2P, dT[:, 1])
                res['res'][7, i, 1, 1] = MAPELoss(x2P, dT[:, 1])
                res['res'][7, i, 1, 2] = MAE(x2P, dT[:, 1])

                res['res'][7, i, 2, 0] = RMSE(x3P, dT[:, 1])
                res['res'][7, i, 2, 1] = MAPELoss(x3P, dT[:, 1])
                res['res'][7, i, 2, 2] = MAE(x3P, dT[:, 1])
                time_end = time.time()
                timeCost += time_end - time_start
            print('SNN time cost', timeCost / (i + 1), 's')
            av = np.mean(res['res'], axis=(1))
            print(p)
            print(av[:, :, 0])
            # print(av[:, :, 1])
            # print(av[:, :, 2])

        #
        # if cutdownX:
        #     with open('resCTotal0-8'+str(xPer), 'wb') as f:
        #         pickle.dump(res, f)
        # else:
        #     with open('resTotal0-8T', 'wb') as f:
        #         pickle.dump(res, f)


    testOnce(cutdownX = False,xPer = 0.85 * 100)
    # testOnce(cutdownX = True,xPer = 0.85 * 100)
    # testOnce(cutdownX = True,xPer = 0.875 * 100)
    # testOnce(cutdownX = True,xPer = 0.90 * 100)
    # testOnce(cutdownX = True,xPer = 0.925 * 100)
    # testOnce(cutdownX = True,xPer = 0.95* 100)
    # testOnce(cutdownX = True,xPer = 0.975* 100)






































