import streamlit as st
import pandas as pd
import numpy as np

st.title("Streamlit 내장 차트 예제")

# 데이터 생성
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)

# Line Chart
st.header("1. st.line_chart()")
st.line_chart(chart_data)

# Area Chart
st.header("2. st.area_chart()")
st.area_chart(chart_data)

# Bar Chart
st.header("3. st.bar_chart()")
st.bar_chart(chart_data)

# Altair Chart
st.header("4. st.altair_chart()")
import altair as alt
alt_chart = alt.Chart(chart_data).mark_circle().encode(
    x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c']
).interactive()
st.altair_chart(alt_chart, use_container_width=True)

# Vega-Lite Chart
st.header("5. st.vega_lite_chart()")
st.vega_lite_chart(chart_data, {
    'mark': {'type': 'circle', 'tooltip': True},
    'encoding': {
        'x': {'field': 'a', 'type': 'quantitative'},
        'y': {'field': 'b', 'type': 'quantitative'},
        'size': {'field': 'c', 'type': 'quantitative'},
    },
})

# Matplotlib/Seaborn Chart
st.header("6. st.pyplot() (Matplotlib/Seaborn)")
import matplotlib.pyplot as plt
import seaborn as sns
fig, ax = plt.subplots()
sns.histplot(chart_data['a'], ax=ax)
st.pyplot(fig)

# PyDeck Chart
st.header("7. st.pydeck_chart()")
import pydeck as pdk
# 이 예제에서는 지리 정보가 필요하므로 더미 데이터를 사용
pydeck_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=37.76,
        longitude=-122.4,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=pydeck_data,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=pydeck_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))

# st.plotly_chart()
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.header("8. st.plotly_chart()")

plotly_fig = px.scatter(x=chart_data['a'], y=chart_data['b'], size=chart_data['c'].abs())
st.plotly_chart(plotly_fig, use_container_width=True)