#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, os, visa, threading, time, string
from numpy import *
from AllFunctionsV1 import *

#############################################################################################
################     Designed by LvXiaolei, revised by YanWeilin & WangYu   #################
################     last update date: 2017-11-24                ############################
#############################################################################################

#########################################################################################
#######  本函数把pyvisa的query命令封装起来，添加基本的异常处理                              #####
#########################################################################################
def PMquery(PM,Commands):
    while 1:
        try:
            EchoContent=PM.query(Commands)
            break
        except ValueError as err:
            print("value err,need reconnect manually. %s" %Commands,err)
        except Exception as err:
            print("query err,%s" %Commands,err)
            time.sleep(2)
            EchoContent=PM.query(Commands,delay=3)
            time.sleep(1)
    return(EchoContent)

#########################################################################################
#######  本函数把pyvisa的query命令封装起来，添加基本的异常处理，增加2s延时                    #####
#########################################################################################
def PMqueryWithDelay(PM,Commands):
    try:
        EchoContent=PM.query(Commands,delay=2)
    except ValueError as err:
        print("value err,need reconnect manually. %s" %Commands,err)
    except Exception as err:
        print("query err,%s" %Commands,err)
        time.sleep(2)
        EchoContent=PM.query(Commands,delay=3)
        time.sleep(1)
    return(EchoContent)

########################################################################################
#######  本函数把pyvisa的write命令封装起来，添加基本的异常处理                              #####
#########################################################################################
def PMwrite(PM,Commands):
    while 1:
        try:
            EchoContent=PM.write(Commands)
            break
        except Exception as err:
            print("write err,%s" %Commands,err)
            time.sleep(3)
    return(EchoContent)

#########################################################################################
#######  本函数统计一个序列中不为零的元素个数                                              #####
#########################################################################################
def NonZeroNumber(Array):
    number=0
    for i in range(len(Array)):
        if Array[i]!=0:
            number+=1        
    return(number)

#########################################################################################
#######  为避免掉线导致已测的数据未保存，每次写入动作都重新打开、关闭文件                        #####
#########################################################################################
def LogfileWrite(logfile,content):
    TRxLog=open(logfile,"a+")
    TRxLog.write(content)
    TRxLog.close()


#########################################################################################
#######   本函数是根据不同条件建立一个GSM call，因为GSM call实在太麻烦了，在此统一处理          #####
#########################################################################################
def SetupGSMCall(PM,GSMcall_mode,GSMAttachWaitTime,mouse,CallStartX,CallStartY):
    while PMquery(PM,"SOURce:GSM:SIGN:CELL:STATe:ALL?") != 'ON,ADJ\n':
        time.sleep(1)
    if GSMcall_mode<4:
        counts=0
        while PMquery(PM,"FETCh:GSM:SIGN:PSWitched:STATe?") != 'ATT\n':
            time.sleep(1)
            counts=counts+1
            if counts==GSMAttachWaitTime:
                break
    while PMquery(PM,"FETCh:GSM:SIGN:CSWitched:STATe?") != 'CEST\n':
        if GSMcall_mode==0:
            PMwrite(PM,"CALL:GSM:SIGN:CSWitched:ACTion CONNect")
            time.sleep(10)
        elif GSMcall_mode in [1,4]:
            pass
        elif GSMcall_mode in [2,5]:
            mouse.click(CallStartX,CallStartY,1)
        else:
            os.popen("adb shell am start -a android.intent.action.CALL tel:112")
        time.sleep(2)


#########################################################################################
#######  本函数从仪表读取并返回LTE bler值。                                              #####
#########################################################################################
def QueryLteBler(PM,InstrPwr,Loss):
    PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %InstrPwr)
    time.sleep(0.1)

    PMwrite(PM,"ABORt:LTE:SIGN:EBLer")
#    TimeStart=time.clock()
    PMwrite(PM,"INIT:LTE:SIGN:EBLer")
    while PMquery(PM,"FETCh:LTE:SIGN:EBLer:STATe?")!='RDY\n':
        time.sleep(0.1)
#    TimeEnd=time.clock()
#    print("test time %.2f seconds" %(TimeEnd-TimeStart))
    LteBler = PMquery(PM,"FETCh:LTE:SIGN:EBLer:RELative?")
    listLteBler = LteBler.split (',')
    while (listLteBler[1]=="INV" or listLteBler[1]=="NAV"):
        print("BLER=NULL, maybe call lost. Please wait for reconnect")
        os.popen ("adb reboot")
        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
        time.sleep(2)
        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
        time.sleep(3)
        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(-50-Loss))
        while PMquery(PM,"SOURce:LTE:SIGN:CELL:STATe:ALL?").strip()!="ON,ADJ":
            time.sleep(2)
        while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
            PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
            time.sleep(3)
        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %InstrPwr)
        PMwrite(PM,"ABORt:LTE:SIGN:EBLer")
        PMwrite(PM,"INIT:LTE:SIGN:EBLer")
        while PMquery(PM,"FETCh:LTE:SIGN:EBLer:STATe?")!='RDY\n':
            time.sleep(0.1)
        LteBler = PMquery(PM,"FETCh:LTE:SIGN:EBLer:RELative?")
        listLteBler = LteBler.split (',')
    return 100-round(float(listLteBler[1]),2)

