import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Configuração da página
st.set_page_config(
    page_title="Análise de Sensibilidade Simplificada",
    page_icon="🛢️",
    layout="wide"
)

# Título e introdução
st.title("Análise de Sensibilidade Simplificada - Projeto de Recuperação Avançada")
st.markdown("""
Este dashboard simplificado permite analisar a sensibilidade econômica do projeto de implementação 
de um sistema de recuperação avançada no Campo de Miranga, utilizando o Método de Monte Carlo.
""")

# Parâmetros base do projeto
parametros_base = {
    'preco_petroleo': 70.0,  # US$/barril
    'investimento_total': 45000000.0,  # US$
    'incremento_recuperacao': 15.0,  # pontos percentuais
    'custo_operacional': 8.0,  # US$/barril
    'taxa_declinio': 5.0,  # %/ano
    'taxa_minima_atratividade': 12.0,  # %
    'anos_projeto': 15,  # anos
    'custo_polimero': 2.2,  # US$/barril
    'custos_fixos_anuais': 1500000.0  # US$
}

# Interface de usuário simplificada
st.sidebar.header("Parâmetros da Simulação")

num_simulacoes = st.sidebar.slider(
    "Número de Simulações",
    min_value=100,
    max_value=1000,
    value=500,
    step=100
)

# Parâmetros principais com ranges simplificados
preco_min = st.sidebar.slider("Preço Mínimo do Petróleo (US$/barril)", 40.0, 60.0, 50.0, 5.0)
preco_max = st.sidebar.slider("Preço Máximo do Petróleo (US$/barril)", 70.0, 100.0, 90.0, 5.0)

investimento_min = st.sidebar.slider("Investimento Mínimo (US$ milhões)", 30.0, 40.0, 36.0, 2.0)
investimento_max = st.sidebar.slider("Investimento Máximo (US$ milhões)", 50.0, 70.0, 63.0, 2.0)

eficiencia_min = st.sidebar.slider("Incremento Mínimo no Fator de Recuperação (pp)", 9.0, 12.0, 10.0, 1.0)
eficiencia_max = st.sidebar.slider("Incremento Máximo no Fator de Recuperação (pp)", 15.0, 20.0, 18.0, 1.0)

