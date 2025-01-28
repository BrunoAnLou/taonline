import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.app_logo import add_logo
import time
import os
import glob2
from datetime import datetime , timedelta
from styles import logo, cores_sidebar

st.set_page_config(page_title='TA Online - Plansul',layout="wide")


hora = datetime.now().time()
hora_atual = pd.to_timedelta(hora.strftime('%H:%M:%S'))



#################################################layout############################################################

logo()
cores_sidebar()

################################## DATA FRAMES #####################################################################

ta = 'C:\\Users\\p739492\\Projetos\\TA_ONLINE\\aaa.csv'
wfm = 'C:\\Users\\p739492\\Projetos\\TA_ONLINE\\base_func.csv'

df = pd.read_csv(ta, sep=',')
base = pd.read_csv(wfm, sep=';',  encoding='latin-1')

df = df.replace('---', 0)

############################################# TRABALHANDO BASE( FUTURO SQL ) #######################################

base['saida'] = pd.to_timedelta(base['saida'])
base['entrada'] = pd.to_timedelta(base['entrada'])

base['CH']= base['saida'] - base['entrada']

base['CH'] = base.apply(lambda row: row['CH'] + pd.Timedelta(days=1) if row['saida']< row['entrada'] else row['CH'], axis=1)


##CH
base['CH'] = abs(base['CH'].dt.total_seconds()/60)

############################################TRABALHANDO DATAFRAME FINAL ##############################################
df['TEMPO_EM_ATENDIMENTO'] = pd.to_timedelta(df['TEMPO_EM_ATENDIMENTO'])
df['PAUSA_PRODUTIVA'] = pd.to_timedelta(df['PAUSA_PRODUTIVA'])
df['TEMPO_TOTAL_LOGADO'] = pd.to_timedelta(df['TEMPO_TOTAL_LOGADO'])
df['HORA_LOGIN'] = pd.to_timedelta(df['HORA_LOGIN'])
df['TMA'] = pd.to_timedelta(df['TMA'])
df['ESTOURO DE PAUSA'] = pd.to_timedelta(df['PAUSAS_OFICIAIS_EXCEDIDO'])
df['TEMPO_TOTAL_LOGADO'] = pd.to_timedelta(df['TEMPO_TOTAL_LOGADO'])


df_rel = df.groupby('AGENTE_NOME').agg({
    'TEMPO_EM_ATENDIMENTO': 'sum',
    'PAUSA_PRODUTIVA': 'sum',
    'TEMPO_TOTAL_LOGADO': 'sum',
    'TMA': 'sum',
    'ESTOURO DE PAUSA': 'sum',
    'TEMPO_TOTAL_LOGADO': 'sum',
    'HORA_LOGIN' : 'min',

}).reset_index()

df_rel['matricula_p'] = df_rel['AGENTE_NOME'].str.slice(0,7)

df_rel['TA_TOTAL'] =  df_rel['TEMPO_EM_ATENDIMENTO'] + df_rel['PAUSA_PRODUTIVA']
df_rel['TA'] = df_rel['TA_TOTAL'].dt.total_seconds().round()/60

df_rel = df_rel.drop(df_rel[df_rel['TA']<1].index)

df_rel['TEMPO_TOTAL_LOGADO_MIN'] = df_rel['TEMPO_TOTAL_LOGADO'].dt.total_seconds()/60

df_rel = df_rel.drop(df_rel[df_rel['TA']<=1].index)

#TRAVA RESULTADO NO HORARIO ATUAL
df_rel['DIFF'] = hora_atual - df_rel['HORA_LOGIN']

###TRAVA RESULTADO NA DATA DO AQUIVO
#df_rel['DIFF'] = hora - data_arquivo

df_rel['DIFF_MIN'] = df_rel['DIFF'].dt.total_seconds()/60

df_rel['TMA'] = df_rel['TMA'].apply(lambda x: str(x).split(' days ')[-1].split('.')[0])
df_rel['ESTOURO DE PAUSA'] = df_rel['ESTOURO DE PAUSA'].apply(lambda x: str(x).split(' days ')[-1].split('.')[0])


