import streamlit as st
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
import seaborn as sns
import matplotlib.pyplot as plt

st.title('Titanic dataset 분석')

df = sns.load_dataset('titanic')
df.dropna(inplace=True)

st.dataframe(df, use_container_width=True)

plt.figure()
g = sns.barplot(x='sex', y='survived', data=df)
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x='sex', y='fare', data=df)
st.pyplot(g.get_figure())

import pandas as pd

def agg_func(col):
    if pd.api.types.is_categorical_dtype(col) or pd.api.types.is_object_dtype(col):
        return 'count'
    elif pd.api.types.is_numeric_dtype(col):
        return 'mean'
    else:
        return 'first'

# 'sex' 열을 제외한 나머지 열에 대해서만 집계를 수행합니다
columns_to_agg = [col for col in df.columns if col != 'sex']

plt.figure()
groupedvalues = df.groupby('sex').agg({col: agg_func(df[col]) for col in columns_to_agg}).reset_index()
g = sns.barplot(x='sex',y='survived',data=groupedvalues)

for index, row in groupedvalues.iterrows():
#    print(row.name, row.survived)
    g.text(row.name, row.survived, round(row.survived, 2), color='black', ha="center") # x, y, 텍스트    
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x='sex', y='survived', hue = 'class', data=df) # hue를 설정한다. hue도 categorial value가 되어야 한다.
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x='sex', y='survived', hue = 'class', order = ['female', 'male'], data=df) # x축의 순서 설정
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x='sex', y='survived', hue = 'class', order = ['female', 'male'], estimator = sum, data=df) # estimator(함수) 변경
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x='sex', y='survived', hue = 'class', order = ['female', 'male'], palette="Blues_d", data=df) # 팔레트 변경
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x = 'sex', y = 'survived', hue = 'class', data = df)
g.set(xlabel='Gender', ylabel='Survival Rate') # x, y축 텍스트 변경
st.pyplot(g.get_figure())

plt.figure()
g = sns.barplot(x = 'sex', y = 'survived', hue = 'class', data = df)
g.set_title("Gender vs Survival Rate in Males and Females") # 타이틀 변경
st.pyplot(g.get_figure())

plt.figure()
group = df.groupby(['pclass', 'survived']) # 등급별 생존별 데이터 그룹화
pclass_survived = group.size().unstack()  # 그룹별 카운트(NA가 아닌 것)을 세고 pivot한다
g = sns.heatmap(pclass_survived, annot = True, fmt='d') # 히트맵을 그리고 데이터를 정수로 표기한다
st.pyplot(g.get_figure())

plt.figure()
g = sns.violinplot(x ="sex", y ="age", hue ="survived", data = df, split = True) # hue를 설정하고 분포 그래프를 그린다
st.pyplot(g.get_figure())

plt.figure()
g = sns.violinplot(x ="sex", y ="age", hue ="survived", data = df, split = True, cut=0) 
female = df[df["sex"]=="female"]
male = df[df["sex"]=="male"]
st.pyplot(g.get_figure())
