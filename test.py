import streamlit as st
import pandas as pd
st.set_page_config(page_title="2025 Uoft Career Fair Navigator")

# --- Load CSV ---
df = pd.read_csv("uoft_career_fair_employers_cleaned.csv")
#hello

# Convert multi-value fields into lists for filtering
multi_cols = ["Level of Study", "Hiring For", "Target Programs", "Opportunities"]
for col in multi_cols:
    df[col + "_list"] = df[col].apply(lambda x: x.split("|") if pd.notnull(x) else [])

# --- Page config ---
st.set_page_config(page_title="UofT Career Fair Dashboard", layout="wide")

# --- Top header ---
st.markdown("<h1 style='text-align:center;'>UofT Career Fair 2025 Employers Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<h4 style='text-align:center; color: #555;'>Review employers dynamically through customizable filters. We will be employed 🙏</h4>", unsafe_allow_html=True)
st.markdown("---")

def reset_filters():
    st.session_state["search_name"] = ""
    st.session_state["level_filter"] = []
    st.session_state["hiring_filter"] = []
    st.session_state["program_filter"] = []
    st.session_state["industry_filter"] = []
    st.session_state["opportunity_filter"] = []

# --- Sidebar ---
with st.sidebar:
    st.markdown("###  Filters")
    
    # Search Employer by Name
    search_name = st.text_input("Search Employer by Name", key="search_name")

    # Multi-select filters
    level_filter = st.multiselect(
        "Level of Study",
        options=sorted(set(sum(df["Level of Study_list"].tolist(), []))),
        key="level_filter"
    )
    hiring_filter = st.multiselect(
        "Hiring For",
        options=sorted(set(sum(df["Hiring For_list"].tolist(), []))),
        key="hiring_filter"
    )
    program_filter = st.multiselect(
        "Target Programs",
        options=sorted(set(sum(df["Target Programs_list"].tolist(), []))),
        key="program_filter"
    )
    industry_filter = st.multiselect(
        "Industry",
        options=sorted(df["Industry"].dropna().unique()),
        key="industry_filter"
    )
    opportunity_filter = st.multiselect(
        "Opportunities",
        options=sorted(set(sum(df["Opportunities_list"].tolist(), []))),
        key="opportunity_filter"
    )

    st.button("Reset Filters", on_click=reset_filters)

# --- Filter function ---
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

# Apply filters
filtered_df = filter_df(df)

# --- Results count ---
st.write(f"**Results: {len(filtered_df)} employers found**")

# Handle no matches
if len(filtered_df) == 0:
    st.warning("No employers match the selected filters.")
else:
    # --- Display Cards in Responsive Layout ---
    cards_per_row = 3
    min_card_height = "420px"  # Equal card height

    for row_idx in range(0, len(filtered_df), cards_per_row):
        cols = st.columns(cards_per_row, gap="large")
        for i, (_, row) in enumerate(filtered_df.iloc[row_idx:row_idx+cards_per_row].iterrows()):
            col = cols[i]
            with col:
                logo_url = row.get("Logo", "")
                card_html = f"""
                <div style='
                    border: 1px solid #ccc;
                    padding: 15px;
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    min-height: {min_card_height};
                '>
                """

                # Logo
                if pd.notnull(logo_url) and logo_url != "":
                    card_html += f"<img src='{logo_url}' width='150'>"

                # Employer info
                card_html += f"""
                <h3>{row['Employer']}</h3>
                <p><a href='{row['Link']}' target='_blank'>Website</a></p>
                <p><strong>Level of Study:</strong> {', '.join(row['Level of Study_list'])}</p>
                <p><strong>Hiring For:</strong> {', '.join(row['Hiring For_list'])}</p>
                <p><strong>Target Programs:</strong> {', '.join(row['Target Programs_list'])}</p>
                <p><strong>Industry:</strong> {row['Industry']}</p>
                <p><strong>Opportunities:</strong> {', '.join(row['Opportunities_list'])}</p>
                </div>
                """

                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("")  # spacing between rows
