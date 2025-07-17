# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 03:08:51 2025

@author: aaqil
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Alzheimer's Disease Data", page_icon="🧠", layout="wide")
st.title("🧠Alzheimer's Disease Data🧠")


df = pd.read_csv('alzheimers_data_clean.csv')

st.sidebar.header("Filter Data 🔍")

selected_gender = st.sidebar.multiselect("Select gender:", df["gender"].unique(), default=df["gender"].unique())

selected_ethnicity = st.sidebar.multiselect("Select ethnicity:", df["ethnicity"].unique(), default=df["ethnicity"].unique())

selected_education_level = st.sidebar.multiselect("Select education level:", df["educationlevel"].unique(), default=df["educationlevel"].unique())


# filtered data based on the mutiselect widgets
#boolean_filter = df["gender"].isin(selected_gender) & df["ethnicity"].isin(selected_ethnicity) & df["educationlevel"].isin(selected_education_level)
#filtered = df.loc[boolean_filter]
# Add a toggle in sidebar
show_filtered = st.sidebar.checkbox("Apply filters", value=True)

if show_filtered:
    working_df = df[
        df["gender"].isin(selected_gender) & 
        df["ethnicity"].isin(selected_ethnicity) & 
        df["educationlevel"].isin(selected_education_level)
    ]
else:
    working_df = df  # Fallback to original



#show headers and averages
num_patients = len(working_df)
avg_age =working_df["age"].mean()
avg_bmi = working_df["bmi"].mean()
avg_alcoholconsumption = working_df["alcoholconsumption"].mean()
avg_physicalactivity = working_df["physicalactivity"].mean()
avg_mmsescore = working_df["mmse"].mean()

col1, col2, col3 = st.columns(3)
col1.metric(label="\# of Patients", value=f"{num_patients:,}")
col2.metric(label="Avg. Age", value=f"{avg_age:,.0f}")
col3.metric(label="Avg. MMSE Score(Mini Memory State Exam)", value=f"{avg_mmsescore:,.0f}")

col4, col5 = st.columns(2)
col4.metric(label="Avg. Alcohol Consumption (units/week)", value=f"{avg_alcoholconsumption:.2f}")
col5.metric(label="Avg. Physical Activity (hours/week)", value=f"{avg_physicalactivity:,.0f}")

#histogram age graphic
fig_histo_age = px.histogram(data_frame=working_df, x='age', color='diagnosis',
                  title='Age Distribution by Alzheimers Diagnosis', labels={'age':'Age', 'diagnosis':'Diagnosis'},
                 nbins=20, opacity=0.7, color_discrete_sequence=['blue', 'red'],
                 width=1000)
fig_histo_age.update_yaxes(title_text='Number of Patients')
fig_histo_age.update_layout(bargap=0.0) 

st.plotly_chart(fig_histo_age)

#symptom bar
symptom_columns = ['confusion', 'disorientation', 'personalitychanges', 
                   'difficultycompletingtasks', 'forgetfulness']

# Calculate % of "yes" for each symptom
symptom_data = {col: (working_df[col] == 'yes').mean() * 100 for col in symptom_columns}
symptom_df = pd.DataFrame(list(symptom_data.items()), columns=['Symptom', 'Percentage'])


fig_bar_symptom = px.bar(symptom_df, x='Symptom', y='Percentage',
             title='Percentage of Patients Reporting Each Symptom',
             labels={'Percentage': 'Percentage (%)'},
             text_auto='.1f')
fig_bar_symptom.update_xaxes(
    ticktext=['Confusion', 'Disorientation', 'Personality Changes', 
              'Task Completion Issues', 'Forgetfulness'],
    tickvals=symptom_df['Symptom']  # Original values
)

st.plotly_chart(fig_bar_symptom)

#box smoking graphic

fig_box_smoking = px.box(working_df, x='smoking', y='mmse', color='diet_quality', 
                         title='MMSE by Smoking Status and Diet Level',
                         color_discrete_sequence=['blue', 'red', 'green'])


st.plotly_chart(fig_box_smoking)

#tree with diet, activity, alcohol, and diag
#What lifestyle factors predict an Alzheimers Diagnosis the most

# Calculate percentages
total = len(working_df)
percent_data = (working_df.groupby(['diet_quality', 'activity_level', 
                            'alcohol_level', 'diagnosis'])
                .size()
                .reset_index(name='count'))
percent_data['percentage'] = (percent_data['count'] / total * 100).round(1)

# Create treemap with percentages
fig_tree = px.treemap(percent_data, 
                 path=['diet_quality', 'activity_level', 'alcohol_level', 'diagnosis'],
                 values='percentage',
                 title='Lifestyle Factors and Diagnosis (Percentage Distribution)',
                 hover_data={'percentage': ':.1f%'},
                 color='percentage',
                 color_continuous_scale='Blues')

# Format text to show percentages
fig_tree.update_traces(textinfo='label+percent entry',
                 texttemplate='%{label}<br>%{value:.1f}%',
                 hovertemplate='<b>%{label}</b><br>Percentage: %{value:.1f}%<extra></extra>')
