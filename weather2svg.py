#!/usr/bin/env python3

import time
import requests
from datetime import datetime
import json
import codecs
import subprocess
import config
import locale
import sys

status = dict([('0','晴'),('1','多云'),('2','阴'),('3','阵雨'),('4','雷阵雨'),('5','雷阵雨并伴有冰雹'),('6','雨夹雪'),('7','小雨'),('8','中雨'),('9','大雨'),('10','暴雨'),('11','大暴雨'),('12','特大暴雨'),('13','阵雪'),('14','小雪'),('15','中雪'),('16','大雪'),('17','暴雪'),('18','雾'),('19','冻雨'),('20','沙尘暴'),('21','小到中雨'),('22','中到大雨'),('23','大到暴雨'),('24','暴雨到大暴雨'),('25','大暴雨到特大暴雨'),('26','小到中雪'),('27','中到大雪'),('28','大到暴雪'),('29','浮尘'),('30','扬沙'),('31','强沙尘暴'),('32','浓雾'),('49','强浓雾'),('53','霾'),('54','中度霾 '),('55','重度霾'),('56','严重霾'),('57','大雾'),('58','特强浓雾'),('301','雨'),('302','雪'),('99','未知')])

if not config.latitude or not config.longitude:
    print("Error: Latitude/Longitude not set in config.py")
    sys.exit(3) # 错误代码 3 对应经纬度未设置

api_url = config.api_url + '&latitude=' + config.latitude + '&longitude=' + config.longitude

max_retries = getattr(config, 'max_retries', 3)
retry_delay = getattr(config, 'retry_delay', 5)

weather = None

for attempt in range(max_retries):
    try:
        r = requests.get(api_url, timeout=10)
        r.raise_for_status()
        
        weather = r.json()
        break
        
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error (Attempt {attempt + 1}/{max_retries}): {errh}")
    except requests.exceptions.RequestException as e:
        print(f"Problem getting data (Attempt {attempt + 1}/{max_retries}): {e}")
    
    if attempt < max_retries - 1:
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
else:
    print("All retries failed. Exiting.")
    sys.exit(2) # 错误代码 2 对应天气数据请求失败

# 指定输出中文
locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')

# process SVG
output = codecs.open('weather-preprocess.svg', 'r', encoding='utf-8').read()

current = datetime.fromisoformat(weather['current']['pubTime'])
sunrise = datetime.fromisoformat(weather['forecastDaily']['sunRiseSet']['value'][0]['from'])
sunset = datetime.fromisoformat(weather['forecastDaily']['sunRiseSet']['value'][0]['to'])
tomorrow_sunrise = datetime.fromisoformat(weather['forecastDaily']['sunRiseSet']['value'][1]['from'])
tomorrow_sunset = datetime.fromisoformat(weather['forecastDaily']['sunRiseSet']['value'][1]['to'])

output = output.replace('#NOW', current.strftime('%Y-%m-%d  %H:%M:%S'))

# current weather
if current > sunrise and current < sunset:
    output = output.replace('#IC',weather['current']['weather']+'d')
else:
    output = output.replace('#IC',weather['current']['weather']+'n')

output = output.replace('#TN',weather['current']['temperature']['value'])
output = output.replace('#HI',weather['forecastDaily']['temperature']['value'][0]['from'])
output = output.replace('#LO',weather['forecastDaily']['temperature']['value'][0]['to'])
output = output.replace('#SUMNOW', status[weather['current']['weather']])
# output = output.replace('#SUMHR', weather['hourly'][0]['weather'][0]['description'])
output = output.replace('#DP0', weather['forecastDaily']['precipitationProbability']['value'][0])

output = output.replace('#DBP', weather['current']['pressure']['value'])
output = output.replace('#DHU', weather['current']['humidity']['value'])

output = output.replace('#SR', sunrise.strftime('%H:%M'))
output = output.replace('#SS', sunset.strftime('%H:%M'))

# battery
proc_out = subprocess.Popen(["lipc-get-prop", "com.lab126.powerd", "battLevel"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
battery_capacity, stderr = proc_out.communicate()

batt_val = battery_capacity.decode("utf-8").strip()
output = output.replace('#BAT', batt_val + '%')

# next 12 hours
for i in range(0, 12):
    istr = "{:02d}".format(i)
    time = datetime.fromisoformat(weather['forecastHourly']['wind']['value'][i]['datetime'])
    if (time > sunrise and time < sunset) or (time > tomorrow_sunrise and time < tomorrow_sunset):
        output = output.replace('#HC'+istr, str(weather['forecastHourly']['weather']['value'][i])+'d')
    else:
        output = output.replace('#HC'+istr, str(weather['forecastHourly']['weather']['value'][i])+'n')
    output = output.replace('#HTM'+istr, time.strftime('%H:%M'))
    output = output.replace('#HTE'+istr, str(weather['forecastHourly']['temperature']['value'][i]))

#next 7 days
for i in range (0, 7):
    istr = str(i)
    output = output.replace('#DA'+istr, datetime.fromisoformat(weather['forecastDaily']['sunRiseSet']['value'][i]['from']).strftime('%-m-%d 周%a'))
    output = output.replace('#DICD'+istr, weather['forecastDaily']['weather']['value'][i]['from']+'d')
    output = output.replace('#DH'+istr, weather['forecastDaily']['temperature']['value'][i]['from'])
    output = output.replace('#DL'+istr, weather['forecastDaily']['temperature']['value'][i]['to'])
    output = output.replace('#DICN'+istr, weather['forecastDaily']['weather']['value'][i]['to']+'n')

#output = output.replace('#SUMDAILY', weather['daily']['summary'])

codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
