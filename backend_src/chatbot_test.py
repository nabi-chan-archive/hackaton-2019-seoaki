# -*- coding: utf-8 -*-
from urllib import parse
import urllib.request

company = "seoulcity"
system = "seoakey"
classgubun = parse.quote("ALL")
var1 = parse.quote("예방접종")

url=f'https://seoakey.run.goorm.io/callNLP?company={company}&system={system}&classgubun={classgubun}&var1={var1}'

text_data = urllib.request.urlopen(url).read().decode('utf-8')
print(text_data)

