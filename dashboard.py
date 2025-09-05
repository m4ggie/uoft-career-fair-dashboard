import streamlit as st
import pandas as pd

# Load CSV
df = pd.read_csv("uoft_career_fair_employers.csv")

# Sidebar filters
level_of_study = st.sidebar.multiselect(
    "Level of Study",
    sorted({x for row in df["Level of Study"] for x in row.split("|")})
)
hiring_for = st.sidebar.multiselect(
    "Hiring For",
    sorted({x for row in df["Hiring For"] for x in row.split("|")})
)
target_programs = st.sidebar.multiselect(
    "Target Programs",
    sorted({x for row in df["Target Programs"] for x in row.split("|")})
)
opportunities = st.sidebar.multiselect(
    "Opportunities",
    sorted({x for row in df["Opportunities"] for x in row.split("|")})
)

# Filter function
def filter_df(df):
    filtered = df.copy()
    if level_of_study:
        filtered = filtered[filtered["Level of Study"].str.split("|").apply(lambda x: any(i in x for i in level_of_study))]
    if hiring_for:
        filtered = filtered[filtered["Hiring For"].str.split("|").apply(lambda x: any(i in x for i in hiring_for))]
    if target_programs:
        filtered = filtered[filtered["Target Programs"].str.split("|").apply(lambda x: any(i in x for i in target_programs))]
    if opportunities:
        filtered = filtered[filtered["Opportunities"].str.split("|").apply(lambda x: any(i in x for i in opportunities))]
    return filtered

filtered_df = filter_df(df)

st.title("UofT Career Fair Employers")
st.write(f"Showing {len(filtered_df)} employers")
st.dataframe(filtered_df)
