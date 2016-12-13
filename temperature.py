#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import requests
import json


channel = 17

def read(channel):

  data = []
  j = 0
  GPIO.setmode(GPIO.BCM)

  time.sleep(1)

  GPIO.setup(channel, GPIO.OUT)
  GPIO.output(channel, GPIO.LOW)
  time.sleep(0.02)
  GPIO.output(channel, GPIO.HIGH)

  GPIO.setup(channel, GPIO.IN)
  
  while GPIO.input(channel) == GPIO.LOW:
       continue

  while GPIO.input(channel) == GPIO.HIGH:
       continue

  while j < 40: 
      k = 0
      while GPIO.input(channel) == GPIO.LOW:
          continue
      
      while GPIO.input(channel) == GPIO.HIGH:
          k += 1
          if k > 100:
               break

      if k < 8:
          data.append(0)
      else:
          data.append(1)
       
      j += 1
  return data  


def parse(data):
  humidity_bit = data[0:8]
  humidity_point_bit = data[8:16]
  temperature_bit = data[16:24]
  temperature_point_bit = data[24:32]
  check_bit = data[32:40]

  humidity = 0
  humidity_point = 0
  temperature = 0
  temperature_point = 0
  check = 0
  
  for i in range(8): 
      humidity += humidity_bit[i] * 2 ** (7 - i)
      humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
      temperature += temperature_bit[i] * 2 ** (7 - i)
      temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
      check += check_bit[i] * 2 ** (7 - i)
    
  tmp = humidity + humidity_point + temperature + temperature_point
  ret = [-100,-100]
  if check == tmp:
     print "temperature : ", temperature, ", humidity : ", humidity
     ret[0] = temperature
     ret[1] = humidity
  else: 
     print "wrong"
     print "temperature : ", temperature, ", humidity : ", humidity, ", check :", check, ", tmp :", tmp
  return ret

def uploadtemperaturetoyeelink(temperature):
  apiurl = 'http://api.yeelink.net/v1.1/device/352824/sensor/397469/datapoints'
  apiheaders = {'U-ApiKey': 'b6cd2eb868fa60a6e30089e04ec5f5e2', 'content-type': 'application/json'} 
  payload = {'value': temperature}
  r = requests.post(apiurl, headers=apiheaders, data=json.dumps(payload))

def uploadhumiditytoyeelink(humidity):
  apiurl = 'http://api.yeelink.net/v1.1/device/352824/sensor/397916/datapoints'
  apiheaders = {'U-ApiKey': 'b6cd2eb868fa60a6e30089e04ec5f5e2', 'content-type': 'application/json'}
  payload = {'value': humidity}
  r = requests.post(apiurl, headers=apiheaders, data=json.dumps(payload))

while (True):
  data = read(channel)
  ret = parse(data)
  GPIO.cleanup()
  temperature = ret[0]
  humidity = ret[1]
  
  if temperature > -100:
     uploadtemperaturetoyeelink(temperature)
  if humidity > -100:
     uploadhumiditytoyeelink(humidity)

  time.sleep(10)

 
