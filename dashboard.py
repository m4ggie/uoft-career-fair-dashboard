import streamlit as st
import pandas as pd

# --- Load CSV ---
df = pd.read_csv("uoft_career_fair_employers.csv")

# Convert multi-value fields into lists for filtering
for col in ["Level of Study", "Hiring For", "Target Programs", "Opportunities"]:
    df[col + "_list"] = df[col].apply(lambda x: x.split("|") if pd.notnull(x) else [])

# --- Sidebar ---
with st.sidebar:
    st.title("Filters")
    
    # Search Employer
    search_name = st.text_input("Search Employer by Name")

    # Expandable filter section
    with st.expander("Filter Options", expanded=True):
        level_filter = st.multiselect(
            "Level of Study",
            options=sorted(set(sum(df["Level of Study_list"].tolist(), [])))
        )
        hiring_filter = st.multiselect(
            "Hiring For",
            options=sorted(set(sum(df["Hiring For_list"].tolist(), [])))
        )
        program_filter = st.multiselect(
            "Target Programs",
            options=sorted(set(sum(df["Target Programs_list"].tolist(), [])))
        )
        industry_filter = st.multiselect(
            "Industry",
            options=sorted(df["Industry"].dropna().unique())
        )
        opportunity_filter = st.multiselect(
            "Opportunities",
            options=sorted(set(sum(df["Opportunities_list"].tolist(), [])))
        )
    
    # Deselect all filters
    if st.button("Deselect All Filters"):
        st.experimental_rerun()
    
    # Search button
    apply_filters = st.button("Search")

# --- Filtering function ---
def filter_df(df):
    temp = df.copy()
    if search_name:
        temp = temp[temp["Employer"].str.contains(search_name, case=False, na=False)]
    if level_filter:
        temp = temp[temp["Level of Study_list"].apply(lambda x: any(i in x for i in level_filter))]
    if hiring_filter:
        temp = temp[temp["Hiring For_list"].apply(lambda x: any(i in x for i in hiring_filter))]
    if program_filter:
        temp = temp[temp["Target Programs_list"].apply(lambda x: any(i in x for i in program_filter))]
    if industry_filter:
        temp = temp[temp["Industry"].isin(industry_filter)]
    if opportunity_filter:
        temp = temp[temp["Opportunities_list"].apply(lambda x: any(i in x for i in opportunity_filter))]
    return temp

# Apply filters (initial load shows all)
if apply_filters or True:
    filtered_df = filter_df(df)

# --- Pagination ---
cards_per_page = 6
total_pages = (len(filtered_df) - 1) // cards_per_page + 1
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (page - 1) * cards_per_page
end_idx = start_idx + cards_per_page
page_data = filtered_df.iloc[start_idx:end_idx]

# --- Display Cards ---
for row_idx in range(0, len(page_data), 3):
    cols = st.columns(3)
    for i, (_, row) in enumerate(page_data.iloc[row_idx:row_idx+3].iterrows()):
        col = cols[i]
        with col:
            st.markdown(
                f"""
                <div style='border:1px solid #ddd; padding:15px; border-radius:10px; background-color:#f9f9f9;'>
                <h3>{row['Employer']}</h3>
                <p><a href='{row['Link']}' target='_blank'>Website</a></p>
                <p><b>Level of Study:</b> {row['Level of Study']}</p>
                <p><b>Hiring For:</b> {row['Hiring For']}</p>
                <p><b>Target Programs:</b> {row['Target Programs']}</p>
                <p><b>Industry:</b> {row['Industry']}</p>
                <p><b>Opportunities:</b> {row['Opportunities']}</p>
                </div>
                """, unsafe_allow_html=True
            )
    st.markdown("---")