st.plotly_chart(fig_tree)

#MMse score by education and diangosis

mean_mmse = working_df.groupby(['educationlevel', 'diagnosis'], as_index=False)['mmse'].mean()

fig_bar_mmse = px.bar(
    mean_mmse,
    x='educationlevel',
    y='mmse',
    color='diagnosis',  # Adds diagnosis as a second category
    barmode='group',    # Groups bars side-by-side
    title='MMSE Scores by Education and Diagnosis',
    labels={'mmse': 'Mean MMSE Score'},
    facet_col='diagnosis',
    text= 'mmse', 
    color_discrete_sequence=['blue', 'red']
) 
fig_bar_mmse.update_traces(
    texttemplate='%{text:.1f}',  # Formats all text labels to 1 decimal
    textposition='outside'       # Optional: improves label visibility
)
st.plotly_chart(fig_bar_mmse)


#sunburst data time
total = len(working_df)
percent_data = (working_df.groupby(['bmi_level', 'cholesterol_total_level', 'diagnosis'])
                .size()
                .reset_index(name='count'))
percent_data['percentage'] = (percent_data['count'] / total * 100).round(1)

fig_sunburst = px.sunburst(percent_data, 
                 path=['bmi_level', 'cholesterol_total_level', 'diagnosis'],
                 values='percentage',
                 title='BMI, Cholesterol, and Alzheimer\'s Diagnosis (Percentage Distribution)',
                 color_continuous_scale='Blues',
                 branchvalues='total',
                 hover_data={'percentage': ':.1f%'})

# Format labels to show percentages
fig_sunburst.update_traces(textinfo='label+percent parent',
                 texttemplate='%{label}<br>%{value:.1f}%',
                 hovertemplate='<b>%{label}</b><br>%{value:.1f}% of parent<br>Path: %{id}<extra></extra>')

# Adjust layout
fig_sunburst.update_layout(margin=dict(t=50, l=0, r=0, b=0),
                 title_font_size=18)

st.plotly_chart(fig_sunburst)

#blood pressure by diagnosis
bp_melted_diag = working_df.melt(id_vars=['diagnosis'], 
                         value_vars=['systolicbp', 'diastolicbp'], 
                         var_name='Blood Pressure Type', 
                         value_name='Blood Pressure (mmHg)')

fig_box_bp = px.box(bp_melted_diag, x='diagnosis', y='Blood Pressure (mmHg)', color='diagnosis',
             facet_col='Blood Pressure Type',
             title='Systolic and Diastolic Blood Pressure by Diagnosis Level',
             color_discrete_sequence=['blue', 'red'])

st.plotly_chart(fig_box_bp)
 
#percentage diagnosis ethnicity
ethnicity_diagnosis = working_df.groupby(['ethnicity', 'diagnosis']).size().reset_index(name='count')

# Calculate total counts per ethnicity
total_per_ethnicity = ethnicity_diagnosis.groupby('ethnicity')['count'].transform('sum')

# Calculate percentage
ethnicity_diagnosis['percentage'] = (ethnicity_diagnosis['count'] / total_per_ethnicity) * 100


fig_bar_ethnicity = px.bar(ethnicity_diagnosis, 
             x='ethnicity', 
             y='percentage', 
             color='diagnosis',
             title='Percentage of Diagnosis Levels within Each Ethnicity',
             labels={'percentage': 'Percentage (%)'},
             barmode='stack',
             text=ethnicity_diagnosis['percentage'].round(1).astype(str),
             color_discrete_sequence=['blue', 'red'])


st.plotly_chart(fig_bar_ethnicity)


#depression by age

depression_by_age = working_df.groupby('age_group')['depression'].value_counts(normalize=True).rename('percentage').reset_index()
depression_by_age['percentage'] *= 100
depression_by_age = depression_by_age[depression_by_age['depression'] == 'yes']


fig_bar_depression = px.bar(depression_by_age, x='age_group', y='percentage',
             title='Percentage of Patients with Depression by Age Group',
             labels={'percentage': 'Percentage (%)'}, 
             text=depression_by_age['percentage'].round(1).astype(str),
             color_discrete_sequence=['blue'])
fig_bar_depression.update_layout(
    title_font_size=15,  # Adjust this value (default is usually ~24)
)


#head injury age

headinjury_by_age = working_df.groupby('age_group')['headinjury'].value_counts(normalize=True).rename('percentage').reset_index()
headinjury_by_age['percentage'] *= 100
headinjury_by_age = headinjury_by_age[headinjury_by_age['headinjury'] == 'yes']

fig_bar_headinjury = px.bar(headinjury_by_age, x='age_group', y='percentage',
             title='Percentage of Patients with Head Injuries by Age Group',
             labels={'percentage': 'Percentage (%)'}, 
             text=headinjury_by_age['percentage'].round(1).astype(str),
             color_discrete_sequence=['red'])
fig_bar_headinjury.update_layout(
    title_font_size=15,  # Adjust this value (default is usually ~24)
)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar_depression, use_container_width=True)

with col2:
    st.plotly_chart(fig_bar_headinjury, use_container_width=True)










