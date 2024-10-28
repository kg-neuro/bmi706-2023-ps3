import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###


@st.cache_data
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


# Uncomment the next line when finished
df = load_data()

### P1.2 ###
st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
year = st.slider("Year", min_value=df["Year"].min(), max_value=df["Year"].max(), value=2012)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = st.radio("M", ["M", "F"])
subset = subset[subset["Sex"] == sex]
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
countries = st.multiselect("Countries", countries, default=countries)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer = st.selectbox("Cancer", subset["Cancer"].unique(), index = 0)
subset = subset[subset["Cancer"] == cancer]
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

#add interval for bonus question of syncing the bar chart with the heatmap
interval = alt.selection_interval(encodings=['x'])

#chart: adjusted to a heat map for question 2.5
chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age:O", title="Age", sort=ages), #sorted in increasing age group for better visualization
    y=alt.Y("Country:N", title="Country"),
    color=alt.Color("Rate:Q", title="Mortality rate per 100k", scale=alt.Scale(type='log', domain=[0.01, 1000], clamp=True)),
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
    width = 500
).add_selection(
    interval
)
### P2.5 ###

#st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")


### BONUS ###
# taken inspiration from pset description and demo to do the bar chart showing population size by country
# want to be able to filter the bar chart by age and also have the bar chart adjust to selected age and countries used in heatmap

#bar chart - use subset as dataframe to ensure it is on the same subset as heatmap
population_country_chart = alt.Chart(subset).mark_bar().encode(
    x=alt.X("sum(Pop)", title="Population size"),
    y=alt.Y("Country:N", title="Country"),
    tooltip=["Pop", "Country"],
).properties(
    title=f"Population size by country for {'males' if sex == 'M' else 'females'} in {year}",
    width = 500
).transform_filter(interval) #add age filter to chart through interval selection of heatmap


combined_charts = chart & population_country_chart

st.altair_chart(combined_charts, use_container_width=True)
