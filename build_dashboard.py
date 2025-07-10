#!/usr/bin/env python3

This script rebuilds enhanced_consumer_dashboard.html from the Excel source.
Usage:
    python build_dashboard.py Excel\ 2\ -\ mod_Consumer\ complaint\ analysis.xlsx

import sys, pandas as pd, plotly.express as px, plotly.graph_objects as go
from datetime import datetime

file_path = sys.argv[1] if len(sys.argv) > 1 else 'Excel 2 - mod_Consumer complaint analysis.xlsx'

complaints = pd.read_excel(file_path, sheet_name='Consumer_Complaints', engine='calamine')
state_df = pd.read_excel(file_path, sheet_name='State_Code_Name', engine='calamine', header=None)
state_df.columns = ['Src','State','Code','code_dup','state_dup']
state_map = dict(zip(state_df['Code'].str.strip(), state_df['State'].str.strip()))

# Dates
parse = lambda x: pd.to_datetime(x, errors='coerce')
complaints['Date received'] = complaints['Date received'].apply(parse)
complaints['Date resolved'] = complaints['Date resolved'].apply(parse)

complaints['State_Name'] = complaints['State'].map(state_map)

na_count = complaints['State_Name'].isna().sum()
unmapped_summary = complaints[complaints['State_Name'].isna()].groupby('State').size().reset_index(name='Complaint_Count').sort_values('Complaint_Count', ascending=False)

# Visuals
product_counts = complaints['Product'].value_counts().nlargest(10).reset_index()
product_counts.columns = ['Product','Count']
fig_product = px.bar(product_counts, x='Product', y='Count', title='Top 10 Products')
state_counts = complaints['State'].value_counts().reset_index()
state_counts.columns = ['State','Count']
fig_state = px.choropleth(state_counts, locations='State', locationmode='USA-states', color='Count', scope='usa', title='Complaints by State')
complaints['YearMonth'] = complaints['Date received'].dt.to_period('M')
monthly_counts = complaints.groupby('YearMonth').size().reset_index(name='Count')
monthly_counts['YearMonth'] = monthly_counts['YearMonth'].dt.to_timestamp()
fig_time = px.line(monthly_counts, x='YearMonth', y='Count', title='Monthly Trend')
company_product = complaints.groupby(['Product','Company']).size().reset_index(name='Count')
initial_product = company_product['Product'].iloc[0]
filtered = company_product[company_product['Product']==initial_product].nlargest(20,'Count')
bar = go.Bar(x=filtered['Company'], y=filtered['Count'])
fig_company = go.Figure(data=[bar])
fig_company.update_layout(title='Top 20 Companies for Product: '+initial_product,
                          updatemenus=[{
                              'active':0,
                              'buttons':[{
                                  'label':prod,
                                  'method':'update',
                                  'args':[{'x':[company_product[company_product['Product']==prod].nlargest(20,'Count')['Company']],
                                           'y':[company_product[company_product['Product']==prod].nlargest(20,'Count')['Count']]},
                                          {'title':'Top 20 Companies for Product: '+prod}]
                              } for prod in company_product['Product'].unique()]
                          }])
complaints['Resolution_Days'] = (complaints['Date resolved'] - complaints['Date received']).dt.days
median_res = complaints.groupby('Product')['Resolution_Days'].median().reset_index().dropna()
fig_median = px.bar(median_res, x='Product', y='Resolution_Days', title='Median Resolution Days by Product')

html_parts = []
for fig in [fig_product, fig_state, fig_time, fig_company, fig_median]:
    html_parts.append(fig.to_html(full_html=False, include_plotlyjs='cdn' if fig==fig_product else False))

html = '<html><head><title>Enhanced Dashboard</title></head><body>' +        '<h1 style="text-align:center;">Enhanced Consumer Complaints Dashboard</h1>' +        ''.join(['<div style="margin-bottom:50px;">'+p+'</div>' for p in html_parts]) +        '<h2>Data Quality Checks</h2>' +        '<p>Total records with missing State Name: '+str(na_count)+'</p>' +        '<p>See table below for unmapped State Codes (top 10 shown)</p>' +        unmapped_summary.head(10).to_html(index=False) +        '</body></html>'

with open('enhanced_consumer_dashboard.html','w') as f:
    f.write(html)
print('Dashboard rebuilt ➜ enhanced_consumer_dashboard.html')