#########################################################################################
#######  本函数设置WCDMA/TDSCdma的仪表下行功率值                                         #####
#########################################################################################
def PMwrite3G_DLPwr(PM,W_TD,InstrPwr):
    if W_TD=="WCDMa":
        PMwrite(PM,"CONFigure:WCDMa:SIGN:RFSettings:COPower %3.2f" %InstrPwr)
    elif W_TD=="TDSCdma":
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:DL:LEVel:PCCPch %3.2f" %InstrPwr)

#########################################################################################
#######  本函数从仪表读取并返回WCDMA或TD-SCDMA BER值。                                   #####
#########################################################################################
def QueryW_TD_Ber(PM,W_TD,RF_output,InstrPwr):
    PMwrite3G_DLPwr(PM,W_TD,InstrPwr)
    PMwrite(PM,"ABORt:%s:SIGN:BER" %W_TD)
    PMwrite(PM,"INIT:%s:SIGN:BER" %W_TD)
    #TimeStart=time.clock()
    while PMquery(PM,"FETCh:%s:SIGN:BER:STATe?" %W_TD)!='RDY\n':
        time.sleep(0.2)
    #TimeEnd=time.clock()
    #print("test time %.2f seconds" %(TimeEnd-TimeStart))
    W_TD_Ber=PMquery(PM,"FETCh:%s:SIGN:BER?" %W_TD)
    listW_TD_Ber = W_TD_Ber.split (',')
    while (listW_TD_Ber[1]=="INV" or listW_TD_Ber[1]=="NAV" or listW_TD_Ber[1]=="NCAP"):
        print("BER=NULL, maybe call lost. Please wait for reconnect")
        os.popen ("adb reboot")
        time.sleep(0.5)
        PMwrite3G_DLPwr(PM,W_TD,(InstrPwr+50))
        PMwrite(PM,"SOURce:%s:SIGN:CELL:STATe OFF" %W_TD)
        PMwrite(PM,"SOURce:%s:SIGN:CELL:STATe ON" %W_TD)
        #os.system("pause")
        time.sleep(2)
        PMwrite(PM,"ROUTe:%s:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1" %W_TD)
        time.sleep(1)
        PMwrite(PM,"ROUTe:%s:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1" %W_TD)
        #os.system("pause")
        while PMquery(PM,"SOURce:%s:SIGN:CELL:STATe:ALL?" %W_TD)!='ON,ADJ\n':
            time.sleep(2)
        while PMquery(PM,"FETCh:%s:SIGN:PSWitched:STATe?" %W_TD)!='ATT\n':
            time.sleep(2)
        while PMquery(PM,"FETCh:%s:SIGN:CSWitched:STATe?" %W_TD) != 'CEST\n':
            PMwrite(PM,"CALL:%s:SIGN:CSWitched:ACTion CONNect" %W_TD)
            time.sleep(4)
        if RF_output=="RF1O":
            PMwrite(PM,"ROUTe:%s:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1" %W_TD)
        PMwrite3G_DLPwr(PM,W_TD,InstrPwr)
        PMwrite(PM,"ABORt:%s:SIGN:BER" %W_TD)
        PMwrite(PM,"INIT:%s:SIGN:BER" %W_TD)
        while PMquery(PM,"FETCh:%s:SIGN:BER:STATe?" %W_TD)!='RDY\n':
            time.sleep(0.2)
        W_TD_Ber=PMquery(PM,"FETCh:%s:SIGN:BER?" %W_TD)
        listW_TD_Ber = W_TD_Ber.split (',')
    return round(float(listW_TD_Ber[1]),2)


#########################################################################################
#######  本函数从仪表读取并返回GSM BER值。                                               #####
#########################################################################################
def QueryGSMBer(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,InstrPwr,mouse,CallStartX,CallStartY):
    if GSMcall_mode in [2, 5]:
        from pymouse import PyMouse
        mouse = PyMouse()
    
    PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %InstrPwr)
    PMwrite(PM,"ABORt:GSM:SIGN:BER:CSWitched?")
    PMwrite(PM,"INIT:GSM:SIGN:BER:CSWitched")
    while PMquery(PM,"FETCh:GSM:SIGN:BER:CSWitched:STATe?")!='RDY\n':
        time.sleep(1)
    GSMBer=PMquery(PM,"FETCh:GSM:SIGN:BER:CSWitched?")
    #####################################################################################
    #######  如果运行GSM READ BER命令之前曾经设置过至少2次pcl，                        #####
    #######  则READ命令会自动把PCL改为上一轮用过的值（记为A），但实际上并未生效           #####
    #######  导致的后果是再次设置PCL=A时命令被忽略，导致错误                            #####
    #######  用INIT/FETCh命令则不会有此问题。                                         #####
    #######  原因不明，怀疑是R&S的bug                                                #####
    #####################################################################################
    listGSMBer = GSMBer.split(',')
    while (listGSMBer[2] in ["INV","NAV", "NCAP"]):
        print("BER=NULL, maybe call lost. Please wait for reconnect")
        #os.popen ("adb reboot")
        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")
        time.sleep(1)
        PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %(InstrPwr+50))
        time.sleep(1)
        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe ON")
        time.sleep(2)
        PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        
        SetupGSMCall(PM,GSMcall_mode,GSMAttachWaitTime,mouse,CallStartX,CallStartY)

        if RF_output=="RF1O":
            PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
        PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %InstrPwr)
        PMwrite(PM,"ABORt:GSM:SIGN:BER:CSWitched?")
        PMwrite(PM,"INIT:GSM:SIGN:BER:CSWitched")
        while PMquery(PM,"FETCh:GSM:SIGN:BER:CSWitched:STATe?")!='RDY\n':
            time.sleep(1)
        GSMBer=PMquery(PM,"FETCh:GSM:SIGN:BER:CSWitched?")
        listGSMBer = GSMBer.split(',')
    return round(float(listGSMBer[2]),2)


