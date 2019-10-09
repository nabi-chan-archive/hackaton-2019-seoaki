# -*- coding: utf-8 -*-
from bottle import route, run, request
from NaverBlogCrawler import *
import pymysql
import pandas as pd
from konlpy.tag import Mecab
from time import time
import json
import math
import re
from collections import Counter
# 앙상블 알고리즘 적용
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

stime = time()
hoststr = "localhost"
usrstr = "root"
passwordstr = "seoakey1009!"
dbstr = "CHATBOT"

mecab = Mecab()

@route('/callMecabBatch')
def callMecabBatch():
     #외부 파라미터 전달 받음
    company = request.query.company
    system = request.query.system
    
    conn = pymysql.connect(host=hoststr, user=usrstr, password=passwordstr, db=dbstr, charset='utf8')
    cursor = conn.cursor()
    
    sql = "select idx, System_User_Gubun, Question from QNA_SET "
    sql += " where Company ='"+company+"' and System='"+system+"' "
    
    df = pd.read_sql(sql, conn)
    
    updateCnt = 0
    duplicateCnt = 0
    
    for index, row in df.iterrows():
        Question = row["Question"]
        System_User_Gubun = row["System_User_Gubun"]
        idx_Qna_Set = row["idx"]
        
        malist = mecab.pos(Question)
        # 형태소 분석된 명사 나열 정보 업데이트
        nouns = ""
        for word in malist:
            if word[1] in ["SL","NNG","NNB","NNP"]:
                nouns += word[0] + " "
        nouns = nouns[:-1]
        
        if len(nouns) > 0 :
            sql4 = "update QNA_SET set Question_Nouns='"+nouns.upper()+"' where Company='"+company+"' and System='"+system+"' and idx='"+str(idx_Qna_Set)+"'; "
            cursor.execute(sql4)
            conn.commit()
            print('업데이트 명사열 : '+nouns.upper())
        
        # 형태소 분석된 값을 토큰에 저장시킴
        for word in malist:
            if word[1] in ["SL","NNG","NNB","NNP"]:
                Noun = word[0]
                # 해당 명사 중복되어 있는지 체크
                sql = " select * from QNA_TOKEN where Company ='"+company+"' and System='"+system+"' and Noun='"+Noun+"' and idx_Qna_Set="+str(idx_Qna_Set)
                df = pd.read_sql(sql, conn)
                
                if df.shape[0] == 0:
                    sql2 = " insert into QNA_TOKEN (Company, System, System_User_Gubun, Noun, idx_Qna_Set, Insert_Dt) "
                    sql2 +=" Values('"+company+"','"+system+"','"+System_User_Gubun+"','"+Noun+"',"+str(idx_Qna_Set)+",SYSDATE()) "
                    cursor.execute(sql2)
                    conn.commit()
                    print("추가된 형태소 : "+Noun)
                    updateCnt = updateCnt + 1
                else : 
                    duplicateCnt = duplicateCnt + 1
                    
    returnStr = "총 중복된 형태소 개수 : "+str(duplicateCnt)
    returnStr += " / "
    returnStr += "총 추가된 형태소 개수 : "+str(updateCnt)
    
    print("총 중복된 형태소 개수 : "+str(duplicateCnt))
    print("총 추가된 형태소 개수 : "+str(updateCnt))

    cursor.close()
    conn.close()
    
    return returnStr

    
