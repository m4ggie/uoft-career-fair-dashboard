import streamlit as st
import pandas as pd

# --- Load CSV ---
df = pd.read_csv("uoft_career_fair_employers.csv")

# Convert multi-value fields into lists for filtering
multi_cols = ["Level of Study", "Hiring For", "Target Programs", "Opportunities"]
for col in multi_cols:
    df[col + "_list"] = df[col].apply(lambda x: x.split("|") if pd.notnull(x) else [])

# --- Sidebar ---
with st.sidebar:
    st.title("Filters")

    search_name = st.text_input("Search Employer by Name")

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

    if st.button("Deselect All Filters"):
        st.experimental_rerun()
    apply_filters = st.button("Search")

# --- Filter Function ---
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
    # --- Display Cards in Scrolling Layout ---
    # Responsive: 3 cards per row on desktop, fewer on narrow screens
    cards_per_row = 3
    for row_idx in range(0, len(filtered_df), cards_per_row):
        cols = st.columns(cards_per_row)
        for i, (_, row) in enumerate(filtered_df.iloc[row_idx:row_idx+cards_per_row].iterrows()):
            col = cols[i]
            with col:
                # Use logo if available, else show employer name only
                logo_url = row.get("Logo", "")
                if pd.notnull(logo_url) and logo_url != "":
                    st.image(logo_url, width=150)

                st.markdown(f"### {row['Employer']}")
                st.markdown(f"[Website]({row['Link']})")
                st.markdown(f"**Level of Study:** {', '.join(row['Level of Study_list'])}")
                st.markdown(f"**Hiring For:** {', '.join(row['Hiring For_list'])}")
                st.markdown(f"**Target Programs:** {', '.join(row['Target Programs_list'])}")
                st.markdown(f"**Industry:** {row['Industry']}")
                st.markdown(f"**Opportunities:** {', '.join(row['Opportunities_list'])}")
                st.markdown("---")
