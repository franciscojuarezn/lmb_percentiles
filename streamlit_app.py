import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv('hitters_perc.csv')

hitters_perc = load_data()

st.title("Player Percentiles")

# Select player
player_filter = st.radio("Choose player type:", ["All Players", "Qualified Players"])

# Filter dataset
if player_filter == "Qualified Players":
    filtered_data = hitters_perc[hitters_perc['isQualified'] == True]
else:
    filtered_data = hitters_perc

# Calculate percentiles
metrics = ['OPS', 'AVG', 'OBP', 'SLG', 'K%', 'BB%', 'Whiff%', 'SwStr%', 'FB%', 'GB%', 'LD%', 'SB%', 'BABIP']
for metric in metrics:
    percentile_column = metric + '_percentile'
    # Recalculate percentiles permetric
    filtered_data[percentile_column] = filtered_data[metric].rank(pct=True) * 100
    # Ensure no percentile is less than 1
    filtered_data[percentile_column] = filtered_data[percentile_column].clip(lower=1)

# Select player, set default
if player_filter == "All Players":
    default_player = "Art Charles" if "Art Charles" in filtered_data['Name'].values else filtered_data['Name'].iloc[0]
else:
    default_player = filtered_data['Name'].iloc[0]

player_name = st.selectbox("Select a player:", filtered_data['Name'].unique(), index=filtered_data['Name'].tolist().index(default_player))

# Get player's data
player_data = filtered_data[filtered_data['Name'] == player_name].iloc[0]

# Function for percentiles
def percentiles_chart(player_data):
    fig = go.Figure()

    reverse_metrics = ['K%', 'Whiff%', 'SwStr%', 'GB%']

    plotted_metrics = []  

    custom_colorscale = [
        [0.0, 'blue'],
        [0.2, 'DodgerBlue'],
        [0.4, 'lightblue'],
        [0.5, 'gray'],
        [0.7, 'lightcoral'],
        [0.8, 'indianred'],
        [0.9, 'firebrick'],
        [1.0, 'darkred']
    ]

    # Metrics for special format
    three_decimal_metrics = ['OBP', 'SLG', 'AVG', 'OPS', 'BABIP']

    for metric in metrics:
        value = player_data.get(metric, None)
        percentile_value = player_data.get(metric + '_percentile', None)

        # Skip nan
        if pd.isna(value) or pd.isna(percentile_value):
            continue

        # Reverse percentile
        if metric in reverse_metrics:
            percentile_value = 100 - percentile_value
            # Ensure no reversed percentile goes below 1
            percentile_value = max(1, percentile_value)

        # Format for 3 decimal points
        if metric in three_decimal_metrics:
            formatted_value = f"{value:.3f}"
        else:
            formatted_value = f"{value}"


        bar_text = f"{formatted_value} ({percentile_value}%)"

        plotted_metrics.append(metric)

        # Add the bar trace
        fig.add_trace(go.Bar(
            x=[percentile_value],  
            y=[metric],  
            orientation='h',
            marker=dict(
                color=[percentile_value],
                colorscale=custom_colorscale,
                cmin=0,
                cmax=100,
            ),
            hoverinfo='none',
            text=[bar_text],  # Show both valuse and percentile
            textposition='none'  # Remove text
        ))

        # Add percentile text
        fig.add_annotation(
            x=percentile_value,
            y=metric,
            text=f"<b>{int(percentile_value)}</b>",
            showarrow=False,
            font=dict(size=12, color='white'), 
            align='center',
            width=18,
            height=18,
            bgcolor='gray',
            bordercolor='black',
            borderpad=4
        )

        # Value text outside the plot
        fig.add_annotation(
            x=105,  
            y=metric,
            text=f"<b>{formatted_value}</b>",
            showarrow=False,
            xref='x',
            xanchor='left', 
            yref='y',
            yanchor='middle',
            font=dict(size=14, color='black')
        )

    # 50% dotted line
    fig.add_shape(
        type='line',
        x0=50,
        y0=-0.5,
        x1=50,
        y1=len(plotted_metrics) - 0.5, 
        line=dict(color="gray", width=2, dash="dash"),
    )

    # Add disclaimer
    fig.add_annotation(
        text="*2.1 PA per team game to qualify",
        x=0, xref="paper",  
        xanchor='left',
        y=-0.05, yref='paper',
        yanchor='bottom',
        showarrow=False,
        font=dict(size=10, color="red")
    )

    # Add watermark
    fig.add_annotation(
        text='@iamfrankjuarez', 
        x=0, xref='paper', 
        xanchor='left', 
        y=-0.10, yref='paper', 
        yanchor='bottom', 
        showarrow=False,
        font=dict(size=12, color='gray'),
        opacity=0.4
    )

    #
    fig.update_layout(
        autosize=True, 
        title=dict(text=f"Percentiles for {player_data['Name']}", font=dict(color="black")),  # Title in black
        xaxis=dict(
            range=[0, 105],  
            showgrid=False,  
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            autorange='reversed',
            tickmode='array',
            tickvals=list(range(len(plotted_metrics))),
            ticktext=[f"{m}   " for m in plotted_metrics],
            tickfont=dict(color='black'),  
            showgrid=True,  
            gridwidth=1.5,
            gridcolor='lightgray',
        ),
        height=800,  
        width=800,  
        showlegend=False,
        margin=dict(l=20, r=50, t=50, b=80),
        plot_bgcolor='beige',  
        paper_bgcolor='beige', 
    )

    st.plotly_chart(fig, use_container_width=True) 

percentiles_chart(player_data)

# Socials and contact functions
def open_socials():
    st.write("Follow me on social media:")
    st.markdown("[Twitter](https://twitter.com/iamfrankjuarez)")
    st.markdown("[LinkedIn](https://linkedin.com/in/francisco-juarez-niebla-4b6271147)")
    st.markdown("[GitHub](https://github.com/franciscojuarezn)")

def show_contact_form():
    st.write("📧 Contact me at: data.frankly@gmail.com")

col1, col2, col3 = st.columns([4,1,1], gap="small")

with col2:
    if st.button("🔗 Socials"):
        open_socials()

with col3:
    if st.button("📧 Contact"):
        show_contact_form()