# Função simplificada para calcular VPL e TIR
def calcular_indicadores(parametros):
    # Extrair parâmetros
    preco = parametros['preco']
    investimento = parametros['investimento']
    eficiencia = parametros['eficiencia']
    custo = parametros['custo']
    declinio = parametros['declinio']
    
    # Parâmetros fixos
    anos_projeto = parametros_base['anos_projeto']
    taxa_minima_atratividade = parametros_base['taxa_minima_atratividade']
    custo_polimero = parametros_base['custo_polimero']
    custos_fixos_anuais = parametros_base['custos_fixos_anuais']
    
    # Fator de ajuste para eficiência
    fator_eficiencia = eficiencia / parametros_base['incremento_recuperacao']
    
    # Produção base e ajustada (simplificada)
    producao_base = [0, 500, 1200, 1800, 2000]  # bpd nos primeiros 5 anos
    producao_ajustada = [p * fator_eficiencia for p in producao_base]
    
    # Calcular produção com declínio após o pico
    for ano in range(5, anos_projeto + 1):
        producao_anterior = producao_ajustada[ano - 1]
        producao_atual = producao_anterior * (1 - declinio / 100)
        producao_ajustada.append(producao_atual)
    
    # Converter para produção anual
    producao_anual = [p * 365 for p in producao_ajustada]
    
    # Receitas
    receita_bruta = [p * preco * 0.9 for p in producao_anual]  # Desconto de 10% pela qualidade
    royalties = [r * 0.1 for r in receita_bruta]  # 10% de royalties
    receita_liquida = [r - roy for r, roy in zip(receita_bruta, royalties)]
    
    # Investimentos (simplificado)
    investimentos = [0] * (anos_projeto + 1)
    investimentos[0] = investimento * 0.5  # 50% no ano 0
    investimentos[1] = investimento * 0.3  # 30% no ano 1
    investimentos[2] = investimento * 0.2  # 20% no ano 2
    
    # Custos operacionais
    custos_fixos = [custos_fixos_anuais] * (anos_projeto + 1)
    custos_fixos[0] = 0  # Não há custos fixos no ano 0
    
    custos_variaveis = [p * custo for p in producao_anual]
    custos_polimero = [p * custo_polimero for p in producao_anual]
    custos_totais = [f + v + p for f, v, p in zip(custos_fixos, custos_variaveis, custos_polimero)]
    
    # Depreciação (simplificada)
    depreciacao = [0] * (anos_projeto + 1)
    valor_depreciavel = investimento * 0.8  # 80% do investimento é depreciável
    for ano in range(1, min(11, anos_projeto + 1)):
        depreciacao[ano] = valor_depreciavel / 10  # Depreciação em 10 anos
    
    # Lucro e impostos
    lucro_antes_impostos = [r - c - d for r, c, d in zip(receita_liquida, custos_totais, depreciacao)]
    impostos = [max(0, l * 0.34) for l in lucro_antes_impostos]  # 34% de impostos
    lucro_liquido = [l - i for l, i in zip(lucro_antes_impostos, impostos)]
    
    # Fluxo de caixa
    fluxo_caixa = [ll + d - inv for ll, d, inv in zip(lucro_liquido, depreciacao, investimentos)]
    
    # Fluxo de caixa descontado
    fator_desconto = [1 / (1 + taxa_minima_atratividade / 100) ** ano for ano in range(anos_projeto + 1)]
    fluxo_caixa_descontado = [fc * fd for fc, fd in zip(fluxo_caixa, fator_desconto)]
    
    # VPL
    vpl = sum(fluxo_caixa_descontado)
    
    # TIR (simplificada)
    if vpl <= 0:
        tir = 0
    else:
        # Estimativa da TIR baseada na relação entre VPL e investimento
        tir = (vpl / investimento) * 15 + 12  # Fórmula aproximada
        tir = min(tir, 50)  # Limitar a TIR máxima
    
    # Payback descontado (simplificado)
    fluxo_acumulado = np.cumsum(fluxo_caixa_descontado)
    if all(f < 0 for f in fluxo_acumulado):
        payback = anos_projeto  # Não recupera o investimento no período
    else:
        for i in range(1, len(fluxo_acumulado)):
            if fluxo_acumulado[i-1] < 0 and fluxo_acumulado[i] >= 0:
                # Interpolação linear
                payback = i - 1 + abs(fluxo_acumulado[i-1]) / abs(fluxo_acumulado[i] - fluxo_acumulado[i-1])
                break
        else:
            payback = 0  # Recupera imediatamente (caso improvável)
    
    return {
        'VPL': vpl,
        'TIR': tir,
        'Payback': payback,
        'Fluxo_Caixa': fluxo_caixa,
        'Fluxo_Caixa_Descontado': fluxo_caixa_descontado
    }

# Função simplificada para realizar a simulação de Monte Carlo
def simular_monte_carlo(num_simulacoes):
    np.random.seed(42)  # Seed fixo para reprodutibilidade
    
    resultados = []
    
    for i in range(num_simulacoes):
        # Gerar valores aleatórios para os parâmetros
        preco = np.random.uniform(preco_min, preco_max)
        investimento = np.random.uniform(investimento_min, investimento_max) * 1000000  # Converter para US$
        eficiencia = np.random.uniform(eficiencia_min, eficiencia_max)
        custo = np.random.uniform(6.8, 10.4)  # Valores fixos para simplificar
        declinio = np.random.uniform(2.0, 10.0)  # Valores fixos para simplificar
        
        parametros_simulacao = {
            'preco': preco,
            'investimento': investimento,
            'eficiencia': eficiencia,
            'custo': custo,
            'declinio': declinio
        }
        
        indicadores = calcular_indicadores(parametros_simulacao)
        
        resultados.append({
            'Simulação': i + 1,
            'Preço do Petróleo (US$/barril)': preco,
            'Investimento Total (US$)': investimento,
            'Incremento Fator Recuperação (pp)': eficiencia,
            'Custo Operacional Variável (US$/barril)': custo,
            'Taxa de Declínio (%/ano)': declinio,
            'VPL (US$)': indicadores['VPL'],
            'TIR (%)': indicadores['TIR'],
            'Payback (anos)': indicadores['Payback']
        })
    
    return pd.DataFrame(resultados)

