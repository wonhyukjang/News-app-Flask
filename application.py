from flask import Flask, jsonify,request
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
import re

import json
import operator
import string
app = Flask(__name__)

stopwordList = []
with open('static/stopwords_en.txt') as f:
    for line in f:
        for x in line.split('\n'):
            if len(x) != 0:
                stopwordList.append(x)

puncList = []

for i in range(len(string.punctuation)):
    puncList.append(string.punctuation[i])
print(puncList)

# Init
newsapi = NewsApiClient(api_key='b8298e78ba414259b97fb2a5b289a14f')

# top_headlines = newsapi.get_top_headlines(q='bitcoin',
#                                           sources='bbc-news,the-verge',
#                                           category='business',
#                                           language='en',
#                                           country='us')

top_headlines_google = newsapi.get_top_headlines(sources='',
                                          language='en',
                                          page_size=100)

top_headlines_cnn = newsapi.get_top_headlines(sources='cnn',
                                          language='en')

top_headlines_fox = newsapi.get_top_headlines(sources='fox-news',
                                          language='en')



def filterNews(news_Source):
    i = 0

    while i != len(news_Source['articles']):
        try :
            if news_Source['articles'][i]['author'] == None or len(news_Source['articles'][i]['author']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        try:
            if news_Source['articles'][i]['title'] == None or len(news_Source['articles'][i]['title']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        try:
            if news_Source['articles'][i]['description'] == None or len(news_Source['articles'][i]['description']) == 0:
                del news_Source['articles'][i]
                continue
            if re.match(r"\<\w+>", news_Source['articles'][i]['description']):
                del news_Source['articles'][i]
                continue
         
        except:
            del news_Source['articles'][i]
            continue
        try:
            if news_Source['articles'][i]['url'] == None or len(news_Source['articles'][i]['url']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        try: 
            if news_Source['articles'][i]['urlToImage'] == None or len(news_Source['articles'][i]['urlToImage']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        try:
            if news_Source['articles'][i]['publishedAt'] == None or len(news_Source['articles'][i]['publishedAt']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        try:
            if news_Source['articles'][i]['source']['name'] == None or len(news_Source['articles'][i]['source']['name']) == 0:
                del news_Source['articles'][i]
                continue
        except:
            del news_Source['articles'][i]
            continue
        published = news_Source['articles'][i]['publishedAt'].split('-')
        news_Source['articles'][i]['publishedAt'] = published[1] + '/' + published[2][:2] + '/' + published[0]
        i += 1
    print(news_Source)

filterNews(top_headlines_google)
filterNews(top_headlines_cnn)
filterNews(top_headlines_fox)

word_Dic = {}
for i in range(len(top_headlines_google['articles'])):
    for itm in top_headlines_google['articles'][i]['title'].split():
        if itm.lower() not in stopwordList and itm.lower() not in puncList and itm.lower().isnumeric() == False and len(itm.lower()) > 1:
            try:
                word_Dic[itm.lower()] += 1
            except:
                word_Dic[itm.lower()] = 1

word_Dic = dict( sorted(word_Dic.items(), key=operator.itemgetter(1),reverse=True))

jsonArray = []

for k,v in word_Dic.items():
    if len(jsonArray) < 30:
        dic = {}
        dic['word'] = k.capitalize()
        dic['count'] = v
        jsonArray.append(dic)
    else:
        break

# /v2/everything
@app.route('/')
def home():
    return app.send_static_file('home.html')


@app.route('/google', methods=['GET'])
def google_route():
    try:
        # JSON_sent = request.get_json()
        # print(JSON_sent)

        # handle your JSON_sent here
        # Pass JSON_received to the frontend
        return jsonify(top_headlines_google)
    except Exception as e:
        print("GOOGLE excepted " + str(e))
        return str(e)

@app.route('/cnn', methods=['GET'])
def cnn_route():
    try:
        # JSON_sent = request.get_json()
        # print(JSON_sent)

        # handle your JSON_sent here
        # Pass JSON_received to the frontend
        return jsonify(top_headlines_cnn)
    except Exception as e:
        print("CNN excepted " + str(e))
        return str(e)

@app.route('/fox', methods=['GET'])
def fox_route():
    try:
        # JSON_sent = request.get_json()
        # print(JSON_sent)

        # handle your JSON_sent here
        # Pass JSON_received to the frontend
        return jsonify(top_headlines_fox)
    except Exception as e:
        print("Fox excepted " + str(e))
        return str(e)

@app.route('/stopWord', methods=['GET'])
def stopWord():
    try:
        return jsonify(jsonArray)
    except Exception as e:
        print("stopWord excepted " + str(e))
        return str(e)

@app.route('/queryTo', methods = ['GET'])
def queryTo():
    # response1 = request.form['Keyword']
    # print(Keyword)
    print(request.get_data())
    keyword = request.args.get('Keyword')
    startFrom = request.args.get('trip-from')
    startTo = request.args.get('trip-to')
    category = request.args.get('category')
    source = request.args.get('source')
    if source == 'all':
        source = None
    all_articles = dict()

    try:
        articles = newsapi.get_everything(q=keyword,    
                                            from_param=startFrom,
                                            to=startTo,
                                            language='en',
                                            sort_by='publishedAt',
                                            page_size = 100,
                                            sources = source)
        filterNews(articles)
        all_articles['article'] = articles
        all_articles['mgs'] = ""
        print(all_articles['article'])
    except NewsAPIException as e:
        print("Error Message", e.get_message())
        all_articles['article'] = None
        all_articles['mgs'] = e.get_message()
    try:
        return jsonify(all_articles)
    except Exception as e:
        print("Query excepted " + str(e))
        
@app.route('/querySource', methods=['GET'])
def querySource():
    category = request.args.get('category')
    if category == 'all':
        category = None
    categoryList = newsapi.get_sources(category=category, language='en', country='us')
    response = []
    response.append({'source_Name': 'all',
                    'source': 'all'})
    for i in range(len(categoryList['sources'])):
        dummyDic = {}
        if i < 10:
            dummyDic['source_Name'] = categoryList['sources'][i]['name']
            dummyDic['source'] = categoryList['sources'][i]['id']
            response.append(dummyDic)
        else:
            break
    try:
        return jsonify(response[:10])
    except Exception as e:
        print("Query excepted " + str(e))
        
@app.route('/json_All')
def search():
    return app.send_static_file('json_All.html')
    
if __name__ == '__main__':
    app.run(debug=True)