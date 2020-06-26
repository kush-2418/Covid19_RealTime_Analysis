#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 23:11:26 2020

@author: kush
"""
# Import Libraries  ****************************************************************************'''

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import geopandas as gpd
import streamlit as st
from PIL import Image
import descartes #pip install descartes
import tweepy
import re
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import datetime

#  Main Function   ****************************************************************************'''


def main():

    # Fetch WorldWide Data ****************************************************************************'''

    def fetchWorldData(day): # returns world dataframe
        if day == 'Today':
            id1= "main_table_countries_today"
        elif day == 'Yesterday':
            id1 = "main_table_countries_yesterday"
        else:
            id1 ='main_table_countries_yesterday2'
            # Testing the URL and sending request to grab HTML data
        URL = 'https://www.worldometers.info/coronavirus/#countries'
        html_page = requests.get(URL).text
        # BeautifulSoup for extracting table data
        soup = BeautifulSoup(html_page,'lxml')
        get_table = soup.find("table",id =id1) # this will get from inspect from webpage
        get_table_data = get_table.tbody.find_all("tr")
    
        dicts ={}
        
            # one tr has one line of table
        for i in range(len(get_table_data)):
            try:
                key = (get_table_data[i].find_all('a',href=True)[0].string)
            except:
                key = (get_table_data[i].find_all('td')[0].string)
            value = [j.string for j in get_table_data[i].find_all('td')]
            dicts[key]= value
        column_names = ['Total Cases','New Cases','Total Deaths','New Deaths', 'Total Recovered','New Recovered','Active Cases','Serious Critical','Tot Cases/1M pop','Total Death/1M pop','Total Tests']
        df= pd.DataFrame(dicts).iloc[2:,:].T.iloc[:,:11] #11 columns
        covid_day = df.loc[df.index.dropna()]
        covid_day.index_name = 'Country'
        covid_day.columns = column_names
        return covid_day
   
#  Fetch Continent Data  ****************************************************************************'''


    def fetchContinentData(day,name):
        if name == 'Select':
            pass
        else:
         
            column_names = ['Countries','Total Cases','New Cases','Total Deaths','New Deaths', 'Total Recovered','New Recovered','Active Cases','Serious Critical','Tot Cases/1M pop','Total Death/1M pop','Total Tests','Tests/1M pop']
    
            url = 'https://www.worldometers.info/coronavirus/#countries'
            html = requests.get(url).text
        
            # BeautifulSoup for extracting table data
            soup = BeautifulSoup(html,'lxml')
            table = soup.find('table',id = ids)
            table_data = table.tbody.find_all('tr')
            dicts = {}
            for i in range(len(table_data)):
                key = (table_data[i].find_all('td')[0].string)
                value = [j.string for j in table_data[i].find_all('td')]
                dicts[key]= value
            continen =[]
            for i in dicts.values():
                if i[15] == name:
                    continen.append(i[1:14])
            contin = pd.DataFrame(continen)
            contin.columns = column_names
            contin.drop(['Tests/1M pop'],axis=1,inplace=True)                
            return contin
                
#  Fetch India Data  ****************************************************************************'''

    def fetchIndiaData():
        url = 'https://www.mohfw.gov.in/'
        web_content = requests.get(url).content
        soup = BeautifulSoup(web_content, "html.parser")
        extract_contents = lambda row: [x.text.replace('\n', '') for x in row]
        stats = [] 
        all_rows = soup.find_all('tr')
        for row in all_rows:
            stat = extract_contents(row.find_all('td')) 
            if len(stat) == 6:
                stats.append(stat)
        #now convert the data into a pandas dataframe for further processing
        new_cols = ["Sr.No", "States/UT","Active","Cured","Deaths","Confirmed"]
        India_data = pd.DataFrame(data = stats, columns = new_cols)
        India_data = India_data.replace(r'^\s*$', np.nan, regex=True)
        India_data =India_data.replace(np.nan, 0)
        India_data.drop(India_data.index[36],inplace=True)
        India_data = India_data.drop(['Sr.No'],axis=1)
        
        date_time = soup.find('div',class_="status-update")
        date_time = extract_contents(date_time.find_all('h2'))
        date_time = str(date_time[0])
        time = date_time.split(':',1)[1]
        time = time[:24].strip().replace('\t',' ')
        return India_data,time
        
# Converts String data to Integer for World Wide Data ****************************************************************************'''
     
    def convertWorldFrame(covid_df):
        def conve_to_int(i):
             i = i.strip('+')
             i = int(i)
             return i
    
        def conv_to_int(i):
            return int(i)
        covid_df['Countries'] = covid_df.index
        covid_df = covid_df.reset_index()
        covid_df = covid_df.drop(['index'],axis=1)
        cols = list(covid_df.columns)
        cols = [cols[-1]] + cols[:-1]
        covid_df = covid_df[cols]
        covid_df = covid_df.replace('None', np.nan, regex=True)
        covid_df = covid_df.replace("",np.nan,regex=True)
        covid_df = covid_df.replace('N/A',np.nan,regex=True)
        covid_df = covid_df.replace(',','',regex=True)
        covid_df = covid_df.drop(['Total Death/1M pop'],axis=1)
        covid_df =covid_df.replace(np.nan, 0)
        new_cols = ['New Cases','New Deaths','New Recovered']
        for i in new_cols:
            covid_df[i] = covid_df[i].astype(str)
            covid_df[i] = covid_df[i].apply(lambda x: conve_to_int(x))
        covid_df['Total Deaths'] = covid_df['Total Deaths'].replace(' ','0')
        covid_df['Total Deaths']= covid_df['Total Deaths'].astype(str)
        covid_df['Total Cases']= covid_df['Total Cases'].astype(str)
        covid_df['Total Recovered']= covid_df['Total Recovered'].astype(str)
        covid_df['Active Cases']= covid_df['Active Cases'].astype(str)
        covid_df['Serious Critical'] = covid_df['Serious Critical'].astype(str)
        covid_df['Tot Cases/1M pop']= covid_df['Tot Cases/1M pop'].astype(str)
        covid_df['Total Tests']= covid_df['Total Tests'].astype(str)
        tot_cols = ['Total Cases','Total Recovered','Active Cases','Total Deaths','Serious Critical','Tot Cases/1M pop','Total Tests']
        for i in tot_cols:
            covid_df[i] = covid_df[i].apply(lambda x: conv_to_int(x))
        return covid_df
    
    
#  Converts String data to Integer for Continent Data  ****************************************************************************'''
     
    def convertContinentFrame(covid_df):
        def conve_to_int(i):
             i = i.strip('+')
             i = int(i)
             return i
    
        def conv_to_int(i):
            return int(i)

        covid_df = covid_df.replace('None', np.nan, regex=True)
        covid_df = covid_df.replace("",np.nan,regex=True)
        covid_df = covid_df.replace('N/A',np.nan,regex=True)
        covid_df = covid_df.replace(',','',regex=True)
        covid_df = covid_df.drop(['Total Death/1M pop'],axis=1)
        covid_df =covid_df.replace(np.nan, 0)
        new_cols = ['New Cases','New Deaths','New Recovered']
        for i in new_cols:
            covid_df[i] = covid_df[i].astype(str)
            covid_df[i] = covid_df[i].apply(lambda x: conve_to_int(x))
        covid_df['Total Deaths'] = covid_df['Total Deaths'].replace(' ','0')
        covid_df['Total Deaths']= covid_df['Total Deaths'].astype(str)
        covid_df['Total Cases']= covid_df['Total Cases'].astype(str)
        covid_df['Total Recovered']= covid_df['Total Recovered'].astype(str)
        covid_df['Active Cases']= covid_df['Active Cases'].astype(str)
        covid_df['Serious Critical'] = covid_df['Serious Critical'].astype(str)
        covid_df['Tot Cases/1M pop']= covid_df['Tot Cases/1M pop'].astype(str)
        covid_df['Total Tests']= covid_df['Total Tests'].astype(str)
        tot_cols = ['Total Cases','Total Recovered','Active Cases','Total Deaths','Serious Critical','Tot Cases/1M pop','Total Tests']
        for i in tot_cols:
            covid_df[i] = covid_df[i].apply(lambda x: conv_to_int(x))
        return covid_df    
        
    
#  Convert String to Integer for India Data  ****************************************************************************'''

    def convertIndiaFrame(India_data):
        def conve_to_int(i):
             i = i.strip('+')
             i = int(i)
             return i
    
        def conv_to_int(i):
            return int(i)
        India_data['Active'] = India_data['Active'].astype(int)
        India_data['Cured'] = India_data['Cured'].astype(str)
        India_data['Cured'] = India_data['Cured'].apply(lambda x: conve_to_int(x))
        India_data['Deaths'] = India_data['Deaths'].astype(str)
        India_data['Deaths'] = India_data['Deaths'].apply(lambda x: conve_to_int(x))
        India_data['Confirmed'] = India_data['Confirmed'].astype(str)
        India_data['Confirmed'] = India_data['Confirmed'].apply(lambda x: conve_to_int(x))
        
        return India_data
    
#  Show Highest/Lowest Cases for World and Continent   ****************************************************************************'''

     

    def showCases(covid_df,status,slide,asc):
        if status=="Total Cases":
            cd = covid_df[['Countries','Total Cases']].sort_values(by='Total Cases',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))
        elif status=="Total Recovered":
            cd = covid_df[['Countries','Total Recovered']].sort_values(by='Total Recovered',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="New Recovered":
            cd= covid_df[['Countries','New Recovered']].sort_values(by='New Recovered',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="New Cases":
            cd = covid_df[['Countries','New Cases']].sort_values(by='New Cases',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="Active Cases":
            cd = covid_df[['Countries','Active Cases']].sort_values(by='Active Cases',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="Total Deaths":
            cd = covid_df[['Countries','Total Deaths']].sort_values(by='Total Deaths',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="New Deaths":
            cd = covid_df[['Countries','New Deaths']].sort_values(by='New Deaths',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        elif status=="Serious Critical Cases":
            cd = covid_df[['Countries','Serious Critical']].sort_values(by='Serious Critical',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

        else:
            rcd = covid_df[['Countries','New Deaths']].sort_values(by='New Deaths',ascending =asc,ignore_index=True).head(slide)
            return st.table(cd.style.background_gradient(cmap='Reds'))

#  Show Highest/Lowest Cases for India   ****************************************************************************'''
     
    def showCasesIndia(India_df,status,slide,asc):
        if status=="Active":
            idf = India_df[['States/UT','Active']].sort_values(by='Active',ascending =asc,ignore_index=True).head(slide)
            return st.table(idf.style.background_gradient(cmap='Reds'))

        elif status=="Cured":
            idf = India_df[['States/UT','Cured']].sort_values(by='Cured',ascending =asc,ignore_index=True).head(slide)
            return st.table(idf.style.background_gradient(cmap='Reds'))

        elif status=="Deaths":
            idf = India_df[['States/UT','Deaths']].sort_values(by='Deaths',ascending =asc,ignore_index=True).head(slide)
            return st.table(idf.style.background_gradient(cmap='Reds'))
      
        else :
            idf = India_df[['States/UT','Confirmed']].sort_values(by='Confirmed',ascending =asc,ignore_index=True).head(slide)
            return st.table(idf.style.background_gradient(cmap='Reds'))

#  Show Bar Charts wrt Total Cases  ****************************************************************************'''
     
                
    def bar_chartTC(df_bar,bars):
        if bars == 'Select':
            pass
        else:
            xl = df_bar[bars].max()
            sns.set(style="darkgrid")
            sns.set(font_scale=1.2)
    
            f,ax = plt.subplots(figsize=(10,8))
            df_bar = df_bar.sort_values(bars,ascending=False)
            sns.set_color_codes('pastel')
            sns.barplot(x='Total Cases',y='Countries',data=df_bar,label="Total Cases",color='red') 
            sns.set_color_codes("muted")
            sns.barplot(x=bars,y='Countries',data=df_bar,label=bars,color='green')
            ax.legend(ncol=3,loc='lower right',frameon=True)
            ax.set(xlim=(0,xl))                                                 
            sns.despine(left=True, bottom=True)
            plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
            for index, value in enumerate(df_bar[bars]):
                plt.text(value, index, str(value), fontsize = 12, verticalalignment = 'center')
            for index, value in enumerate(df_bar['Total Cases']):
                plt.text(value, index, str(value), fontsize = 12, verticalalignment = 'top')
            st.pyplot()

#  Show Bar Charts  for World and Continents  ****************************************************************************'''
     
            
    def bar_chartCon(df_bar1,cbar):
        sns.set(style="darkgrid")
        sns.set(font_scale=1.2)
        plt.rcParams['figure.figsize']=10,8
        ax = df_bar1.plot(kind='bar',x='Countries',y=cbar)
        plt.subplots_adjust(bottom= 0.2, top = 0.98)
        plt.xticks(rotation=45)

        ax.set(xlabel='Countries',ylabel=cbar)
        totals = []
    
        # find the values and append to list
        for i in ax.patches:
            totals.append(i.get_height())
        total = sum(totals)
        for i in ax.patches:
            # get_width pulls left or right; get_y pushes up or down
            ax.text(i.get_x()-.03, i.get_height()+.5,str(i.get_height()), fontsize=15,
                    color='red')
        st.pyplot()
        
#  Show Bar Charts for India  ****************************************************************************'''
     
        
    def bar_chartState(df_bar1,cbar):
    
        sns.set(style="darkgrid")
        sns.set(font_scale=1.2)
        plt.rcParams['figure.figsize']=12,8
        ax = df_bar1.plot(kind='barh',x='States/UT',y=cbar)
        plt.subplots_adjust(bottom= 0.2, top = 0.98)
        plt.yticks(rotation=25)


        ax.set(xlabel='States/UT',ylabel=cbar)
        for index, value in enumerate(df_bar1[cbar]):
            plt.text(value, index, str(value), fontsize = 12, verticalalignment = 'top')
        st.pyplot()   
        
#  Show Pie Charts for World and Continents   ****************************************************************************'''
    
     
    def pie_chart(covid_df,don): # a1
        
        a1 = ["Total Cases","Total Recovered",'Total Deaths']
        b1 = ["Total Cases","Total Recovered","Active Cases"]
        c1 = ["Total Cases","Total Recovered","Serious Critical"]
        d1 = ['Total Cases','Total Deaths','Active Cases']
        e1 = ['Total Cases','Total Deaths','Serious Critical']
        f1 = ['Total Cases','Active Cases','Serious Critical']
        g1 = ["Total Recovered",'Total Deaths',"Active Cases"]
        h1 = ["Total Recovered",'Total Deaths',"Serious Critical"]
        i1 = ["Total Recovered",'Active Cases',"Serious Critical"]
        j1 = ['Total Deaths',"Active Cases","Serious Critical"]
        try:
        
            if don == a1:
                a = a1[0]
                b = a1[1]
                c = a1[2]
                c1 = 'skyblue'
                c2 = 'yellowgreen'
                c3 = 'red'
            elif don == b1:
                a = b1[0]
                b = b1[1]
                c = b1[2]
                c1 = 'skyblue'
                c2 = 'yellowgreen'
                c3 = 'tomato'
            elif don == c1:
                a = c1[0]
                b = c1[1]
                c = c1[2]
                c1 = 'skyblue'
                c2 = 'yellowgreen'
                c3 = 'indigo'
            elif don == d1:
                a = d1[0]
                b = d1[1]
                c = d1[2]
                c1 = 'skyblue'
                c2 = 'red'
                c3 = 'tomato'
            elif don == e1:
                a = e1[0]
                b = e1[1]
                c = e1[2]
                c1 = 'skyblue'
                c2 = 'red'
                c3 = 'indigo'
            elif don == f1:
                a = f1[0]
                b = f1[1]
                c = f1[2]
                c1 = 'skyblue'
                c2 = 'tomato'
                c3 = 'indigo'
            elif don == g1:
                a = g1[0]
                b = g1[1]
                c = g1[2]
                c1 = 'yellowgreen'
                c2 = 'red'
                c3 = 'tomato'
            elif don == h1:
                a = h1[0]
                b = h1[1]
                c = h1[2]
                c1 = 'yellowgreen'
                c2 = 'red'
                c3 = 'indigo'
            elif don == i1:
                a = i1[0]
                b = i1[1]
                c = i1[2]
                c1 = 'yellowgreen'
                c2 = 'tomato'
                c3 = 'indigo'
            elif don == j1:
                a = j1[0]
                b = j1[1]
                c = j1[2]
                c1 = 'red'
                c2 = 'tomato'
                c3 = 'indigo'
       
            sns.set(style="darkgrid")
            sns.set(font_scale=0.9)
            group_size = [sum(covid_df[a]),
                          sum(covid_df[b]),
                          sum(covid_df[c])]
            group_labels = ['{}\n'.format(a) + str(sum(covid_df[a])),
                            '{}\n'.format(b)+ str(sum(covid_df[b])),
                            '{}\n'.format(c) + str(sum(covid_df[c]))]
            custom_colors = [c1,c2,c3]
            plt.subplots(figsize = (6,3),subplot_kw=dict(aspect="equal"))
            plt.pie(group_size, labels = group_labels, colors = custom_colors)
            central_circle = plt.Circle((0,0), 0.6, color = 'white')
            fig = plt.gcf()
            fig.gca().add_artist(central_circle)
            plt.title('{},{} and {} Cases in World'.format(a,b,c), fontsize = 10)
            st.pyplot()
        except UnboundLocalError:
            st.error("Please select in sequence")
#  Show Pie Charts for India  ****************************************************************************'''

     
    def donut_chartIndia(India_df,don): 
        a1 = ["Active","Cured",'Deaths']
        b1 = ["Active","Cured",'Confirmed']
        c1 = ["Active",'Deaths','Confirmed']
        d1 = ["Cured","Deaths",'Confirmed']
        try:
        
            if don == a1:
                a = a1[0]
                b = a1[1]
                c = a1[2]
                c1 = 'skyblue'
                c2 = 'yellowgreen'
                c3 = 'red'
            elif don == b1:
                a = b1[0]
                b = b1[1]
                c = b1[2]
                c1 = 'skyblue'
                c2 = 'yellowgreen'
                c3 = 'tomato'
            elif don == c1:
                a = c1[0]
                b = c1[1]
                c = c1[2]
                c1 = 'skyblue'
                c2 = 'red'
                c3 = 'tomato'
            elif don == d1:
                a = d1[0]
                b = d1[1]
                c = d1[2]
                c1 = 'yellowgreen'
                c2 = 'red'
                c3 = 'tomato'
     
            sns.set(style="darkgrid")
            sns.set(font_scale=0.9)
            group_size = [sum(India_df[a]),
                          sum(India_df[b]),
                          sum(India_df[c])]
            group_labels = ['{}\n'.format(a) + str(sum(India_df[a])),
                            '{}\n'.format(b)+ str(sum(India_df[b])),
                            '{}\n'.format(c) + str(sum(India_df[c]))]
            custom_colors = [c1,c2,c3]
            plt.subplots(figsize = (6,3),subplot_kw=dict(aspect="equal"))
            plt.pie(group_size, labels = group_labels, colors = custom_colors)
            central_circle = plt.Circle((0,0), 0.6, color = 'white')
            fig = plt.gcf()
            fig.gca().add_artist(central_circle)
            plt.title('{},{} and {} Cases in India'.format(a,b,c), fontsize = 10)
            st.pyplot()
        except UnboundLocalError:
            st.error("Please select in sequence")
            
            
  #  Show Percentage Charts for World and Continents   ****************************************************************************'''
     
    def percentage_charts(df,inputs):
        if inputs =='Select':
            pass
        else:
            fig, ax = plt.subplots(figsize=(9, 8), subplot_kw=dict(aspect="equal"))
            state = df['Countries'].head(10)
            cases = df[inputs].head(10)
            def func(pct, allvals):
                absolute = int(pct/100.*np.sum(allvals))
                return "{:.1f}%\n({:d})".format(pct, absolute)
            wedges, texts, autotexts = ax.pie(cases, autopct=lambda pct: func(pct, cases),
                                             textprops=dict(color="black"),counterclock=True, shadow=True)
            plt.legend(state, loc="upper right")
            ax.set_title("Percentage of {} in Different Countries".format(inputs,))
            plt.setp(autotexts,size=9,weight='bold')
            st.pyplot()
            
            

#  Show Percentage Charts for India  ****************************************************************************'''
     
    def percentage_chartsInd(df,inputs):
        if inputs =='Select':
            pass
        else:
            df = df[['States/UT',inputs]].sort_values(by=inputs,ascending =False,ignore_index=True)
            fig, ax = plt.subplots(figsize=(9, 8))
            state = df['States/UT'].head(7)
            cases = df[inputs].head(7)
            def func(pct, allvals):
                absolute = int(pct/100.*np.sum(allvals))
                return "{:.1f}%\n({:d})".format(pct, absolute)
            wedges, texts, autotexts = ax.pie(cases, autopct=lambda pct: func(pct, cases),pctdistance = .5,
                                              textprops=dict(color="black"),counterclock=True, shadow=True)
            #wedges,texts,autotexts = ax.pie(cases, explode=explode,autopct='%1.2f%%',shadow=True, radius=3)

            plt.legend(state, loc="upper right")
            ax.set_title("Percentage of {} cases in different States/UT".format(inputs,))
            plt.setp(autotexts,size=11,weight='bold')
            st.pyplot()    

#  Show Country Overview   ****************************************************************************'''
     
    def country_overview(df,cont):
        x = df[df['Countries']==cont]
        blankIndex=[''] * len(x)
        x.index=blankIndex
        st.success("The Total COVID19 Cases in {} are {} with {} Recovered Cases".format(x['Countries'][0],x['Total Cases'][0],x['Total Recovered'][0]))
        st.info("Till date {} Covid19 tests have been performed".format(x['Total Tests'][0]))
        st.warning("Currently the Active cases in {} are {} with {} Serious Critical Cases".format(x['Countries'][0],x['Active Cases'][0],x['Serious Critical'][0]))
        st.info("The New cases in {} are {} with {} New Death Cases".format(x['Countries'][0],x['New Cases'][0],x['New Deaths'][0]))
        st.error("As of today {} people have been died due to Covid19".format(x['Total Deaths'][0]))
        
        
#  Show States Overview   ****************************************************************************'''
     
    def states_overview(df,cont,time):
        x = df[df['States/UT']==cont]
        blankIndex=[''] * len(x)
        x.index=blankIndex
        st.success("As of {} the Total Confirmed COVID19 Cases in {} are {}".format(time,x['States/UT'][0],x['Confirmed'][0]))
        st.warning("Currently the Active cases in {} are {}".format(x['States/UT'][0],x['Active'][0]))
        st.info("The {} patients have been cured till date ".format(x['Cured'][0]))
        st.error("Till now {} people have been died due to Covid19".format(x['Deaths'][0]))
        
        
#  Quick Analysis   ****************************************************************************'''
     
    def quickAnalysisWorldCont(df_data,cn):
        x = convertContinentFrame(df_data)
        st.success("The Total COVID19 Cases in {} are {} with {} Recovered Cases".format(cn,x['Total Cases'].sum(),x['Total Recovered'].sum()))
        st.info("Till date {} Covid19 tests have been performed".format(x['Total Tests'].sum()))
        st.warning("Currently the Active cases in {} are {} with {} Serious Critical Cases".format(cn,x['Active Cases'].sum(),x['Serious Critical'].sum()))
        st.info("The New cases in {} are {} with {} New Death Cases".format(cn,x['New Cases'].sum(),x['New Deaths'].sum()))
        st.error("Total {} people have been died due to Covid19".format(x['Total Deaths'].sum()))
    
#  Plot Maps   ****************************************************************************'''
     
    def IndiaMapdfMerged(India_data):
        map_data = gpd.read_file('India_geom/Indian_States.shp')
        map_data.rename(columns = {'st_nm':'States/UT'}, inplace = True)
        map_data['States/UT'] = map_data['States/UT'].str.replace('&', 'and')
        map_data['States/UT'].replace('Arunanchal Pradesh', 'Arunachal Pradesh', inplace = True)
        map_data['States/UT'].replace('Telangana', 'Telengana', inplace = True)
        map_data['States/UT'].replace('NCT of Delhi', 'Delhi', inplace = True)

        # merge both the dataframes - state_data and map_data
        merged_data = pd.merge(map_data, India_data, how = 'left', on = 'States/UT')
        return merged_data
     
    def plotIndiaMap(merged_df,maps):
        fig, ax = plt.subplots(1, figsize=(10, 12))
        ax.axis('off')
        ax.set_title('Covid-19 State/UT Wise — {} Cases'.format(maps), 
                     fontdict =  {'fontsize': '25', 'fontweight' : '3'})
        merged_df.plot(column = maps, cmap='YlGnBu', 
                         linewidth=0.8, ax=ax, edgecolor='0.8', 
                         legend = True)
        st.pyplot()       
        
#  World Wide Analysis   ****************************************************************************'''

        
    def worldWideAnalysis(world_df):
    
        covid_df = convertWorldFrame(world_df)
        
        if st.checkbox("Show/Hide Whole Data"):
            st.table(world_df)
        st.sidebar.markdown("<body style='background-color:blue;'><h3 style='text-align: center; color: white;'>Please Select the Tasks</h3></body>", unsafe_allow_html=True)
        world = st.sidebar.selectbox("",(["Select","Show Countries with Highest Cases","Show Countries with Lowest Cases","Country Wise Quick Update","Show Bar Graphs","Show Pie Charts","Show Percentage Charts"]))
        if world== "Select":
            pass
        elif world == "Show Countries with Highest Cases":
            high = st.slider("",5,25)
            st.success('{} Countries with Highest Cases'.format(high))
            
            asc=False
            status = st.radio("",("Total Cases","Total Recovered","New Recovered","New Cases","Active Cases",'Total Deaths',"New Deaths","Serious Critical Cases"))
            showCases(covid_df,status,high,asc)

        elif world == 'Show Countries with Lowest Cases':
            low = st.slider("",5,25)
            st.success('{} Countries with Lowest Cases'.format(low))
            asc = True
            status = st.radio("",("Total Cases","Total Recovered","New Recovered","New Cases","Active Cases",'Total Deaths',"New Deaths","Serious Critical Cases"))
            showCases(covid_df,status,low,asc)
            
        elif world == "Country Wise Quick Update":
            world_df['Countries'] = world_df.index
            world_df = world_df.reset_index()
            world_df = world_df.drop(['index'],axis=1)
            country_df = world_df['Countries'].values
            con_list = list(country_df)
        
            cont = st.selectbox("",con_list)
            country_overview(world_df,cont)
        
                
        elif world == "Show Bar Graphs":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Bar Graphs</h3></body>", unsafe_allow_html=True)
            if st.checkbox("Total Cases vs"):
                bar_cols = ['Select','Total Deaths', 'Total Recovered','New Recovered','Active Cases','Serious Critical','Total Tests']
                color_code = ['#f57542','#42f5a1','#d6413c','#5c6cd1','#e80c17']
                bars = st.selectbox("",bar_cols)
                df_bar =covid_df.head(10)
                bar_chartTC(df_bar,bars)
                
            if st.checkbox("Countries vs"):
                bar_col = ['Select',"Total Cases","New Cases", "Total Deaths","New Deaths","Total Recovered","New Recovered","Active Cases","Serious Critical",'Total Tests']
                bars = st.selectbox("",bar_col,key='world')
                df_bar =covid_df.head(10)
                if bars == bar_col[1]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[2]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[3]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[4]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[5]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[6]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[7]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[8]:
                    bar_chartCon(df_bar,bars)
                elif bars == bar_col[9]:
                    bar_chartCon(df_bar,bars)
                else:
                    pass
        elif world == "Show Pie Charts":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Pie Chart</h3></body>", unsafe_allow_html=True)
            st.markdown('### Select any three in sequence')
            don= st.multiselect("",("Total Cases","Total Recovered",'Total Deaths',"Active Cases","Serious Critical"),key='don')
            if st.button('Show Charts'):
                pie_chart(covid_df,don)
        elif world == 'Show Percentage Charts':
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Percetage Chart</h3></body>", unsafe_allow_html=True)
            sel = ['Select','Total Cases','New Cases','Total Deaths','New Deaths', 'Total Recovered','New Recovered','Active Cases','Serious Critical','Total Tests']
            inputs = st.selectbox("",sel)
            percentage_charts(covid_df,inputs)
            
#  Continent Analysis   ****************************************************************************'''

        
    def continentAnalysis(contin1):
        contin = convertContinentFrame(contin1)
        st.sidebar.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: blue;'>Please Select the Task</h3>", unsafe_allow_html=True)
        world = st.sidebar.selectbox("",(["Select","Show Countries with Highest Cases","Show Countries with Lowest Cases","Country Wise Quick Update","Show Bar Graphs","Show Pie Charts","Show Percentage Charts"]))
        if world== "Select":
            pass
        elif world == "Show Countries with Highest Cases":
            high = st.slider("",5,25)
            st.success('{} Countries with Highest Cases'.format(high))
            
            asc=False
            status = st.radio("",("Total Cases","Total Recovered","New Recovered","New Cases","Active Cases",'Total Deaths',"New Deaths","Serious Critical Cases"))
            showCases(contin,status,high,asc)

        elif world == 'Show Countries with Lowest Cases':
            low = st.slider("",5,25)
            st.success('{} Countries with Lowest Cases'.format(low))
            asc = True
            status = st.radio("",("Total Cases","Total Recovered","New Recovered","New Cases","Active Cases",'Total Deaths',"New Deaths","Serious Critical Cases"))
            showCases(contin,status,low,asc)
        elif world == "Country Wise Quick Update":
           
            country_df = contin1['Countries'].values
            con_list = list(country_df)
            cont = st.selectbox("",con_list)
            country_overview(contin1,cont)

        elif world == "Show Bar Graphs":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Bar Graphs</h3></body>", unsafe_allow_html=True)
            if st.checkbox("Total Cases vs"):
                bar_cols = ['Select',"Total Recovered",'Total Deaths',"Active Cases","Serious Critical",'Total Tests']
                color_code = ['#f57542','#42f5a1','#d6413c','#5c6cd1','#e80c17']
                bars = st.selectbox("",bar_cols)
                df_bar =contin.head(10)
                bar_chartTC(df_bar,bars)

               
            if st.checkbox("Countries vs"):
                    bar_col = ['Select',"Total Cases","New Cases", "Total Deaths","New Deaths","Total Recovered","New Recovered","Active Cases","Serious Critical",'Total Tests']
                    bars = st.selectbox("",bar_col)
                    df_bar =contin.head(10)
                    if bars == bar_col[1]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[2]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[3]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[4]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[5]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[6]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[7]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[8]:
                        bar_chartCon(df_bar,bars)
                    elif bars == bar_col[9]:
                        bar_chartCon(df_bar,bars)
                    else:
                        pass
        elif world == "Show Pie Charts":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Pie Chart</h3></body>", unsafe_allow_html=True)
            st.markdown('Select any three')
            don= st.multiselect("",("Total Cases","Total Recovered",'Total Deaths',"Active Cases","Serious Critical"),key='don')
            if st.button('Show Chart'):
                pie_chart(contin,don)
        elif world == 'Show Percentage Charts':
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Percetage Chart</h3></body>", unsafe_allow_html=True)
            sel = ['Select','Total Cases','New Cases','Total Deaths','New Deaths', 'Total Recovered','New Recovered','Active Cases','Serious Critical','Total Tests']
            inputs = st.selectbox("",sel)
            percentage_charts(contin,inputs) 

#  India Analysis   ****************************************************************************'''

    def IndiaAnalysis(India,time):
        st.sidebar.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: blue;'>Select the Task</h3>", unsafe_allow_html=True)
        world = st.sidebar.selectbox("",(["Select","Show States/UT with Highest Cases","Show States/UT with Lowest Cases","State/UT Wise Quick Update","Show Bar Graphs","Show Pie Charts","Show Percentage Charts","Show Maps"]))
        if world== "Select":
            pass
        
        elif world == "Show States/UT with Highest Cases":
            high = st.slider("",5,25)
            st.success('{} States/UT with Highest Cases'.format(high))
            
            asc=False
            status = st.radio("",("Active","Cured","Deaths",'Confirmed'))
            showCasesIndia(India,status,high,asc)

        elif world == 'Show States/UT with Lowest Cases':
            low = st.slider("",5,25)
            st.success('{} States/UT with Highest Cases'.format(low))
            asc = True
            status = st.radio("",("Active","Cured","Deaths",'Confirmed'))
            showCasesIndia(India,status,low,asc)
        elif world == "State/UT Wise Quick Update":
           
            country_df = India['States/UT'].values
            con_list = list(country_df)
            cont = st.selectbox("",con_list)
            states_overview(India,cont,time)

        elif world == "Show Bar Graphs":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Bar Graphs</h3></body>", unsafe_allow_html=True)
               
            if st.checkbox("States/UT vs"):
                    bar_col = ['Select',"Active","Cured","Deaths",'Confirmed']
                    bars = st.selectbox("",bar_col)
                    df_bar =India.head(10)
                    if bars == bar_col[1]:
                        bar_chartState(df_bar,bars)
                    elif bars == bar_col[2]:
                        bar_chartState(df_bar,bars)
                    elif bars == bar_col[3]:
                        bar_chartState(df_bar,bars)
                    elif bars == bar_col[4]:
                        bar_chartState(df_bar,bars)
                
                    else:
                        pass
        elif world == "Show Pie Charts":
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Pie Chart</h3></body>", unsafe_allow_html=True)
            st.markdown('Select any three')
            don= st.multiselect("",("Active","Cured","Deaths",'Confirmed'),key='don')
            if st.button('Show Chart'):
                donut_chartIndia(India,don)
        elif world == 'Show Percentage Charts':
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #f57842;'>Show Percetage Chart</h3></body>", unsafe_allow_html=True)
            sel = ['Select',"Active","Cured","Deaths",'Confirmed']
            inputs = st.selectbox("",sel)
            percentage_chartsInd(India,inputs)
        elif world == 'Show Maps':
            merged_df = IndiaMapdfMerged(India)
            sel = ['Select',"Active","Cured","Deaths",'Confirmed']
            maps = st.selectbox("",sel)

            if maps =='Select':
                pass
            else:
                plotIndiaMap(merged_df,maps)
            
# Twitter Analysis   ****************************************************************************'''


    def tweetAnalyse(tag,time):
        consumer_key ='djhTsqoKfTpL1copeb8QO904U'
        consumer_secret = '9FAxaIGeIVHEXuXJiVKdDZZurPBsiKPsH7pPkYXcYoXOc39VMx'
        access_token ='492233591-l0MtoDBAcJDin897QgS6njrqW0FaCvXVADa2T0zA'
        access_token_secret = 'of3OcbhlMHqIkz34WKrjUlP6sUfI5WZKgDcVoZkxz1U0J'
        def clean_tweet(tweet): 
            return ' '.join(re.sub("(RT @[\w]*)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())
        
        def get_tweet_sentiment(tweet):
            analysis = TextBlob(clean_tweet(tweet))
            if analysis.sentiment.polarity > 0:
                return 'Positive'
            elif analysis.sentiment.polarity==0:
                return 'Neutral'
            else:
                return 'Negative'
    
        search_word= tag
        date_since = time
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        api = tweepy.API(auth,wait_on_rate_limit=True)
        fetched_tweets = api.search(q=search_word,count=100,lang='en',since=date_since)
        tweets = []
        for tweet in fetched_tweets:
            parsed_tweet = {}
            parsed_tweet['text'] = tweet.text
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text)
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
        return tweets
        

    def worldCloudPos(tweets):
        tweets = pd.DataFrame(tweets)
        posdf = tweets[tweets['sentiment'] == 'Positive'].reset_index()
        posdf = posdf.drop('index',axis=1)
        def clean_tweet(tweet): 
            return ' '.join(re.sub("(RT @[\w]*)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())
        posdf['text'] = posdf['text'].apply(lambda x: clean_tweet(x))
        pos = posdf['text'].apply(lambda x:''.join(x)).str.cat(sep=' ')

        plt.figure(figsize=(8,8))
        wordcloud = WordCloud(stopwords=STOPWORDS,background_color='white',
                              collocations=False,
                              width=1400,
                              height=1300).generate(pos)
        plt.imshow(wordcloud)

        plt.axis('off')
        plt.savefig('worldCloudPos.jpg')
        img = Image.open("worldCloudPos.jpg")
        return img

    def worldCloudNeg(tweets):
        tweets = pd.DataFrame(tweets)
        posdf = tweets[tweets['sentiment'] == 'Negative'].reset_index()
        posdf = posdf.drop('index',axis=1)
        def clean_tweet(tweet): 
            return ' '.join(re.sub("(RT @[\w]*)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())
        posdf['text'] = posdf['text'].apply(lambda x: clean_tweet(x))
        pos = posdf['text'].apply(lambda x:''.join(x)).str.cat(sep=' ')

        plt.figure(figsize=(8,8))
        wordcloud = WordCloud(stopwords=STOPWORDS,background_color='white',
                              collocations=False,
                              width=1400,
                              height=1300).generate(pos)
        plt.imshow(wordcloud)

        plt.axis('off')
        plt.savefig('worldCloudNeg.jpg')
        img = Image.open("worldCloudNeg.jpg")
        return img
                
# News Paper Headlines  ****************************************************************************'''


    def paperHeadlines(paper,number):
        
        top_news = []

        if paper == 'Dainik Bhaskar':
            web_content = requests.get("https://www.bhaskar.com/coronavirus/")
            soup = BeautifulSoup(web_content.text, "html.parser")
            for a in soup.findAll('a',attrs={'class':"list_thumb"}):
                x = a.get('title')
                top_news.append(x)
        elif paper == 'Patrika':
            web_content = requests.get('https://www.patrika.com/topic/coronavirus/')
            soup = BeautifulSoup(web_content.text, "html.parser")

            top = soup.find_all('div',attrs={'class':'ctbl-text'})
            for i in top:
                top_news.append(i.text.strip())
        elif paper == 'Navbharat':
            web_content = requests.get('https://navbharattimes.indiatimes.com/coronavirus/trending/74460387.cms')
            soup = BeautifulSoup(web_content.text, "html.parser")

            top = soup.find_all('a',attrs={'class':'cor_rest_art'})
            for i in top:
                top_news.append(i.text.strip())
        elif paper == 'Amarujala':
            web_content = requests.get('https://www.amarujala.com/tags/corona-special-news?page=1')
            soup = BeautifulSoup(web_content.text, "html.parser")

            top = soup.find_all('h3')
            for i in top:
                top_news.append(i.text.strip())
        return top_news[:number]
            
# Front Page  ****************************************************************************'''

        
    st.markdown("<body style='background-color:white;'><h1 style='text-align: center; color: blue;'>COVID19 REAL TIME ANALYSIS</h1></body>", unsafe_allow_html=True)
    img = Image.open('/Users/kush/Downloads/Covid19/covid-19-banner.jpg')
    st.image(img,width=700)
    st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: green;'>Helpline Number for Corona Virus : +91-11-23978046 or 1075</h3></body>", unsafe_allow_html=True)
    st.markdown("<a href='https://www.mohfw.gov.in//'><marquee>Click here for Guidelines by Health Ministry of India</marquee></a>",unsafe_allow_html=True)
    st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: red;'>#INDIAFIGHTSCORONA 👊</h3></body>", unsafe_allow_html=True)
    day = ['Select','Today','Yesterday','2 Days Ago']
    
    st.markdown("<body style='background-color:white;'><h1 style='text-align: center; color: green;'>SELECT YOUR ACTIVITIES FROM THE SIDEBAR 👈</h1></body>", unsafe_allow_html=True)
    activities = ["Select","Covid19 Ananlysis Worldwide","Covid19 Analysis Continent Wise ","Covid19 Analysis India ","Tweet Analysis","Indian News Paper Headlines"]
    st.sidebar.markdown("<body style='background-color:blue;'><h3 style='text-align: center; color: white;'>Please Select the Activities</h3></body>", unsafe_allow_html=True)

# Activity 1  World Wide Analysis ****************************************************************************'''

    activity = st.sidebar.selectbox("",activities)
    if activity == activities[1]:
        
        st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Day</h3></body>", unsafe_allow_html=True)
        days = st.selectbox('',day)
        if days=='Select':
            pass
        else:
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Task from Sidebar</h3></body>", unsafe_allow_html=True)
            world_df = fetchWorldData(days)
            if st.button('Quick Analysis'):
                cn = 'World'
                quickAnalysisWorldCont(world_df,cn)
            worldWideAnalysis(world_df)
            
            
# Activity 2 Continent Analysis ****************************************************************************'''


    elif activity == activities[2]:
        continents =  ['Select','Europe','North America','Asia','South America','Africa','Oceania']
        st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Day</h3></body>", unsafe_allow_html=True)
        days = st.selectbox('',day)
        
        if days =='Select':
            pass
        elif days == 'Today':
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Continent</h3></body>", unsafe_allow_html=True)
            st.sidebar.markdown("<body style='background-color:blue;'><h3 style='text-align: center; color: white;'>Perform the following</h3></body>", unsafe_allow_html=True)

            continents = st.selectbox("",continents)
            ids = "main_table_countries_today"
            if continents == 'Select':
                pass
            else:
                continent_df = fetchContinentData(ids,continents)
                if st.button('Quick Analysis'):
                    quickAnalysisWorldCont(continent_df,continents)
                st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Task from Sidebar</h3></body>", unsafe_allow_html=True)

                if st.sidebar.checkbox('Show/Hide Data',False,key='today'):
                    st.table(continent_df)
                if st.sidebar.checkbox('Perform the Analysis',False,key='analyse1'):
                    continentAnalysis(continent_df)
              
            
        elif days == 'Yesterday':
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Continent</h3></body>", unsafe_allow_html=True)
            st.sidebar.markdown("<body style='background-color:blue;'><h3 style='text-align: center; color: white;'>Perform the following</h3></body>", unsafe_allow_html=True)

            continents = st.selectbox("",continents)
            ids = "main_table_countries_yesterday" 
            if continents == 'Select':
                pass
            else: 
                continent_df = fetchContinentData(ids,continents)
                if st.button('Quick Analysis'):
                    quickAnalysisWorldCont(continent_df,continents)
                st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Task from Sidebar</h3></body>", unsafe_allow_html=True)
    
                
                if st.sidebar.checkbox('Show/Hide Data',False,key='yesterday'):
                    st.table(continent_df)
                if st.sidebar.checkbox('Perform the Analysis',False,key='analyse2'):
                    continentAnalysis(continent_df)
                
                
                
        else:
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Continent</h3></body>", unsafe_allow_html=True)
            st.sidebar.markdown("<body style='background-color:blue;'><h3 style='text-align: center; color: white;'>Perform the following</h3></body>", unsafe_allow_html=True)
            
            continents = st.selectbox("",continents)
            ids = "main_table_countries_yesterday2"   
            if continents == "Select":
                pass
            else:
                continent_df = fetchContinentData(ids,continents)
                if st.button('Quick Analysis'):
                    quickAnalysisWorldCont(continent_df,continents)
                st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Task from Sidebar</h3></body>", unsafe_allow_html=True)
    
                if st.sidebar.checkbox('Show/Hide Data',False,key='yesterday2'):
                    st.table(continent_df)
                if st.sidebar.checkbox('Perform the Analysis',False,key='analyse2'):
                    continentAnalysis(continent_df)
        
        
# Activity 3 India Analysis ****************************************************************************'''

    elif activity == activities[3]:
        India_df,time = fetchIndiaData()

        India_df = convertIndiaFrame(India_df)
        st.sidebar.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: blue;'>Check the box</h3></body>", unsafe_allow_html=True)
        if st.checkbox("Show/Hide Data",key='Indiashow'):
            st.table(India_df.style.background_gradient(cmap='Reds'))
        st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: #a84c32;'>Please Select the Task from Sidebar</h3></body>", unsafe_allow_html=True)

        if st.sidebar.checkbox('Perform the Analysis',False,key='analyse1'):
            IndiaAnalysis(India_df,time)
                    
# Activity 4 Twitter Analysis ****************************************************************************'''

    elif activity == activities[4]:
        st.markdown("<body style='background-color:white;'><h1 style='text-align: center; color: #a84c32;'>Covid 19 Tweet Analyzer </h1></body>", unsafe_allow_html=True)
        st.markdown("### Enter the Keyword Related to Covid19")
        tag = st.text_input("")
        st.markdown("### Date from which you want to see the tweets")
        time = st.date_input(" ",datetime.datetime.now())
        st.markdown("### How many tweets you want to see")

        count = st.slider("",1,30)
        st.success("You want to analyze the tweets for a word '{}' since {} ".format(tag,time))
        
        
        if st.checkbox("Positive Tweets"):
                st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: brown;'>Perform the Task</h3></body>", unsafe_allow_html=True)

                
                tweets = tweetAnalyse(tag,time)

                postweets = [tweet for tweet in tweets if tweet['sentiment']=='Positive']
                selc = ["Select",'Positive Tweets Percentage',"Positive Tweets",'Positive Tweets Word Cloud','Top Hastags','Top Users Mentioned']
                choose = st.selectbox("",selc)
                if choose == selc[1]:
                    st.info("Positive Tweets Percentage: {}".format(100*len(postweets)/len(tweets)))
                    
                elif choose == selc[2]:
                    for tweet in postweets[:count]:
                        
                        st.info(tweet['text'])
                    
                elif choose == selc[3]:
                    img = worldCloudPos(tweets)
                    st.image(img)
                elif choose == selc[4]:
                    tweets = pd.DataFrame(tweets)
                    posdf = tweets[tweets['sentiment'] == 'Positive'].reset_index()
                    posdf = posdf.drop('index',axis=1)
                    posdf['text'].str.findall('(#\w+)').apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False)[:10].plot(kind='bar')

                    sns.set(style="darkgrid")
                    sns.set(font_scale=1.2)
                    plt.rcParams['figure.figsize']=12,8
                    plt.tight_layout()
                    plt.grid(False)
                    plt.title('Top Hashtags', fontsize=14)
                    st.pyplot()
                elif choose == selc[5]:
                    
                    tweets = pd.DataFrame(tweets)
                    posdf = tweets[tweets['sentiment'] == 'Positive'].reset_index()
                    posdf = posdf.drop('index',axis=1)

                    posdf['text'].str.findall('(@[A-Za-z0-9]+)').apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False)[:10].plot(kind='bar')
                    sns.set(style="darkgrid")
                    sns.set(font_scale=1.2)
                    plt.rcParams['figure.figsize']=12,8
                    plt.grid(False)
                    plt.tight_layout()
                    plt.title('Top Users Mentioned', fontsize=14)
                    st.pyplot()
                    
        elif st.checkbox("Negative Tweets"):
                st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: brown;'>Perform the Task</h3></body>", unsafe_allow_html=True)

                tweets = tweetAnalyse(tag,time)

                postweets = [tweet for tweet in tweets if tweet['sentiment']=='Negative']
                selc = ["Select",'Negative Tweets Percentage',"Negative Tweets",'Negative Tweets Word Cloud','Top Hastags','Top Users Mentioned']
                choose = st.selectbox("",selc)
                if choose == selc[1]:
                    st.info("Negative Tweets Percentage: {}".format(100*len(postweets)/len(tweets)))
                    
                elif choose == selc[2]:
                    for tweet in postweets[:count]:
                        
                        st.info(tweet['text'])
                    
                elif choose == selc[3]:
                    img = worldCloudNeg(tweets)
                    st.image(img)
                elif choose == selc[4]:
                    tweets = pd.DataFrame(tweets)
                    posdf = tweets[tweets['sentiment'] == 'Negative'].reset_index()
                    posdf = posdf.drop('index',axis=1)
                    posdf['text'].str.findall('(#\w+)').apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False)[:10].plot(kind='bar')

                    sns.set(style="darkgrid")
                    sns.set(font_scale=1.2)
                    plt.rcParams['figure.figsize']=12,8
                    plt.tight_layout()
                    plt.grid(False)
                    plt.title('Top Hashtags', fontsize=14)
                    st.pyplot()
                    
                elif choose == selc[5]:
                    
                    tweets = pd.DataFrame(tweets)
                    posdf = tweets[tweets['sentiment'] == 'Negative'].reset_index()
                    posdf = posdf.drop('index',axis=1)

                    posdf['text'].str.findall('(@[A-Za-z0-9]+)').apply(lambda x: pd.value_counts(x)).sum(axis=0).sort_values(ascending=False)[:10].plot(kind='bar')
                    sns.set(style="darkgrid")
                    sns.set(font_scale=1.2)
                    plt.rcParams['figure.figsize']=12,8
                    plt.grid(False)
                    plt.tight_layout()
                    plt.title('Top Users Mentioned', fontsize=14)
                    st.pyplot()
              
# Activity 5 Hindi News Paper Headlines ****************************************************************************'''

        
    elif activity == activities[5]:
        st.markdown("<body style='background-color:white;'><h1 style='text-align: center; color: #a84c32;'>Covid19 Hindi Newspaper Headlines</h1></body>", unsafe_allow_html=True)
        news = ['Select','Dainik Bhaskar','Patrika','Navbharat','Amarujala']
        paper = st.selectbox('',news)
        if paper == 'Select':
            pass
        else:
            st.markdown("<body style='background-color:white;'><h3 style='text-align: center; color: green;'>Slide through the slider to see the COVID19 news</h3></body>", unsafe_allow_html=True)            
            number = st.slider(" ",1,15)
            headlines = paperHeadlines(paper,number)
            for i in headlines:
                
                st.info(i)
            
    
    else:
            pass
        
# END OF CODE ****************************************************************************'''

                
if __name__== '__main__':
    main()