# Executar simulação quando o botão for pressionado
if st.sidebar.button("Executar Simulação"):
    with st.spinner("Executando simulação de Monte Carlo..."):
        resultados_simulacao = simular_monte_carlo(num_simulacoes)
        st.session_state.resultados = resultados_simulacao
        st.success(f"Simulação concluída com {num_simulacoes} iterações!")

# Mostrar resultados da simulação se disponíveis
if 'resultados' in st.session_state:
    resultados = st.session_state.resultados
    
    # Layout em duas colunas
    col1, col2 = st.columns(2)
    
    with col1:
        # Estatísticas descritivas
        st.header("Resultados da Simulação")
        
        vpl_medio = resultados['VPL (US$)'].mean()
        vpl_mediano = resultados['VPL (US$)'].median()
        prob_vpl_negativo = (resultados['VPL (US$)'] < 0).mean() * 100
        
        tir_media = resultados['TIR (%)'].mean()
        tir_mediana = resultados['TIR (%)'].median()
        prob_tir_abaixo_tma = (resultados['TIR (%)'] < parametros_base['taxa_minima_atratividade']).mean() * 100
        
        payback_medio = resultados['Payback (anos)'].mean()
        
        # Métricas em formato de cartões
        st.metric("VPL Médio", f"US$ {vpl_medio:,.2f}")
        st.metric("TIR Média", f"{tir_media:.2f}%")
        st.metric("Payback Médio", f"{payback_medio:.2f} anos")
        st.metric("Probabilidade de VPL Negativo", f"{prob_vpl_negativo:.2f}%")
        st.metric("Probabilidade de TIR < TMA", f"{prob_tir_abaixo_tma:.2f}%")
        
        # Histograma do VPL
        fig_vpl = px.histogram(
            resultados, 
            x='VPL (US$)',
            nbins=20,
            title="Distribuição do VPL",
            color_discrete_sequence=['#1f77b4']
        )
        fig_vpl.add_vline(x=0, line_dash="dash", line_color="red")
        fig_vpl.add_vline(x=vpl_medio, line_dash="dash", line_color="green")
        st.plotly_chart(fig_vpl, use_container_width=True)
    
    with col2:
        # Histograma da TIR
        fig_tir = px.histogram(
            resultados, 
            x='TIR (%)',
            nbins=20,
            title="Distribuição da TIR",
            color_discrete_sequence=['#ff7f0e']
        )
        fig_tir.add_vline(x=parametros_base['taxa_minima_atratividade'], line_dash="dash", line_color="red")
        fig_tir.add_vline(x=tir_media, line_dash="dash", line_color="green")
        st.plotly_chart(fig_tir, use_container_width=True)
        
        # Análise de sensibilidade simplificada
        st.subheader("Análise de Sensibilidade")
        
        # Gráficos de dispersão para análise de sensibilidade
        fig_scatter = px.scatter(
            resultados,
            x='Preço do Petróleo (US$/barril)',
            y='VPL (US$)',
            color='TIR (%)',
            title="VPL vs. Preço do Petróleo",
            trendline="ols"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Dados brutos em formato de tabela
    st.subheader("Dados da Simulação")
    st.dataframe(resultados.head(10))  # Mostrar apenas as primeiras 10 linhas
    
    # Botão para download dos resultados
    csv = resultados.to_csv(index=False)
    st.download_button(
        label="Download dos Resultados (CSV)",
        data=csv,
        file_name="resultados_monte_carlo_simplificado.csv",
        mime="text/csv"
    )


# Rodapé
st.markdown("---")
st.markdown("""
**Projeto de Instalações Petrolíferas Onshore** | Implementação de Sistema de Recuperação Avançada no Campo de Miranga
""")