###########################################################################################################
df_final = pd.merge(df_rel, base[['matricula_p', 'CH', 'no_gestor','no_coord', 'no_empregado']], on='matricula_p', how='left')


def pausas(CH):
    if CH <= 380:
        return timedelta(minutes=40)
    else:
        return timedelta(minutes=80)

df_final['PO'] = df_final['CH'].apply(pausas)
df_final['TEMPO INDISPONIVEL'] = df_final['TEMPO_TOTAL_LOGADO'] -  df_final['TA_TOTAL'] - df_final['PO']
df_final['TEMPO INDISPONIVEL'] = df_final['TEMPO INDISPONIVEL'].apply(lambda x: str(x).split(' days ')[-1].split('.')[0])


####META
def metaoriginal(CH):
    if CH<= 380:
        return CH *0.83
    else:
        return CH* 0.81



df_final['Meta_Original'] = df_final['CH'].apply(metaoriginal)

def metafinal(row):

    if row['CH'] <= 380:
        multiplicador = 0.83
    else: 
        multiplicador = 0.81

    diff_min = row['DIFF_MIN'] * multiplicador

    if row['TEMPO_TOTAL_LOGADO_MIN']> row['CH']:
        return row['TEMPO_TOTAL_LOGADO_MIN']*multiplicador
    
    elif diff_min > row['Meta_Original']:
        return row['Meta_Original']
    
    else:
        return diff_min


df_final['Meta'] = df_final.apply(metafinal, axis=1)



df_final['%'] = df_final['TA'] / df_final['Meta'] *100

def cor_pct(val):
    if float(val) > 90:
        return 'background-color: #B4FED0; color: black'
    if float(val) > 80:
        return 'background-color: #FFDE59; color: black'
    if float(val) < 80:
        return 'background-color: #FC4A4A; color: black'

#VISAO COORD


df_coord_ta = df_final.groupby('no_coord')[['TA']].sum()
df_coord_meta = df_final.groupby('no_coord')[['Meta']].sum()

df_coordenadores = pd.merge(df_coord_ta, df_coord_meta, on='no_coord')
df_coordenadores['%'] = df_coordenadores['TA']/df_coordenadores['Meta']*100

df_coordenadores = df_coordenadores.sort_values(by="%", ascending= False)

df_coordenadores.reset_index(inplace=True)

df_coordenadores.index+=1

df_coordenadores = df_coordenadores.map(lambda x: '{:.1f}'.format(x) if isinstance(x, float) else x)

##global

df_global_ta=  df_coord_ta['TA'].sum().round(1)
df_global_meta = df_coord_meta['Meta'].sum().round(1)

df_global = pd.DataFrame({'TA':[df_global_ta],'Meta':[df_global_meta]})

df_global['%'] = (df_global['TA']/df_global['Meta']*100).round(1)



###VISaO SUPERVISOR

df_sup_ta = df_final.groupby('no_gestor')[['TA']].sum()
df_sup_meta = df_final.groupby('no_gestor')[['Meta']].sum()

df_supervisores = pd.merge(df_sup_ta, df_sup_meta, on = 'no_gestor', how= 'left')
df_supervisores = pd.merge(df_supervisores ,df_final[['no_gestor','no_coord']], on= 'no_gestor').drop_duplicates()
df_supervisores['%'] = (df_supervisores['TA']/df_supervisores['Meta']*100)

df_supervisores = df_supervisores.sort_values(by='%', ascending=False)

df_supervisores.reset_index(inplace=True)

df_supervisores.index+=1

df_supervisores = df_supervisores.map(lambda x: '{:.0f}'.format(x) if isinstance(x, float) else x)
df_supervisores = df_supervisores[['no_gestor','no_coord','TA','Meta','%']]

##VISÃO OPERADOR##


df_op_ta = df_final.groupby('no_empregado')[['TA']].sum()
df_op_meta = df_final.groupby('no_empregado')[['Meta']].sum()
df_op_tma = df_final.groupby('no_empregado')[['TMA']].sum()
df_op_pe = df_final.groupby('no_empregado')[['ESTOURO DE PAUSA']].sum()
df_op_ind= df_final.groupby('no_empregado')[['TEMPO INDISPONIVEL']].sum()


