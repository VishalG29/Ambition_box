from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import json
import plotly.utils

app = Flask(__name__)
df = pd.read_csv('merged.csv')

def create_chart(func, data, **kwargs):
    fig = func(data, **kwargs)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(size=12))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    return render_template('index.html', 
                         locations=sorted(df['location'].unique()), 
                         industries=sorted(df['industry'].unique()), 
                         types=sorted(df['type'].unique()))

@app.route('/submit', methods=['POST'])
def submit():
    form = request.form
    filtered_df = df.copy()
    
    for field, col in [('location', 'location'), ('industry', 'industry'), ('type', 'type')]:
        val = form.get(field)
        if val and val != 'All':
            filtered_df = filtered_df[filtered_df[col] == val]
    
    if form.get('rating'):
        try:
            filtered_df = filtered_df[filtered_df['company_rating'] >= float(form.get('rating'))]
        except ValueError:
            pass
    
    if form.get('view_type') == 'table':
        table_html = filtered_df.to_html(classes='table table-striped table-hover', table_id='dataTable', escape=False, index=False) if len(filtered_df) > 0 else "<p class='text-center text-muted'>No data found matching your criteria.</p>"
        return render_template('results.html', view_type='table', table_html=table_html, data_count=len(filtered_df))
    
    if len(filtered_df) == 0:
        return render_template('results.html', view_type='visualizations', error="No data found matching your criteria.")
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
    graphs = []
    
    # Chart configurations
    charts = [
        (px.bar, filtered_df.nlargest(10, 'company_rating')[['company_name', 'company_rating']], 
         dict(x='company_rating', y='company_name', orientation='h', title='🏆 Top 10 Companies by Rating', color='company_rating', color_continuous_scale='viridis')),
        (px.histogram, filtered_df, 
         dict(x='company_rating', title='📊 Company Rating Distribution', nbins=15, color_discrete_sequence=[colors[0]])),
        (px.pie, None, 
         dict(values=filtered_df['industry'].value_counts().head(8).values, names=filtered_df['industry'].value_counts().head(8).index, title='🏭 Companies by Industry', hole=0.4, color_discrete_sequence=colors)),
        (px.bar, None,
         dict(x=filtered_df['size'].value_counts().index, y=filtered_df['size'].value_counts().values, title='🏢 Company Size Distribution', color=filtered_df['size'].value_counts().values, color_continuous_scale='plasma')),
        (px.scatter, filtered_df,
         dict(x='years_old', y='company_rating', title='📈 Company Age vs Rating', color='industry', hover_data=['company_name'], color_discrete_sequence=colors)),
        (px.bar, None,
         dict(x=filtered_df.groupby('location')['company_rating'].mean().sort_values(ascending=True).tail(10).values, y=filtered_df.groupby('location')['company_rating'].mean().sort_values(ascending=True).tail(10).index, orientation='h', title='📍 Top Locations by Average Rating', color=filtered_df.groupby('location')['company_rating'].mean().sort_values(ascending=True).tail(10).values, color_continuous_scale='turbo'))
    ]
    
    for func, data, kwargs in charts:
        if data is None:
            fig = func(**kwargs)
        else:
            fig = func(data, **kwargs)
        
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(size=12))
        if 'height' not in kwargs and ('Top 10 Companies' in kwargs.get('title', '') or 'Top Locations' in kwargs.get('title', '')):
            fig.update_layout(height=400)
        if 'Company Size' in kwargs.get('title', ''):
            fig.update_xaxes(tickangle=45)
        
        graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    return render_template('results.html', view_type='visualizations', graphs=graphs, data_count=len(filtered_df))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
