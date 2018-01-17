# WeixinSpider

### 接口基本配置

```python
# mongodb数据库地址
MONGO_URI = 'localhost'

# mongodb数据库名称
MONGO_DB = 'weixin'

# 代理接口地址
ROXY_POOL_URL = 'http://127.0.0.1:5000/get'

# 代理最大获取次数
MAX_COUNT = 5

# 微信文章关键字
KEYWORD = '风景'
```
### 方法说明
```
#  get_proxy
说明：获取代理URL
  参数名称   是否必须   参数说明
    无           无         无
    
# get_html
说明： 调用代理获取html
  参数名称   是否必须   参数说明
    url        是       抓取网页的url
    count      是       获取次数默认是1
    
# get_index
说明： 获取html
  参数名称   是否必须   参数说明
  keyword    是        关键字
  page       是        页码
    
# parse_index
说明： 获取详情页URL
  参数名称   是否必须   参数说明
  html        是        一级页码response      

  
# get_detail
说明： 获取详情页response
  参数名称   是否必须   参数说明
    URL      是        详情页的url
  
  
# parse_detail
说明： 解析字段
  参数名称   是否必须   参数说明
   html        是      详情页response     

# save_to_mongo
说明： 存储到mongodb
  参数名称   是否必须   参数说明
   data        是      详情页response 
   
```
```angular2html
cookie是登录后获取的
```


