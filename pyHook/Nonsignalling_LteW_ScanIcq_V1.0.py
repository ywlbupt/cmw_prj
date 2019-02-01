#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, os, visa, threading, time, string, numpy
from AllFunctionsV1 import *
from pymouse import PyMouse
from pykeyboard import PyKeyboard

ReadCurrentFlag = 0                # 为1则读电流。会大幅增加测试时间，建议测试点很少的时候用。需事先用adb命令关闭USB供电（但仍会有很小的充电电流）
ReadCurrentWaitTime = "10"         # 每个channel读电流前等待稳定的时间。可以是数字（单位是秒）或"Manual"
ModeChosen = 0                     # 目前可选0——FDDLTE、1——TDDLTE和2——WCDMA
bandChosen = ["OB3"]               # 为简化程序，每次只支持一个LTE或WCDMA band，写法均是"OB*"
LteBW = "B200"                     # 仅用于LTE。B050 B100 B200分别代表LTE带宽为1.4/5/10/20MHz。目前只支持5/10/20MHz选项
ScanType = "LMH"                   # 信道扫描类型，可设置为中间信道（“M")或低中高信道（"LMH"）或逐个信道（"each"）
IpNP = 21.5                        # InterpolateTargetPower，拟合/插值的目标功率
RGIlist = list(range(54,56+1))     # RGI扫描范围，功率值最好覆盖IpNP值以得出合理拟合结果。建议的序列长度为3～5个数。
##########        mode=0为指定一个PAcurrent值，分解出Icq1和Icq2，分别按规律扩展后，再组合出新的PAcurrent序列       #########
##########        mode=1为直接指定Icq1和Icq2序列，组合出新的PAcurrent序列                                     #########
##########        mode=2为直接写一个PAcurrent序列                                                          #########
##########        PAcurrentListExtendFlag为1的话，则把PAcurrentListExtend序列附在上述生成的序列后面            #########
PAcurrentGenerateMode=0            # PAcurrent序列的生成方式，按如上说明选择。
PAcurrentListExtendFlag=0          # Flag为1的话，则把PAcurrentListExtend序列附在上述生成的序列后面

if PAcurrentGenerateMode == 0:
    PAcurrentInitial=52870     # PAcurrent当前值
    period=16                  # 不同Icq，ACLR性能做规律变化的周期。目前发现都是16
    ScanRangeIcq1=1            # 对Icq当前值左右的值也纳入。此范围建议不要太大，否则乘出来的组合数太多。
    LeftExtendPeriodIcq1=1     # 向左扩展n个周期。此范围建议不要太大，否则乘出来的组合数太多。
    RightExtendPeriodIcq1=1    # 向右扩展n个周期。此范围建议不要太大，否则乘出来的组合数太多。
    ScanRangeIcq2=4
    LeftExtendPeriodIcq2=4
    RightExtendPeriodIcq2=4
elif PAcurrentGenerateMode == 1:
    Icq1List = [184,185,186]
    Icq2List = [213,214]
elif PAcurrentGenerateMode == 2:
    PAcurrentList = [36023,44215,40119,36039,44231,40135,36007,44199,40103,35751,39847,35735,43927,43943,39831,44247,28148,40151,36055,27892,35767,27636,36295,40391,44487,43959,31908,39863,32164,40087,31652,44183,35991,44471,40375,40407,36311,35719,39815,44503,36279,31732,32244,31988,35783,43975,39879,31668,31924,36071,36327,40423,44263,44519,35975,32180,40167,40071,43911,27572,27828,28084,27556,27812,28068,35814,40439,44535,35799,36343,39910,44006,39895,35830,43991,39894,43990,39926,44022,35798,36263,40359,44455,39878,43974,35782,36087,40183,44279,44167,40344,44440,35815,44007,40360,39911,40182,44278,36086,31636,32148,36248,44456,31892,36247,40343,28132,44439,39862,36264,35766,43958,27876,40166,36070,44262,31973,27620,32229,40376,31717,44472,44246,40150]
