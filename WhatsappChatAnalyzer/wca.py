#----------------------------------Whatspp chat analysis-----------------------------------
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before pyplot import
import matplotlib.pyplot as plt
import pandas as pd 
import re
import seaborn as sns
from collections import Counter
from urlextract import URLExtract
import io
import base64
from wordcloud import WordCloud
from io import BytesIO
import emoji

# Add emoji-support font
plt.rcParams['font.family'] = 'Segoe UI Emoji'  # For Windows


def preprcessor(data):       
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\u202f\w{2}\s-\s"
    message=re.split(pattern,data)[1:]
    dates=re.findall(pattern,data)
    df=pd.DataFrame({'user_message': message,'message_dates':dates})
    #seprate user and their meassage
    user=[]
    messages=[]
    for message in df['user_message']:
        entery=re.split(r'([\w\W]+?):\s',message)
        if entery[1:]:
            user.append(entery[1])        
            messages.append(entery[2])
        else:
            user.append('group-notification')
            messages.append(entery[0])
    df['users']=user
    df['messages']=messages
    df=df.drop(columns=['user_message'])
    #convert to datetime format
    df['message_dates'] = pd.to_datetime(df['message_dates'], format='%m/%d/%y, %I:%M %p - ', errors='coerce')
    df=df.rename(columns={'message_dates':'date'})
    df['year']=df['date'].dt.year
    df['month']=df['date'].dt.month_name()
    df['day']=df['date'].dt.day
    df['hour']=df['date'].dt.hour
    df['minutes']=df['date'].dt.minute    
    return df

def gen_active_user_plot(df):
     
    #--------Graph of busy users-------- 
    x=df['users'].value_counts().head()
    
    fig, ax=plt.subplots()
    ax.bar(x.index,x.values,color='red', edgecolor='#ffffff')    
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')     

    # Set the title and labels
    ax.set_title('Most Active Users',color='#ffffff')
    ax.set_xlabel('Users',color='#ffffff')
    ax.set_ylabel('Messages',color='#ffffff')  

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff') 
    

    # Save the plot to a bytes buffer 
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    b_users_graph = graph.decode('utf-8')    
    return b_users_graph

def gen_wordcloud(df):    
    wc= WordCloud(width=1300,height=1100,background_color='#333333',min_font_size=20) 
    df_wc=wc.generate(df['messages'].str.cat(sep=" "))
    # Create a matplotlib figure  
    
    plt.figure(figsize=(9, 7),facecolor='#333333',edgecolor='white')    
    plt.imshow(df_wc, interpolation='bilinear')    
    
    
    # Save the image to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image to base64 so it can be embedded inline in HTML
    wc_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()    
    return wc_graph

def most_common_word(df):
    f=open('stop_hinglish.txt','r')
    stop_word=f.read()
    df=df[df['messages'] !='group-notification']
    df=df[df['messages'] !='<Media omitted>\n']
    words=[]
    for message in df['messages']:
        for word in message.lower().split():
            if word not in stop_word:
                words.append(word)
    mcw_df=pd.DataFrame(Counter(words).most_common(20))    
    fig, ax=plt.subplots()
    ax.barh(mcw_df[0],mcw_df[1],color='red', edgecolor='#ffffff')    
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')     

    # Set the title and labels
    ax.set_title('Most Common Word',color='#ffffff')
    ax.set_xlabel('Count',color='#ffffff')
    ax.set_ylabel('Words',color='#ffffff')  

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff')                

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    mcw_graph = graph.decode('utf-8')
    return mcw_graph

def emoji_analysis(df):
    emjis=[]
    for message in df['messages']:
        emjis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df=pd.DataFrame(Counter(emjis).most_common(len(Counter(emjis))))
    
    fig, ax=plt.subplots()
    ax.pie(emoji_df[1].head(10),labels=emoji_df[0].head(10),shadow=True,autopct="%0.2f")    
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')     

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    emoji_graph = graph.decode('utf-8')
    return emoji_graph,emoji_df

def show_dataframe(df):    
    # Convert DataFrame to HTML
    df_html = df.to_html(classes='table table-bordered', index=False)
    return df_html

