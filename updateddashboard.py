import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Reading CSV files
orders_data = pd.read_csv('orders_cleaned.csv')
rules_data = pd.read_csv('association_rules_results.csv')

st.set_page_config(layout='wide')
st.title(':department_store: Minger Electronics Insights Dashboard')
col1, col2 = st.columns((2))
# Adding dashboard filter
st.sidebar.title("Dashboard Filters")

# Making tabs
tab = st.sidebar.radio("Navigation", ('Order Insights', 'Market Basket Analysis'))

if tab == 'Order Insights':
    st.header("Order Details")
    st.write(orders_data)  # Display orders CSV as a table
    
    # Picking the date 
    orders_data['Order Date'] = pd.to_datetime(orders_data['Order Date'])
    start_date = pd.to_datetime(orders_data['Order Date']).min()
    end_date = pd.to_datetime(orders_data['Order Date']).max()

    start = pd.to_datetime(st.sidebar.date_input('Select Start Date', start_date))
    end = pd.to_datetime(st.sidebar.date_input('Select End Date', end_date))
    orders_data = orders_data[(orders_data['Order Date'] >= start) & (orders_data['Order Date'] <= end)].copy()

    # Product by "Category" and "Market"
    market = st.sidebar.selectbox('Select your Market', orders_data['Market'].unique())
    category = st.sidebar.multiselect('Select your Category', orders_data['Category'].unique())

    # Filtering the dashboard using the "Market" and "Product" category
    if market and category:
        filtered_data = orders_data[(orders_data["Market"].isin([market])) & (orders_data["Category"].isin(category))]
    elif market:
        filtered_data = orders_data[orders_data["Market"].isin([market])]
    elif category:
        # Retrieving subcategories belonging to the selected category
        subcategories = orders_data[orders_data["Category"].isin(category)]["Sub-Category"].unique().tolist()
        # Filtering based on both category and its subcategories
        filtered_data = orders_data[(orders_data["Category"].isin(category)) | (orders_data["Sub-Category"].isin(subcategories))]
    else:
        filtered_data = orders_data.copy()

    # Charts for the Order Insights

    # Sales Over Time
    st.subheader('Sales over time')
    filtered_data.loc[:, "year_month"] = filtered_data["Order Date"].dt.to_period("M")
    sales_over_time = pd.DataFrame(filtered_data.groupby(filtered_data["year_month"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    sales_over_time = sales_over_time.sort_values(by="year_month")
    sales_over_time_chart = px.line(sales_over_time, x="year_month", y="Sales", labels={"Sales": "Amount"}, height=500, width=1500, template="gridon")
    st.plotly_chart(sales_over_time_chart, use_container_width=True)

    # Sales by Sub-Category
    st.subheader('Sales by Sub Category')
    sales_by_subcat = filtered_data.groupby(by=['Sub-Category'], as_index=False)['Sales'].sum()
    sales_by_subcat_chart = px.bar(sales_by_subcat, x='Sub-Category', y='Sales', height=600, width=700)
    st.plotly_chart(sales_by_subcat_chart, use_container_width=True)

    # Profit by Country
    st.subheader('Profit by Country')
    profit_by_country = filtered_data.groupby(by=['Country'], as_index=False)['Profit'].sum()
    profit_by_country_chart = px.bar(profit_by_country, x="Country", y="Profit")
    st.plotly_chart(profit_by_country_chart, use_container_width=True)

    # Sales by Ship Mode
    st.subheader('Sales by Ship Mode')
    sales_by_ship_mode_chart = px.box(filtered_data, x='Ship Mode', y='Sales', height=400, width=600)
    st.plotly_chart(sales_by_ship_mode_chart, use_container_width=True)

    # Segment-wise Sales Distribution
    st.subheader('Segment wise profit distribution')
    segment_wise_sales = px.pie(orders_data, values="Sales", names='Segment')
    segment_wise_sales.update_traces(text=orders_data['Segment'], textposition='outside')
    st.plotly_chart(segment_wise_sales, use_container_width=True)

    # Relationship between Sales and Profits
    st.subheader('Relationship between Sales and Profits')
    scatter_plot = px.scatter(orders_data, x="Quantity", y="Profit", size='Sales')
    scatter_plot['layout'].update(title=" Sales vs. Profits using Scatter Plot.",
                                  titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                                  yaxis=dict(title="Profit", titlefont=dict(size=19)))
    st.plotly_chart(scatter_plot, use_container_width=True)

else:
  st.header("Market Basket Analysis Association Rules")
st.write(rules_data)

st.subheader("Association Rules Heat Map - Top 15 Antecedents and Consequents")
# Filter rules_data to include only the top 15 antecedents and consequents based on support
top_antecedents = rules_data['antecedents'].value_counts().head(15).index
top_consequents = rules_data['consequents'].value_counts().head(15).index
filtered_rules_data_top = rules_data[(rules_data['antecedents'].isin(top_antecedents)) & 
                                 (rules_data['consequents'].isin(top_consequents))]

# Create a pivot table with filtered data for top 15
pivot_data_top = filtered_rules_data_top.pivot_table(index='antecedents', columns='consequents', values='lift', aggfunc='mean')

# Create the heatmap for top 15
heatfig_top, ax_top = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_data_top, ax=ax_top, annot=True, cmap="viridis", fmt=".2f", annot_kws={"size": 10})
st.pyplot(heatfig_top)

st.subheader("Association Rules Heat Map - Lowest 15 Antecedents and Consequents")
# Filter rules_data to include only the lowest 15 antecedents and consequents based on support
bottom_antecedents = rules_data['antecedents'].value_counts().tail(15).index
bottom_consequents = rules_data['consequents'].value_counts().tail(15).index
filtered_rules_data_bottom = rules_data[(rules_data['antecedents'].isin(bottom_antecedents)) & 
                                 (rules_data['consequents'].isin(bottom_consequents))]

# Create a pivot table with filtered data for bottom 15
pivot_data_bottom = filtered_rules_data_bottom.pivot_table(index='antecedents', columns='consequents', values='lift', aggfunc='mean')

# Create the heatmap for bottom 15
heatfig_bottom, ax_bottom = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_data_bottom, ax=ax_bottom, annot=True, cmap="viridis", fmt=".2f", annot_kws={"size": 10})
st.pyplot(heatfig_bottom)

chart1, chart2 = st.columns(2)
with chart1:
    heat_bar_chart_top = px.bar(filtered_rules_data_top, x='support', y='antecedents', orientation='h', title='Top Antecedents Support')
    st.plotly_chart(heat_bar_chart_top, use_container_width=True)
    heat_bar_chart_bottom = px.bar(filtered_rules_data_bottom, x='support', y='antecedents', orientation='h', title='Lowest Antecedents Support')
    st.plotly_chart(heat_bar_chart_bottom, use_container_width=True)
with chart2:
    heat_con_chart_top = px.bar(filtered_rules_data_top, x='support', y='consequents', orientation='h', title='Top Consequents Support')
    st.plotly_chart(heat_con_chart_top, use_container_width=True)
    heat_con_chart_bottom = px.bar(filtered_rules_data_bottom, x='support', y='consequents', orientation='h', title='Lowest Consequents Support')
    st.plotly_chart(heat_con_chart_bottom, use_container_width=True)

# The Treemap
st.subheader("Hierarchical View of Antecedents with Their Consequents and Support")
treemap_chart_top = px.treemap(filtered_rules_data_top, path=["antecedents", "consequents"], values="support", hover_data=["support"],
                           color="consequents")
treemap_chart_top.update_layout(width=900, height=700)  # Increase treemap size
st.plotly_chart(treemap_chart_top, use_container_width=True)

treemap_chart_bottom = px.treemap(filtered_rules_data_bottom, path=["antecedents", "consequents"], values="support", hover_data=["support"],
                           color="consequents")
treemap_chart_bottom.update_layout(width=900, height=700)  # Increase treemap size
st.plotly_chart(treemap_chart_bottom, use_container_width=True)
