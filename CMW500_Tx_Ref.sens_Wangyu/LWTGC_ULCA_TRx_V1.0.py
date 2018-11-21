#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, os, visa, threading, time, string, numpy
from AllFunctionsV1 import *

#############################################################################################
##########     Designed by LvXiaolei, revised/updated by YanWeilin & WangYu   ###############
################     last update date: 2018-7-7                ############################
#############################################################################################

# 和仪表连接方式，请配置正确的IP地址或GPIB号。如果在默认地址找不到NI visa库，则需手工指定库地址
rm = visa.ResourceManager()
#rm = visa.ResourceManager('C:\windows\system32/visa32.dll')
rm.list_resources()
PM = rm.open_resource("GPIB0::20::INSTR")
#PM = rm.open_resource("TCPIP0::192.168.0.2::inst0::INSTR")
LogFile="ACLR_RefSens" + time.strftime('%Y%m%d',time.localtime(time.time())) + ".txt"
print(PMquery(PM,"*IDN?"))

######################### 测量项定制、通用参数定制。##############################################
LteFdd_measure=0               # 是否测量LTE FDD，1为enable，0为disable
LteTdd_measure=0               # 是否测量LTE FDD，1为enable，0为disable
LteFdd_CULCA_measure=0         # 是否测量LTE FDD连续CA，1为enable，0为disable。只测ULCA ACLR，不测灵敏度
LteTdd_CULCA_measure=1         # 是否测量LTE TDD连续CA，1为enable，0为disable。只测ULCA ACLR，不测灵敏度
WCDMA_measure=0                # 是否测量WCDMA制式 
TD_measure=0                   # 是否测量TD制式
GSM_measure=0                  # 是否测量GSM制式
CDMA_measure=0                 # 是否测量CDMA制式，目前只测量发射机参数。

##########        GSM call有多种发起方式，前4种需要插SIM卡。根据实际情况选择：          #########################
##########        mode=0为仪表端发起呼叫，手机端手动接听或设置自动接听，手机有SIM卡       #########################
##########        mode=1为手机发起呼叫，需人工拨号。手机有SIM卡                       #########################
##########        mode=2为手机发起呼叫，自动模拟鼠标点击QXDM-call start，需安装模拟鼠标的插件。手机有SIM卡       ####
##########        mode=3为手机发起呼叫，用adb shell下发命令，需插USB线。手机有SIM卡     #########################
##########        mode=4为手机发起强呼，需人工拨号。手机无SIM卡                       #########################
##########        mode=5为手机发起强呼，自动模拟鼠标点击QXDM-call start，需安装模拟鼠标的插件，手机无SIM卡       ####
##########        mode=6为手机发起强呼，用adb shell下发命令，需插USB线。手机无SIM卡    #########################

##########        CDMA call有2种发起方式（都需要插CDMA SIM卡）。根据实际情况选择：      #########################
##########        mode=0为仪表端发起呼叫，手机端接听                                 #########################
##########        mode=1为手机发起呼叫，需人工拨号。                                 #########################
##########        mode=2为手机发起呼叫，自动模拟鼠标点击QXDM-call start，需安装模拟鼠标的插件。      ###############
GSMcall_mode=1             # 决定从哪一端发起GSM呼叫。见上面说明。
GSMAttachWaitTime=10       # 有SIM卡时，等待手机attach的最长时间，单位是秒
CDMAcall_mode=1            # 决定从哪一端发起CDMA呼叫。见上面说明。
Rx_measure=0               # Rx测量项总开关，是否测量各个制式的Rx灵敏度。不测ULCA和CDMA的灵敏度
Fdd_Max_Min_mearsure=0     # 在各FDD制式下，是否连续测量最大/最小功率下的灵敏度。为0则只测当前功率下的灵敏度

UEPwrCtrl="MAXPower"       # MAXPower, MINPower, CLOop分别代表手机功控为最大/最小/内环，适用于所有制式
CLTPower=22                # closed loop target power闭环功控的目标功率，单位是dBm。对所有制式适用。
RF_output="RF1C"           # 仪表的Tx通道，可设置为RF1C、RF1O、RF2C或RF2O。C=Common，O=Output。测分集时一般设为RF1O
RF_input="RF1C"            # 仪表的Rx通道，可设置为RF1C或RF2C。一般不用改。
ScanType="LMH"             # 信道扫描类型，可设置为中信道（“M”）或低中高信道（"LMH"）或逐个信道（"each"）

LteBW="B100"               # B014 B050 B100 B200分别代表LTE带宽为1.4/5/10/20MHz。目前只支持5/10/20MHz选项
Lte_DlRB="N50"             # ZERO N1 N12 N20 N25 N50 N100分别代表下行LTE 0/1/12/20/25/50/100个RB
Lte_UlRB="N12"             # ZERO N1 N12 N20 N25 N50 N100分别代表上行LTE 0/1/12/20/25/50/100个RB
ULpartialRB=0              # 为1时，接收机测试时b5、8、20等窄频段按照3GPP要求，设置上行为20/25个partial RB。为0则都按Lte_UL/DLRB设置。
         ###### ULpartialRB仅对接收机测试有影响。发射机测试时一直保持用Lte_UlRB的设置。  #########
LteDlModType="QPSK"        # QPSK, Q16, Q64,Q256分别代表LTE下行调制方式为QPSK，16QAM或64QAM
LteUlModType="QPSK"        # QPSK, Q16, Q64分别代表LTE上行调制方式为QPSK，16QAM或64QAM

LteBW_CULCA="B200"         # 上行连续CA的带宽。目前只支持20MHz选项。对于B39，SCC设为15MHz
UlRB_CULCA="N100"          # 上行连续CA的下行RB设置
DlRB_CULCA="N100"          # 建立连接时，上行连续CA的下行RB设置
DlRB_CULCA_measure='ZERO'  # 测量ACLR时，上行连续CA的下行RB设置。按照惯例需设为ZERO
CULCA_SCChigher=1          # 为1则SCC比PCC高198channel。为0则SCC channel低于PCC


######################### Band definition   ##############################################
bandLteFdd = ["OB1", "OB2", "OB3", "OB4", "OB5", "OB7", "OB8", "OB20", "OB28"]   #D2T频段
bandLteFdd = ["OB1", "OB3", "OB5", "OB7", "OB8"]                                 #D2T国际版频段
bandLteFdd = ["OB1", "OB3", "OB5", "OB7", "OB8", "OB20"]                         #E10国际版频段
bandLteFdd = ["OB1", "OB3", "OB4", "OB5", "OB7", "OB8", "OB20"]                  #E4频段
bandLteFdd = ["OB1", "OB3", "OB4", "OB7", "OB20"]                  #E4频段
bandLteFdd = ["OB1", "OB2", "OB3", "OB4", "OB5", "OB7", "OB8", "OB20", "OB28"]   #F2频段

bandLteTdd = ["OB38", "OB39", "OB40", "OB41", "OB34"] 
bandLteTdd = ["OB38", "OB40"] 

bandLteFdd_CULCA = ["OB3", "OB7"]
bandLteTdd_CULCA = ["OB38", "OB40", "OB41", "OB39"]

bandWCDMA = ["OB1", "OB2", "OB4", "OB5", "OB8"]
bandWCDMA = ["OB4", "OB5", "OB8"]
bandWCDMA = ["OB1", "OB2"]

bandTDS = ["B1", "B2"]  #Pyvisa里用B1表示TD B39， B2表示TD B34

bandGSM = ["G085", "G09", "G18", "G19"]
bandGSM = ["G09", "G18"]

bandCDMA = ["USC", "NAPC"]   #Pyvisa里用USC表示CDMA BC0， NAPC表示CDMA BC1

