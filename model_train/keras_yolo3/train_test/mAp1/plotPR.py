import demjson
import numpy
import matplotlib.pyplot as plt
import cv2
import time

from pylab import *
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

VOC_LABELS = {
    '0':'none',
    '1':'fire',
    '2':'smoke',
    '3':'lamp',
    '4':'helmet',
    '5':'hat',
    '6':'head',
}
COLOR_LABELS={
    'fire':'red',
    'smoke':'gray',
    'lamp':'yellow',
    'helmet':'orange',
    'hat':'green',
    'head':'blue'
}

labels = ['fire','smoke','lamp','head','helmet','hat']
labelsX=['select_threshold','nms','TP','FP','TN','FN','precision_rate','recall_rate']
dictLabels = {}
for label in labels:
    labelY = label
    label={}
    for xl in labelsX:
        label[xl] = 0
    dictLabels[labelY] = label

print (dictLabels)

#从存储预测文件中 计算select_threshold 下，分类 准确率，召回率
def testP (select_threshold,listPre):
    for preDict in listPre:
        preDict = dict(preDict)
        fileName = preDict['fileName']

        fileNameObjs = list(str(fileName).split("jpg")[1])

        predictInfo = list(demjson.decode(str(preDict['predictInfo'])))
        rclasses=[]
        rscores=[]
        rbboxes=[]
        for i in range(len(predictInfo)):
            info = dict(predictInfo[i])
            if float(info['rscores']) >= select_threshold:
                rclasses.append(VOC_LABELS[str(info['rclasses'])])
                rscores.append(float(info['rscores']))
                rbboxes.append(tuple(info['rbboxes']))
        for label in labels:
            dictLabels[label]['select_threshold'] = select_threshold
            if  label in rclasses:
                if label in fileNameObjs:
                    dictLabels[label]['TP'] += 1
                else:
                    dictLabels[label]['FN'] += 1
            else:
                if label in fileNameObjs:
                    dictLabels[label]['FP'] += 1
                else:
                    dictLabels[label]['TN'] += 1
    # print (str(dictLabels))
    resultL = []
    for label in labels:
        resultLL = []
        x_label = dict(dictLabels[label])
        x_label['precision_rate'] = float(x_label['TP']) / float(x_label['TP']+x_label['FP'])
        x_label['recall_rate'] = float(x_label['TP']) / float(x_label['TP']+x_label['FN'])
        # print (label+","+str(select_threshold)+","+str(x_label['precision_rate'])+","+str(x_label['recall_rate']))
        resultLL.append(label)
        resultLL.append(str(select_threshold))
        resultLL.append(str(x_label['precision_rate']))
        resultLL.append(str(x_label['recall_rate']))
        resultL.append(resultLL)
    return resultL

# 在阈值范围内 分类的准确率 召回率 并存储
def testPs (wSFile,wfile,step = 0.002,startScore = 0.65):
    sumL = int((1-startScore)/step)
    pLabelL = [['label','select_threshold','precision_rate','recall_rate']]
    listPre=[]
    with open(wfile, 'rb') as f:
        line = f.readline()
        line = demjson.decode(line)
        listPre = list(line)
    for i in range(1,sumL):
        pDict = {}
        select_threshold = startScore+i*step
        resultL = testP(select_threshold,listPre)
        pLabelL = numpy.append(pLabelL,resultL,axis=0)

    print (str(pLabelL))
    numpy.save(wSFile,pLabelL)







# 绘制分类的准确率 召回率曲线图
def plotPR (prTxt):
    labelPRArray = numpy.load(prTxt)
    labelDict = {}
    for label in labels:
        spr={}
        select_threshold=[]
        precision_rate=[]
        recall_rate=[]
        print (len(labelPRArray))
        for pr in labelPRArray :
            print (pr)
            if label == pr[0]:
                #'{:s} | {:.3f}'.format(class_name, score),
                select_threshold.append(float("{:.4f}".format(float(pr[1]))))
                precision_rate.append(float("{:.4f}".format(float(pr[2]))))
                recall_rate.append(float("{:.4f}".format(float(pr[3]))))
        spr['select_threshold']=select_threshold
        spr['precision_rate'] = precision_rate
        spr['recall_rate'] = recall_rate
        labelDict[label]= str(spr)

    print (str(labelDict))
    # plotPRClass(labelDict,'fire')
    plotPRClassTicker(labelDict,'fire')
    # plotPRClasses(labelDict)

