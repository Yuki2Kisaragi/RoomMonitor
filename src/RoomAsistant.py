#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import requests
import json
import RPi.GPIO as GPIO

import EnvironmentData
import DistanceData

def send_to_SORACOM_HarvestData(Data_Temp,Data_Humidity,Data_AirPressure,Data_distance):
	
	# Data_Temp,Data_Humidity,Data_AirPressure = read_EnviromentData()

	# JSONを整形
	json_data = {"Temperature": Data_Temp, "Humidity": Data_Humidity, "AirPressure": Data_AirPressure,'Distance': round(Data_distance*10)/10}
	encode_json_data = json.dumps(json_data)
	print(json_data)
	# SORACOM Harvestに送信
	print(requests.post('http://harvest.soracom.io', data=encode_json_data, headers={'Content-Type': 'application/json'}))

def DEBUG_send_to_SORACOM_HarvestData(Data_Temp,Data_Humidity,Data_AirPressure,Data_distance):
	"""
	@brief デバッグ用関数. HTTP送信せず、JSONデータを作成して表示するのみの処理。

	"""

	# JSONを整形
	json_data = {"Temperature": Data_Temp, "Humidity": Data_Humidity, "AirPressure": Data_AirPressure,'Distance': round(Data_distance*10)/10}
	encode_json_data = json.dumps(json_data)
	print(json_data)

def arg_parse():
	pass


def main():
	# 第一引数を interval に設定
	interval=5 if len(sys.argv)==1 else int(sys.argv[1])

	while(1):
		start_time = time.time()
		distance = DistanceData.read_distance()
		temp,humidity,air_pressure = EnvironmentData.read_EnviromentData()
		try:
			# 本番用
			# send_to_SORACOM_HarvestData(temp,humidity,air_pressure,distance)
			
			# Debug
			DEBUG_send_to_SORACOM_HarvestData(temp,humidity,air_pressure,distance)
		
		except KeyboardInterrupt:
			pass

		# 指定した秒数に１回実行するためのウェイトを入れる
		wait = start_time + interval - start_time
		if wait > 0:
			time.sleep(wait)

if __name__ == '__main__':
	main()
	