if PAcurrentListExtendFlag == 1:
    PAcurrentListExtend = [51415]  # 可以手工加上几个感兴趣的点。Flag=1则启用。
########################################################################################
#####   Icq1和Icq2都有每隔16个值出现一次局部最优值的规律。                  ####################
#####   实测发现Icq1的变化对性能的影响小于Icq2。因此建议优先扫描Icq2         ####################
########################################################################################

# 和仪表连接方式，请配置正确的IP地址或GPIB号
rm = visa.ResourceManager()
rm.list_resources()
PM = rm.open_resource("GPIB0::20::INSTR")
#PM = rm.open_resource("TCPIP0::192.168.0.2::inst0::INSTR")
print(PM.query("*IDN?"))
if ReadCurrentFlag == 1:
    PM_DCsupply = rm.open_resource("GPIB0::5::INSTR")
    print(PM_DCsupply.query("*IDN?"))
LogFile="NonSig_ScanIcq" + time.strftime('%Y%m%d',time.localtime(time.time())) + ".txt"
########################################################################################
##### ^^^^^^^^^^  以上是参数定义部分，可根据实际情况修改。   ^^^^^^^^^^^^^^^^^^^           #####
#####                                                                              #####
#####             以下程序主体部分，一般不修改                                           #####
########################################################################################

######################### Main function   ##############################################
def main():
    global Icq1List
    global Icq2List
    global PAcurrentList
    # 配置线损
    lossName = PM.query ("CONFigure:BASE:FDCorrection:CTABle:CATalog?")
    time.sleep(1)
    if lossName.find ("CMW_loss") !=  -1:
        PM.write("CONFigure:BASE:FDCorrection:CTABle:DELete 'CMW_loss'")
    PM.write("CONFigure:BASE:FDCorrection:CTABle:CREate 'CMW_loss', 1920000000, 0.8, 1980000000, 0.8, \
             2110000000, 0.8, 2170000000, 0.8, 1850000000, 0.8 1910000000, 0.8, 1930000000, 0.8, 1990000000, 0.8,\
             824000000, 0.5, 849000000, 0.5, 869000000, 0.5, 894000000, 0.5, 925000000, 0.5, 960000000, 0.5, \
             880000000, 0.5, 915000000, 0.5, 2350000000, 0.9, 2535000000, 0.9, 2593000000, 0.9")
    PM.write("CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF1")  #配置RF1 Common口的Tx Rx方向损耗
    PM.write("CONFigure:FDCorrection:ACTivate RF1O, 'CMW_loss', TX, RF1")    #配置RF1 OUT口的Tx方向损耗

    if PAcurrentGenerateMode == 0:
        Icq1=int(PAcurrentInitial/256)
        Icq2=int(PAcurrentInitial - Icq1*256)
        Icq1List=[]
        Icq2List=[]
        for ii in range(-LeftExtendPeriodIcq1,RightExtendPeriodIcq1+1):
            Temp_Icq1=list(range(Icq1+ii*period-ScanRangeIcq1,Icq1+ii*period+ScanRangeIcq1+1))
            Icq1List.extend(Temp_Icq1)
        for ii in range(-LeftExtendPeriodIcq2,RightExtendPeriodIcq2+1):
            Temp_Icq2=list(range(Icq2+ii*period-ScanRangeIcq2,Icq2+ii*period+ScanRangeIcq2+1))
            Icq2List.extend(Temp_Icq2)
    if PAcurrentGenerateMode <2:
        PAcurrentList = zeros(len(Icq1List)*len(Icq2List))
        for ii in range(len(Icq1List)):
            for jj in range(len(Icq2List)):
                PAcurrentList[ii+jj*len(Icq1List)] = (Icq1List[ii]*256+Icq2List[jj])
        PAcurrentList = list(map(int,PAcurrentList))
        print("Icq1List is %s" %Icq1List)
        print("Icq2List is %s" %Icq2List)
    if PAcurrentListExtendFlag == 1:
        PAcurrentList.extend(PAcurrentListExtend)
    print("PAcurrentList length is %d" %(len(PAcurrentList)))
    print("PAcurrentList is %s" %PAcurrentList)

    if ModeChosen in [0,1]:
        ChannelList = channelLteList(bandChosen,LteBW,ScanType)
    elif ModeChosen == 2:
        ChannelList = channel3GList(bandChosen,ScanType)
    if ReadCurrentFlag ==0:
        print("expected test time is %3.1f minutes" %float(len(PAcurrentList)*len(RGIlist)*len(ChannelList)*16/60))
    else:
        print("Reading current needed, expected test time is %3.1f minutes" %float(len(PAcurrentList)*len(RGIlist)*len(ChannelList)))
        