RepeatFlag=0
if RepeatFlag==1:
    bandtemp = []
    for temp in range(10):
        bandtemp += bandLteFdd               #把一个序列复制n遍以做老化测试。
        #bandGSM.extend(bandGSM)          #把一个序列复制2^n遍以做老化测试。注意n值不要太大。
    bandLteFdd=bandtemp
    print(bandLteFdd)

######################### Reference Sensitivity seek parameters definition   ############################
CoarseStepLte=0.8
FineStepLte=0.2
UpperLimitLte=-123

CoarseStepWCDMA=0.8
FineStepWCDMA=0.2
UpperLimitWCDMA=-109

CoarseStepTDS=0.8
FineStepTDS=0.2
UpperLimitTDS=-108

CoarseStepGSM=0.8
FineStepGSM=0.2
UpperLimitGSM=-106

########################################################################################
##### ^^^^^^^^^^  以上是参数定义部分，可根据实际情况修改。   ^^^^^^^^^^^^^^^^^^^           #####
#####                                                                              #####
#####             以下程序主体部分，一般不修改                                           #####
########################################################################################

if ((GSM_measure==1 and GSMcall_mode in [2, 5]) or (CDMA_measure==1 and CDMAcall_mode == 2)):
    from pymouse import PyMouse
    mouse = PyMouse()
    #####   获取QXDM——call manager——infinite call——start控件的位置   #####################
    #############      防止中途掉话。GSM测试过程中请不要操作鼠标和键盘    ######################
    input("Move mouse to QXDM——call manager——infinite call——‘start’ then press Enter" )
    (CallStartX,CallStartY)=mouse.position()      #获取当前坐标的位置
    print(CallStartX,CallStartY)
else:
    mouse=0
    CallStartX=0
    CallStartY=0

######################### Main function   ##############################################
def main():
    PMwrite(PM,"*RST;*OPC?")
    PMwrite(PM,"*CLS;*OPC?")
    time.sleep(2)
    # 配置线损
    lossName = PMqueryWithDelay(PM,"CONFigure:BASE:FDCorrection:CTABle:CATalog?")
    if lossName.find ("CMW_loss") != -1:
        PMwrite(PM,"CONFigure:BASE:FDCorrection:CTABle:DELete 'CMW_loss'")
    PMwrite(PM,"CONFigure:BASE:FDCorrection:CTABle:CREate 'CMW_loss', 1920000000, 0.8, 1980000000, 0.8, \
        2110000000, 0.8, 2170000000, 0.8, 1850000000, 0.8, 1910000000, 0.8, 1930000000, 0.8, 1990000000, 0.8,\
        824000000, 0.5, 849000000, 0.5, 869000000, 0.5, 894000000, 0.5, 925000000, 0.5, 960000000, 0.5, \
        880000000, 0.5, 915000000, 0.5, 2350000000, 0.9, 2535000000, 0.9, 2593000000, 0.9")
    PMwrite(PM,"CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF1")  #配置RF1 Common口的Tx Rx方向损耗
    PMwrite(PM,"CONFigure:FDCorrection:ACTivate RF1O, 'CMW_loss', TX, RF1")    #配置RF1 OUT口的Tx方向损耗
    TimeStart=time.clock()
    LogfileWrite(LogFile, "\n*******        Test start        *******\n")
    
