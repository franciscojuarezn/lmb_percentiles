import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv('hitters_perc.csv')

hitters_perc = load_data()

# Streamlit app
st.title("Player Percentiles")

# Select player filter: All players or Qualified players
player_filter = st.radio("Choose player type:", ["All Players", "Qualified Players"])

# Filter dataset based on the 'isQualified' column
if player_filter == "Qualified Players":
    filtered_data = hitters_perc[hitters_perc['isQualified'] == True]
else:
    filtered_data = hitters_perc

# Recalculate percentiles based on the filtered data
metrics = ['OPS', 'AVG', 'OBP', 'SLG', 'K%', 'BB%', 'Whiff%', 'SwStr%', 'FB%', 'GB%', 'LD%', 'SB%', 'BABIP']
for metric in metrics:
    percentile_column = metric + '_percentile'
    # Recalculate percentiles for each metric
    filtered_data[percentile_column] = filtered_data[metric].rank(pct=True) * 100

# Select player from filtered data, defaulting to "Art Charles" when "All Players" is selected
if player_filter == "All Players":
    default_player = "Art Charles" if "Art Charles" in filtered_data['Name'].values else filtered_data['Name'].iloc[0]
else:
    default_player = filtered_data['Name'].iloc[0]

player_name = st.selectbox("Select a player:", filtered_data['Name'].unique(), index=filtered_data['Name'].tolist().index(default_player))

# Get selected player's data
player_data = filtered_data[filtered_data['Name'] == player_name].iloc[0]

# Function to create the percentiles chart
def percentiles_chart(player_data):
    fig = go.Figure()

    # Correctly ordered metrics list
    reverse_metrics = ['K%', 'Whiff%', 'SwStr%', 'GB%']  # Reverse percentiles for these metrics

    plotted_metrics = []  # List to keep track of metrics that are plotted

    # Custom color scale: blue -> gray -> red
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

    # Metrics to be formatted with 3 decimal places
    three_decimal_metrics = ['OBP', 'SLG', 'AVG', 'OPS', 'BABIP']

    for metric in metrics:
        value = player_data.get(metric, None)  # Metric value
        percentile_value = player_data.get(metric + '_percentile', None)  # Percentile value

        # Skip metrics with NaN values
        if pd.isna(value) or pd.isna(percentile_value):
            continue

        # Reverse percentile for specific metrics
        if metric in reverse_metrics:
            percentile_value = 100 - percentile_value

        # Format the value to 3 decimal places only for specific metrics
        if metric in three_decimal_metrics:
            formatted_value = f"{value:.3f}"
        else:
            formatted_value = f"{value}"

        # Set text for the bar
        bar_text = f"{formatted_value} ({percentile_value}%)"

        # Add the metric to the plotted metrics list
        plotted_metrics.append(metric)

        # Add the bar trace
        fig.add_trace(go.Bar(
            x=[percentile_value],  # Percentile value
            y=[metric],  # Metric name
            orientation='h',
            marker=dict(
                color=[percentile_value],  # Color based on percentile
                colorscale=custom_colorscale,  # Apply the custom color scale
                cmin=0,
                cmax=100,
            ),
            hoverinfo='none',
            text=[bar_text],  # Show both actual value and percentile
            textposition='none'  # Remove text from inside the bars (handled by annotations)
        ))

        # Add percentile text inside a gray square at the end of the bar
        fig.add_annotation(
            x=percentile_value,
            y=metric,
            text=f"<b>{int(percentile_value)}</b>",
            showarrow=False,
            font=dict(size=12, color='white'),  # Keep this text white
            align='center',
            width=18,
            height=18,
            bgcolor='gray',  # Gray square
            bordercolor='black',
            borderpad=4
        )

        # Add actual value text outside the plot (aligned to the right side, further away from the grid)
        fig.add_annotation(
            x=105,  # Keep the value aligned on the right side
            y=metric,
            text=f"<b>{formatted_value}</b>",  # Make the text bold, formatted correctly
            showarrow=False,
            xref='x',
            xanchor='left',  # Keep it outside the grid
            yref='y',
            yanchor='middle',
            font=dict(size=14, color='black')
        )

    # Add a vertical gray line at the 50th percentile
    fig.add_shape(
        type='line',
        x0=50,
        y0=-0.5,
        x1=50,
        y1=len(plotted_metrics) - 0.5,  # Adjusted to the number of plotted metrics
        line=dict(color="gray", width=2, dash="dash"),
    )

    # Add disclaimer
    fig.add_annotation(
        text="*2.1 PA per team game to qualify",
        x=0, xref="paper",  # Anchored to the left side of the chart
        xanchor='left',
        y=-0.05, yref='paper',
        yanchor='bottom',
        showarrow=False,
        font=dict(size=10, color="red")
    )

    # Add watermark below the disclaimer
    fig.add_annotation(
        text='@iamfrankjuarez', 
        x=0, xref='paper',  # Anchored to the left side below the disclaimer
        xanchor='left', 
        y=-0.10, yref='paper',  # Position it lower than the disclaimer
        yanchor='bottom', 
        showarrow=False,
        font=dict(size=12, color='gray'),
        opacity=0.4
    )

    # Update layout for better visualization and mobile responsiveness
    fig.update_layout(
        autosize=True,  # Enable autosize for responsiveness
        title=dict(text=f"Percentiles for {player_data['Name']}", font=dict(color="black")),  # Title in black
        xaxis=dict(
            range=[0, 105],  # Reduced range to bring values closer to the bars
            showgrid=False,  # Disable vertical gridlines
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            autorange='reversed',
            tickmode='array',
            tickvals=list(range(len(plotted_metrics))),
            ticktext=[f"{m}   " for m in plotted_metrics],
            tickfont=dict(color='black'),  # Set y-axis text color to black
            showgrid=True,  # Enable horizontal gridlines
            gridwidth=1,  # Set gridline width
            gridcolor='lightgray',  # Set gridline color
        ),
        height=800,  # Fixed height
        width=800,  # Fixed width
        showlegend=False,
        margin=dict(l=20, r=50, t=50, b=80),  # Adjusted bottom margin for watermark and disclaimer
        plot_bgcolor='beige',  # Set plot background color to beige
        paper_bgcolor='beige',  # Set overall background color to beige
    )

    # Display the plotly chart in Streamlit with mobile responsiveness
    st.plotly_chart(fig, use_container_width=True)  # Use container width to make it responsive

# Plot the percentiles chart for the selected player
percentiles_chart(player_data)

# Socials and contact functions
def open_socials():
    st.write("Follow me on social media:")
    st.markdown("[Twitter](https://twitter.com/iamfrankjuarez)")
    st.markdown("[LinkedIn](https://linkedin.com/in/francisco-juarez-niebla-4b6271147)")
    st.markdown("[GitHub](https://github.com/franciscojuarezn)")

def show_contact_form():
    st.write("📧 Contact me at: data.frankly@gmail.com")

# Socials and Contact section at the bottom of the page
col1, col2, col3 = st.columns([4,1,1], gap="small")

with col2:
    if st.button("🔗 Socials"):
        open_socials()

with col3:
    if st.button("📧 Contact"):
        show_contact_form()
