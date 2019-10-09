# -*- coding: utf-8 -*-
##https://daewonyoon.tistory.com/259
#bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
#pip install PyMySQL
from konlpy.tag import Mecab
m = Mecab()
print(m.pos('서울 놀러갈만한곳'))

from db_utils import *
from NaverBlogCrawler import *
# school DB
#create_db()

# student TABLE
#create_table()

insert_student('cupjoo@naver.com', '변유철')
select_student('cupjoo@naver.com')
update_email('new@naver.com', 'cupjoo@naver.com')
#delete_student('new@naver.com')
