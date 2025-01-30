import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from datetime import date
from pandas.tseries.offsets import BDay

# Função para calcular o número de dias úteis entre duas datas
def calcular_dias_uteis(data_inicial, data_final):
    datas_uteis = pd.date_range(start=data_inicial, end=data_final, freq=BDay())
    return len(datas_uteis)

# Função para simulação Monte Carlo
def simulacao_monte_carlo(media_retornos, desvio_retornos, dias_simulados, preco_inicial, num_simulacoes):
    retornos_simulados = np.random.normal(media_retornos, desvio_retornos, (dias_simulados, num_simulacoes))
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial
    
    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_simulados[dia - 1, :])
    
    return precos_simulados[1:, :]

# Interface Streamlit
def monte_carlo():
    st.title("Simulação Monte Carlo de Preços")
    
    tipo_ativo = st.selectbox("Selecione o ativo", ["Açúcar", "Dólar"])
    ativo = "SB=F" if tipo_ativo == "Açúcar" else "USDBRL=X"
    
    start_date = date(2013, 1, 1)
    today = date.today()
    data = yf.download(ativo, start=start_date, end=today, auto_adjust=True, multi_level_index=False)
    
    data['Retornos'] = data['Close'].pct_change()
    media_retornos = data['Retornos'].mean()
    desvio_retornos = data['Retornos'].std()
    preco_atual = data['Close'].iloc[-1]
    
    data_futura = st.date_input("Selecione a data para simulação", value=pd.to_datetime("2025-08-01"))
    dias_simulados = calcular_dias_uteis(today, data_futura)
    
    num_simulacoes = 500000
    simulacoes = simulacao_monte_carlo(media_retornos, desvio_retornos, dias_simulados, preco_atual, num_simulacoes)
    
    datas_futuras = pd.date_range(start=today, periods=dias_simulados, freq=BDay())
    df_simulacoes = pd.DataFrame(simulacoes, index=datas_futuras)
    
    df_mensal = df_simulacoes.resample('ME').mean()
    percentil_20 = df_simulacoes.resample('ME').quantile(0.2)
    percentil_80 = df_simulacoes.resample('ME').quantile(0.8)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_mensal.index, y=df_mensal.mean(axis=1), mode='lines', name='Média Simulada', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=percentil_20.index, y=percentil_20.mean(axis=1), mode='lines', name='Percentil 20', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=percentil_80.index, y=percentil_80.mean(axis=1), mode='lines', name='Percentil 80', line=dict(color='green', dash='dot')))
    
    fig.update_layout(
        title="Projeção de Preços ao Longo do Tempo",
        xaxis_title="Meses",
        yaxis_title="Preço Simulado",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig)

if __name__ == "__main__":
    monte_carlo()