#########################   获取各个控件的位置     ##########################################
#########################   测试过程中请不要操作鼠标和键盘     ###############################
    mouse = PyMouse()
    key = PyKeyboard()
    input("Move mouse to 'Tear Down' then press Enter" )
    (IsTearDownX,IsTearDownY) = mouse.position()      #获取当前坐标的位置
    print(IsTearDownX,IsTearDownY)
    input("Move mouse to 'Tx Channel' then press Enter" )
    (TxChannelX,TxChannelY) = mouse.position()      #获取当前坐标的位置
    print(TxChannelX,TxChannelY)
    input("Move mouse to 'Set Radio Config' then press Enter" )
    (SetRadioConfigX,SetRadioConfigY) = mouse.position()      #获取当前坐标的位置
    print(SetRadioConfigX,SetRadioConfigY)
    input("Move mouse to 'RGI' then press Enter" )
    (RGIx,RGIy) = mouse.position()      #获取当前坐标的位置
    print(RGIx,RGIy)
    input("Move mouse to 'PA current' then press Enter" )
    (PAcurrentX,PAcurrentY) = mouse.position()      #获取当前坐标的位置
    print(PAcurrentX,PAcurrentY)
    input("Move mouse to 'Tx Override' then press Enter" )
    (TxOverrideX,TxOverrideY) = mouse.position()      #获取当前坐标的位置
    print(TxOverrideX,TxOverrideY)
