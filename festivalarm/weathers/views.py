from django.shortcuts import render
from django.http import JsonResponse

from .api import getWeather



def index(request):
    
    # body로 넘어온 지역코드 
    regionId = request.GET.get('regionId')

    # 파라미터로 도시를 넣으면 해당 도시의 3~10일 뒤 기상예보를 반환
    result = getWeather(regionId)
    
    return result