df_operadores = pd.merge(df_op_ta, df_op_meta, on = 'no_empregado', how= 'left').drop_duplicates()
df_operadores = pd.merge(df_operadores,df_final[['no_empregado','no_gestor']], on= 'no_empregado').drop_duplicates()

df_operadores['%'] = (df_operadores['TA']/df_operadores['Meta']*100)

df_operadores = df_operadores.sort_values(by='%', ascending=False)
df_operadores.reset_index(drop=True, inplace=True)

df_operadores.index+=1

df_operadores = df_operadores[['no_empregado','no_gestor','TA','Meta','%']]

df_operadores = df_operadores.map(lambda x: '{:.0f}'.format(x) if isinstance(x, float) else x)


###Filtros

supervisores = df_supervisores['no_gestor'].tolist()
coordenadores = df_coordenadores['no_coord'].tolist()

###Cor

df_supervisores_cor = df_supervisores.style.map(cor_pct, subset=pd.IndexSlice[df_supervisores.index , ['%']])
df_operadores_cor = df_operadores.style.map(cor_pct, subset=pd.IndexSlice[df_operadores.index , ['%']])

container = st.container(border= True)


with container:
    
    col1, col2, col3 = st.columns(3)
    visao = col1.selectbox('Selecione visão:', ['Coordenação','Supervisão', 'Operação'])



    if visao == 'Coordenação':

        fig2 = px.pie(df_coordenadores,names= 'no_coord', values = "TA")
        fig3 = px.bar(df_coordenadores, x="no_coord", y="TA")
        fig3.layout.update(height=300, width=400)        
        fig2.layout.update(height=300, width=400)


    if visao == 'Supervisão':
        select_coord = col2.selectbox('Selecione Coordenador', coordenadores)
        fil_coord = df_supervisores[df_supervisores['no_coord'] == select_coord]

        fig1 = go.Figure(data=[
            go.Bar(name='Ta',x=fil_coord['no_gestor'],y=fil_coord['TA']),
            go.Bar(name='Meta',x=fil_coord['no_gestor'],y=fil_coord['Meta'])
        ])
        fig1.layout.update(height=500, width=930)

        fig2 = px.bar(fil_coord, x="no_gestor", y="%")
        fig2.layout.update(height=500, width=890, yaxis=dict(range=[0,130]))

    if visao == 'Operação':
        
        select_sup = col2.selectbox('Selecione Supervisor:',supervisores)
        
        fil_sup = df_operadores[df_operadores['no_gestor']== select_sup]
            
        fig1 = go.Figure(data=[
            go.Bar(name='Ta',x=fil_sup['no_empregado'],y=fil_sup['TA']),
            go.Bar(name='Meta',x=fil_sup['no_empregado'],y=fil_sup['Meta'])
        ])
        fig1.layout.update(height=500, width=930)

        fig3 = px.bar(fil_sup, x="no_empregado", y="%")
        fig3.layout.update(height=500, width=890, yaxis=dict(range=[0,130]))
            

container2 = st.container(border=True)
container2_1 = st.container(border = True)

with container2:
    
    col4, col5, col6, col7, col8 = st.columns(5)
    col9, col10 = st.columns(2)
    
    if visao == 'Coordenação':

        container2_1.write(df_coordenadores)
        col4.metric(label='Ta Global',value=df_global['TA'], delta="1")
        col5.metric(label='Meta Global',value=df_global['Meta'])
        col6.metric(label = 'Final', value = df_global['%'])
        col9.write(fig3)
        col10.write(fig2)

    if visao == 'Supervisão':

        grafico1 = col4.radio("Escolha uma visão",['Alcance','TA X Meta'])
            
        if grafico1 == 'Alcance':
            fig1
            container2_1.write(fil_coord)

        else:
            fig2
            container2_1.write(fil_coord)


    if visao == 'Operação':

        grafico1 = col4.radio("Escolha uma visão",['Alcance','TA X Meta'])
        
        if grafico1 == 'Alcance':
            st.plotly_chart(fig3)
            container2_1.write(fil_sup)

        else:
            st.plotly_chart(fig1)
            container2_1.write(fil_sup)