def monthly_timeline(df,user="Overall"):

    if user != 'Overall':
        df=df[df['users']==user]
    df['month_num']=df['date'].dt.month
    timeline=df.groupby(['year', 'month_num','month']).count()['messages'].reset_index()
    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    timeline['time']=time
    #plot  
    fig, ax=plt.subplots()    
    ax.plot(timeline['time'],timeline['messages'],color='green')      
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333') 
    plt.xticks(rotation='vertical')       

    # Set the title and labels
    ax.set_title('Monthly Timeline',color='#ffffff')
    ax.set_xlabel('Time',color='#ffffff')
    ax.set_ylabel('Messages',color='#ffffff') 

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff')               

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    MTL_Plot = graph.decode('utf-8')
    return MTL_Plot

def daily_timeline(df,user="Overall"):

    if user != 'Overall':
        df=df[df['users']==user]
    df['only_date']=df['date'].dt.date
    daily_timeline=df.groupby('only_date').count()['messages'].reset_index()
    
    #plot 
     
    fig, ax=plt.subplots()
    ax.plot(daily_timeline['only_date'],daily_timeline['messages'],color='orange')      
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333') 
    plt.xticks(rotation='vertical')       

    # Set the title and labels
    ax.set_title(' Timeline',color='#ffffff')
    ax.set_xlabel('Time',color='#ffffff')
    ax.set_ylabel('Messages',color='#ffffff') 

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff')
               

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    DTL_Plot = graph.decode('utf-8')
    return DTL_Plot

def most_active_day(df,user="Overall"):
    if user != 'Overall':
        df=df[df['users']==user]
    df['days']=df['date'].dt.day_name()
    mad=df['days'].value_counts()
    
    fig, ax=plt.subplots()
    ax.bar(mad.index,mad.values,color='yellow', edgecolor='#ffffff')    
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')     

    # Set the title and labels
    ax.set_title('Most Active Day',color='#ffffff')
    ax.set_xlabel('Day',color='#ffffff')
    ax.set_ylabel('Messages',color='#ffffff')  

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff')
                

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    most_active_day = graph.decode('utf-8')
    return most_active_day

def most_active_month(df,user="Overall"):
    if user != 'Overall':
        df=df[df['users']==user]    
    mam=df['month'].value_counts()
    
    fig, ax=plt.subplots()
    ax.bar(mam.index,mam.values,color='blue', edgecolor='#ffffff')    
    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')     

    # Set the title and labels
    ax.set_title('Most Active Month',color='#ffffff')
    ax.set_xlabel('Month',color='#ffffff')
    ax.set_ylabel('Messages',color='#ffffff')  

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(grid_color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#ffffff')            
    ax.spines['left'].set_color('#ffffff')
                

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    most_active_months = graph.decode('utf-8')
    return most_active_months

def dt_heatmap(df,user="Overall"):
    if user != 'Overall':
        df=df[df['users']==user]    
    period=[]
    for hour in df[['days','hour']]['hour']:
        if hour == 23:
            period.append(str(hour)+"-"+str('00'))
        elif hour == 0:
            period.append(str('00')+"-"+str(hour+1))
        else:
            period.append(str(hour)+"-"+str(hour+1))
    df['period']=period
    user_heatmap=df.pivot_table(index='days',columns='period',values='messages',aggfunc='count').fillna(0)
    
    fig, ax=plt.subplots()
    ax=sns.heatmap(user_heatmap, cmap="bwr") 

    fig.set_facecolor('#333333')
    ax.set_facecolor('#333333')   

    # Customize tick label colors
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')    
    
    ax.set_xlabel('Days',color='#ffffff')
    ax.set_ylabel('Time Period',color='#ffffff')
     

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the bytes buffer to a base64 string
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    activity_heatmap = graph.decode('utf-8')
    return activity_heatmap

def fetch_stats(df,user="Overall"):
    b_users_graph=gen_active_user_plot(df)  
    
    if user != 'Overall':
        df=df[df['users']==user]
    #----------Total Mssages------------
    num_messages= df.shape[0] 
    #---------------Total words---------
    words=[]
    for word in df['messages']:
        words.extend(word.split())  
    #-----------Shared Media------------
    num_media_messages=df[df['messages']=='<Media omitted>\n'].shape[0] 
    #-----------shared Links------------
    extract=URLExtract()
    links=[]
    for link in df['messages']:
        links.extend(extract.find_urls(link)) 
    #--------------wordcloud------------
    wc_graph=gen_wordcloud(df)
    #------most common word plot-----------
    mcw_graph=most_common_word(df)  
    #----------emogi plot----------------
    emoji_plot,emoji_df=emoji_analysis(df) 
    emoje_df=show_dataframe(emoji_df)
    return num_messages,len(words),num_media_messages,len(links),links,b_users_graph,wc_graph,mcw_graph,emoji_plot,emoje_df
    