#########################################################################################
#######   本函数用梯度法寻找LTE FDD/TDD指定信道的灵敏度，返回灵敏度值和BLER值。                #####
#########################################################################################
def SeekLteSens(PM,UpperLimit,CoarseStep,FineStep,Loss):
    ### coarse seek循环。当BLER>0时，设置flag=0，功率稍增，转入fine seek  ###
    InstrPwr=UpperLimit
    CoarseSeekFlag=1
    PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:SFRames 400")
    while CoarseSeekFlag==1:
        LteBler = QueryLteBler(PM,InstrPwr,Loss)
        print("%71.2f, %3.2f coarse" %(InstrPwr, LteBler))
        if LteBler>0.2:                   #第一次测到BLER>0.2则等几秒再复测，避免偶然干扰。以第二次测试为准
            PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(-50-Loss))
            time.sleep(3)
            LteBler = QueryLteBler(PM,InstrPwr,Loss)
            print("%71.2f, %3.2f coarse 2nd" %(InstrPwr, LteBler))
            if LteBler>0.2 and LteBler<=30:    #如果BLER>0.2则设置flag为0，功率稍增，跳出coarse seek循环，否则继续
                InstrPwr=InstrPwr+CoarseStep/2
                CoarseSeekFlag=0
            elif LteBler>30:                 #如果BLER>30则功率回退更大一点
                PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(-50-Loss))
                time.sleep(3)
                InstrPwr=InstrPwr+CoarseStep*1.5
                LteBler = QueryLteBler(PM,InstrPwr,Loss)
                print("%71.2f, %3.2f coarse 3rd" %(InstrPwr, LteBler))
                if  LteBler<=5:
                    CoarseSeekFlag=0
                else:
                    InstrPwr=InstrPwr+CoarseStep
            else:
                InstrPwr=InstrPwr-CoarseStep
        else:
            InstrPwr=InstrPwr-CoarseStep

    ###从coarse seek循环跳出后，进入fine seek循环。在临界点上下各测试一次，BLER分别为pass/fail视为找到 ###
    FineSeekFlag=1
    #PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:SFRames 400")
    while FineSeekFlag==1:
        LteBler = QueryLteBler(PM,InstrPwr,Loss)
        print("%71.2f, %3.2f fine" %(InstrPwr, LteBler))
        if LteBler<5:
            InstrPwr=InstrPwr-FineStep
        else:
            LteBlerPlus = QueryLteBler(PM,InstrPwr,Loss)
            LteBlerMinus = QueryLteBler(PM,InstrPwr+FineStep,Loss)
            print("%71.2f, %3.2f, %3.2f, %3.2f fine 2nd" %(InstrPwr+FineStep, LteBlerMinus, InstrPwr, LteBlerPlus))
            if LteBlerMinus<5 and LteBlerPlus>=5:
                while 1:
                    try:
                        LteFCPwr = float(PMquery(PM,"SENSe:LTE:SIGN:DL:PCC:FCPower?"))#读取仪表当前的full cell power
                        RSepre=InstrPwr+FineStep
                        PMwrite(PM,"CONFigure:LTE:SIGN:UEReport:ENABle OFF")
                        PMwrite(PM,"CONFigure:LTE:SIGN:UEReport:ENABle ON")
                        time.sleep(1)
                        RSRP = float(PMquery(PM,"SENSe:LTE:SIGN:UEReport:RSRP:range?").split(',')[1])
                        RSRQ = float(PMquery(PM,"SENSe:LTE:SIGN:UEReport:RSRQ:range?").split(',')[1])
                        FineSeekFlag=0
                        time.sleep(1)
                        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(-50-Loss))
                        break       #while循环用来捕捉读数的异常。如果三种数据都正确读出，则跳出循环
                        #一个channel测试结束，设置flag=0以跳出fineseek循环，把仪表发射功率设置为高以保证切换channel不掉线
                    except Exception:
                        print("read FCPower or UEReport error, retrying")
                        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
                        time.sleep(2)
                        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
                        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(-50-Loss))
                        while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
                            PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
                            time.sleep(1)
                        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel %3.2f" %(InstrPwr+FineStep))
            elif LteBlerMinus<5 and LteBlerPlus<5:
                InstrPwr=InstrPwr-FineStep
            else:
                InstrPwr=InstrPwr+FineStep*2
    return(RSepre,LteFCPwr,LteBlerMinus,RSRP,RSRQ)