############################    LTE ACLR & Rx_Sens.lev test ##################################################
    if (LteFdd_measure==1 or LteTdd_measure==1):
        os.popen ("adb reboot")
        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
        channelLteFdd=channelLteList(bandLteFdd,LteBW,ScanType)
        channelLteTdd=channelLteList(bandLteTdd,LteBW,ScanType)
        if LteFdd_measure==1 and LteTdd_measure==1:
            bandLte=bandLteFdd+bandLteTdd
            channelLte=channelLteFdd+channelLteTdd
        elif LteFdd_measure==1 and LteTdd_measure==0:
            bandLte=bandLteFdd
            channelLte=channelLteFdd
        elif LteFdd_measure==0 and LteTdd_measure==1:
            bandLte=bandLteTdd
            channelLte=channelLteTdd

        PMwrite(PM,"ROUTe:LTE:MEAS:SCENario:CSPath 'LTE Sig1'")
        if LteFdd_measure==1:
            PMwrite(PM,"CONFigure:LTE:SIGN:DMODe FDD")
        else:
            PMwrite(PM,"CONFigure:LTE:SIGN:DMODe TDD")
        PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLte[0])
        PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:CHANnel:UL %d" %channelLte[0][0])
        if RF_output=="RF1C":
            PMwrite(PM,"ROUTe:LTE:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        elif RF_output=="RF1O":
            PMwrite(PM,"ROUTe:LTE:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")#设置仪表初始功率，高一些以更快注册
        PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:MSUBframes 0, 10, 2")
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:CLTPower %s" %CLTPower)         #设置内环功控的目标功率
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET %s" %UEPwrCtrl)             #设置手机发射功率为最大/最小/内环
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PMAX 30")
        PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
        PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL %s" %LteBW)              #设置仪表下行带宽
        time.sleep(2)
        if LteBW=="B100":
            print("LTE bandwidth is 10MHz")
        elif LteBW=="B200":
            print("LTE bandwidth is 20MHz")
        elif LteBW=="B050":
            print("LTE bandwidth is 5MHz")

        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(Lte_DlRB, LteDlModType))#设置仪表下行RB数和调制方式
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:DL LOW") #设置partial RB的位置。对于b20，此项设置单独处理。
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:RBPosition:UL HIGH")
        PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:REPetition SINGleshot")                   #设置BLER测量的模式为单次
        PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:SCONdition NONE")                         #设置BLER测量的停止条件为无
        PMwrite(PM,"CONFigure:LTE:SIGN:EBLer:SFRames 400")                             #设置BLER测量的frame数量

        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
        while PMquery(PM,"SOURce:LTE:SIGN:CELL:STATe:ALL?").strip()!="ON,ADJ":
            time.sleep(2)
        # 尝试建立callbox和手机连接
        #os.system("pause")
        while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
            PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
            time.sleep(5)
        print("LTE connect established!")
        PMwrite(PM,"CONFigure:LTE:SIGN:UEReport:ENABle ON")
        print("band channel  txpwr  UTRA2  UTRA1  E-UTRA1 E-UTRA1 UTRA1  UTRA2  RS_EPRE BLER RSRP RSRQ")
        LogfileWrite(LogFile, "band channel  txpwr  UTRA2  UTRA1  E-UTRA1 E-UTRA1 UTRA1  UTRA2  FCPower BLER RSepre RSRP   RSRQ\n")

        for i in range(len(bandLte)):
            if LteFdd_measure==1 and i==len(bandLteFdd):  #Fdd到Tdd切换时：
                os.popen ("adb reboot")
                PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
                PMwrite(PM,"CONFigure:LTE:SIGN:DMODe TDD")
                PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLteTdd[0])
                PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")
                PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
                while PMquery(PM,"SOURce:LTE:SIGN:CELL:STATe:ALL?").strip()!="ON,ADJ":
                    time.sleep(1)
                while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
                    PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
                    time.sleep(1)
            else:
                PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLte[i])
                time.sleep(2)            
                
            if bandLte[i] in ["OB20", "OB13"]:
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:DL HIGH")
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:RBPosition:UL LOW")
            else:
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:DL LOW")
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:RBPosition:UL HIGH")
            if UEPwrCtrl == "MINPower":
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:ENPMode MANual")
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:ENPower -20")

            for j in range(len(channelLte[i])):
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:CHANnel:UL %d" %channelLte[i][j])
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL %s,%s,KEEP" %(Lte_UlRB, LteUlModType))
                   # 发射机测试总是用Full RB测试。ULpartialRB=1时，接收机测试的RB数按照3GPP36.521，Table7.3.3-2执行
                time.sleep(3)
                PMwrite(PM,"ABORt:LTE:SIGN:EBLer") #在20MHz BW下，测完Rx需设置BLER OFF，否则后续的ACLR测量出错
                PMwrite(PM,"ABORt:LTE:MEAS:MEValuation")
                time.sleep(2)
                while 1:
                    try:
                        LteAclr = PMqueryWithDelay(PM,"READ:LTE:MEAS:MEValuation:ACLR:AVERage?")
                        listLteAclr = list(map(float,LteAclr.split(',')))
                        break
                    except Exception:
                        print("read LteAclr error")
                        os.popen ("adb reboot")
                        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
                        time.sleep(2)
                        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
                        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")
                        while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
                            PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
                            time.sleep(5)
                        PMwrite(PM,"ABORt:LTE:MEAS:MEValuation")
                        time.sleep(1)
                print("%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f" \
                       %(bandLte[i], channelLte[i][j],listLteAclr[4],listLteAclr[1],listLteAclr[2],\
                         listLteAclr[3],listLteAclr[5],listLteAclr[6],listLteAclr[7]))
    
                if Rx_measure==1:
                    if ULpartialRB==1:     #ULpartialRB=1时，接收机测试的RB数按照3GPP36.521，Table7.3.3-2执行
                        if (LteBW == "B100"):
                            if (bandLte[i] in ["OB5", "OB8", "OB18", "OB19", "OB26", "OB27", "OB28", "OB30"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N25,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB12", "OB13", "OB17", "OB20"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N20,%s,KEEP" %LteUlModType)
                        elif (LteBW == "B050"):
                            if (bandLte[i] in ["OB12", "OB13", "OB17"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N20,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB14"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N15,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB31"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N5,%s,KEEP" %LteUlModType)
                        elif (LteBW == "B150"):
                            if (bandLte[i] in ["OB2", "OB3", "OB9", "OB22", "OB25"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N50,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB18", "OB19", "OB21", "OB26", "OB28"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N25,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB20"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N20,%s,KEEP" %LteUlModType)
                                os.system("pause")
                        elif (LteBW == "B200"):
                            if (bandLte[i] in ["OB2", "OB3", "OB9", "OB22", "OB25"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N50,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB7"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N75,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB28"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N25,%s,KEEP" %LteUlModType)
                            elif (bandLte[i] in ["OB20"]):
                                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:RMC:UL N20,%s,KEEP" %LteUlModType)
                                os.system("pause")
                            

                    (RSepre,LteFCPwr,LteBler,RSRP,RSRQ)=SeekLteSens(PM,UpperLimitLte,CoarseStepLte,FineStepLte,20)
                    if (Fdd_Max_Min_mearsure==1 and (bandLte[i] in bandLteFdd)):
                        if UEPwrCtrl=="MAXPower":
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MINPower")
                            (RSepre_2nd,LteFCPwr_2nd,LteBler_2nd,RSRP_2nd,RSRQ_2nd)=SeekLteSens(PM,UpperLimitLte,CoarseStepLte,FineStepLte,2)
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
                        if UEPwrCtrl=="MINPower":
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
                            (RSepre_2nd,LteFCPwr_2nd,LteBler_2nd,RSRP_2nd,RSRQ_2nd)=SeekLteSens(PM,UpperLimitLte,CoarseStepLte,FineStepLte,2)
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MINPower")
                        if UEPwrCtrl=="CLOop":
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
                            (RSepre_2nd,LteFCPwr_2nd,LteBler_2nd,RSRP_2nd,RSRQ_2nd)=SeekLteSens(PM,UpperLimitLte,CoarseStepLte,FineStepLte,2)
                            PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET CLOop")
                        LogfileWrite(LogFile, "%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f  %3.1f   %3.1f  \
%3.2f %3.1f %3.1f  %3.1f   %3.2f  %3.1f %3.1f %3.1f\n" %(bandLte[i], channelLte[i][j], listLteAclr[4],listLteAclr[1], \
                            listLteAclr[2],listLteAclr[3], listLteAclr[5], listLteAclr[6],listLteAclr[7], LteFCPwr,\
                            LteBler, RSepre, RSRP, RSRQ, LteFCPwr_2nd, LteBler_2nd,RSepre_2nd, RSRP_2nd, RSRQ_2nd))
                    else:
                        LogfileWrite(LogFile, "%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f  %3.1f   %3.2f %3.1f %3.1f %3.1f\n" \
                                 %(bandLte[i], channelLte[i][j], listLteAclr[4],listLteAclr[1], listLteAclr[2],listLteAclr[3],\
                                   listLteAclr[5], listLteAclr[6],listLteAclr[7],LteFCPwr,LteBler, RSepre, RSRP, RSRQ))
                    PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")
                        
                else:
                    LogfileWrite(LogFile, "%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f\n" \
                                 %(bandLte[i], channelLte[i][j], listLteAclr[4],listLteAclr[1], listLteAclr[2],\
                                   listLteAclr[3],listLteAclr[5], listLteAclr[6],listLteAclr[7]))
            if UEPwrCtrl == "MINPower":
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:ENPMode ULPC")

        PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion DISConnect")
        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
        print("-------------------LTE test finished ....----------------")

############################    LTE Contiguous ULCA ACLR test ##################################################
    if (LteFdd_CULCA_measure==1 or LteTdd_CULCA_measure==1):
        os.popen ("adb reboot")
        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
        channelLteFdd_CULCA=channelLteCULCAList(bandLteFdd_CULCA,LteBW_CULCA,ScanType)
        channelLteTdd_CULCA=channelLteCULCAList(bandLteTdd_CULCA,LteBW_CULCA,ScanType)
        PMwrite(PM,"ROUTe:LTE:MEAS:SCENario:CSPath 'LTE Sig1'")
        PMwrite(PM,"ROUTe:LTE:SIGN:SCENario:CATRfout:FLEXible SUW1,RF1C,RX1,RF1C,TX1,SUW2,RF1C,TX3")
        PMwrite(PM,"CONFigure:LTE:SIGN:SCC:UUL ON,RF1C,RX3")
        PMwrite(PM,"CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF3")
        time.sleep(3)

        if (LteFdd_CULCA_measure==1 and LteTdd_CULCA_measure==1):
            bandLte_CULCA = bandLteFdd_CULCA + bandLteTdd_CULCA
            channelLte_CULCA = channelLteFdd_CULCA + channelLteTdd_CULCA
        elif (LteFdd_CULCA_measure==1 and LteTdd_CULCA_measure==0):
            bandLte_CULCA=bandLteFdd_CULCA
            channelLte_CULCA=channelLteFdd_CULCA
        elif (LteFdd_CULCA_measure==0 and LteTdd_CULCA_measure==1):
            bandLte_CULCA=bandLteTdd_CULCA
            channelLte_CULCA=channelLteTdd_CULCA

        if PMquery(PM,"ROUTe:LTE:SIGN:SCENario?") != 'CATR\n':
            os.system("pause")
        PMwrite(PM,"CONFigure:LTE:SIGN:DMODe:UCSPecific OFF")
        if LteFdd_CULCA_measure==1:
            PMwrite(PM,"CONFigure:LTE:SIGN:DMODe FDD")
        else:
            PMwrite(PM,"CONFigure:LTE:SIGN:DMODe TDD")
        PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLte_CULCA[0])
        PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL %d" %channelLte_CULCA[0][0])
        PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL %s" %LteBW_CULCA)              #设置仪表下行带宽

        PMwrite(PM,"CONFigure:LTE:SIGN:SCC:AMODe AUTO")   # 建立RRC连接时，SCC自动激活到“MAC Activated”状态
        PMwrite(PM,"CONFigure:LTE:SIGN:SCC:UUL ON,RF1C,RX3")
        PMwrite(PM,"CONFigure:LTE:SIGN:SCC:BAND %s" %bandLte_CULCA[0])
        if CULCA_SCChigher ==1:
            PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:SCC:CHANnel:UL %d" %(channelLte_CULCA[0][0]+198))
        else:
            PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:SCC:CHANnel:UL %d" %(channelLte_CULCA[0][0]-198))
        PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:SCC:DL %s" %LteBW_CULCA)
        PMwrite(PM,"CONFigure:LTE:SIGN:SCC:CAGGregation:MODE INTRaband")
        PMwrite(PM,"LTE Sig1:FrameTrigger SCC1")
        time.sleep(2)
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))#设置仪表下行RB数和调制方式
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:UL %s,%s,KEEP" %(UlRB_CULCA, LteUlModType))
        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:UL %s,%s,KEEP" %(UlRB_CULCA, LteUlModType))
        PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80") #设置仪表初始功率，高一些以更快注册
        PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:MSUBframes 0, 10, 2")
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:CLTPower %s" %CLTPower)         #设置内环功控的目标功率
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET %s" %UEPwrCtrl)             #设置手机发射功率为最大/最小/内环
        PMwrite(PM,"CONFigure:LTE:SIGN:UL:PMAX 24")
        PMwrite(PM,"CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")

        PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
        while PMquery(PM,"SOURce:LTE:SIGN:CELL:STATe:ALL?").strip()!="ON,ADJ":
            time.sleep(1)
        # 尝试建立callbox和手机连接
        while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
            PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
            time.sleep(4)
        print("connect established!")
        #PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:SEXecute")
        PMwrite(PM,"CONFigure:LTE:SIGN:UEReport:ENABle OFF")
        print("band channel  txpwr  UTRA2  UTRA1  E-UTRA1 E-UTRA1 UTRA1  UTRA2  RS_EPRE RSRP RSRQ")
        LogfileWrite(LogFile, "band channel  txpwr  UTRA2  UTRA1  E-UTRA1 E-UTRA1 UTRA1  UTRA2 RSRP   RSRQ\n")

        for i in range(len(bandLte_CULCA)):
            PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
            PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
            if LteFdd_CULCA_measure==1 and i==len(bandLteFdd_CULCA):  #Fdd到Tdd切换时：
                os.popen ("adb reboot")
                PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
                PMwrite(PM,"CONFigure:LTE:SIGN:DMODe TDD")
                PMwrite(PM,"CONFigure:LTE:SIGN:SCC:CAGGregation:MODE OFF")
                PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLteTdd_CULCA[0])
                PMwrite(PM,"CONFigure:LTE:SIGN:SCC:BAND %s" %bandLteTdd_CULCA[0])
                PMwrite(PM,"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")
                PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe ON")
                while PMquery(PM,"SOURce:LTE:SIGN:CELL:STATe:ALL?").strip()!="ON,ADJ":
                    time.sleep(1)
                while PMquery(PM,"FETCh:LTE:SIGN:PSWitched:STATe?") != 'CEST\n':
                    PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion CONNect")
                    time.sleep(1)
            else:
                PMwrite(PM,"CONFigure:LTE:SIGN:PCC:BAND %s" %bandLte_CULCA[i])
                PMwrite(PM,"CONFigure:LTE:SIGN:SCC:BAND %s" %bandLte_CULCA[i])
                time.sleep(2)
                
            if UEPwrCtrl == "MINPower":
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:ENPMode MANual")
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:ENPower -20")
            PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL %s" %LteBW_CULCA)    
            PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:SCC:DL %s" %LteBW_CULCA)
            for j in range(len(channelLte_CULCA[i])):
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
                if bandLte_CULCA[i] == "OB39":
                    PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL N75,%s,KEEP" %LteDlModType)
                else:
                    PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
                    
                time.sleep(1)
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL %d" %channelLte_CULCA[i][j])
                PMwrite(PM,"CONFigure:LTE:SIGN:SCC:CAGGregation:MODE OFF")
                if CULCA_SCChigher ==1:
                    PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
                    if bandLte_CULCA[i] == "OB39":       #对于B39做特殊处理
                        PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:SCC:DL B150")
                        PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:SCC:CHANnel:UL %d" %(channelLte_CULCA[i][j]+171))
                        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL N75,%s,KEEP" %LteDlModType)
                    else:
                        PMwrite(PM,"CONFigure:LTE:SIGN:CELL:BANDwidth:SCC:DL %s" %LteBW_CULCA)
                        PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:SCC:CHANnel:UL %d" %(channelLte_CULCA[i][j]+198))
                        PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA, LteDlModType))
                else:
                    PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:SCC:CHANnel:UL %d" %(channelLte_CULCA[i][j]-198))
                PMwrite(PM,"CONFigure:LTE:SIGN:SCC:CAGGregation:MODE INTRaband")
                time.sleep(1)
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:PCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA_measure, LteDlModType))
                PMwrite(PM,"CONFigure:LTE:SIGN:CONNection:SCC:RMC:DL %s,%s,KEEP" %(DlRB_CULCA_measure, LteDlModType))
                PMwrite(PM,"ABORt:LTE:SIGN:EBLer") #在20MHz BW下，测完Rx需设置BLER OFF，否则后续的ACLR测量出错
                PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MINPower")
                time.sleep(0.2)
                PMwrite(PM,"CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET %s" %UEPwrCtrl) #两次设置TPC。否则可能overdriven
                PMwrite(PM,"ABORt:LTE:MEAS:MEValuation")
                time.sleep(1)
                while 1:
                    try:
                        LteAclr = PMqueryWithDelay(PM,"READ:LTE:MEAS:MEValuation:ACLR:AVERage?")
                        listLteAclr = list(map(float,LteAclr.split(',')))
                        break
                    except Exception:
                        print("read LteAclr error")
                        os.system("pause")
                        PMwrite(PM,"ABORt:LTE:MEAS:MEValuation")
                        time.sleep(1)
                print("%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f" \
                       %(bandLte_CULCA[i], channelLte_CULCA[i][j],listLteAclr[4],listLteAclr[1],listLteAclr[2],\
                         listLteAclr[3],listLteAclr[5],listLteAclr[6],listLteAclr[7]))
                LogfileWrite(LogFile, "%-4s  %d   %3.2f  %3.2f  %3.2f  %3.2f   %3.2f   %3.2f  %3.2f\n" \
                        %(bandLte_CULCA[i], channelLte_CULCA[i][j], listLteAclr[4],listLteAclr[1], listLteAclr[2],\
                        listLteAclr[3],listLteAclr[5], listLteAclr[6],listLteAclr[7]))
            if UEPwrCtrl == "MINPower":
                PMwrite(PM,"CONFigure:LTE:SIGN:RFSettings:PCC:ENPMode ULPC")

        #PMwrite(PM,"CALL:LTE:SIGN:PSWitched:ACTion DISConnect")
        #PMwrite(PM,"SOURce:LTE:SIGN:CELL:STATe OFF")
        print("-------------------LTE contiguous ULCA ACLR test finished ....----------------")

