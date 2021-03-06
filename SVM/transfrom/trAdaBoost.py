# -*- coding: UTF-8 -*-

import numpy as np
from SVM.SVC import svc


#   parameter全是list
#   返回训练后的模型
#   TrainS 原训练样本
#   TrainA 辅助训练样本
#   LabelS 原训练样本标签
#   LabelA 辅助训练样本标签
#   DataT  测试样本
#   LabelT 测试样本标签
#   N 迭代次数
#   param=[C, tol, maxIter, kTup]

class trClassifier:
    def __init__(self, svcs, beta_Ts):
        self.svcs = svcs
        #   构造一个队列减少计算量
        self.core = []
        for i in range(len(svcs)):
            self.core.append(beta_Ts[i])

    def predict(self, x):
        left = 1
        right = 1
        for i in range(len(self.svcs)):
            predict = self.svcs[i].predict(x)
            if predict > 0:
                predict = 1
            elif predict < 0:
                predict = 0
            else:
                raise NameError("Error : predict = 0")

            #  当core等于0时，predict永远返回1，但此时第i次迭代的分类表现很好（error=0），
            #  于是单独使用第i次训练得到的分类器作为总分类器
            if self.core[i] == 0:
                if predict == 1:
                    return 1
                else:
                    return -1
            else:
                left *= self.core[i] ** (-predict)
                right *= self.core[i] ** (-0.5)

        if left >= right:
            return 1
        else:
            return -1


def trAdaBoost(trans_A, trans_S, label_A, label_S, param, N=20, errorRate=0.05, checker='', nonTr=False):
    # print("trAdaBoost.")

    trans_data = trans_A + trans_S

    row_A = len(trans_A)
    row_S = len(trans_S)

    # 初始化权重
    # 权重C：C越大系统越重视对应样本
    weights = np.mat([1 / (row_A + row_S)] * (row_A + row_S))

    beta = 1 / (1 + np.sqrt(2 * np.log(row_A / N)))

    tempSvcs = []
    tempBeta_Ts = []

    svcs = []
    beta_Ts = []
    result = np.ones([row_A + row_S, N])

    # print('params initial finished.')

    if nonTr:
        errorRate = 1.5

    for i in range(N):

        # 归一化权重
        weights = calculate_P(weights)

        # 训练分类器并返回预测结果
        result[:, i], classifier = train_classify(trans_data, label_A + label_S, param, weights.tolist()[0])

        # 计算错误率
        error_rate = calculate_error_rate(np.mat(label_S), result[row_A:row_A + row_S, i],
                                          weights[0, row_A:row_A + row_S])
        # print('Core %s, Error rate: %s' % (str(proNum), str(error_rate)))
        # print('')
        if error_rate > 0.5:
            error_rate = 0.5  # 确保eta小于0.5

        beta_T = error_rate / (1 - error_rate)

        tempSvcs.append(classifier)

        if nonTr:
            beta_T = 0

        tempBeta_Ts.append(beta_T)

        if error_rate <= errorRate:
            if i == 0:  # didn't boost
                break  # 防止过拟合

            # collect boost result
            bootLog = open("D:\\WINTER\\Pycharm_project\\srpProject\\SVM\\boostingLog", 'a')
            bootLog.write(checker + " in Boost ,error rate: %s \n" % (str(error_rate)))
            bootLog.close()
            break

        bootLog = open("D:\\WINTER\\Pycharm_project\\srpProject\\SVM\\boostingLog", 'a')
        bootLog.write(checker + " in Boost ,error rate: %s \n" % (str(error_rate)))
        bootLog.close()

        # 调整源域样本权重
        for j in range(row_S):
            weights[0, row_A + j] = weights[0, row_A + j] * np.power(beta_T,
                                                                     -np.abs(result[row_A + j, i] - label_S[j]) / 2)

        # 调整辅域样本权重
        for j in range(row_A):
            weights[0, j] = weights[0, j] * np.power(beta, np.abs(result[j, i] - label_A[j]) / 2)

    # 记录后N/2个分类器，向上取整
    num = int(len(tempSvcs) / 2)

    for i in range(num, len(tempSvcs)):
        svcs.append(tempSvcs[i])
        beta_Ts.append(tempBeta_Ts[i])

    # 构造训练出来的集成分类器并返回
    classifier = trClassifier(svcs, beta_Ts)

    # print("trAdaBoost finished.")

    return classifier


# 归一化权重
def calculate_P(weights):
    total = np.sum(weights)
    return weights / total


#  训练分类器，返回对源数据集的分类结果以及分类器
def train_classify(trans_data, trans_labels, param, P):
    classifier = svc(trans_data, trans_labels, param[0], param[1], param[2], param[3], cWeight=P)

    result = [0] * len(trans_data)
    for i in range(len(trans_data)):
        temp = classifier.predict(trans_data[i])
        if temp < 0:
            result[i] = 0
        elif temp > 0:
            result[i] = 1
        else:
            raise NameError("Error : predict = 0")
    return result, classifier


# 计算错误率
def calculate_error_rate(label_R, label_P, weight):
    for i in range(len(label_P)):
        if label_P[i] == 0:
            label_P[i] = -1

    error = 0

    labels = label_R.tolist()[0]

    weights = weight.tolist()[0]

    for i in range(len(label_P)):
        if label_P[i] != labels[i]:
            error += weights[i]

    return error / np.sum(weight)