#########################   获取各个控件的位置     ##########################################
#########################   测试过程中请不要操作鼠标和键盘     ###############################
    
    TimeStart = time.clock()
    print("test start. Please check instrument parameters")
    interpolateTemp = numpy.zeros([len(RGIlist),4])  #用来做拟合/插值，便于比较
    
    for ii in range(len(bandChosen)):
        if ModeChosen == 0:
            PMwrite(PM,"CONFigure:LTE:MEAS:DMODe FDD")
        elif ModeChosen == 1:
            PMwrite(PM,"CONFigure:LTE:MEAS:DMODe TDD")
        if ModeChosen in [0,1]:
            PMwrite(PM,"ROUTe:LTE:MEAS:SCENario:SALone RF1C, RX1")
            PMwrite(PM,"CONFigure:LTE:MEAS:BAND %s" %bandChosen[ii])
            PMwrite(PM,"CONFigure:LTE:MEAS:RFSettings:PCC:FREQuency %dCH" %ChannelList[ii][0])
            PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
            PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:MSUBframes 0, 10, 2")
            PMwrite(PM,"CONFigure:LTE:MEAS:PCC:CBANdwidth %s" %LteBW)
            PMwrite(PM,"TRIGger:LTE:MEAS:MEValuation:SOURce 'Free Run (Fast Sync)'")
            PMwrite(PM,"CONFigure:LTE:MEAS:RFSettings:ENPMode MANual")
            PMwrite(PM,"CONFigure:LTE:MEAS:RFSettings:ENPower 24")
            PMwrite(PM,"CONFigure:LTE:MEAS:RFSettings:UMARgin 12")
            PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:MOEXception ON")
        elif ModeChosen == 2:
            PMwrite(PM,"ROUTe:WCDMa:MEAS:SCENario:SALone RF1C, RX1")
            PMwrite(PM,"CONFigure:WCDMa:MEAS:BAND %s" %bandChosen[ii])
            PMwrite(PM,"CONFigure:WCDMa:MEAS:RFSettings:FREQuency %d CH" %ChannelList[ii][0])
            PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
            PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 10")
            PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:SCOunt:SPECtrum 10")
            PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:MOEXception ON")
            PMwrite(PM,"TRIGger:WCDMa:MEAS:MEValuation:SOURce 'Free Run (Fast Sync)'")
            PMwrite(PM,"CONFigure:WCDMA:MEAS:RFSettings:ENPower 24")
            PMwrite(PM,"CONFigure:WCDMA:MEAS:RFSettings:UMARgin 12")
        os.system("pause")
            
        time.sleep(1)
        for jj in range(len(ChannelList[ii])):
            mouse.click(IsTearDownX,IsTearDownY,1)
            mouse.click(SetRadioConfigX,SetRadioConfigY,1)
            time.sleep(3)
            mouse.click(IsTearDownX,IsTearDownY,1)
            mouse.click(TxChannelX,TxChannelY,1,2)
            key.type_string(str(ChannelList[ii][jj]))
            mouse.click(SetRadioConfigX,SetRadioConfigY,1)
            time.sleep(0.2)
               
            if ModeChosen in [0,1]:
                PMwrite(PM,"CONFigure:LTE:MEAS:RFSettings:PCC:FREQuency %dCH" %ChannelList[ii][jj])
            elif ModeChosen == 2:
                PMwrite(PM,"CONFigure:WCDMa:MEAS:RFSettings:FREQuency %d CH" %ChannelList[ii][jj])
            time.sleep(1)
            
            for kk in range(len(PAcurrentList)):
                mouse.click(PAcurrentX,PAcurrentY,1,2)
                key.type_string(str(PAcurrentList[kk]))
                time.sleep(0.2)
                Icqq1 = numpy.floor(PAcurrentList[kk]/256)
                Icqq2 = PAcurrentList[kk]-Icqq1*256
                TestFlag=1
                for ll in range(len(RGIlist)):
                    mouse.click(RGIx,RGIy,1,2)
                    key.type_string(str(RGIlist[ll]))
                    time.sleep(0.1)
                    mouse.click(TxOverrideX,TxOverrideY,1)
                    time.sleep(0.1)
                    
                    try:
                        if ModeChosen in [0,1]:
                            PM.write("ABORt:LTE:MEAS:MEValuation")
                            PM.write("INIT:LTE:MEAS:MEValuation")
                            time.sleep(0.7)
                            LteAclr = PMquery(PM,"FETCh:LTE:MEAS:MEValuation:ACLR:AVERage?")  #读取UE发射功率
                            LteAclrList = list(map(float,LteAclr.split (',')))
                            UEPwr = LteAclrList[4]
                            ChPwr = LteAclrList[4]
                            AdjCLRn = LteAclrList[3]
                            AdjCLRp = LteAclrList[5]
                        elif ModeChosen == 2:
                            PMwrite(PM,"ABORt:WCDMa:MEAS:MEValuation")
                            WAclrList = PMqueryWithDelay(PM,"READ:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?").split(',')
                            UEPwr = float(WAclrList[15])
                            ChPwr = float(WAclrList[1])
                            AdjCLRn = ChPwr-float(WAclrList[3])
                            AdjCLRp = ChPwr-float(WAclrList[4])
                    except Exception:
                        print("TxPwr underdriven or overdriven, ignored")
                        TestFlag = -1
                        break
                    if (AdjCLRn<30 and ChPwr<23):
                        print("ACLR too bad, ignored")
                        TestFlag = 0
                        break

                    if TestFlag == 1:
                        interpolateTemp[ll][0] = AdjCLRn
                        interpolateTemp[ll][1] = ChPwr
                        interpolateTemp[ll][2] = AdjCLRp
                        if ReadCurrentFlag == 1:
                            if ReadCurrentWaitTime == "Manual":
                                os.system("pause")
                            else:
                                time.sleep(int(ReadCurrentWaitTime))
                            if ModeChosen ==1:
                                CurrentLength = 40
                            else:
                                CurrentLength = 15
                            Current=numpy.zeros(CurrentLength)
                            for k in range(CurrentLength):
                                Current[k]=float(PMquery(PM_DCsupply,"MEASure:CURRent?"))
                                print(Current[k])
                                time.sleep(0.1+numpy.random.rand()*0.3)
                            if ModeChosen ==1:
                                temp_current = sorted(Current)
                                interpolateTemp[ll][3] = average(temp_current[2:(CurrentLength-2)])
                            else:
                                interpolateTemp[ll][3] = average(Current)
                        else:
                            interpolateTemp[ll][3] = 0.001
                        print("%-4s %d %s %s %3d %3d %3.2f %3.2f %3.2f %1.3f" %(bandChosen[ii], ChannelList[ii][jj],\
                            RGIlist[ll],PAcurrentList[kk],Icqq1, Icqq2, AdjCLRn,ChPwr,AdjCLRp,interpolateTemp[ll][3]))

                    elif TestFlag == -1:
                        print("%-4s %d %s %s %3d %3d underdriven or overdriven, ignored" %(bandChosen[ii], ChannelList[ii][jj],\
                            RGIlist[ll],PAcurrentList[kk],Icqq1, Icqq2))
                    else:
                        print("%-4s %d %s %s %3d %3d ACLR too bad, ignored" %(bandChosen[ii], ChannelList[ii][jj],\
                            RGIlist[ll],PAcurrentList[kk],Icqq1, Icqq2))

                if TestFlag==1:
                    Tmp1 = numpy.polyfit(interpolateTemp[:,1],interpolateTemp[:,0],len(RGIlist)-1)
                    Tmp2 = numpy.polyfit(interpolateTemp[:,1],interpolateTemp[:,2],len(RGIlist)-1)
                    Tmp3 = numpy.polyfit(interpolateTemp[:,1],interpolateTemp[:,3],len(RGIlist)-1)
                    interpolateAclrLeft  = numpy.polyval(Tmp1, IpNP)
                    interpolateAclrRight = numpy.polyval(Tmp2, IpNP)
                    interpolateCurrent   = numpy.polyval(Tmp3, IpNP) 
                    print("%-4s %d -- %s %3d %3d %3.2f %3.1f %3.2f %1.3f" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, interpolateAclrLeft,IpNP,interpolateAclrRight, interpolateCurrent))
                    LogfileWrite(LogFile, "%-4s %d -- %s %3d %3d %3.2f %3.1f %3.2f %1.3f\n" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, interpolateAclrLeft,IpNP,interpolateAclrRight, interpolateCurrent))
                elif TestFlag == -1:
                    print("%-4s %d -- %s %3d %3d --   %3.1f   --" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, IpNP))
                    LogfileWrite(LogFile, "%-4s %d -- %s %3d %3d --   %3.1f   --\n" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, IpNP))
                else:
                    print("%-4s %d -- %s %3d %3d bad  %3.1f  bad" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, IpNP))
                    LogfileWrite(LogFile, "%-4s %d -- %s %3d %3d bad  %3.1f  bad\n" %(bandChosen[ii], ChannelList[ii][jj],\
                        PAcurrentList[kk],Icqq1, Icqq2, IpNP))

############################## All test end  ##########################
    TimeEnd = time.clock()
    print("The total test time is %.1f minutes" %((TimeEnd-TimeStart)/60))
    endtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print("Test finished at %s" %endtime)
    LogfileWrite(LogFile, "Test finished at %s\n\n" %endtime)

if __name__  ==  '__main__':
    main()
