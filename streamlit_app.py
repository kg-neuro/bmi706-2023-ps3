import altair as alt
import pandas as pd
import streamlit as st
     
### P1.2 ###
@st.cache
def load_data():
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000
    return df

df = load_data()

### P1.2 ###

st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
year = st.slider(
    "Choose the year",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=2012
)
subset = df[df["Year"] == year]
st.write(subset)
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = "M"
subset = subset[subset["Sex"] == sex]
sex_select = st.radio("Select the sex", subset,index=None)
st.write("You selected", sex_select)
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]

country_select = st.multiselect(
    "Select countries to compare",
    options=subset[subset["Country"].isin(selected_countries)],
    default=countries 
)

st.write("You selected", country_select)
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer = "Malignant neoplasm of stomach"
subset = subset[subset["Cancer"] == cancer]
cancer_select = st.selectbox("Choose cancer type", subset)
st.write("You selected", cancer_select)
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

chart = alt.Chart(subset).mark_bar().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Rate", title="Mortality rate per 100k", scale=alt.Scale(type='log', domain=(0.01, 1000), clamp=True)),
    color="Country",
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)
### P2.5 ###

st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
