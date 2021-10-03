#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import requests
import json
import RPi.GPIO as GPIO

# 距離を読む関数
def read_distance():
	# 必要なライブラリのインポート・設定

	# 使用するピンの設定
	GPIO.setmode(GPIO.BOARD)
	TRIG = 11 # ボード上の11番ピン(GPIO17)
	ECHO = 13 # ボード上の13番ピン(GPIO27)

	# ピンのモードをそれぞれ出力用と入力用に設定
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.output(TRIG, GPIO.LOW)

	# TRIG に短いパルスを送る
	GPIO.output(TRIG, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(TRIG, GPIO.LOW)

	# ECHO ピンがHIGHになるのを待つ
	signaloff = time.time()
	while GPIO.input(ECHO) == GPIO.LOW:
		signaloff = time.time()

	# ECHO ピンがLOWになるのを待つ
	signalon = signaloff
	while time.time() < signaloff + 0.1:
		if GPIO.input(ECHO) == GPIO.LOW:
			signalon = time.time()
			break

	# GPIO を初期化しておく
	GPIO.cleanup()

	# 時刻の差から、物体までの往復の時間を求め、距離を計算する
	timepassed = signalon - signaloff
	distance = timepassed * 17000

	# 500cm 以上の場合はノイズと判断する
	if distance <= 500:
		print("データ取得")
		return distance
	else:
		print("距離500㎝以上：ノイズ判定")
		return distance

# SORACOM Harvestへ送る
def send_to_Harvest(Data_distance):
	"""
	@description: 距離情報をソラコムハーベストに送信する
	@param      : Data_distance(距離情報)
	@
	"""
	if Data_distance:
			print("距離: {:.1f} cm".format(Data_distance))
			headers = {'Content-Type': 'application/json'}
			payload = {'distance': round(Data_distance*10)/10 }
			print("データ送信")

	try:
		print(requests.post('http://harvest.soracom.io', data=json.dumps(payload), headers=headers, timeout=5))

	except requests.exceptions.ConnectTimeout:
		print("ERROR: 接続がタイムアウトしました。connect_air.sh は実行していますか？")
		sys.exit(1)
		
	if  (requests.post('http://harvest.soracom.io', data=json.dumps(payload), headers=headers, timeout=5)).status_code == 400:
			print('ERROR: データ送信に失敗しました。Harvest が有効になっていない可能性があります。')
			sys.exit(1)


if __name__ == '__main__':
	# 第一引数を interval に設定
	interval=5 if len(sys.argv)==1 else int(sys.argv[1])

	while True:
		start_time = time.time()
		distance = read_distance()

		send_to_Harvest(distance)
				
		# 指定した秒数に１回実行するためのウェイトを入れる
		wait = start_time + interval - start_time
		if wait > 0:
			time.sleep(wait)

