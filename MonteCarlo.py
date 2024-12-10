import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de estilo do seaborn
sns.set_style("whitegrid")

# Valores padrão
valores_padrao = {
    "Açúcar": {
        "arquivo_csv": 'Dados Históricos - Açúcar NY nº11 Futuros (6).csv',
        "valor_minimo_padrao": 20.0,
        "limite_inferior": 15,
        "limite_superior": 35
    },
    "Dólar": {
        "arquivo_csv": 'USD_BRL Dados Históricos (2).csv',
        "valor_minimo_padrao": 5.0,
        "limite_inferior": 4,
        "limite_superior": 6
    },
    "SBV24": {
        "arquivo_csv": 'sbv24.csv',
        "valor_minimo_padrao": 20.0,
        "limite_inferior": 15,
        "limite_superior": 35
    }
}

# Função para carregar e processar os dados do CSV
def carregar_dados(tipo_ativo):
    config = valores_padrao[tipo_ativo]
    data = pd.read_csv(config["arquivo_csv"])
    data = data.rename(columns={'Último': 'Close', 'Data': 'Date'})
    data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
    data = data.sort_values(by='Date', ascending=True)
    data['Close'] = data['Close'].str.replace(',', '.').astype(float)
    data.set_index('Date', inplace=True)
    data['Daily Return'] = data['Close'].pct_change()
    
    return data, config["valor_minimo_padrao"], config["limite_inferior"], config["limite_superior"]

# Função para simulação Monte Carlo
def simulacao_monte_carlo(media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior):
    retornos_diarios_simulados = np.random.normal(media_retornos_diarios, desvio_padrao_retornos_diarios, (dias_simulados, num_simulacoes))

    preco_inicial = data['Close'].iloc[-1]
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial

    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_diarios_simulados[dia - 1, :])
        precos_simulados[dia, :] = np.maximum(np.minimum(precos_simulados[dia, :], limite_superior), limite_inferior)

    return precos_simulados[1:, :]

# Configuração do título do aplicativo Streamlit e remoção da barra lateral
st.set_page_config(page_title="Simulação Monte Carlo de Preços", page_icon="📈", layout="wide")

# Exibir a imagem
st.markdown('<img src="https://ibea.com.br/wp-content/uploads/2020/10/Capturar1.png" alt="logo" style="width:200px;">', unsafe_allow_html=True)

# Adicionar espaço antes do título
st.write("")

# Título do sidebar
st.sidebar.title('Simulações de Monte Carlo')

# Menu suspenso para selecionar o tipo de ativo
tipo_ativo = st.sidebar.selectbox("Selecione o tipo de ativo", ["Açúcar", "Dólar", "SBV24"])

# Input dos valores desejados
tempo_desejado = st.sidebar.slider("Para quantos dias você quer avaliar o preço?", min_value=1, max_value=180, value=30)
valor_minimo = st.sidebar.number_input("Digite o valor de teste desejado:", value=valores_padrao[tipo_ativo]["valor_minimo_padrao"])

# Botão para simular
if st.sidebar.button("Simular"):
    # Carregar dados do CSV correspondente ao tipo de ativo selecionado
    data, valor_minimo_padrao, limite_inferior, limite_superior = carregar_dados(tipo_ativo)

    # Calcular média e desvio padrão dos retornos diários
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()

    # Simulação Monte Carlo para próximos 6 meses
    dias_simulados = tempo_desejado
    num_simulacoes = 1000000

    simulacoes = simulacao_monte_carlo(media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior)

    # Número de dias desejados para a previsão
    dias_previsao = tempo_desejado

    # Pegar os últimos preços simulados para os próximos dias
    precos_finais_simulados = simulacoes[-dias_previsao:]

    # Calcular probabilidades com base nos preços finais simulados
    probabilidade_abaixo = (precos_finais_simulados < valor_minimo).mean() * 100
    probabilidade_acima = (precos_finais_simulados >= valor_minimo).mean() * 100
    media_simulada = precos_finais_simulados.mean()

    # Exibição dos resultados
    st.write("Probabilidade de estar abaixo de {} pontos nos próximos {} dias:".format(valor_minimo, dias_previsao), "<span style='color:green'>{:.2f}%</span>".format(probabilidade_abaixo), unsafe_allow_html=True)
    st.write("Probabilidade de estar acima de {} pontos nos próximos {} dias:".format(valor_minimo, dias_previsao), "<span style='color:green'>{:.2f}%</span>".format(probabilidade_acima), unsafe_allow_html=True)
    st.write("Valor médio dos preços simulados nos próximos {} dias:".format(dias_previsao), "<span style='color:green'>{:.2f}</span>".format(media_simulada.mean()), unsafe_allow_html=True)

    # Visualização das simulações e estatísticas
    st.subheader("Visualização das Simulações Monte Carlo para Próximos {} Dias".format(dias_previsao))
    fig, ax = plt.subplots(figsize=(8, 4))  # Criar a figura explicitamente

    # Plotar as simulações
    for i in range(50):  # Mantido 50 simulações
        ax.plot(simulacoes[:, i], linewidth=0.5, alpha=0.3)  # Reduzido a largura da linha e a opacidade para melhorar a visualização

    plt.xlabel("Dias")
    plt.ylabel("Preço de Fechamento")
    plt.ylim(limite_inferior, limite_superior)  # Limitando o eixo y conforme o ativo selecionado
    plt.grid(axis='y')  # Adicionando linhas de grade no eixo horizontal
    plt.grid(False, axis='x')  # Removendo linhas de grade no eixo vertical

    # Exibindo o gráfico no Streamlit
    st.pyplot(fig)
