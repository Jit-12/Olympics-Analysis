import streamlit as st
import pandas as pd
import numpy as np
import preprocessor,helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import scipy

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df,region_df)

st.sidebar.title("Olympics Analysis")
st.sidebar.image("https://www.urbanriver.com/wp-content/uploads/2012/04/olympic-rings.gif")
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally','Overall Analysis','Country-wise Analysis','Athlete-wise Analysis')
)


if user_menu == 'Medal Tally':
    st.sidebar.header('Medal Tally')
    years,country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox('Select Year',years)
    selected_country = st.sidebar.selectbox('Select Country', country)
    medal_tally = helper.fetch_medal_tally(df,selected_year,selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('Overall Tally')
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year))
    st.table(medal_tally)


if user_menu == "Overall Analysis":
    st.title("Overall Analysis")

    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athlets = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]
    st.title("Top Stats")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Athletes")
        st.title(athlets)
    with col3:
        st.header("Nations")
        st.title(nations)

    nations_over_time = helper.data_over_time(df,'region')
    fig1 = px.line(nations_over_time, x='Edition', y='region',labels={'region':'No. of Countries'})
    st.title("Participating Nations over the years")
    st.plotly_chart(fig1)

    events_over_time = helper.data_over_time(df,'Event')
    fig = px.line(events_over_time, x='Edition', y='Event',labels={'Event':'No. of Events'})
    st.title("No. of Events over the years")
    st.plotly_chart(fig)

    athletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athletes_over_time, x='Edition', y='Name',labels={'Name':'No. of Athletes'})
    st.title("No. of Athletes over the years")
    st.plotly_chart(fig)

    st.title("Events over the years(Every Sport)")
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    fig, ax = plt.subplots(figsize=(25, 25))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int),
        annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox("Select a sport",sport_list)
    x = helper.most_successful(df,selected_sport)
    st.table(x)

if user_menu == "Country-wise Analysis":
    st.sidebar.title("Country-wise Analysis")

    country_list = np.unique(df['region'].dropna().values).tolist()
    country_list.sort()
    country_selected = st.sidebar.selectbox("Select Country", country_list)
    country_df = helper.yearwise_medal_tally(df,country_selected)
    fig = px.line(country_df, x='Year', y='Medal', labels={'Year': 'Edition', 'Medal': 'Medals'})
    st.title(country_selected + ' Medal Tally over the years')
    st.plotly_chart(fig)


    pt=helper.country_sport_heatmap(df,country_selected)
    if pt.empty:
        st.title(country_selected + " has no medal in any sports")
    else:
        fig,ax=plt.subplots(figsize=(25,25))
        ax = sns.heatmap(pt,annot=True)
        st.title(country_selected + ' excels in the following sports')
        st.pyplot(fig)

    st.title("Top Athletes from " + country_selected)
    top15_df = helper.most_successful_countrywise(df,country_selected)
    st.table(top15_df)


if user_menu == "Athlete-wise Analysis":
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False).update_layout(xaxis_title='Age',autosize=False,width=900,height=600)
    st.title('Distribution of Age')
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=900, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    st.title("Height vs Weight")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select a sport", sport_list)
    temp_df = helper.weight_height(df,selected_sport)
    fig,ax = plt.subplots()
    ax = sns.scatterplot(x=temp_df['Weight'],y=temp_df['Height'],hue=temp_df['Medal'],style=temp_df['Sex'],s=60)
    st.pyplot(fig)

    st.title("Male vs Female Participation over the years")
    final = helper.male_female(df)
    fig = px.line(final, x='Year', y=['Male', 'Female'])
    st.plotly_chart(fig)