#https://github.com/xotrs/naver-blog-crawler 참고

import re
import json
import math
import datetime
import requests
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup

naver_client_id = "KiK6l00dj30ghG2UhuYB"
naver_client_secret = "vI6bCXMTj2"


def naver_blog_crawling(search_blog_keyword, display_count, sort_type):
    #search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    return get_blog_post(search_blog_keyword, display_count, 1, sort_type)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", naver_client_id)
    request.add_header("X-Naver-Client-Secret", naver_client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()
    print("status " + str(response_code) )
    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))

            if blog_pagination_total_count >= 1000:
                blog_pagination_count = 1000
            else:
                blog_pagination_count = blog_pagination_total_count

            print("키워드 " + search_blog_keyword + "에 해당하는 포스팅 수 : " + str(response_body_dict['total']))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 실제 페이징 수 : " + str(blog_pagination_total_count))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 처리할 수 있는 페이징 수 : " + str(blog_pagination_count))

        return blog_pagination_count


def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type):
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)
    returnValue =""
    for i in range(1, search_result_blog_page_count + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type

        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", naver_client_id)
        request.add_header("X-Naver-Client-Secret", naver_client_secret)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()
        print("status " + str(response_code) )
        if response_code is 200:
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode('utf-8'))
            print(response_body_dict)
            print(len(response_body_dict['items']))
            for j in range(0, len(response_body_dict['items'])):
                blog_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")

                get_blog_post_content_code = requests.get(blog_post_url)
                get_blog_post_content_text = get_blog_post_content_code.text
                remove_html_tag = re.compile('<.*?>')
                blog_post_title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                

                blog_post_description = re.sub(remove_html_tag, '',
                                                       response_body_dict['items'][j]['description'])
                blog_post_postdate = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'],
                                                                        "%Y%m%d").strftime("%y.%m.%d")
                
                print("포스팅 URL : " + blog_post_url)
                print("포스팅 제목 : " + blog_post_title)
                print("포스팅 설명 : " + blog_post_description)
                print("포스팅 날짜 : " + blog_post_postdate)
                #print("블로거 이름 : " + blog_post_blogger_name)
                #print("포스팅 내용 : " + blog_post_full_contents)
                returnValue += "url : " + blog_post_url
                returnValue += "title : " + blog_post_title
                returnValue += "post_desc : " + blog_post_description
                returnValue += "post_date : " + blog_post_postdate
                j += 1
            return returnValue


#if __name__ == '__main__':
#naver_blog_crawling("서울 아이 나들이", 5, "sim")
