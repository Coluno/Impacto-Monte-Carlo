import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Função para simulação Monte Carlo
def simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior):
    retornos_diarios_simulados = np.random.normal(media_retornos_diarios, desvio_padrao_retornos_diarios, (dias_simulados, num_simulacoes))
    preco_inicial = float(data['Close'].iloc[-1])
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial

    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_diarios_simulados[dia - 1, :])
        precos_simulados[dia, :] = np.maximum(np.minimum(precos_simulados[dia, :], limite_superior), limite_inferior)

    return precos_simulados[1:, :]

# Aplicativo Streamlit para Monte Carlo
def main():
    st.title("Simulação Monte Carlo de Preços")

    # Seleção do tipo de ativo
    tipo_ativo = st.selectbox("Selecione o tipo de ativo", ["Açúcar", "Dólar"])

    # Carregar dados do Yahoo Finance
    ativo = "SB=F" if tipo_ativo == "Açúcar" else "USDBRL=X"
    data = yf.download(ativo, start="2013-01-01", end="2099-01-01")
    data['Daily Return'] = data['Close'].pct_change()
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()

    # Configuração da simulação
    dias_simulados = st.slider("Dias a serem simulados", min_value=1, max_value=252, value=30)
    num_simulacoes = st.number_input("Número de simulações", min_value=100, max_value=1000000, value=10000, step=1000)
    limite_inferior = st.number_input("Limite inferior de preço (R$)", value=data['Close'].iloc[-1] - 10)
    limite_superior = st.number_input("Limite superior de preço (R$)", value=data['Close'].iloc[-1] + 10)
    valor_simulado = st.number_input("Valor para análise (R$)", value=float(data['Close'].iloc[-1]))

    if st.button("Iniciar Simulação"):
        simulacoes = simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior)

        # Estatísticas
        media_simulada = np.mean(simulacoes[-1])
        percentil_20 = np.percentile(simulacoes[-1], 20)
        percentil_80 = np.percentile(simulacoes[-1], 80)
        prob_acima_valor = np.mean(simulacoes[-1] > valor_simulado) * 100
        prob_abaixo_valor = np.mean(simulacoes[-1] < valor_simulado) * 100

        # Gráfico de Simulação
        fig = go.Figure()
        for i in range(min(100, num_simulacoes)):  # Plotar até 100 simulações
            fig.add_trace(go.Scatter(x=np.arange(1, dias_simulados + 1), y=simulacoes[:, i], mode='lines', line=dict(width=0.8), name=f'Simulação {i+1}'))
        fig.update_layout(title="Simulações Monte Carlo", xaxis_title="Dias", yaxis_title="Preço Simulado", showlegend=False)
        st.plotly_chart(fig)

        # Gráfico de Histograma
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=simulacoes[-1], nbinsx=100, marker_color='blue', opacity=0.75))
        fig_hist.update_layout(title="Distribuição de Preços Simulados", xaxis_title="Preço Simulado", yaxis_title="Frequência")
        st.plotly_chart(fig_hist)

        # Exibir resultados
        st.write(f"Média dos valores simulados: **{media_simulada:.2f}**")
        st.write(f"Percentil 20: **{percentil_20:.2f}**")
        st.write(f"Percentil 80: **{percentil_80:.2f}**")
        st.write(f"Probabilidade de o preço estar acima do valor inserido: **{prob_acima_valor:.2f}%**")
        st.write(f"Probabilidade de o preço estar abaixo do valor inserido: **{prob_abaixo_valor:.2f}%**")

if __name__ == "__main__":
    main()