def plotPRClass(labelDict,label):
    labelDict = labelDict[label]
    labelClassDict = dict(demjson.decode(labelDict))

    plt.figure(1)  # 创建图表1
    plt.title('Precision/Recall')  # give plot a title
    plt.xlabel('Recall')  # make axis labels
    plt.ylabel('Precision')
    plt.figure(1)
    # plt.xlim([0.00, 1.00])
    # plt.ylim([0.00, 1.00])

    select_threshold = labelClassDict['select_threshold']
    precision_rate = labelClassDict['precision_rate']
    recall_rate = labelClassDict['recall_rate']
    F1 = []
    for i in range(len(precision_rate)):
            p = precision_rate[i]
            r = recall_rate[i]
            f1 = 2*p*r / (p+r)
            F1.append(f1)
    plt.figure(1)
    plt.plot(select_threshold, precision_rate,color=COLOR_LABELS[label], label='p')
    plt.plot(select_threshold, recall_rate, color=COLOR_LABELS['smoke'], label='r')
    plt.plot(recall_rate, precision_rate, color=COLOR_LABELS['helmet'], label='p-r')
    # plt.plot(select_threshold, F1, color=COLOR_LABELS[label], label="threshold_F1")
    plt.legend()
    timeName = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
    # plt.savefig("./data/" + timeName + ".png")
    plt.show()


def plotPRClassTicker(labelDict,label):
    labelDict = labelDict[label]
    labelClassDict = dict(demjson.decode(labelDict))

    figure(1)  # 创建图表1
    title('Precision/Recall')  # give plot a title
    xlabel('Recall')  # make axis labels
    ylabel('Precision')

    xmajorLocator = MultipleLocator(0.1)  # 将x主刻度标签设置为20的倍数
    xmajorFormatter = FormatStrFormatter('%1.1f')  # 设置x轴标签文本的格式
    xminorLocator = MultipleLocator(0.01)  # 将x轴次刻度标签设置为5的倍数

    ymajorLocator = MultipleLocator(0.1)  # 将y轴主刻度标签设置为0.5的倍数
    ymajorFormatter = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
    yminorLocator = MultipleLocator(0.01)  # 将此y轴次刻度标签设置为0.1的倍数

    ax = subplot(111)
    select_threshold = labelClassDict['select_threshold']
    precision_rate = labelClassDict['precision_rate']
    recall_rate = labelClassDict['recall_rate']
    F1 = []
    for i in range(len(precision_rate)):
            p = precision_rate[i]
            r = recall_rate[i]
            f1 = 2*p*r / (p+r)
            F1.append(f1)
    plot(select_threshold, precision_rate,color=COLOR_LABELS[label], label='p')
    plot(select_threshold, recall_rate, color=COLOR_LABELS['smoke'], label='r')
    plot(recall_rate, precision_rate, color=COLOR_LABELS['helmet'], label='p-r')
    plot(select_threshold, F1, color=COLOR_LABELS[label], label="threshold_F1")

    # 设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormatter)

    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormatter)

    # 显示次刻度标签的位置,没有标签文本
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)

    ax.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

    timeName = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
    # plt.savefig("./data/" + timeName + ".png")
    show()




def plotPRClasses(labelDict):
    print(str(labelDict))

    plt.figure(1)  # 创建图表1
    plt.title('Precision/Recall')  # give plot a title
    plt.xlabel('Recall')  # make axis labels
    plt.ylabel('Precision')
    plt.figure(1)
    plt.xlim([0.00, 1.00])
    plt.ylim([0.00, 1.00])
    for label in labels :
        labelClassDict = dict(demjson.decode(labelDict[label]))
        select_threshold = labelClassDict['select_threshold']
        precision_rate = labelClassDict['precision_rate']
        recall_rate = labelClassDict['recall_rate']
        F1 = []
        for i in range(len(precision_rate)):
            p = precision_rate[i]
            r = recall_rate[i]
            f1 = 2*p*r / (p+r)
            F1.append(f1)
        plt.figure(1)
        plt.plot(recall_rate, precision_rate,color=COLOR_LABELS[label], label=label)
        # plt.plot(select_threshold, F1, color=COLOR_LABELS[label], label=label)
    plt.legend()
    timeName = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
    plt.savefig("./data/" + timeName + ".png")
    plt.show()


if __name__=='__main__':
    testPs("./data/Label_PR.txt.npy","./data/wPreFile.txt")
    plotPR("./data/Label_PR.txt.npy")