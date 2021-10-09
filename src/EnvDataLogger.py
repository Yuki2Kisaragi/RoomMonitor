#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from time import sleep
import datetime
import csv
import struct
import logging
from logging import handlers
import subprocess
from os import strerror ,path
import multiprocessing
from concurrent.futures import ProcessPoolExecutor




class Logger(object):

    def __init__(self,name):
        self.Header_List = ['time', 'Temperature[deg]', 'Humidity[ppm]', 'AirPressure[Pa]', 'Distance[cm]']
        self.name = name
        self.LOG_STORAGE_PATH = ""
                
    def start_logger(self):

            self.LoggerIsActivated = True

            # ロガーを取得
            # logging module は直接インスタンスを作成することはできないので、logging.getLogger(__name__)を用いてインスタンス化する
            self.lg = logging.getLogger(__name__)
            # ロギングレベルを設定
            self.lg.setLevel(logging.DEBUG)

            # ローテーティングファイルハンドラを作成 & ロガーに追加
            # 第一引数にエイリアス名、第二引数に保存先PATH
            self.rh = DailyRotatingFileHandler(
                # r"rh","../AirCleaner_Log/Logger"
                r"rh",self.LOG_STORAGE_PATH,
                self.name
                )
            
            # このハンドラに対する閾値を DEBUG に設定します。 DEBUGレベルよりも深刻でないログメッセージは無視されます
            self.rh.setLevel(logging.DEBUG)
            # 指定されたハンドラ rh をロガーに追加
            self.lg.addHandler(self.rh)

            # Header作成
            with open(self.rh.baseFilename,'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.Header_List)
                writer.writeheader()

    def terminate_logger(self,WaringStop=False):
        self.LoggerIsActivated = False      
        self.rh.close()
        self.lg.removeHandler(self.rh)
        if WaringStop == True:
            self.LogStop_from_AbnormalStop = True
        
        print("Logger is terminated.")



    def run(self):
        """
        @brief 実行プロセス処理 本文

        @summary 
        """

        while True:                    
            self.lg.debug("%s,%s,%s,%s,%s",datetime.datetime.now().strftime("%H:%M:%S"),byteArray[0],byteArray[1],hex(byteArray[2]),modestr)
            """
            LogFile Layout 
            16:43:26,48,0,0,S
            16:43:29,48,0,0,A                    
            """



class DailyRotatingFileHandler(handlers.RotatingFileHandler):

    def __init__(self, alias, basedir,process_name, mode="a", maxBytes=1000000, backupCount=100, encoding="utf-8", delay=0):
        """
        @summary Set self.baseFilename to date string of today.
                The handler create logFile named self.baseFilename

        """
        self.basedir_ = basedir
        self.alias_ = alias
        self.fileno = 0
        self.maxBytes = maxBytes
        self.process_name= process_name
        self.baseFilename = self.getBaseFilename()
        print("maxbyte:",maxBytes)
        print("filename:",self.baseFilename)
        

        handlers.RotatingFileHandler.__init__(self, self.baseFilename, mode, maxBytes, backupCount, encoding, delay)

    def getBaseFilename(self):
        """
        @summary: Return logFile name string formatted to "today.log.alias"
                  ファイル名を変更する
        """
        self.today_ = datetime.datetime.now()
        basename_ = self.today_.strftime("%Y%m%d_%H%M%S") + "_No" + str(self.fileno) + "." + "csv"
        return path.join(self.basedir_, basename_)


    def shouldRollover(self, record):
        """
        @summary: 
        Rollover happen 
        1. When the logFile size is get over maxBytes.
        2. When date is changed.

        @see: BaseRotatingHandler.emit
        """

        if self.stream is None:                
            self.stream = self._open()

        # print("(Ro)maxbyte:",self.maxBytes)

        if self.maxBytes > 0 :
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  
            print("{} (Ro)msg:{}".format(self.process_name, msg))
            print("{}(Ro)tell:{}".format(self.process_name, self.stream.tell() + len(msg)  ))
            if self.stream.tell() + len(msg) >= self.maxBytes:
                if self.today_ == datetime.date.today():
                    self.fileno += 1
                else:
                    self.fileno = 0
                    self.baseFilename = self.getBaseFilename()
                return 1

        return 0
    def shutdown(self):
        handlers.RotatingFileHandler.close(self)




if __name__ == "__main__":
  
    # プロセス生成したい関数を登録
    process_pool = [] 
    process_pool.append(Logger("RoomEnvLogger").run) 

    with ProcessPoolExecutor(max_workers=2) as executor: # max_workerは同時に動かすプロセスの最大数 Noneを指定するとコア数 * 4の値になる
        for process in process_pool:
            results = executor.submit(process) # submit関数で、list内の関数をプロセス生成


