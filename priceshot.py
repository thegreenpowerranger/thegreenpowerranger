import streamlit as st
import time
import os
import pandas as pd
from datetime import datetime
import pickle
import numpy as np
from matplotlib import pyplot as plt 
from matplotlib import dates as mpl_dates

from dashboard_functions import html_scraper_galatec

#to run code: open terminal in same folder and "streamlit run test_streamlit.py"
st.set_page_config(page_title="Daily Price Shot Dashboard", page_icon=":shark:", layout="wide")

col1, col2, col3 = st.columns([1,2,1])
### ----------
with open('url.pkl', 'rb') as f:
    url = pickle.load(f)

df_parquet=pd.read_parquet('db.parquet')
df_parquet.sort_values(by=['date'],ascending=False)

article_list=df_parquet['articlenumber'].unique()
articles=[]
for i in article_list:
    #defining framework
    article=df_parquet[df_parquet['articlenumber']==i].sort_values(by='date',ascending=False)
    
    #capturing last row's (last update's) data via iloc0 since descending sortd
    articlenumber=article['articlenumber'].iloc[0]
    name=article['name'].iloc[0]
    last_price=article['price'].iloc[0]
    last_date=article['date'].iloc[0]
    
    lowest_price=article['price'].min()
    number_of_snapshots=article.shape[0]
    mean=article['price'].mean()
    std=article['price'].std()
    price_change_pct_mean=((last_price/mean)-1)*100
    price_change_abs=(last_price-mean)
    price_change_quartile=((last_price/article['price'].quantile(0.25))-1)*100
    
    article_url=article['source_link'].iloc[0]
    article_description=article['description'].iloc[0]
    article_type1=article['product_type1'].iloc[0]
    article_type2=article['product_type2'].iloc[0]
    article_type3=article['product_type3'].iloc[0]
    article_storage=article['storage'].iloc[0]
    article_discount=article['discount'].iloc[0]
    
    article_consolidated=[
    articlenumber,
    name,
    last_price,
    last_date,
    lowest_price,
    number_of_snapshots,
    mean,
    std,
    price_change_pct_mean,
    price_change_abs,
    price_change_quartile,
    article_url,
    article_description,
    article_type1,
    article_type2,
    article_type3,
    article_storage,
    article_discount
    ]

    articles.append(article_consolidated)

#needs to be consistent with above in for-loop columns
column_names=[
	'articlenumber',
	'name',
	'last_price',
	'last_date',
	'lowest_price',
	'number_of_snapshots',
	'mean',
	'std',
	'price_change_pct_mean',
	'price_change_abs',
	'price_change_quartile',
	'source_link',
   'description',
   'product_type1',
   'product_type2',
   'product_type3',
   'storage',
   'discount'
]

#df_articles represents entire article based dataframe with all columns
df_articles=pd.DataFrame(articles,columns=column_names)

df_dashboard_1=df_articles[df_articles['last_price'].notnull()][['name','price_change_pct_mean','articlenumber','last_price','discount']]
df_dashboard_1=df_dashboard_1.sort_values(by=['price_change_pct_mean'],ascending=True)

df_dashboard_2=df_articles[df_articles['last_price'].notnull()][['name','price_change_quartile','articlenumber','last_price','discount']]
df_dashboard_2=df_dashboard_2.sort_values(by=['price_change_quartile'],ascending=True)

watchlist=[
    '8605482',
    '362339',
    '13752255',
    '10296535',
    '17794023',
    '16771721',
    '20987855',
    '22490710'
]
df_watchlist=df_articles.loc[df_articles.apply(lambda x: x.articlenumber in watchlist, axis=1)][['name','last_price','price_change_pct_mean','articlenumber']]

### ---------

col1.markdown(" # Daily Price Shot :woman-golfing: Dashboard")
col1.write(" All prices and data sourced from Digitec Galaxus AG. :flag-ch: \n - https://www.digitec.ch \n- https://www.galaxus.ch \n \n")
col1.markdown(" ###### Watchlist Ranking :rainbow:")
col1.write("(Currently hard-coded watchlist products)")
col1.dataframe(df_watchlist)