#############################    WCDMA ACLR & Rx_Sens.lev test ###########################################
    if WCDMA_measure==1:
        os.popen ("adb reboot")  #重启手机便于自动注册
        print("-------------------WCDMA test start...-------------------")
        PMwrite(PM,"CALL:WCDMa:SIGN:CSWitched:ACTion DISConnect")
        PMwrite(PM,"CALL:WCDMa:SIGN:PSWitched:ACTion DISConnect")
        PMwrite(PM,"SOURce:WCDMa:SIGN:CELL:STATe OFF")
        channelWCDMA=channel3GList(bandWCDMA,ScanType)

        # 设置参数
        PMwrite(PM,"ROUTe:WCDMa:MEAS:SCENario:CSPath 'WCDMA Sig1'")
        PMwrite(PM,"CONFigure:WCDMa:SIGN:CARRier:BAND %s" %bandWCDMA[0])
        PMwrite(PM,"CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL %d" %channelWCDMA[0][0])
        PMwrite(PM,"CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:TMODe MODE1")
        PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 10")
        PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:SCOunt:SPECtrum 10")
        PMwrite(PM,"CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
        PMwrite(PM,"SOURce:WCDMa:SIGN:CELL:STATe ON")
        time.sleep(4)
        
        while PMquery(PM,"SOURce:WCDMa:SIGN:CELL:STATe:ALL?")!='ON,ADJ\n':
            time.sleep(1)
        while PMquery(PM,"FETCh:WCDMa:SIGN:PSWitched:STATe?")!='ATT\n':
            time.sleep(1)
        # 建立callbox和手机连接。CEST=Call ESTablished
        while PMquery(PM,"FETCh:WCDMa:SIGN:CSWitched:STATe?") != 'CEST\n':
            PMwrite(PM,"CALL:WCDMa:SIGN:CSWitched:ACTion CONNect")
            time.sleep(4)
        print("WCDMA connect established!")
        
        if UEPwrCtrl=="MAXPower":
            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        elif UEPwrCtrl=="MINPower":
            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL0")
        elif UEPwrCtrl=="CLOop":
            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET CLOop")
            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:TPOWer:REFerence TOTal")
            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:TPOWer %s" %CLTPower)
        PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PRECondition")
        PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PEXecute")
        time.sleep(1)
        print("band  channel  UEpwr  ChPwr  AltCLR  AdjCLR  AdjCLR  AltCLR  RefSens  BER")
        LogfileWrite(LogFile, "band  channel  UEpwr  ChPwr  AltCLR  AdjCLR  AdjCLR  AltCLR  RefSens  BER\n")
        
        for i in range (len(bandWCDMA)):
            PMwrite(PM,"CONFigure:WCDMa:SIGN:CARRier:BAND %s" %bandWCDMA[i])
            time.sleep(3)
            for j in range(len(channelWCDMA[i])):
                PMwrite(PM,"CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL %d" %channelWCDMA[i][j])
                time.sleep(3)
                if RF_output=="RF1O":
                    PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                PMwrite(PM,"ABORt:WCDMa:MEAS:MEValuation")
                time.sleep(1)
                WAclr = PMqueryWithDelay(PM,"READ:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?").split(',')
                while WAclr[15] in ["INV", "NAV", "NCAP"]:
                    print("TxPwr=NULL, maybe call lost. Please wait for reconnect")
                    os.popen ("adb reboot")
                    #os.system("pause")
                    PMwrite(PM,"SOURce:WCDMa:SIGN:CELL:STATe OFF")
                    time.sleep(2)
                    PMwrite(PM,"SOURce:WCDMa:SIGN:CELL:STATe ON")
                    time.sleep(3)
                    PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
                    while PMquery(PM,"FETCh:WCDMa:SIGN:PSWitched:STATe?")!='ATT\n':
                        time.sleep(1)
                    while PMquery(PM,"FETCh:WCDMa:SIGN:CSWitched:STATe?") != 'CEST\n':
                        PMwrite(PM,"CALL:WCDMa:SIGN:CSWitched:ACTion CONNect")
                        time.sleep(4)
                    if RF_output=="RF1O":
                        PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                    PMwrite(PM,"ABORt:WCDMa:MEAS:MEValuation")
                    WAclr = PMqueryWithDelay(PM,"READ:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?").split(',')
                UEPwr = float(WAclr[15])
                ChPwr = float(WAclr[1])
                print("%-4s  %d     %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f" %(bandWCDMA[i], channelWCDMA[i][j],\
                          UEPwr, ChPwr, float(WAclr[2])-ChPwr,float(WAclr[3])-ChPwr, \
                          float(WAclr[4])-ChPwr, float(WAclr[5])-ChPwr))
                if Rx_measure==1:
                    PMwrite(PM,"CONFigure:WCDMa:SIGN:BER:TBLocks 100")
                    (WRefSens,WBer)=SeekW_TD_Sens(PM,"WCDMa",RF_output,UpperLimitWCDMA,CoarseStepWCDMA,FineStepWCDMA)
                    if (Fdd_Max_Min_mearsure==1):
                        if UEPwrCtrl=="MAXPower":
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL0")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PRECondition")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PEXecute")
                            (WRefSens_2nd,WBer_2nd)=SeekW_TD_Sens(PM,"WCDMa",RF_output,UpperLimitWCDMA,CoarseStepWCDMA,FineStepWCDMA)
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
                        if UEPwrCtrl=="MINPower":
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PRECondition")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PEXecute")
                            (WRefSens_2nd,WBer_2nd)=SeekW_TD_Sens(PM,"WCDMa",RF_output,UpperLimitWCDMA,CoarseStepWCDMA,FineStepWCDMA)
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL0")
                        if UEPwrCtrl=="CLOop":
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PRECondition")
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PEXecute")
                            (WRefSens_2nd,WBer_2nd)=SeekW_TD_Sens(PM,"WCDMa",RF_output,UpperLimitWCDMA,CoarseStepWCDMA,FineStepWCDMA)
                            PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:SET CLOop")
                        PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PRECondition")
                        PMwrite(PM,"CONFigure:WCDMa:SIGN:UL:TPC:PEXecute")
                        LogfileWrite(LogFile, "%-4s  %d     %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f\n" \
                            %(bandWCDMA[i], channelWCDMA[i][j],UEPwr, ChPwr, float(WAclr[2])-ChPwr,\
                            float(WAclr[3])-ChPwr, float(WAclr[4])-ChPwr, float(WAclr[5])-ChPwr,\
                            WRefSens,WBer,WRefSens_2nd,WBer_2nd))
                    else:
                        LogfileWrite(LogFile, "%-4s  %d     %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f\n" \
                            %(bandWCDMA[i], channelWCDMA[i][j],UEPwr, ChPwr, float(WAclr[2])-ChPwr,\
                            float(WAclr[3])-ChPwr, float(WAclr[4])-ChPwr, float(WAclr[5])-ChPwr,WRefSens,WBer))

                else:
                    LogfileWrite(LogFile, "%-4s  %d     %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f\n"\
                            %(bandWCDMA[i],channelWCDMA[i][j], UEPwr, ChPwr, float(WAclr[2])-ChPwr,\
                            float(WAclr[3])-ChPwr,float(WAclr[4])-ChPwr, float(WAclr[5])-ChPwr))
                PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        PMwrite(PM,"CALL:WCDMa:SIGN:CSWitched:ACTion DISConnect")
        PMwrite(PM,"CALL:WCDMa:SIGN:PSWitched:ACTion DISConnect")
        PMwrite(PM,"SOURce:WCDMa:SIGN:CELL:STATe OFF")
        print("-------------------WCDMA ACLR test end-------------------")
    