@route('/callNLP')
def callNLP():
    # 외부 파라미터 전달 받음
    company = request.query.company
    system = request.query.system
    classgubun = request.query.classgubun
    var1 = request.query.var1
    
    # 의미 없는 단어 삭제를 통한 필요한 데이터 가져오기
    def replace_all(text, dic2):
        for i, j in dic2.items():
            text = text.replace(i,j)
        return text
    
    dic = {"문의" : ""}
    checkquestion = var1.upper()
    checkquestion = replace_all(checkquestion, dic)
    
    malist = mecab.pos(checkquestion)
    nouns = ""
    nounsstring = ""
    nounsCnt = 0
    for word in malist:
        if word[1] in ["SL","NNG","NNB","NNP"]:
            nouns +="'"+word[0]+"',"
            nounsstring += word[0]+" "
            nounsCnt = nounsCnt + 1
    nouns = nouns[:-1]
    nounsstring = nounsstring[:-1]
    print(nouns)
    
    resultCnt = nounsCnt
    
    #DB 조회
    conn = pymysql.connect(host=hoststr, user=usrstr, password=passwordstr, db=dbstr, charset='utf8')
    
    issmaltalk = 0
    #0개이면 강제 종료
    if resultCnt == 0 : 
        return "분석할수 있는 데이터가 없음"
    else : 
        sql = " select A.idx As idx, A.company AS Company, A.System AS System, A.Question As Question, A.Answer As Answer, A.Question_Nouns As Question_Nouns, A.Use_Yn As Use_Yn, 0.0 AS AVG_Cnt, 0.0 AS Cnt, 0.0 AS Cnt2 "
        sql +=" from QNA_SET A inner join (select idx_qna_set, count(noun) AS CNT from QNA_TOKEN Where "
        sql += " Company ='"+company+"' and System='"+system+"' and System_User_Gubun in ('ALL','"+classgubun+"') and Noun in ("+nouns+") group by idx_Qna_Set) B on A.idx = B.idx_Qna_Set "
        sql +=" Where A.Use_Yn = 1 "
        sql +=" order by System_Sub_Gubun asc "
        df = pd.read_sql(sql, conn)
        print("--QNA SET 조회---")
        
        #0개이면 네이버에게 물어봐
        if df.shape[0] == 0 :
            print("--네이버 블로그 조회---")
            return naver_blog_crawling(checkquestion, 5, "sim")        
    
    #조회 완료시 코넥션 종료
    conn.close()
    
    #질문이 중복되었을 경우 중복제거
    df = df.drop_duplicates(['Question'], keep='first')
    df = df.reset_index(drop=True)
    
    print('DB 조회 종료 : 소요시간 [%1.2f]초 '% (time() - stime))
    
    #유사도 구하기 시작
    WORD = re.compile(r'\w+') #이부분 추가 확인해야함
    def textToVector(text):
        words = WORD.findall(text)
        return Counter(words)        
    
    def textNormalizeTfidf(text):
        malist = mecab.pos(text)
        nouns2 = []
        for word in malist:
            if word[1] in ["SL","NNG","NNB","NNP"]:
                nouns2.append(word[0])
        return nouns2
    
    
    def tfidfconsineCall():
        vectorize = TfidfVectorizer(tokenizer=textNormalizeTfidf, min_df=1, sublinear_tf=True)
        X = vectorize.fit_transform(df['Question_Nouns'])
        features = vectorize.get_feature_names()
        
        #기존 질문 벡터
        question_query = checkquestion
        srch_vector = vectorize.transform([question_query])
        cosine_similar = linear_kernel(srch_vector, X).flatten()
        
        return cosine_similar
    
    def textNormalize(text):
        malist = mecab.pos(text)
        nouns = ""
        for word in malist:
            if word[1] in ["SL","NNG","NNB","NNP"]:
                nouns += word[0] +" "
        nouns = nouns[:-1]
        return nouns
    
    def cosDistance(vector1, vector2):
        intersection = set(vector1.keys()) & set(vector2.keys())
        numerator = sum([vector1[x]*vector2[x] for x in intersection])
        
        sum1 = sum([vector1[x] **2 for x in vector1.keys()])
        sum2 = sum([vector2[x] **2 for x in vector2.keys()])
        
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator
        

    #기준 질문 벡터
    vector1 = textToVector(textNormalize(checkquestion))
    
    #두번째 알고리즘 콜
    tfidf_cosine_similar = tfidfconsineCall()
    
    #기존 질문 벡터화 후 코사인 유사도 값 돌출
    maxSimilarity = 0
    for index, row in df.iterrows():
        text2 = row['Question_Nouns']
        vector2 = textToVector(text2)
        
        cosine = cosDistance(vector1, vector2)
        df.set_value(index=index, col='Cnt', value=cosine)
        
        tf_idf_value = tfidf_cosine_similar[index]
        avg_cnt = (cosine + tf_idf_value) / 2
        
        df.set_value(index=index, col='Cnt2', value=tf_idf_value)
        df.set_value(index=index, col='AVG_Cnt', value=avg_cnt)
        
        if maxSimilarity == 0:
            maxSimilarity = avg_cnt
            
        if maxSimilarity < avg_cnt:
            maxSimilarity = avg_cnt
        
        #consine 0 에서 평균값 0일때도 변경
        if avg_cnt == 0.0:
            df.drop(index, inplace=True) # 유사도가 0이면 삭제
            
    print('유사도 계산 종료 : 소요시간 [%1.2f]초 '% (time() - stime))
    print("Max 유사도 : ", maxSimilarity)
    print("유사도가 높은 질문과 답변 쌍입니다.")
    df = df.sort_values(['AVG_Cnt'], ascending=[False])
    
    maxdf80 = df.loc[df['AVG_Cnt'] > 0.80]
    total_row80 = maxdf80.shape[0]
    
    maxdf60 = df.loc[df['AVG_Cnt'] > 0.60]
    total_row60 = maxdf60.shape[0]
    
    maxdf30 = df.loc[df['AVG_Cnt'] > 0.30]
    total_row30 = maxdf30.shape[0]
    
    if total_row80 > 0 :
        maxdf80 = maxdf80.sort_values(['AVG_Cnt'], ascending=[False])
        maxdf80 = maxdf80.reset_index(drop=True)
        print(' {} / {} / score : {} '.format(maxdf80['System'],maxdf80['Question'],maxdf80['AVG_Cnt']))
        json4 = maxdf80.to_json(orient='records') 
    elif total_row60 > 0 :
        maxdf60 = maxdf60.sort_values(['AVG_Cnt'], ascending=[False])
        maxdf60 = maxdf60.reset_index(drop=True)
        print(' {} / {} / score : {} '.format(maxdf60['System'],maxdf60['Question'],maxdf60['AVG_Cnt']))
        json4 = maxdf60.to_json(orient='records')
    elif total_row30 > 0 :
        maxdf30 = maxdf30.sort_values(['AVG_Cnt'], ascending=[False])
        maxdf30 = maxdf30.reset_index(drop=True)
        print(' {} / {} / score : {} '.format(maxdf30['System'],maxdf30['Question'],maxdf30['AVG_Cnt']))
        json4 = maxdf30.to_json(orient='records')
    else:
        print("유사도 0.3 이하 이면 미답변으로 처리합니다.")
        return "유사도 0.3 이하 이면 미답변으로 처리합니다."
    
    #returnstr = "질의 : "+checkquestion +" / 토큰 : "+ nouns
    return json4



if __name__ == '__main__':
    run(port=80, host='0.0.0.0')