from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pycountry

app = Flask(__name__)

def iso2_to_iso3(iso2):
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except:
        return None

def iso2_to_name(iso2):
    try:
        return pycountry.countries.get(alpha_2=iso2).name
    except:
        return iso2

def format_top10(top10str):
    if pd.isna(top10str):
        return ''
    return "<br>".join([x.strip() for x in top10str.split(",")])

@app.route('/')
def index():
    # 国ごとの情報
    df = pd.read_csv('Starbucks_Processed.csv')
    df['Store_Count'] = df['Store_Count'].astype(int)
    df['Country_ISO3'] = df['Country'].apply(iso2_to_iso3)
    df['Country_Name'] = df['Country'].apply(iso2_to_name)
    df['Top10_Line'] = df['Top10_String'].apply(format_top10)
    df = df[df['Country_ISO3'].notna()]

    # 店舗ごとの座標
    df_points = pd.read_csv('Longitude_Latitude.csv', header=None, names=['Longitude', 'Latitude'])

    # 色スケール
    custom_scale = [
        [0.00, "rgb(245,255,245)"],
        [0.01, "rgb(200,255,200)"],
        [0.03, "rgb(144,238,144)"],
        [0.06, "rgb(50,205,50)"],
        [0.10, "rgb(34,139,34)"],
        [1.00, "rgb(0,100,0)"],
    ]

    # 地図（Choropleth部分）
    fig = px.choropleth(
        df,
        locations='Country_ISO3',
        locationmode='ISO-3',
        color='Store_Count',
        color_continuous_scale=custom_scale,
        hover_name='Country_Name',
        hover_data={
            'Store_Count': True,
            'Top10_Line': True,
        },
        title='Global Distribution of Starbucks Stores'
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Store Count: %{customdata[0]}<br>Top 10 Cities:<br>%{customdata[1]}"
    )
    fig.update_geos(
        showcoastlines=True,
        showland=True,
        landcolor="white",
        bgcolor="white",
        fitbounds="locations"
    )

    # 赤点（店舗プロット、ホバー時情報ナシにする！）
    fig.add_trace(
        go.Scattergeo(
            lon = df_points['Longitude'],
            lat = df_points['Latitude'],
            mode = 'markers',
            marker = dict(
                size = 2,
                color = 'red',
                opacity=0.8,
            ),
            hoverinfo='skip',   # ← これでホバー時なにも出さない！
            showlegend=False
        )
    )

    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    # displayModeBar 完全オフ
    chart_html = fig.to_html(
        full_html=False,
        config={
            'displayModeBar': False
        }
    )

    return render_template('index.html', chart_html=chart_html)

if __name__ == '__main__':
    app.run(debug=True)
