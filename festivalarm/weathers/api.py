from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from datetime import datetime, date

from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus

from my_secrets import WEATHER_SERVICE_KEY

def getWeather(regionId):
    
    today = datetime.today().date().strftime("%Y%m%d") + '0600'
    print(today)

    url = 'http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst'
    
    # response를 JSON 형식으로 받기 위한 queryParams 입력
    queryParams = '?' + urlencode({ 
        quote_plus('serviceKey') : WEATHER_SERVICE_KEY, 
        quote_plus('pageNo') : '1', 
        quote_plus('numOfRows') : '10', 
        quote_plus('dataType') : 'JSON', 
        quote_plus('regId') : regionId, 
        quote_plus('tmFc') : today })
    
    # 응답 받아온 뒤 utf-8로 인코딩
    response = urlopen(url + queryParams)
    json_api = response.read().decode("utf-8")

    json_query = json.loads(json_api)
    
    result = json_query.get('response')['body']['items']['item']
    
    resultCode = json_query.get('response')['header']['resultCode']
    
    print(resultCode)
    print(result)
    
    return JsonResponse({'resultCode':resultCode , 'result':result})