#########################################################################################
#######   本函数用梯度法寻找WCDMA或TDSCDMA指定信道的灵敏度，返回灵敏度值和BER值。              #####
#########################################################################################
def SeekW_TD_Sens(PM,W_TD,RF_output,UpperLimit,CoarseStep,FineStep):
    ### coarse seek循环。当BER>0时，设置flag=0，功率稍增，转入fine seek  ###
    InstrPwr=UpperLimit
    CoarseSeekFlag=1
    #PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:SFRames %d" %FrameNumber)
    while CoarseSeekFlag==1:
        W_TD_Ber = QueryW_TD_Ber(PM,W_TD,RF_output,InstrPwr)
        print("%51.2f, %3.2f" %(InstrPwr, W_TD_Ber))
        if W_TD_Ber>0.1:                   #第一次测到BER>0.1则等几秒再复测，避免偶然干扰。以第二次测试为准
            PMwrite3G_DLPwr(PM,W_TD,(InstrPwr+50))
            time.sleep(2)
            W_TD_Ber = QueryW_TD_Ber(PM,W_TD,RF_output,InstrPwr)
            print("%51.2f, %3.2f" %(InstrPwr, W_TD_Ber))
            if W_TD_Ber>0.1:               #如果BER>1则设置flag为0，功率稍增，跳出coarse seek循环，否则继续
                InstrPwr=InstrPwr+CoarseStep
                CoarseSeekFlag=0
            else:
                InstrPwr=InstrPwr-CoarseStep/2
        else:
            InstrPwr=InstrPwr-CoarseStep

    ###从coarse seek循环跳出后，进入fine seek循环。在临界点复测一遍，满足条件则标记成功，跳出循环 ###
    FineSeekFlag=1
    StatisticNumber=4
    FineW_TD_Ber=zeros(StatisticNumber)
    while FineSeekFlag==1:
        print("%14.2f" %InstrPwr, end="  ")
        for k in range(StatisticNumber):
            FineW_TD_Ber[k] = QueryW_TD_Ber(PM,W_TD,RF_output,InstrPwr)
            if FineW_TD_Ber[k]>0.1:
                break
        print(FineW_TD_Ber, end="  ")
        print("max=%3.2f, aver=%3.2f, std=%3.2f" %(max(FineW_TD_Ber),average(FineW_TD_Ber),std(FineW_TD_Ber)))
        if max(FineW_TD_Ber)<=0.1 and (average(FineW_TD_Ber)>=0.03 or NonZeroNumber(FineW_TD_Ber)>=StatisticNumber/2):
            FineSeekFlag=0
            PMwrite3G_DLPwr(PM,W_TD,(InstrPwr+50))
        elif max(FineW_TD_Ber)<=0.1 and (average(FineW_TD_Ber)<0.03 or std(FineW_TD_Ber)>0.05):
            InstrPwr=InstrPwr-FineStep
        else:
            while FineSeekFlag==1:
                InstrPwr=InstrPwr+FineStep     #功率设置到临界点上方，再测一轮，满足条件则成功，否则功率继续上升
                print("%14.2f" %InstrPwr, end="  ")
                for k in range(StatisticNumber):
                    FineW_TD_Ber[k] = QueryW_TD_Ber(PM,W_TD,RF_output,InstrPwr)
                    if FineW_TD_Ber[k]>0.1:
                        break
                print(FineW_TD_Ber, end="  ")
                print("max=%3.2f, aver=%3.2f, std=%3.2f 2nd" %(max(FineW_TD_Ber),average(FineW_TD_Ber),std(FineW_TD_Ber)))
                if max(FineW_TD_Ber)<=0.1 and (average(FineW_TD_Ber)>=0.02 or NonZeroNumber(FineW_TD_Ber)>=StatisticNumber/2):
                    FineSeekFlag=0
                    PMwrite3G_DLPwr(PM,W_TD,(InstrPwr+50))
                elif max(FineW_TD_Ber)<=0.1 and (average(FineW_TD_Ber)<0.02 or std(FineW_TD_Ber)>0.04):
                    InstrPwr=InstrPwr-2*FineStep
                #elif max(FineW_TD_Ber)<=0.1 and average(FineW_TD_Ber)<=0.08 and std(FineW_TD_Ber)<=0.07:
                #    #在这个循环中，后两个是弱条件限制，一般都能满足
                #    FineSeekFlag=0
                #    PMwrite3G_DLPwr(PM,W_TD,(InstrPwr+50))
                #    #一个channel测试结束，设置flag=0以跳出循环，把仪表发射功率设置为较高的功率以切换channel时不掉线
    return(round(InstrPwr,2),round(average(FineW_TD_Ber),2))


