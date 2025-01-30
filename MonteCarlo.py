import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import time
import seaborn as sns
import math
import scipy.stats as stats
import io  
import plotly.express as px
import plotly.graph_objs as go
import scipy.stats as si
import smtplib
import statsmodels.api as sm
import plotly.graph_objs as go
import plotly.subplots as sp
import requests

from bcb import Expectativas
from arch import arch_model
from bs4 import BeautifulSoup
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from pandas.tseries.offsets import BDay
from datetime import datetime, timedelta, date
from matplotlib.ticker import FuncFormatter
from scipy.stats import norm
from plotly.subplots import make_subplots
from email.mime.text import MIMEText

from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
def calcular_dias_uteis(data_inicial, data_final):
    datas_uteis = pd.date_range(start=data_inicial, end=data_final, freq=BDay())
    return len(datas_uteis)

# Função para simulação Monte Carlo
def simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior):
    retornos_diarios_simulados = np.random.normal(media_retornos_diarios, desvio_padrao_retornos_diarios, (dias_simulados, num_simulacoes))

    preco_inicial = float(data['Close'].iloc[-1])
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial

    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_diarios_simulados[dia - 1, :])
        precos_simulados[dia, :] = np.maximum(np.minimum(precos_simulados[dia, :], limite_superior), limite_inferior)

    return precos_simulados[1:, :]

# Função para a interface gráfica da aba do Monte Carlo
def monte_carlo():
    st.title("Simulação Monte Carlo de Preços")

    # Selecionar o tipo de ativo
    tipo_ativo = st.selectbox("Selecione o tipo de ativo", ["Açúcar", "Dólar"])

    # Carregar dados do Yahoo Finance correspondente ao tipo de ativo selecionado
    if tipo_ativo == "Açúcar":
        ativo = "SB=F"
    elif tipo_ativo == "Dólar":
        ativo = "USDBRL=X"
        
    start_date = date(2013, 1, 1)
    today = date.today()
    end_date = today.strftime('%Y-%m-%d')
    data = yf.download(ativo, start=start_date, end=end_date, multi_level_index=False, auto_adjust=True)
    
    # Calcular média e desvio padrão dos retornos diários
    data['Daily Return'] = data['Close'].pct_change()
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()

    # Selecionar a data para simulação
    data_simulacao = st.date_input("Selecione a data para simulação", value=pd.to_datetime('2025-01-01'))

    # Calcular o número de dias úteis até a data de simulação
    hoje = pd.to_datetime('today').date()
    dias_simulados = calcular_dias_uteis(hoje, data_simulacao)

    # Input para o valor desejado para a simulação
    if "valor_simulado" not in st.session_state:
        st.session_state["valor_simulado"] = float(data['Close'].iloc[-1])
    valor_simulado = st.number_input("Qual valor deseja simular?",value=st.session_state["valor_simulado"],step=0.01)
    limite_inferior = data['Close'].iloc[-1] - 10
    limite_superior = data['Close'].iloc[-1] + 10

    # Simulação Monte Carlo
    num_simulacoes = 500000
    simulacoes = simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior)

    if st.button("Simular"):
        # Calculando os outputs
        media_simulada = np.mean(simulacoes[-1])
        percentil_20 = np.percentile(simulacoes[-1], 20)
        percentil_80 = np.percentile(simulacoes[-1], 80)
        prob_acima_valor = np.mean(simulacoes[-1] > valor_simulado) * 100
        prob_abaixo_valor = np.mean(simulacoes[-1] < valor_simulado) * 100

        # Criando novo gráfico com médias mensais
        datas_futuras = pd.date_range(start=hoje, periods=dias_simulados, freq=BDay())
        df_simulacoes = pd.DataFrame(simulacoes, index=datas_futuras)
        df_mensal = df_simulacoes.resample('M').agg(['mean', lambda x: np.percentile(x, 20), lambda x: np.percentile(x, 80)])
        df_mensal.columns = ['Média', 'Percentil 20', 'Percentil 80']

        fig_mensal = go.Figure()
        fig_mensal.add_trace(go.Scatter(x=df_mensal.index, y=df_mensal['Média'], mode='lines', name='Média'))
        fig_mensal.add_trace(go.Scatter(x=df_mensal.index, y=df_mensal['Percentil 20'], mode='lines', name='Percentil 20'))
        fig_mensal.add_trace(go.Scatter(x=df_mensal.index, y=df_mensal['Percentil 80'], mode='lines', name='Percentil 80'))

        st.plotly_chart(fig_mensal)

        # Exibir os outputs
        st.write("Média dos valores simulados: **{:.4f}**".format(media_simulada))
        st.write("Percentil 20: **{:.4f}**".format(percentil_20))
        st.write("Percentil 80: **{:.4f}**".format(percentil_80))
        st.write("Probabilidade do ativo estar acima do valor inserido: **{:.2f}%**".format(prob_acima_valor))
        st.write("Probabilidade do ativo estar abaixo do valor inserido: **{:.2f}%**".format(prob_abaixo_valor))

        st.write("Desvio padrão dos valores simulados: **{:.4f}**".format(np.std(simulacoes[-1])))
        st.write("Mediana dos valores simulados: **{:.4f}**".format(np.median(simulacoes[-1])))

if __name__ == "__main__":
    monte_carlo()
