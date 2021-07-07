# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 18:08:23 2021
@author: INVISION
"""

import pandas as pd

df = pd.read_excel('HOSPITAL_TEMPLATE.xlsx')

today = "2021.07.07."
doctor = "김동현"
hospital = "동현치과"
contact = "010-7334-3551"
address = "경기도 군포시 군포로"


df['문서명'].iloc[0] = today + " " + hospital
df['참여자 이름'].iloc[0] = doctor
df['이메일 또는 휴대전화번호'].iloc[0] = contact
df['1-텍스트'].iloc[0] = hospital # 치과의원명
df['2-텍스트'].iloc[0] = today # 오늘날짜(계약일)
df['3-텍스트'].iloc[0] = hospital # 치과의원명
df['4-텍스트'].iloc[0] = address # 치과 주소
df['5-텍스트'].iloc[0] = doctor # 치과의원 대표자 성명

df.to_excel(hospital+".xlsx", index=False, na_rep='')  


