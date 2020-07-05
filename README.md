# Covid19 Real Time Cases Analysis

1. [ Demo ](#demo)
2. [ Overview ](#overview)
3. [ Installation](#install)
4. [ Run ](#run)
<a name="demo"></a>
### Demo
#### Link https://covid-realtime-analysis.herokuapp.com

<a name="overview"></a>
### Overview
This Covid19 Real Time Case Analysis project web scraps real time data, makes visualizations and performs analysis regarding the COVID-19 epidemic. The project plots bar charts, pie charts, percentage charts and Maps with the highest number of Covid19 cases, recovered cases, death cases, cured cases, total tests and new cases. The project also consists of a Tweet analyser which shows the number of positive and negative tweets along with top hashtags, mentions and word cloud. The real time Hindi newspaper headlines are also displayed by the project. The project is divided into 5 phases:

#### Activities

1. [ Covi19 Worldwide Analysis ](#world)
2. [ Covid19 Continent wise Analysis ](#continent)
3. [ Covid19 India wise Analysis ](#India)
4. [ Tweet Analyser ](#tweet)
5. [ Indian Newspaper Headlines ](#news)

<a name="world"></a>
### Covid19 Worldwide Analysis
This phase web scraps the Covid19 data from (https://www.worldometers.info) using python BeautifulSoup. The user is asked to select the data for any of the three days i.e. Today, Yesterday and Day before Yesterday. After the selection user can perform the following tasks:
* Show Countries with Highest Cases (Total Cases, New Cases, Acive Cases, Recovered Cases, New Deaths, New Recovered,  Serious Cases etc.) accross the world
* Show Countries with Lowest Cases (Total Cases, New Cases, Acive Cases, Recovered Cases, New Deaths, New Recovered,  Serious Cases etc.) accross the world
* Country wise Quick Update - Displays the short summary of all type of cases wrt to each country of the world
* Show Bar Graphs
  * Total cases vs All other cases
  * Country vs All other cases
 * Show Pie Charts -  Pie charts are displayed between any three type of cases accross the world
* Show Percentage Charts - Displays the percentage of cases accross the world

<a name="continent"></a>
### Covid19 Continent wise Analysis

This phase also web scraps the Covid19 data from (https://www.worldometers.info) using python BeautifulSoup. The user is asked to select the data for any of the three days i.e. Today, Yesterday and Day before Yesterday. 
After the selection user is asked to select the Continent for which he/she wants to see the analysis. The user can perform the following tasks:

* Show Countries with Highest Cases (Total Cases, New Cases, Acive Cases, Recovered Cases, New Deaths, New Recovered,  Serious Cases etc.) accross the continent
* Show Countries with Lowest Cases (Total Cases, New Cases, Acive Cases, Recovered Cases, New Deaths, New Recovered,  Serious Cases etc.) accross the continent
* Country wise Quick Update - Displays the short summary of all type of cases wrt to each country of the continent
* Show Bar Graphs
  * Total cases vs All other cases
  * Country vs All other cases
 * Show Pie Charts -  Pie charts are displayed between any three type of cases accross the continent
* Show Percentage Charts - Displays the percentage of cases accross the continent

<a name="India"></a>
### Covid19 India wise Analysis

This phase web scraps the Covid19 data from (https://www.mohfw.gov.in) using python BeautifulSoup. 
After the selection user is asked to select the Continent for which he/she wants to see the analysis. The user can perform the following tasks:

* Show States/UT with Highest Cases ( Acive Cases, Cured Cases, Death Cases and Confirmed Cases ) accross India
* Show States/UT with Lowest Cases ( Acive Cases, Cured Cases, Death Cases and Confirmed Cases ) accross India
* States/UT wise Quick Update - Displays the short summary of all type of cases wrt to each country of the continent
* Show Bar Graphs
  * States/UT vs All other cases
 * Show Pie Charts -  Pie charts are displayed between any three type of cases accross India
* Show Percentage Charts - Displays the percentage of cases accross India
* Show Maps - Displays the maps with ( Acive Cases, Cured Cases, Death Cases and Confirmed Cases )

<a name="tweet"></a>
### Twitter Analyser

This phase asks user to input the word and data since which they want to analyse tweets. The user can select the number of tweets he/she wants to see through a slider.
After doing the above steps a user can than see the positive and negative tweets and their percentage, the word cloud for the positive and negative tweets, the top hashtags and mentions in the tweets.
The tweets are analysed using TextBlob library.

<a name="news"></a>
### Indian News Paper Headlines

This phase web scrapes the current top news headlines from the Indian Hindi Newspaper. 
* [ Dainik Bhaskar ](https://www.bhaskar.com/coronavirus/)
* [ Patrika ](https://www.patrika.com/topic/coronavirus/) 
* [ Navbharat times ](https://navbharattimes.indiatimes.com/coronavirus/trending/74460387.cms)
* [ Amar Ujala ](https://www.amarujala.com/tags/corona-special-news?page=1)


<a name="install"></a>
### Installation

The Code is written in Python 3.7. To install the required packages and libraries, run this command in the project directory after cloning the repository:

> pip install -r requirements.txt

<a name="run" > </a>
### Run

Create an environment and clone this repository. To run this project run a command into terminal :

> streamlit run app.py