#########################################################################################
#######   本函数用梯度法寻找GSM指定信道的灵敏度，返回灵敏度值和BER值。                         #####
#########################################################################################
def SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimit,CoarseStep,FineStep,mouse,CallStartX,CallStartY):
    ### coarse seek循环。当BER>0时，设置flag=0，功率稍增，转入fine seek  ###
    InstrPwr=UpperLimit
    CoarseSeekFlag=1
    while CoarseSeekFlag==1:
        GSMBer = QueryGSMBer(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,InstrPwr,mouse,CallStartX,CallStartY)
        print("%51.2f, %3.2f" %(InstrPwr, GSMBer))
        if GSMBer>2.4:                   #第一次测到BER>2.4则等几秒再复测，避免偶然干扰。以第二次测试为准
            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %(InstrPwr+50))
            time.sleep(2)
            GSMBer = QueryGSMBer(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,InstrPwr,mouse,CallStartX,CallStartY)
            print("%51.2f, %3.2f" %(InstrPwr, GSMBer))
            if GSMBer>2.4:               #如果BLER>2.4则设置flag为0，功率稍增，跳出coarse seek循环，否则继续
                InstrPwr=InstrPwr+CoarseStep
                CoarseSeekFlag=0
            else:
                InstrPwr=InstrPwr-CoarseStep/2
        else:
            InstrPwr=InstrPwr-CoarseStep

    ###从coarse seek循环跳出后，进入fine seek循环。在临界点复测一遍，满足条件则标记成功，跳出循环 ###
    FineSeekFlag=1
    StatisticNumber=4
    FineGSMBer=zeros(StatisticNumber)
    while FineSeekFlag==1:
        print("%14.2f" %InstrPwr, end="  ")
        for k in range(StatisticNumber):
            FineGSMBer[k] = QueryGSMBer(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,InstrPwr,mouse,CallStartX,CallStartY)
            if FineGSMBer[k]>2.4:
                break
        print(FineGSMBer, end="  ")
        print("max=%3.2f, aver=%3.2f, std=%3.2f" %(max(FineGSMBer),average(FineGSMBer),std(FineGSMBer)))
        if max(FineGSMBer)<=2.4 and average(FineGSMBer)>2 and std(FineGSMBer)<=0.3:
            FineSeekFlag=0
            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %(UpperLimit+50))
        elif max(FineGSMBer)<=2.4 and (average(FineGSMBer)<=2 or std(FineGSMBer)>0.3):
            InstrPwr=InstrPwr-FineStep
        else:
            while FineSeekFlag==1:
                InstrPwr=InstrPwr+FineStep     #功率设置到临界点上方，再测一轮，满足条件则成功
                print("%14.2f" %InstrPwr, end="  ")
                for k in range(StatisticNumber):
                    FineGSMBer[k] = QueryGSMBer(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,InstrPwr,mouse,CallStartX,CallStartY)
                    if FineGSMBer[k]>2.4:
                        break
                print(FineGSMBer, end="  ")
                print("max=%3.2f, aver=%3.2f, std=%3.2f 2nd" %(max(FineGSMBer),average(FineGSMBer),std(FineGSMBer)))
                if max(FineGSMBer)<=2.4 and average(FineGSMBer)>=1.6 and std(FineGSMBer)<=1:
                    #在这个循环中，后两个是弱条件限制，一般都能满足。
                    FineSeekFlag=0
                    PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:TCH %3.2f" %(UpperLimit+50))
                    #一个channel测试结束，设置flag=0以跳出循环，把仪表发射功率设置为较高的功率以切换channel时不掉线
                elif max(FineGSMBer)>2.4:
                    pass
                else:
                    InstrPwr=InstrPwr-2*FineStep
    return(round(InstrPwr,2),round(average(FineGSMBer),2))