col1.markdown(" ###### Check out what moves your product made! :dancer:")
articlenumber_searched=col1.text_input("Search for Articlenumber")
if articlenumber_searched!="":
   chart=df_parquet[df_parquet['articlenumber']==articlenumber_searched]
   chart_data=pd.DataFrame(df_parquet[df_parquet['articlenumber']==articlenumber_searched][['price','date']].set_index('date'))
   chart_name=df_articles[df_articles['articlenumber']==articlenumber_searched]['name'].iloc[0]
   chart_last_price=df_articles[df_articles['articlenumber']==articlenumber_searched]['last_price'].iloc[0]
   chart_mean=df_articles[df_articles['articlenumber']==articlenumber_searched]['mean'].iloc[0]
   chart_std=df_articles[df_articles['articlenumber']==articlenumber_searched]['std'].iloc[0]
   chart_type=df_articles[df_articles['articlenumber']==articlenumber_searched]['product_type1'].iloc[0]
   chart_storage=df_articles[df_articles['articlenumber']==articlenumber_searched]['storage'].iloc[0]
   chart_description=df_articles[df_articles['articlenumber']==articlenumber_searched]['description'].iloc[0]
   col1.markdown(f' ###### Historical Prices: {chart_name}')
   col1.line_chart(chart_data,use_container_width=True) #to individualize more use altair chart
   #this chart has been indexed with date
   #https://docs.streamlit.io/1.7.0/library/api-reference/charts/st.altair_chart
   
   with col1.expander("Click to see more details"):
      st.write(
         '- Last captured price: ' +str(chart_last_price)+'\n '
         + '- Arithmetic mean: ' +str(chart_mean)+'\n'
         + '- Standard deviation: ' +str(chart_std)+'\n'
         + '- Product type: ' +str(chart_type)+'\n'
         + '- Product storage: ' +str(chart_storage)+'\n'
         + '- Product description: ' +str(chart_description)+'\n'
         )
   col1.write('URL Link: '+str(df_articles[df_articles['articlenumber']==articlenumber_searched]['source_link'].iloc[0]))

col2.markdown(" ###### Find your piece :gift: (or your peace? :peace_symbol:)")
string=col2.text_input("Search for your product with below text box")
search_df=df_articles[df_articles['name'].str.contains(string)]
col2.dataframe(search_df)

col2.markdown(" ###### Add new products to our working list :weight_lifter:")
url_to_check=col2.text_input("Enter in below box your URL Link from Digitec Galaxus AG")
if url_to_check!="":
   with open('url.pkl', 'rb') as f:
    url = pickle.load(f)

   result=html_scraper_galatec(str(url_to_check))
   
   check_long_url=None
   check_short_url=None
   new_url=url_to_check
   new_url_short=str(new_url[(new_url.index('product/'))+len('product/'):])
   
   #test one
   if new_url in url:
       check_long_url='Failed, already existing'
   else:
       check_long_url='Success, not existing'
   #test two
   for i in url:
       if i.find(str(new_url_short))!=-1:
           check_short_url='Failed, already existing'
       elif check_short_url!='Failed, already existing':
           check_short_url='Success, not existing'
   
   check_articlenumber=None
   if df_articles['articlenumber'].eq(result['articlenumber']).any():
      check_articlenumber='Failed, already existing'
   else:
      check_articlenumber='Success, not existing'

   col2.write(
      f"Results on status of coverage: \n - Product in URL working list (identical): {check_long_url} \n - Product in URL working list (similar link): {check_short_url} \n  - Product in Database (historically): {check_articlenumber}\n "
      )

   if check_long_url=='Success, not existing' and check_short_url=='Success, not existing' and check_articlenumber=='Success, not existing':
      col2.success('Hurray we found your product and we can add it!')
      col2.write('We found below product on Digitec Galaxus AG platform. Please check whether all details are accurate. Thereafter, we check whether we can add it or not.')
      col2.write(result)

      col2.write('Do you want to add this product to our workinglist?')
      if col2.button('Hell yeah!'):
         url.append(url_to_check)
         with open('url.pkl','wb') as f: #read rb, write wb
            pickle.dump(url,f)
         col2.success("Well then hell fuckin yeah, we added your product to our working list!")

   elif check_long_url=='Success, not existing' and check_short_url=='Success, not existing' and check_articlenumber=='Failed, already existing':
      col2.warning('Product was in database but has been deleted :-( Do you want to add it again?)')
      col2.write('We found below product on Digitec Galaxus AG platform. Please check whether all details are accurate. Thereafter, we check whether we can add it or not.')
      col2.write(result)

      col2.write('Do you want to add this product to our workinglist?')
      if col2.button('Hell yeah!'):
         url.append(url_to_check)
         with open('url.pkl','wb') as f: #read rb, write wb
            pickle.dump(url,f)
         col2.success("Well then hell fuckin yeah, we added your product to our working list!")
   else:
      result_article=result['articlenumber']
      col2.error(f'Oh looks like we are already having your product on our working list. Maybe you are using a slightly different link or you just recently added this product, but there is no records yet available. Find more info with articlenumber: {result_article}')


time=datetime.fromtimestamp(os.path.getmtime("db.parquet")).strftime('%Y-%m-%d %H:%M:%S %Z')
col3.metric(label="Last Update Arrived at", value=time)
unique_products=len(article_list)
col3.metric(label="Number of Products in Database", value=unique_products)

unique_products_worklist=len(url)
col3.metric(label="Number of Products on Workinglist", value=unique_products_worklist)

col3.markdown(" ###### Top 10 Price Drops against mean :hot_pepper:")
col3.dataframe(df_dashboard_1.head(10))
col3.markdown(" ###### Top 10 Price Drops against 1st quartile :fire:")
col3.dataframe(df_dashboard_2.head(10))

#col3.download_button(label='Download URL list as CSV',data=df_articles.to_csv().encode('utf-8'),file_name=data.csv)