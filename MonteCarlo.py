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

# Função para calcular dias úteis
def calcular_dias_uteis(data_inicial, data_final):
    dias = pd.date_range(start=data_inicial, end=data_final, freq='B')  # Considera apenas dias úteis
    return len(dias)

# Aplicativo Streamlit para Monte Carlo
def main():
    st.title("Simulação Monte Carlo de Preços")

    # Entrada do usuário para o ativo
    ativo = st.text_input("Insira o código do ativo (exemplo: 'SB=F' para Açúcar, 'USDBRL=X' para Dólar):", value="SB=F")

    # Carregar dados do Yahoo Finance
    data = yf.download(ativo, start="2013-01-01", end=pd.to_datetime('today').strftime('%Y-%m-%d'))
    if data.empty:
        st.error("Não foi possível carregar os dados. Verifique o código do ativo.")
        return

    data['Daily Return'] = data['Close'].pct_change()
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()

    # Seleção da data final da simulação
    data_simulacao = st.date_input("Escolha a data final da simulação", value=pd.to_datetime('2025-01-01'))
    dias_simulados = calcular_dias_uteis(pd.to_datetime('today').date(), data_simulacao)

    # Input do valor desejado
    valor_simulado = st.number_input("Qual valor deseja simular (R$)?", value=float(data['Close'].iloc[-1]))

    # Configuração de limites
    limite_inferior = st.number_input("Limite inferior de preço (R$)", value=float(data['Close'].iloc[-1]) - 10)
    limite_superior = st.number_input("Limite superior de preço (R$)", value=float(data['Close'].iloc[-1]) + 10)

    # Número de simulações
    num_simulacoes = st.number_input("Número de simulações", min_value=100, max_value=1000000, value=10000, step=1000)

    # Botão para iniciar a simulação
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
