### API URL, don't touch
api_url = 'https://weatherapi.market.xiaomi.com/wtr-v3/weather/all?isGlobal=false&locale=zh_cn&appKey=weather20151024&sign=zUFJoAR2ZVrDy1vF3D07'

### Adjust your lat/lon
latitude = ''
longitude = ''

# 最大重试次数
max_retries = 3
# 每次重试之间的等待时间（秒）
retry_delay = 5

# 当遇到错误时, 设置为 True 会在屏幕上显示详细 log
debug = True  