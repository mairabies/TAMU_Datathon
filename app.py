import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from flask import render_template

file_path = 'data/movies.csv'
movies_df = pd.read_csv(file_path)

app = dash.Dash(__name__, external_stylesheets=['/assets/bootstrap.css'])

app.title = "Movie Dashboard"

app.layout = html.Div([
    html.H1("Movie Dashboard", style={'text-align': 'center'}),
    html.P("By Maira Athar", style={'text-align': 'center'}),
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='genre-dropdown',
                        options=[{'label': genre, 'value': genre} for genre in movies_df['genre'].unique()],
                        multi=True,
                        value=[],  # Initialize with no selection
                        className='quartz-dropdown form-control',  # Apply Quartz Bootstrap styling
                        style={'width': '100%'}, 
                        placeholder="Genre?"
                    ),
                    dcc.Dropdown(
                        id='rating-dropdown',
                        options=[{'label': rating, 'value': rating} for rating in movies_df['rating'].dropna().unique()],
                        multi=True,
                        value=[],  # Initialize with no selection
                        className='quartz-dropdown form-control',  # Same here for consistency
                        style={'width': '100%'},
                        placeholder="Rating?"
                    ),
                ]),
                width=6  # Make the left side take up 50% of the screen
            ),
            
            # Right side (Sliders)
            dbc.Col(
    html.Div([
        html.Label('Select Runtime Range:'),
        dcc.RangeSlider(
            id='runtime-slider',
            min=movies_df['runtime'].min(),
            max=movies_df['runtime'].max(),
            step=1,
            marks={i: str(i) for i in range(60, 361, 60)},  # Adjust to your preferred interval
            value=[movies_df['runtime'].min(), movies_df['runtime'].max()],
            className="custom-range-slider"
        ),
        html.Label('Select Score Range:'),
        dcc.RangeSlider(
            id='score-slider',
            min=movies_df['score'].min(),
            max=movies_df['score'].max(),
            step=0.1,
            marks={round(i, 1): str(round(i, 1)) for i in range(int(movies_df['score'].min()), int(movies_df['score'].max()) + 1)}, 
            value=[movies_df['score'].min(), movies_df['score'].max()],
            className="custom-range-slider"
        ),
    ]),
    width=6,  # Make the right side take up 50% of the screen
    className="sliders-container"  # Add custom class for styling
)
        ], className="mb-4"),  # Add margin below the row
        
        # Graphs in an Asymmetrical Grid Layout
        dbc.Row([
            dbc.Col(dcc.Graph(id='genre-popularity-graph', className='graph-container'), width=6),
            dbc.Col(dcc.Graph(id='heatmap-graph', className='graph-container'), width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id='gross-vs-budget-graph', className='graph-container'), width=12),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id='score-distribution-graph', className='graph-container'), width=4),
            dbc.Col(dcc.Graph(id='sunburst-graph', className='graph-container'), width=8),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id='top-directors-graph', className='graph-container'), width=6),
            dbc.Col(dcc.Graph(id='runtime-distribution-graph', className='graph-container'), width=6),
        ], className="mb-4"), 

        dbc.Row([
            dbc.Col(dcc.Graph(id='release-trend-graph', className='graph-container'), width=7),
            dbc.Col(dcc.Graph(id='average-score-genre-graph', className='graph-container'), width=5),
        ], className="mb-4")
    ], fluid=True)
])