#############################    TD-SCDMA ACLR & Rx_Sens.lev test ###########################################
    if TD_measure==1:
        os.popen ("adb reboot")  #重启手机便于自动注册
        print("-------------------TDSCDMA test start...-----------------")
        PMwrite(PM,"SOURce:TDSCdma:SIGN:CELL:STATe OFF")
        channelTDS=channel3GList(bandTDS,ScanType)

        # 设置参数
        PMwrite(PM,"ROUTe:TDSCdma:MEAS:SCENario:CSPath 'TD-SCDMA Sig1'")
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:RFSettings:BAND %s" %bandTDS[0])
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:RFSettings:CHANnel %d" %channelTDS[0][0])
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:CONNection:TMODe:RMC:TMODe MODE1")  #设置test mode为loop mode1
        PMwrite(PM,"ROUTe:TDSCdma:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        PMwrite(PM,"CONFigure:TDSCdma:MEAS:MEValuation:REPetition SINGleshot")
        PMwrite(PM,"CONF:TDSC:MEAS:MEV:SCO:MOD 10")
        PMwrite(PM,"CONF:TDSC:MEAS:MEV:SCO:SPEC 10")
        PMwrite(PM,"SOURce:TDSCdma:SIGN:CELL:STATe ON")
        time.sleep(4)

        while PMquery(PM,"SOURce:TDSCdma:SIGN:CELL:STATe:ALL?")!='ON,ADJ\n':
            time.sleep(1)
        while PMquery(PM,"FETCh:TDSCdma:SIGN:PSWitched:STATe?")!='ATT\n':
            time.sleep(1)
        # 建立callbox和手机连接。CEST=Call ESTablished
        while PMquery(PM,"FETCh:TDSCdma:SIGN:CSWitched:STATe?") != 'CEST\n':
            PMwrite(PM,"CALL:TDSCdma:SIGN:CSWitched:ACTion CONNect")
            time.sleep(8)
        print("TD-SCDMA connect established!")
        time.sleep(1)
        if UEPwrCtrl=="MAXPower":
            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET ALL1")
        elif UEPwrCtrl=="MINPower":
            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET ALL0")
        elif UEPwrCtrl=="CLOop":
            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:TPOWer %s" %CLTPower)
            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET CLOop")
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:PRECondition")
        PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:PEXecute")
        print("band  channel  UEpwr  ChPwr  AltCLR  AdjCLR  AdjCLR  AltCLR  RefSens  BER")
        LogfileWrite(LogFile, "band  channel  UEpwr  ChPwr  AltCLR  AdjCLR  AdjCLR  AltCLR  RefSens  BER\n")

        for i in range (len(bandTDS)):
            if i>0:
                time.sleep(2)
                PMwrite(PM, "CONFigure:TDSCdma:SIGN:RFSettings:BAND %s" %bandTDS[i])
                time.sleep(3)
             
            for j in range(len(channelTDS[i])):
                PMwrite(PM,"CONFigure:TDSCdma:SIGN:RFSettings:CHANnel %d" %channelTDS[i][j])
                time.sleep(2)
                if RF_output=="RF1O":
                    PMwrite(PM,"ROUTe:TDSCdma:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                while 1:
                    PMwrite(PM,"ABORt:TDSCdma:MEAS:MEValuation")
                    time.sleep(2)
                    TDSAclr = PMqueryWithDelay(PM,"READ:TDSCdma:MEAS:MEValuation:SPECtrum:AVERage?").split(',')
                    if TDSAclr[0] =="0":
                        break
                    else:
                        time.sleep(4)
                        TDSAclr = PMqueryWithDelay(PM,"READ:TDSCdma:MEAS:MEValuation:SPECtrum:AVERage?").split(',')
                        if TDSAclr[0] =="0":
                            break
                        else:
                            print("TxPwr=NULL, maybe call lost. Please wait for reconnect")
                            os.popen ("adb reboot")
                            PMwrite(PM,"SOURce:TDSCdma:SIGN:CELL:STATe OFF")
                            PMwrite(PM,"SOURce:TDSCdma:SIGN:CELL:STATe ON")
                            time.sleep(4)
                            PMwrite(PM,"ROUTe:TDSCdma:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
                            while PMquery(PM,"SOURce:TDSCdma:SIGN:CELL:STATe:ALL?")!='ON,ADJ\n':
                                time.sleep(2)
                            while PMquery(PM,"FETCh:TDSCdma:SIGN:PSWitched:STATe?")!='ATT\n':
                                time.sleep(1)
                            while PMquery(PM,"FETCh:TDSCdma:SIGN:CSWitched:STATe?") != 'CEST\n':
                                PMwrite(PM,"CALL:TDSCdma:SIGN:CSWitched:ACTion CONNect")
                                time.sleep(4)
                            if UEPwrCtrl=="MAXPower":
                                PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET ALL1")
                            elif UEPwrCtrl=="MINPower":
                                PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET ALL0")
                            elif UEPwrCtrl=="CLOop":
                                PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:TPOWer %s" %CLTPower)
                                PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:SET CLOop")
                            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:PRECondition")
                            PMwrite(PM,"CONFigure:TDSCdma:SIGN:UL:TPC:PEXecute")
                            if RF_output=="RF1O":
                                PMwrite(PM,"ROUTe:TDSCdma:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                UEPwr = float(TDSAclr[13])
                ChPwr = float(TDSAclr[1])
                print("%s    %-5d    %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f" %(bandTDS[i], \
                        channelTDS[i][j], UEPwr, ChPwr, float(TDSAclr[2]) - ChPwr, float(TDSAclr[3]) - ChPwr, \
                        float(TDSAclr[4])-ChPwr, float(TDSAclr[5]) - ChPwr))
                if Rx_measure==1:
                    PMwrite(PM,"CONFigure:TDSCdma:SIGN:BER:TBLocks 200")
                    (TDSRefSens,TDSBer)=SeekW_TD_Sens(PM,"TDSCdma",RF_output,UpperLimitTDS,CoarseStepTDS,FineStepTDS)
                    LogfileWrite(LogFile, "%s    %-5d    %3.2f  %3.2f %3.2f  %3.2f   %3.2f  %3.2f  %3.2f  %3.2f\n" \
                        %(bandTDS[i], channelTDS[i][j],UEPwr, ChPwr, float(TDSAclr[2])-ChPwr,\
                        float(TDSAclr[3])-ChPwr, float(TDSAclr[4])-ChPwr, float(TDSAclr[5])-ChPwr,\
                        TDSRefSens,TDSBer))
                else:
                    LogfileWrite(LogFile, "%s    %-5d    %3.2f  %3.2f %3.2f  %3.2f   %3.2f  %3.2f\n" \
                        %(bandTDS[i], channelTDS[i][j], UEPwr, ChPwr, float(TDSAclr[2])-ChPwr,\
                        float(TDSAclr[3])-ChPwr, float(TDSAclr[4])-ChPwr, float(TDSAclr[5])-ChPwr))
                PMwrite(PM,"ROUTe:TDSCdma:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        print("-------------------TD-SCDMA test end---------------------")
        PMwrite(PM,"CALL:TDSCdma:SIGN:CSWitched:ACTion DISConnect")
        PMwrite(PM,"CALL:TDSCdma:SIGN:PSWitched:ACTion DISConnect")
        PMwrite(PM,"SOURce:TDSCdma:SIGN:CELL:STATe OFF")

##############################     GSM Spectrum Switching & Rx_Sens.lev test   ##########################
    if GSM_measure==1:
        print("-------------------GSM test start... --------------------")
        os.popen ("adb reboot")  #重启手机便于搜网
        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")
        channelGSM=channelGSMList(bandGSM,ScanType)

        # 设置参数
        PMwrite(PM,"ROUTe:GSM:MEAS:SCENario:CSPath 'GSM Sig1'")
        time.sleep(1)
        PMwrite(PM,"CONFigure:GSM:SIGN:BAND:BCCH %s" %bandGSM[0])
        time.sleep(1)
        PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:LEVel:BCCH -60")
        PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH %d" %channelGSM[0][0])
        PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 10")
        time.sleep(1)
        PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
        PMwrite(PM,"CONF:GSM:MEAS:MEV:SCO:MOD 10")
        PMwrite(PM,"CONF:GSM:MEAS:MEV:SCO:SSW 10")
        PMwrite(PM,"CONF:GSM:MEAS:MEV:SCO:SMOD 10")
        PMwrite(PM,"CONF:GSM:MEAS:MEV:SSWitching:OFRequence 0.4e+6,0.6e+6,1.2e+6,1.8e+6,OFF,OFF,OFF,OFF,OFF,OFF,\
                   OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF")
        PMwrite(PM,"CONFigure:GSM:MEAS:MEValuation:REPetition SINGleshot")
        PMwrite(PM,"CONFigure:GSM:SIGN:BER:CSWitched:MMODe BBB")
                     #如果设置成Berst by Burst，返回值位置在[2]。RBER/FER、BER mode返回值在[4]
        PMwrite(PM,"CONFigure:GSM:SIGN:BER:CSWitched:SCOunt 100")
        PMwrite(PM,"CONFigure:GSM:SIGN:BER:CSWitched:RTDelay MAN,8")
        PMwrite(PM,"CONFigure:GSM:SIGN:BER:CSWitched:SCONdition NONE")

        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe ON")
        time.sleep(3)
        SetupGSMCall(PM,GSMcall_mode,GSMAttachWaitTime,mouse,CallStartX,CallStartY)
        print("gsm connect established!")
        print("band  channel  txpwr  -1.2MHz   -600kHz   -400kHz   400kHz  600kHz    1.2MHz")
        LogfileWrite(LogFile, "band  channel  txpwr  -1.2MHz   -600kHz   -400kHz   400kHz  600kHz    1.2MHz   GSMSens   BER\n")

        for i in range(len(bandGSM)):
            if i>0:
                if bandGSM[i]==bandGSM[i-1]:
                    pass
                elif GSMcall_mode==0:       # 发起handover
                    PMwrite(PM,"PREPare:GSM:SIGN:HANDover:TARGet %s" %bandGSM[i])
                    PMwrite(PM,"PREPare:GSM:SIGN:HANDover:CHANnel:TCH %s" %channelGSM[i][0])
                    PMwrite(PM,"PREPare:GSM:SIGN:HANDover:LEVel:TCH -60")
                    PMwrite(PM,"PREPare:GSM:SIGN:HANDover:PCL 5")
                    PMwrite(PM,"PREPare:GSM:SIGN:HANDover:TSLot 3")
                    PMwrite(PM,"CALL:GSM:SIGN:HANDover:STARt")
                    time.sleep (3)
                    if PMquery(PM,"SENSe:GSM:SIGN:BAND:TCH?")!=("%s\n" %bandGSM[i]):  #如handover不成功则cell OFF/ON并重新发起呼叫
                        os.popen ("adb reboot")
                        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")
                        time.sleep(1)
                        PMwrite(PM,"CONFigure:GSM:SIGN:BAND:BCCH %s" %bandGSM[i])
                        time.sleep(1)
                        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe ON")
                        time.sleep(3)
                else:
                    os.popen ("adb reboot")
                    PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")
                    time.sleep(2)
                    PMwrite(PM,"CONFigure:GSM:SIGN:BAND:BCCH %s" %bandGSM[i])
                    time.sleep(2)
                    PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe ON")
                    time.sleep(2)
                SetupGSMCall(PM,GSMcall_mode,GSMAttachWaitTime,mouse,CallStartX,CallStartY)
            if UEPwrCtrl=="MAXPower":
                if bandGSM[i]=="G085" or bandGSM[i]=="G09": iPCL = 5
                else:      iPCL = 0
            elif UEPwrCtrl=="CLOop":
                if bandGSM[i]=="G085" or bandGSM[i]=="G09": iPCL = round(5+(33-float(CLTPower))/2)
                else:      iPCL = round((30-float(CLTPower))/2)
            else:
                if bandGSM[i]=="G085" or bandGSM[i]=="G09": iPCL = 19
                else:      iPCL = 15
            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched %d" %(iPCL))
            time.sleep(2)

            for j in range(len(channelGSM[i])):
                PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH %d" %channelGSM[i][j])
                time.sleep(2)
                if RF_output=="RF1O":
                    PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                PMwrite(PM,"ABORt:GSM:MEAS:MEValuation")
                time.sleep(1)
                try:
                    GSSwitchResults = PMqueryWithDelay(PM,"READ:GSM:MEAS:MEValuation:SSWitching:FREQuency?")
                except Exception:
                    print("READ:GSM:MEAS:MEValuation:SSWitching:FREQuency timeout")
                    PMwrite(PM,"ABORt:GSM:MEAS:MEValuation")
                    time.sleep(2)
                    GSSwitchResults = PMqueryWithDelay(PM,"READ:GSM:MEAS:MEValuation:SSWitching:FREQuency?")
                listGSS = GSSwitchResults.split(',')
                while listGSS[21] in ["INV", "NAV", "NCAP"]:
                    print("TxPwr=NULL, maybe call lost. Please wait for reconnect")
                    #os.popen ("adb reboot")
                    PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")
                    time.sleep(2)
                    PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe ON")
                    time.sleep(3)
                    PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
                    SetupGSMCall(PM,GSMcall_mode,GSMAttachWaitTime,mouse,CallStartX,CallStartY)
                    if RF_output=="RF1O":
                        PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                    PMwrite(PM,"ABORt:GSM:MEAS:MEValuation")
                    time.sleep(2)
                    GSSwitchResults = PMqueryWithDelay(PM,"READ:GSM:MEAS:MEValuation:SSWitching:FREQuency?")
                    listGSS = GSSwitchResults.split(',')
                print("%-4s  %-4d      %3.2f  %3.2f    %3.2f    %3.2f    %3.2f  %3.2f    %3.2f" %(bandGSM[i], channelGSM[i][j], \
                        float(listGSS[21]), float(listGSS[18]), float(listGSS[19]), float(listGSS[20]), float(listGSS[22]),\
                        float(listGSS[23]), float(listGSS[24])))

                if Rx_measure==1:
                    (GSMSens,GSMBer)=SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimitGSM,CoarseStepGSM,FineStepGSM,mouse,CallStartX,CallStartY)
                    if (Fdd_Max_Min_mearsure==1 and (bandGSM[i]=="G085" or bandGSM[i]=="G09")):
                        if UEPwrCtrl=="MAXPower":
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 19")
                            (GSMSens_2nd,GSMBer_2nd)=SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimitGSM,CoarseStepGSM,FineStepGSM,mouse,CallStartX,CallStartY)
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 5")
                        elif (UEPwrCtrl=="MINPower" or UEPwrCtrl=="CLOop"):
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 5")
                            (GSMSens_2nd,GSMBer_2nd)=SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimitGSM,CoarseStepGSM,FineStepGSM,mouse,CallStartX,CallStartY)
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 19")
                        LogfileWrite(LogFile, "%-4s  %-4d      %3.2f  %3.2f    %3.2f    %3.2f    %3.2f  %3.2f    %3.2f   %3.2f \
  %3.2f %3.2f   %3.2f\n" %(bandGSM[i], channelGSM[i][j], float(listGSS[21]), float(listGSS[18]), \
                            float(listGSS[19]),float(listGSS[20]), float(listGSS[22]),float(listGSS[23]), \
                            float(listGSS[24]),GSMSens,GSMBer,GSMSens_2nd,GSMBer_2nd))
                    elif (Fdd_Max_Min_mearsure==1 and (bandGSM[i]=="G18" or bandGSM[i]=="G19")):
                        if UEPwrCtrl=="MAXPower":
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 15")
                            (GSMSens_2nd,GSMBer_2nd)=SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimitGSM,CoarseStepGSM,FineStepGSM,mouse,CallStartX,CallStartY)
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 0")
                        elif (UEPwrCtrl=="MINPower" or UEPwrCtrl=="CLOop"):
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 0")
                            (GSMSens_2nd,GSMBer_2nd)=SeekGSMSens(PM,RF_output,GSMcall_mode,GSMAttachWaitTime,UpperLimitGSM,CoarseStepGSM,FineStepGSM,mouse,CallStartX,CallStartY)
                            PMwrite(PM,"CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched 15")
                        LogfileWrite(LogFile, "%-4s  %-4d     %3.2f  %3.2f    %3.2f    %3.2f    %3.2f  %3.2f    %3.2f   %3.2f \
  %3.2f %3.2f   %3.2f\n" %(bandGSM[i], channelGSM[i][j], float(listGSS[21]), float(listGSS[18]), \
                            float(listGSS[19]),float(listGSS[20]), float(listGSS[22]),float(listGSS[23]), \
                            float(listGSS[24]),GSMSens,GSMBer,GSMSens_2nd,GSMBer_2nd))
                    else:
                        LogfileWrite(LogFile, "%-4s  %-4d     %3.2f  %3.2f    %3.2f    %3.2f    %3.2f  %3.2f    %3.2f   %3.2f   %3.2f\n" \
                          %(bandGSM[i], channelGSM[i][j], float(listGSS[21]), float(listGSS[18]), float(listGSS[19]),\
                            float(listGSS[20]), float(listGSS[22]),float(listGSS[23]), float(listGSS[24]),GSMSens,GSMBer))
                        
                else:
                    LogfileWrite(LogFile, "%-4s  %-4d     %3.2f  %3.2f    %3.2f    %3.2f    %3.2f  %3.2f    %3.2f\n" \
                          %(bandGSM[i], channelGSM[i][j], float(listGSS[21]), float(listGSS[18]), float(listGSS[19]),\
                            float(listGSS[20]), float(listGSS[22]),float(listGSS[23]), float(listGSS[24])))
                PMwrite(PM,"ROUTe:GSM:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
            PMwrite(PM,"CALL:GSM:SIGN:CSWitched:ACTion DISConnect")

        print("--------GSM Spectrum Switching/Ref.sens test end---------")
        PMwrite(PM,"SOURce:GSM:SIGN:CELL:STATe OFF")

#############################    CDMA ACLR test ###########################################
    if CDMA_measure==1:
        os.popen ("adb reboot")  #重启手机便于自动注册
        input("Please change CDMA SIM card then press Enter" )
        #if IN=="e":            break
        PMwrite(PM,"SOURce:CDMA:SIGN:STATe OFF")
        channelCDMA=channel3GList(bandCDMA,ScanType)
        
        PMwrite(PM,"ROUTe:CDMA:MEAS:SCENario:CSPath 'CDMA2000 Sig1'")
        PMwrite(PM,"CONFigure:CDMA:SIGN:RFSettings:BCLass %s" %bandCDMA[0])
        PMwrite(PM,"CONFigure:CDMA:SIGN:RFSettings:CHANnel %d" %channelCDMA[0][0])
        PMwrite(PM,"CONFigure:CDMA:SIGN:LAYer:SOPTion:FIRSt SO2")
        PMwrite(PM,"CONFigure:CDMA:SIGN:RPControl:PCBits AUP")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:REPetition SINGleshot")
        PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:CDMA -50")
        PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:EPMode MAX")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:RESult:ACP ON")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:RESult:POWer ON")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:ACP:FOFFsets 1,1.1,1.2,1.3,OFF,OFF,OFF,OFF,OFF,OFF")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:ACP:RBW F30K")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:SCOunt:MODulation 10")
        PMwrite(PM,"CONFigure:CDMA:MEAS:MEValuation:SCOunt:SPECtrum 10")
        PMwrite(PM,"ROUTe:EVDO:SIGN:SCENario:SCELl RF1C, RX1, RF1C, TX1")
        PMwrite(PM,"SOURce:CDMA:SIGN:STATe ON")
        print("-------------------CDMA test start...-----------------")
        time.sleep(4)

        # 建立callbox和手机连接
        while PMquery(PM,"FETCh:CDMA:SIGN:SOPTion:STATe?") != 'CONN\n':
            if CDMAcall_mode == 0:
                while PMquery(PM,"FETCh:CDMA:SIGN:SOPTion:STATe?") != 'REG\n':
                    time.sleep(4)
                PMwrite(PM,"CALL:CDMA:SIGN:SOPTion:ACTion CONNect")
            elif CDMAcall_mode == 2:
                mouse.click(CallStartX,CallStartY,1)
            time.sleep(4)
        print ("connect established!")

        if UEPwrCtrl=="MINPower":
            PMwrite(PM,"CONFigure:CDMA:SIGN:RPControl:PCBits AUTO")
            PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:EPMode MIN")
        elif UEPwrCtrl=="CLOop":
            PMwrite(PM,"CONFigure:CDMA:SIGN:RPControl:PCBits AUTO")
            PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:EPMode MANual")
            PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:MANual %s" %CLTPower)
        else:
            PMwrite(PM,"CONFigure:CDMA:SIGN:RPControl:PCBits AUP")
        print ("band channel txpwr aclr(-3) aclr(-2) aclr(-1) aclr(1) aclr(2) aclr(3)")

        for i in range (len(bandCDMA)):
            PMwrite(PM,"CONFigure:CDMA:SIGN:RFSettings:BCLass %s" %bandCDMA[i])
            for j in range(len(channelCDMA[i])):
                time.sleep(2)
                PMwrite(PM,"CONFigure:CDMA:SIGN:RFSettings:CHANnel %d" %channelCDMA[i][j])
                if RF_output=="RF1O":
                    PMwrite(PM,"ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
                PMwrite(PM,"ABORt:CDMA:MEAS:MEValuation")
                time.sleep(1)
                PMwrite(PM,"INIT:CDMA:MEAS:MEValuation")
                while (PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:STATe?") != "RDY\n"):
                    time.sleep(1)
                CdmaPower = PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:ACP:AVERage?").split(',')[1]  #1.23MHz BW功率
                CdmaAclr = PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:TRACe:ACP:AVERage?").split(',')
                if CdmaAclr[0] != '0':
                    print("CMW500 MINPower bug. Set power to -40dBm then restart test")
                    PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:EPMode MANual")
                    PMwrite(PM,"CONFigure:CDMA:SIGN:RFPower:MANual -40")
                    PMwrite(PM,"ABORt:CDMA:MEAS:MEValuation")
                    time.sleep(1)
                    PMwrite(PM,"INIT:CDMA:MEAS:MEValuation")
                    while (PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:STATe?") != "RDY\n"):
                        time.sleep(1)
                    CdmaPower = PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:ACP:AVERage?").split(',')[1]
                    CdmaAclr = PMquery(PM,"FETCh:CDMA:MEAS:MEValuation:TRACe:ACP:AVERage?").split(',')
                print ("%s  %4d    %3.2f %3.2f   %3.2f   %3.2f   %3.2f  %3.2f  %3.2f" \
                    %(bandCDMA[i], channelCDMA[i][j], float(CdmaPower), float (CdmaAclr[8]), float (CdmaAclr[9]), \
                      float (CdmaAclr[10]), float (CdmaAclr[12]), float (CdmaAclr[13]), float (CdmaAclr[14])))
                LogfileWrite (LogFile, "%s  %d  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f  %3.2f\n" \
                    %(bandCDMA[i], channelCDMA[i][j], float(CdmaPower), float (CdmaAclr[8]), float (CdmaAclr[9]), \
                      float (CdmaAclr[10]), float (CdmaAclr[12]), float (CdmaAclr[13]), float (CdmaAclr[14])))
                PMwrite(PM,"ROUTe:EVDO:SIGN:SCENario:SCELl RF1C, RX1, RF1C, TX1")
        print("-------------------CDMA test end---------------------")

############################## All test end  ##########################
    TimeEnd=time.clock()
    print("The total test time is %.1f minutes" %((TimeEnd-TimeStart)/60))
    endtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print("Test finished at %s" %endtime)
    LogfileWrite(LogFile, "Test finished at %s\n\n" %endtime)
    
if __name__ == '__main__':
    main()
