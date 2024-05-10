
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
tab = st.sidebar.radio("Navigation", ('Order Details', 'Market Basket Analysis'))

if tab == 'Order Details':
    st.header("Order Details")
    st.write(orders_data)
    # Picking the date 
    orders_data['Order Date'] = pd.to_datetime(orders_data['Order Date'])
    start_date = pd.to_datetime(orders_data['Order Date']).min()
    end_date = pd.to_datetime(orders_data['Order Date']).max()

    start = pd.to_datetime(st.sidebar.date_input('Pick start date', start_date))
    end = pd.to_datetime(st.sidebar.date_input('Pick end date', end_date))
    orders_data = orders_data[(orders_data['Order Date'] >= start) & (orders_data['Order Date'] <= end)].copy()

    # Product by category and market
    market = st.sidebar.selectbox('Pick your Market', orders_data['Market'].unique())
    category = st.sidebar.multiselect('Pick your category', orders_data['Category'].unique())

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

    # Charts for the Orders Dataset

    # Sales by Sub Category
    st.subheader('Sales by Sub Category')
    grp = filtered_data.groupby(by=['Sub-Category'], as_index=False)['Sales'].sum()
    fig1 = px.bar(grp, x='Sub-Category', y='Sales', height=600, width=700)
    st.plotly_chart(fig1, use_container_width=True)

    # Sales by Ship Mode
    st.subheader('Sales by Ship Mode')
    fig2 = px.box(filtered_data, x='Ship Mode', y='Sales', height=400, width=600)
    st.plotly_chart(fig2, use_container_width=True)

    # Profit by Country
    st.subheader('Profit by Country')
    grp = filtered_data.groupby(by=['Country'], as_index=False)['Profit'].sum()
    fig3 = px.bar(grp, x="Country", y="Profit")
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        # Scatter plot to show relationship between profit and sales
        scatter = px.scatter(orders_data, x="Quantity", y="Profit", size='Sales')
        scatter['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                                 titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                                 yaxis=dict(title="Profit", titlefont=dict(size=19)))
        st.plotly_chart(scatter, use_container_width=True)

    with chart2:
        # Segment wise sales distribution
        st.subheader('Segment wise profit distribution')

        fig5 = px.pie(orders_data, values="Sales", names='Segment')
        fig5.update_traces(text=orders_data['Segment'], textposition='outside')
        st.plotly_chart(fig5, use_container_width=True)

    # Line chart to show sales over time
    filtered_data.loc[:, "month_year"] = filtered_data["Order Date"].dt.to_period("M")
    st.subheader('Sales over time')

    line = pd.DataFrame(filtered_data.groupby(filtered_data["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    line = line.sort_values(by="month_year")
    fig4 = px.line(line, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1500, template="gridon")
    st.plotly_chart(fig4, use_container_width=True)

else:
    st.header("Market Basket Analysis Association Rules")
    st.write(rules_data)

    st.subheader("Association Rules Heat Map")
    # Creating the heatmap based on selected axes
    pivot_data = rules_data.pivot_table(index=rules_data['antecedents'], columns=rules_data['consequents'], values='lift')

    heatfig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_data, ax=ax, annot=True, cmap="viridis")
    st.pyplot(heatfig)

    chart1, chart2 = st.columns((2))
    with chart1:
        fig6 = px.bar(rules_data, x='support', y='antecedents', orientation='h', title='Top Antecedents based on Support')
        st.plotly_chart(fig6, use_container_width=True)
    with chart2:
        fig7 = px.bar(rules_data, x='support', y='consequents', orientation='h', title='Top Consequents based on Support')
        st.plotly_chart(fig7, use_container_width=True)

    # The Treemap
    st.subheader("Hierarchical view of Antecedents with their Consequents based Support")
    fig10 = px.treemap(rules_data, path=["antecedents", "consequents"], values="support", hover_data=["support"],
                       color="consequents")
    fig10.update_layout(width=800, height=650)
    st.plotly_chart(fig10, use_container_width=True)