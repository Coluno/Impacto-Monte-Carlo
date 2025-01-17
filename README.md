# Gestão de Risco e Derivativos na Indústria Açucareira - Simulação de Monte Carlo

## Descrição
Este projeto implementa uma Simulação de Monte Carlo para prever cenários futuros de preços de ativos financeiros, como o dólar ou o açúcar. A ferramenta foi desenvolvida em Python com o framework Streamlit, permitindo uma interface interativa e intuitiva para análise e previsão.

A Simulação de Monte Carlo é um método estatístico que utiliza retornos históricos para modelar o comportamento futuro dos preços, considerando incertezas e variabilidades. Essa abordagem é amplamente utilizada para suportar decisões estratégicas e gerenciamento de riscos em mercados financeiros.

## Funcionalidades
- Simulação Monte Carlo:
Realiza até 1.000.000 de simulações para modelar possíveis preços futuros.
Permite definir limites superior e inferior para os preços simulados.

- Análise de Probabilidades:
Probabilidade de o preço simulado ultrapassar ou ficar abaixo de um valor definido.
Cálculo de percentis (20% e 80%) para os preços simulados.

-Visualização Gráfica:
Gráficos interativos exibindo as trajetórias simuladas dos preços.
Histograma das distribuições de preços simulados.
]
- Customização da Simulação:
Selecione o ativo a ser analisado (dólar ou açúcar).
Escolha o número de dias úteis para projeção.
## Tecnologias Utilizadas
- Python: Linguagem principal do projeto.
- Streamlit: Framework para criação da interface interativa.
- NumPy: Geração de números aleatórios e cálculos estatísticos.
- Pandas: Manipulação e análise de dados financeiros.
- yFinance: Obtenção de dados históricos de preços dos ativos.
- Plotly: Visualização interativa de gráficos e dados.

## Requisitos
- Python: 3.12 ou superior.
 
## Bibliotecas:
- streamlit
- numpy
- pandas
- yfinance
- plotly
  
## Instalação
Clone o Repositório

- Instale as Dependências
> pip install -r requirements.txt

## Como Utilizar
- Selecione o Ativo:
Escolha o ativo a ser analisado, como o dólar (USDBRL=X) ou o açúcar (SB=F).

- Defina a Data de Simulação:
Informe o prazo (em dias úteis) até o qual deseja projetar os preços.

- Insira o Valor Simulado:
Informe o preço-alvo para cálculo de probabilidades.

## Colaboradores
Gabriel Canuto de Alencar

## Licença
Este projeto está licenciado sob a MIT License.