# Callbacks to update graphs based on user input
@app.callback(
    Output('genre-popularity-graph', 'figure'),
    Output('average-score-genre-graph', 'figure'),
    Output('gross-vs-budget-graph', 'figure'),
    Output('score-distribution-graph', 'figure'),
    Output('release-trend-graph', 'figure'),
    Output('top-directors-graph', 'figure'),
    Output('runtime-distribution-graph', 'figure'),
    Output('sunburst-graph', 'figure'), 
    Output('heatmap-graph', 'figure'),    
    Input('genre-dropdown', 'value'),
    Input('rating-dropdown', 'value'),
    Input('runtime-slider', 'value'),
    Input('score-slider', 'value')
)
def update_graphs(selected_genres, selected_ratings, runtime_range, score_range):
    # Filter the data based on the user inputs
    if not selected_genres:  # Handle case when dropdown is cleared
        selected_genres = movies_df['genre'].unique().tolist()
    if not selected_ratings:  # Handle case when rating dropdown is cleared
        selected_ratings = movies_df['rating'].dropna().unique().tolist()
        
    filtered_df = movies_df[
        movies_df['genre'].isin(selected_genres) &
        movies_df['rating'].isin(selected_ratings) &
        (movies_df['runtime'] >= runtime_range[0]) & (movies_df['runtime'] <= runtime_range[1]) &
        (movies_df['score'] >= score_range[0]) & (movies_df['score'] <= score_range[1])
    ]

    # 1. Genre Popularity Bar Chart
    genre_counts = filtered_df['genre'].value_counts().head(10)
    genre_popularity_fig = px.bar(
        x=genre_counts.index, 
        y=genre_counts.values, 
        labels={'x': 'Genre', 'y': 'Number of Movies'}, 
        title="Top 10 Most Common Movie Genres"
    )

    genre_popularity_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#e83384'
    )  

    genre_popularity_fig.update_layout(
        title=dict(text="Top Most Common Movie Genres", x=0.5),
        xaxis_title="Genre",
        yaxis_title="Number of Movies",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )

    # 2. Average Score by Genre
    average_score_by_genre = filtered_df.groupby('genre')['score'].mean().sort_values(ascending=False).head(10)
    
    score_min = average_score_by_genre.min()
    score_max = average_score_by_genre.max()

    average_score_genre_fig = px.bar(average_score_by_genre, x=average_score_by_genre.index, y=average_score_by_genre.values, 
                                     labels={'x': 'Genre', 'y': 'Average Score'}, 
                                     title="Top Genres by Average IMDb Score")
    average_score_genre_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#c16bdb'
    )  

    average_score_genre_fig.update_layout(
        title=dict(text="Top Genres by Average IMDb Score", x=0.5),
        xaxis_title="Genre",
        yaxis_title="Average Score",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
        yaxis=dict(
            range=[score_min, score_max], 
        )
    )

    # 3. Gross vs. Budget Scatter Plot
    gross_vs_budget_fig = px.scatter(filtered_df, x='budget', y='gross', log_x=True, log_y=True,
                                     title="Gross Earnings vs. Budget",
                                     labels={'budget': 'Budget ($)', 'gross': 'Gross Earnings ($)'})
    gross_vs_budget_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#c16bdb'
    )  

    gross_vs_budget_fig.update_layout(
        title=dict(text="Gross Earnings vs. Budget", x=0.5),
        xaxis_title="Budget ($)",
        yaxis_title="Gross Earnings ($)",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )

    # 4. Score Distribution Histogram
    score_distribution_fig = px.histogram(filtered_df, x='score', nbins=20, 
                                           title="Distribution of IMDb Scores", 
                                           labels={'score': 'IMDb Score'})

    score_distribution_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#e83384'
    )  

    score_distribution_fig.update_layout(
        title=dict(text="Distribution of IMDb Scores", x=0.5),
        xaxis_title="IMDb Score",
        yaxis_title="Count",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )

    # 5. Release Trend Over Time
    movies_per_year = filtered_df['year'].value_counts().sort_index()
    release_trend_fig = px.line(movies_per_year, x=movies_per_year.index, y=movies_per_year.values,
                                title="Number of Movies Released Over Time",
                                labels={'x': 'Year', 'y': 'Number of Movies'})
    release_trend_fig.update_traces(
        line=dict(color='#e84886', width=2),
        marker=dict(size=5) 
    )

    release_trend_fig.update_layout(
        title=dict(text="Number of Movies Released Over Time", x=0.5),
        xaxis_title="Year",
        yaxis_title="Number of Movies",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )

    # 6. Top 10 Directors by Average Score
    top_directors = filtered_df.groupby('director')['score'].mean().sort_values(ascending=False).head(10)
    
    score_min = top_directors.min()
    score_max = top_directors.max() # For better view of ratings
    
    top_directors_fig = px.bar(top_directors, x=top_directors.values, y=top_directors.index, 
                                title="Top 10 Directors by Average IMDb Score",
                                labels={'x': 'Average Score', 'y': 'Director'})

    top_directors_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#33b6e2'
    )  

    top_directors_fig.update_layout(
        title=dict(text="Top 10 Directors by Average IMDb Score", x=0.5),
        xaxis_title="Average Score",
        yaxis_title="Director",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
        xaxis=dict(
            range=[score_min, score_max] 
        )
    )

    # 7. Runtime Distribution by Genre (Box Plot)
    top_genres = filtered_df['genre'].value_counts().head(10).index
    
    filtered_runtime_df = filtered_df[filtered_df['genre'].isin(top_genres)]
    runtime_distribution_fig = px.box(filtered_runtime_df, x='genre', y='runtime', 
                                      title="Runtime Distribution by Genre (Top 10 Genres)",
                                      labels={'x': 'Genre', 'y': 'Runtime (minutes)'})
    
    runtime_distribution_fig.update_traces(
        marker=dict(line=dict(width=0)), 
        marker_color='#e83384'
    )  

    runtime_distribution_fig.update_layout(
        title=dict(text="Runtime Distribution by Genre (Top 10 Genres)", x=0.5),
        xaxis_title="Genre",
        yaxis_title="Runtime (minutes)",
        title_font=dict(size=20), 
        font=dict(color="#e9e9e7"), 
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )

    sunburst_fig = px.sunburst(
        filtered_df,
        path=['genre', 'rating'],
        values='runtime',
        title="Sunburst Chart of Genre and Rating Distribution",
        labels={'runtime': 'Runtime (minutes)'},
        color='runtime',  # Color by a continuous variable like 'runtime'
        color_continuous_scale='plasma'  # Apply the plasma gradient
    )
    
    sunburst_fig.update_layout(
        title=dict(text="Sunburst Chart of Genre and Rating Distribution", x=0.5),
        title_font=dict(size=20),
        font=dict(color="#e9e9e7"),
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )



    # 9. Heatmap: Genre vs Score
    genre_score_counts = filtered_df.groupby(['genre', 'score']).size().unstack(fill_value=0)
    
    
    genre_score_heatmap_fig = px.imshow(
        genre_score_counts,
        labels={'x': 'Score', 'y': 'Genre', 'color': 'Number of Movies'},
        title="Heatmap of Genre vs Score"
    )
    genre_score_heatmap_fig.update_layout(
        title=dict(text="Heatmap of Genre vs Score", x=0.5),
        title_font=dict(size=20),
        font=dict(color="#e9e9e7"),
        paper_bgcolor="#212429",
        plot_bgcolor="#453552",
    )
    return (genre_popularity_fig, average_score_genre_fig, gross_vs_budget_fig, score_distribution_fig,
        release_trend_fig, top_directors_fig, runtime_distribution_fig, sunburst_fig, genre_score_heatmap_fig)


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
