# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 03:08:13 2022

@author: Mary Jane MacArthur
"""

def get_yt_metadata(city_str):
    from googlesearch import search
    from googleapiclient.discovery import build
    import pandas as pd
    import numpy as np
    import datetime as dtm
    from statistics import mean
    
    query = 'youtube covid-19 ' + city_str
    
    URL_list = [] 
    for i in search(query, tld = 'com', num=20, stop=20, pause=2):
        if i[0:32] == 'https://www.youtube.com/watch?v=':   
            URL_list.append(i) 
    print(URL_list)
    
    #Gets the video ids from the URLs
    id_list = []
    for i in URL_list:
        i = i + '&'
        id_str = ''
        j = 0
        isurl = False
        while i[j] != '&':
            if isurl == True:
                id_str = id_str + i[j]
            if i[j] == '=':
                isurl = True
            j = j + 1
        id_list.append(id_str)  
        
    api_bad = True
    while api_bad:
        print("Enter an API key")
        api_key = input()
        service = build('youtube', 'v3', developerKey = api_key)
        try:
            request = service.videos().list(part = 'statistics',id=id_list[0]) 
            response = request.execute()
        except: 
            print("Not a valid API key. Please try again.")
            api_key = 'bad key'
        if api_key != 'bad key':
            api_bad = False 
    
    
    #Creates an empty data frame that will be populated with info from APIs
    yt_data_df = pd.DataFrame(np.nan, index=[i for i in range(len(URL_list))], columns=['URL','Video Title', 'Channel Title', 'Views', 'Likes', 'Dislikes', 'Comments', 'Date', 'Duration', 'Definition', 'Captions', 'Licensed Content'])
    yt_data_df['URL'] = [i for i in URL_list] 
    
    #Creates list that will be used for timestamps later
    datetime_str_list = []
    
    row_num = 0
    for i in id_list:
        request = service.videos().list(part = 'statistics',id=i) 
        response = request.execute()
        try:
            yt_data_df.loc[row_num, 'Views'] = response['items'][0]['statistics']['viewCount'] 
        except:
            yt_data_df.loc[row_num, 'Views'] = 0
        try:
            yt_data_df.loc[row_num, 'Likes'] = response['items'][0]['statistics']['likeCount'] 
        except:
            yt_data_df.loc[row_num, 'Likes'] = 0
        try:
            yt_data_df.loc[row_num, 'Dislikes'] = response['items'][0]['statistics']['dislikeCount'] 
        except:
            yt_data_df.loc[row_num, 'Dislikes'] = 0
        try:
            yt_data_df.loc[row_num, 'Comments'] = response['items'][0]['statistics']['commentCount'] 
        except:
            yt_data_df.loc[row_num, 'Comments'] = 0
        request = service.videos().list(part = 'contentDetails',id=i) 
        response = request.execute()
        duration_str = response['items'][0]['contentDetails']['duration']
        duration_str = duration_str.replace('PT', '')
        duration_str = duration_str.replace('H', ' hours ')
        duration_str = duration_str.replace('M', ' minutes ')
        duration_str = duration_str.replace('S', ' seconds')
        yt_data_df.loc[row_num, 'Duration'] = duration_str
        yt_data_df.loc[row_num, 'Definition'] = response['items'][0]['contentDetails']['definition'] 
        if response['items'][0]['contentDetails']['caption'] == 'true':
            yt_data_df.loc[row_num, 'Captions'] = 'Yes' 
        else:
            yt_data_df.loc[row_num, 'Captions'] = 'No'
        if response['items'][0]['contentDetails']['licensedContent'] == 'true':
            yt_data_df.loc[row_num, 'Licensed Content'] = 'Yes' 
        else:
            yt_data_df.loc[row_num, 'Licensed Content'] = 'No'
        request = service.videos().list(part = 'snippet',id=i) 
        response = request.execute()
        yt_data_df.loc[row_num, 'Date'] = (response['items'][0]['snippet']['publishedAt'])[0:10]
        vid_datetime = (response['items'][0]['snippet']['publishedAt'])[0:10] + ' ' + (response['items'][0]['snippet']['publishedAt'])[11:18]
        datetime_str_list.append(vid_datetime)
        yt_data_df.loc[row_num, 'Video Title'] = response['items'][0]['snippet']['title'] 
        yt_data_df.loc[row_num, 'Channel Title'] = response['items'][0]['snippet']['channelTitle'] 
        row_num = row_num + 1
    
    yt_data_df = yt_data_df.set_index('URL')
    
    datetime_list = []
    timestamp_list = []
    format = '%Y-%m-%d %H:%M:%S'
    for i in datetime_str_list:
        datetime_list.append(dtm.datetime.strptime(i, format))
    for i in datetime_list:
        timestamp_list.append(int(round(i.timestamp())))
    avg_ts = mean(timestamp_list) 
    ct = dtm.datetime.now()
    c_ts = int(round(ct.timestamp()))
    diff = c_ts - avg_ts 
    
    if diff <= 259200: #three days
        score = 5
    elif 259200 < diff <= 604800: #3-7 days
        score = 4
    elif 604800 < diff <= 1209600: #7-14 days
        score = 3
    elif 1209600 < diff <= 5184000: #2 weeks to 60 days
        score = 2
    elif 5184000 < diff <= 10368000: #60 to 120 days
        score = 1
    else:
        score = 0
    return_items = []
    return_items.append(yt_data_df)
    return_items.append(score)
    return return_items
    
    
if __name__ == "__main__":
    print("Enter a location")
    loc = input()
    results_list = get_yt_metadata(loc)