#########################################################################################
#######  本函数读取LTE band列表，根据带宽和信道间隔设定返回channel列表                       #####
#########################################################################################
def channelLteList(bandLte,LteBW,ScanType):
    channelLte=[]
    for i in range(len(bandLte)):
        channelLte.append([])
        if bandLte[i]=="OB1":
            if ScanType=="M":          channelLte[i]=[18300]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[18025, 18300, 18575]
                elif ScanType=="each": channelLte[i]=list(range(18025,18575+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[18050, 18300, 18550]
                elif ScanType=="each": channelLte[i]=list(range(18050,18550+1,50))
            elif LteBW=="B150":
                if ScanType=="LMH":    channelLte[i]=[18075, 18300, 18525]
                elif ScanType=="each": channelLte[i]=list(range(18075,18525+1,75))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[18100, 18300, 18500]
                elif ScanType=="each": channelLte[i]=list(range(18100,18500+1,100))
        elif bandLte[i]=="OB2":
            if ScanType=="M":          channelLte[i]=[18900]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[18625, 18900, 19175]
                elif ScanType=="each": channelLte[i]=list(range(18625,19175+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[18650, 18900, 19150]
                elif ScanType=="each": channelLte[i]=list(range(18650,19150+1,50))
            elif LteBW=="B150":
                if ScanType=="LMH":    channelLte[i]=[18675, 18900, 19175]
                elif ScanType=="each": channelLte[i]=list(range(18675,19175+1,75))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[18700, 18900, 19100]
                elif ScanType=="each": channelLte[i]=list(range(18700,19100+1,100))
        elif bandLte[i]=="OB3":
            if ScanType=="M":          channelLte[i]=[19575]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[19225, 19575, 19925]
                elif ScanType=="each": channelLte[i]=list(range(19225,19925+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[19250, 19575, 19900]
                elif ScanType=="each": channelLte[i]=list(range(19250,19900+1,50))
            elif LteBW=="B150":
                if ScanType=="LMH":    channelLte[i]=[19275, 19575, 19925]
                elif ScanType=="each": channelLte[i]=list(range(19275,19925+1,75))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[19300, 19575, 19850]
                elif ScanType=="each": channelLte[i]=list(range(19300,19850+1,100))
        elif bandLte[i]=="OB4":
            if ScanType=="M":          channelLte[i]=[20175]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[19975, 20175, 20375]
                elif ScanType=="each": channelLte[i]=list(range(19975,20375+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[20000, 20175, 20350]
                elif ScanType=="each": channelLte[i]=list(range(20000,20350+1,50))
            elif LteBW=="B150":
                if ScanType=="LMH":    channelLte[i]=[20025, 20175, 20375]
                elif ScanType=="each": channelLte[i]=list(range(20025,20375+1,75))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[20050, 20175, 20300]
                elif ScanType=="each": channelLte[i]=list(range(20050,20300+1,100))
        elif bandLte[i]=="OB5":
            if ScanType=="M":          channelLte[i]=[20525]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[20425, 20525, 20625]
                elif ScanType=="each": channelLte[i]=list(range(20425,20625+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[20450, 20525, 20600]
                elif ScanType=="each": channelLte[i]=list(range(20450,20600+1,50))
            if LteBW=="B150":
                if ScanType=="LMH":    channelLte[i]=[20475, 20525, 20575]
                elif ScanType=="each": channelLte[i]=list(range(20475,20625+1,75))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[20500, 20525, 20550]
                elif ScanType=="each": channelLte[i]=list(range(20500,20550+1,100))
        elif bandLte[i]=="OB7":
            if ScanType=="M":          channelLte[i]=[21100]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[20775, 21100, 21425]
                elif ScanType=="each": channelLte[i]=list(range(20775,21425+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[20800, 21100, 21400]
                elif ScanType=="each": channelLte[i]=list(range(20800,21400+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[20850, 21100, 21350]
                elif ScanType=="each": channelLte[i]=list(range(20850,21350+1,100))
        elif bandLte[i]=="OB8":
            if ScanType=="M":          channelLte[i]=[21625]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[21475, 21625, 21775]
                elif ScanType=="each": channelLte[i]=list(range(21475,21775+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[21500, 21625, 21750]
                elif ScanType=="each": channelLte[i]=list(range(21500,21750+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[21550, 21625, 21700]
                elif ScanType=="each": channelLte[i]=list(range(21550,21700+1,100))
        elif bandLte[i]=="OB12":
            if ScanType=="M":          channelLte[i]=[23095]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[23035, 23095, 23155]
                elif ScanType=="each": channelLte[i]=list(range(23035,23155+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[23060, 23095, 23130]
                elif ScanType=="each": channelLte[i]=[23060, 23095, 23130]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band12,please check")
        elif bandLte[i]=="OB13":
            if ScanType=="M":          channelLte[i]=[23230]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[23205, 23230, 23255]
                elif ScanType=="each": channelLte[i]=[23205, 23230, 23255]
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[23230]
                elif ScanType=="each": channelLte[i]=[23230]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band13,please check")
        elif bandLte[i]=="OB17":
            if ScanType=="M":          channelLte[i]=[23790]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[23755, 23790, 23825]
                elif ScanType=="each": channelLte[i]=list(range(23755,23825+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[23780, 23790, 23800]
                elif ScanType=="each": channelLte[i]=[23780, 23790, 23800]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band17,please check")
        elif bandLte[i]=="OB18":
            if ScanType=="M":          channelLte[i]=[23925]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[23875, 23925, 23975]
                elif ScanType=="each": channelLte[i]=list(range(23875,23975+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[23900, 23925, 23950]
                elif ScanType=="each": channelLte[i]=[23900, 23950]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band18,please check")
        elif bandLte[i]=="OB19":
            if ScanType=="M":          channelLte[i]=[24075]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[24025, 24075, 24125]
                elif ScanType=="each": channelLte[i]=list(range(24025,24125+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[24050, 24075, 24100]
                elif ScanType=="each": channelLte[i]=[24050, 24100]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band19,please check")
        elif bandLte[i]=="OB20":
            if ScanType=="M":          channelLte[i]=[24300]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[24175, 24300, 24425]
                elif ScanType=="each": channelLte[i]=list(range(24175,24425+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[24200, 24300, 24400]
                elif ScanType=="each": channelLte[i]=list(range(24200,24400+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[24250, 24300, 24350]
                elif ScanType=="each": channelLte[i]=[24250, 24300, 24350]
        elif bandLte[i]=="OB25":
            if ScanType=="M":          channelLte[i]=[26365]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[26065, 26365, 26665]
                elif ScanType=="each": channelLte[i]=list(range(26065,26665+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[26090, 26365, 26640]
                elif ScanType=="each": channelLte[i]=list(range(26090,26640+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[26140, 26365, 26590]
                elif ScanType=="each": channelLte[i]=list(range(26140,26590+1,100))
        elif bandLte[i]=="OB26":
            if ScanType=="M":          channelLte[i]=[26865]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[26715, 26865, 27015]
                elif ScanType=="each": channelLte[i]=list(range(26715,27015+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[26740, 26865, 26990]
                elif ScanType=="each": channelLte[i]=list(range(26740,26990+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[26790, 26865, 26940]
                elif ScanType=="each": channelLte[i]=list(range(26790,26940+1,100))
        elif bandLte[i]=="OB28":
            if ScanType=="M":          channelLte[i]=[27435]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[27235, 27435, 27635]
                elif ScanType=="each": channelLte[i]=list(range(27235,27635+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[27260, 27435, 27610]
                elif ScanType=="each": channelLte[i]=list(range(27260,27610+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[27210, 27435, 27560]
                elif ScanType=="each": channelLte[i]=list(range(27210,27560+1,100))
        elif bandLte[i]=="OB30":
            if ScanType=="M":          channelLte[i]=[27710]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[27685, 27710, 27735]
                elif ScanType=="each": channelLte[i]=list(range(27685,27735+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[27710]
                elif ScanType=="each": channelLte[i]=[27710]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band30,please check")
        elif bandLte[i]=="OB66":
            if ScanType=="M":          channelLte[i]=[132322]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[131997,132022,132647]
                elif ScanType=="each": channelLte[i]=list(range(131997,132647+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[132022, 132322, 132622]
                elif ScanType=="each": channelLte[i]=list(range(132022,132622+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[132072, 132322, 132572]
                elif ScanType=="each": channelLte[i]=list(range(132072,132572+1,100))

        elif bandLte[i]=="OB34":
            if ScanType=="M":          channelLte[i]=[36275]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[36225, 36275, 36325]
                elif ScanType=="each": channelLte[i]=list(range(36225,36325+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[36250, 36275, 36300]
                elif ScanType=="each": channelLte[i]=[36250, 36275, 36300]
            elif LteBW=="B200":
                print("20MHz BW not supported in Band34,please check")
        elif bandLte[i]=="OB38":
            if ScanType=="M":          channelLte[i]=[38000]
            if LteBW=="B050":
                if ScanType=="LMH":    channelLte[i]=[37775, 38000, 38225]
                elif ScanType=="each": channelLte[i]=list(range(37775,38225+1,25))
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[37800, 38000, 38200]
                elif ScanType=="each": channelLte[i]=list(range(37800,38200+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[37850, 38000, 38150]
                elif ScanType=="each": channelLte[i]=list(range(37850,38150+1,100))
        elif bandLte[i]=="OB39":
            if ScanType=="M":          channelLte[i]=[38450]
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[38300, 38450, 38600]
                elif ScanType=="each": channelLte[i]=list(range(38300,38600+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[38350, 38450, 38550]
                elif ScanType=="each": channelLte[i]=[38350, 38450, 38550]
        elif bandLte[i]=="OB40":
            if ScanType=="M":          channelLte[i]=[39150]
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[38700, 39150, 39600]
                elif ScanType=="each": channelLte[i]=list(range(38700,39600+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[38750, 39150, 39550]
                elif ScanType=="each": channelLte[i]=list(range(38750,39550+1,100))
        elif bandLte[i]=="OB41":
            if ScanType=="M":          channelLte[i]=[40640]
            if LteBW=="B100":
                if ScanType=="LMH":    channelLte[i]=[40090, 40640, 41190]
                elif ScanType=="each": channelLte[i]=list(range(40090,41190+1,50))
            elif LteBW=="B200":
                if ScanType=="LMH":    channelLte[i]=[40140, 40640, 41140]
                elif ScanType=="each": channelLte[i]=list(range(40140,41140+1,100))
        else:
            print("LTE band %s not defined, please check Allfunctions file" %bandLte[i])
    return(channelLte)



#########################################################################################
#######  本函数读取LTE ULCA band列表，根据带宽和信道间隔设定返回channel列表                  #####
#########################################################################################
def channelLteCULCAList(bandLte_CULCA,LteBW,ScanType):
    channelLte_CULCA=[]
    for i in range(len(bandLte_CULCA)):
        channelLte_CULCA.append([])
        if LteBW != "B200":
            print("BandWidth not defined")
        else:
            if bandLte_CULCA[i]=="OB1":
                if ScanType=="M":      channelLte_CULCA[i]=[18300]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[18100, 18201, 18302]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(18100,18302+1,100))
            elif bandLte_CULCA[i]=="OB3":
                if ScanType=="M":      channelLte_CULCA[i]=[19476]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[19300, 19476, 19652]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(19300,19652+1,100))
            elif bandLte_CULCA[i]=="OB7":
                if ScanType=="M":      channelLte_CULCA[i]=[19476]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[20850, 21001, 21152]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(20850,21152+1,100))

            elif bandLte_CULCA[i]=="OB38":
                if ScanType=="M":      channelLte_CULCA[i]=[38000]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[37850, 37901, 37952]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(37850,37952+1,100))
            elif bandLte_CULCA[i]=="OB39":
                if ScanType=="M":      channelLte_CULCA[i]=[38350]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[38350, 38401, 38376]
                elif ScanType=="each": channelLte_CULCA[i]=[38350, 38450, 38550]
            elif bandLte_CULCA[i]=="OB40":
                if ScanType=="M":      channelLte_CULCA[i]=[39150]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[38750, 39051, 39352]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(38750,39352+1,100))
            elif bandLte_CULCA[i]=="OB41":
                if ScanType=="M":      channelLte_CULCA[i]=[40640]
                elif ScanType=="LMH":  channelLte_CULCA[i]=[40140, 40641, 40942]
                elif ScanType=="each": channelLte_CULCA[i]=list(range(40140,40942+1,100))
            else:
                print("LTE band %s not defined, please check Allfunctions file" %bandLte_CULCA[i])
    return(channelLte_CULCA)


#########################################################################################
#######  本函数读取3G(WCDMA、TD-SCDMA或CDMA2000）band列表，根据信道间隔设定返回channel列表           #####
#########################################################################################
def channel3GList(band3G,ScanType):
    channel3G=[]
    for i in range(len(band3G)):
        channel3G.append([])
        if band3G[i]=="OB1":
            if ScanType=="M":        channel3G[i]=[9750]
            elif ScanType=="LMH":    channel3G[i]=[9612, 9750, 9888]
            elif ScanType=="each":   channel3G[i]=list(range(9612,9888+1,25))
        elif band3G[i]=="OB2":
            if ScanType=="M":        channel3G[i]=[9400]
            elif ScanType=="LMH":    channel3G[i]=[9262, 9400, 9538]
            elif ScanType=="each":   channel3G[i]=list(range(9262,9538+1,25))
        elif band3G[i]=="OB3":
            if ScanType=="M":        channel3G[i]=[1112]
            elif ScanType=="LMH":    channel3G[i]=[937, 1112, 1288]
            elif ScanType=="each":   channel3G[i]=list(range(937,1288+1,25))
        elif band3G[i]=="OB4":
            if ScanType=="M":        channel3G[i]=[1587]
            elif ScanType=="LMH":    channel3G[i]=[1312, 1587, 1862]
            elif ScanType=="each":   channel3G[i]=list(range(1312,1862+1,25))
        elif band3G[i]=="OB5":
            if ScanType=="M":        channel3G[i]=[4182]
            elif ScanType=="LMH":    channel3G[i]=[4132, 4182, 4233]
            elif ScanType=="each":   channel3G[i]=list(range(4132,4233+1,25))
        elif band3G[i]=="OB6":
            if ScanType=="M":        channel3G[i]=[4175]
            elif ScanType=="LMH":    channel3G[i]=[4162, 4175, 4188]
            elif ScanType=="each":   channel3G[i]=list(range(4162,4188+1,25))
        elif band3G[i]=="OB8":
            if ScanType=="M":        channel3G[i]=[2787]
            elif ScanType=="LMH":    channel3G[i]=[2712, 2787, 2863]
            elif ScanType=="each":   channel3G[i]=list(range(2712,2863+1,25))
        elif band3G[i]=="OB9":
            if ScanType=="M":        channel3G[i]=[8837]
            elif ScanType=="LMH":    channel3G[i]=[8762, 8837, 8912]
            elif ScanType=="each":   channel3G[i]=list(range(8762,8912+1,25))
        elif band3G[i]=="OB19":
            if ScanType=="M":        channel3G[i]=[337]
            elif ScanType=="LMH":    channel3G[i]=[312, 337, 362]
            elif ScanType=="each":   channel3G[i]=list(range(312,362+1,25))

        ###########       以下是TD band     #############
        elif band3G[i]=="B1":
            if ScanType=="M":        channel3G[i]=[9500]
            elif ScanType=="LMH":    channel3G[i]=[9404, 9500, 9596]
            elif ScanType=="each":   channel3G[i]=list(range(9404,9596+1,8))
        elif band3G[i]=="B2":
            if ScanType=="M":        channel3G[i]=[10087]
            elif ScanType=="LMH":    channel3G[i]=[10054, 10087, 10121]
            elif ScanType=="each":   channel3G[i]=list(range(10054,10121+1,8))

        ###########       以下是CDMA2000 band     #############
        elif band3G[i]=="USC":       # BC0, US-Cellular, 同LTE band5
            if ScanType=="M":        channel3G[i]=[384]
            elif ScanType=="LMH":    channel3G[i]=[1013, 384, 777]
            elif ScanType=="each":   channel3G[i]=list(range(22,777+1,41))
        elif band3G[i]=="NAPC":      #BC1, North American PCS, 同LTE band2
            if ScanType=="M":        channel3G[i]=[600]
            elif ScanType=="LMH":    channel3G[i]=[25, 600,1175]
            elif ScanType=="each":   channel3G[i]=list(range(25,1175+1,41))
        else:
            print("3G band %s not defined, please check" %band3G[i])
    return(channel3G)

#########################################################################################
#######  本函数读取GSM band列表，根据信道间隔设定返回channel列表                            #####
#########################################################################################
def channelGSMList(bandGSM,ScanType):
    channelGSM=[]
    for i in range(len(bandGSM)):
        channelGSM.append([])
        if bandGSM[i]=="G085":
            if ScanType=="M":        channelGSM[i]=[192]
            elif ScanType=="LMH":    channelGSM[i]=[128, 192, 251]
            elif ScanType=="each":   channelGSM[i]=list(range(128,251+1,1))
        elif bandGSM[i]=="G09":
            if ScanType=="M":        channelGSM[i]=[62]
            elif ScanType=="LMH":    channelGSM[i]=[975, 62, 124]
            elif ScanType=="each":   channelGSM[i]=list(range(975,1023+1,1))+list(range(0,124+1,1))
        elif bandGSM[i]=="G18":
            if ScanType=="M":        channelGSM[i]=[698]
            elif ScanType=="LMH":    channelGSM[i]=[512, 698, 885]
            elif ScanType=="each":   channelGSM[i]=list(range(512,885+1,13))
        elif bandGSM[i]=="G19":
            if ScanType=="M":        channelGSM[i]=[661]
            elif ScanType=="LMH":    channelGSM[i]=[512, 661, 810]
            elif ScanType=="each":   channelGSM[i]=list(range(512,810+1,11))
        else:
            print("GSM band %s not defined, please check" %bandGSM[i])
    return(channelGSM)

