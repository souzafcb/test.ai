import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# Configuração da Página
st.set_page_config(page_title="Comparador de Metodologias Analíticas", layout="wide")

# --- Funções Utilitárias ---

def detect_delimiter(file):
    """Tenta detectar o delimitador de um arquivo CSV."""
    try:
        sample = file.read(1024).decode('utf-8')
        file.seek(0)
        if ';' in sample:
            return ';'
        return ','
    except:
        file.seek(0)
        return ','

def calculate_stats(df, m1_col, m2_col):
    """Calcula estatísticas descritivas e de comparação."""
    stats_dict = {}
    
    for col, name in [(m1_col, 'M1'), (m2_col, 'M2')]:
        data = df[col]
        stats_dict[name] = {
            'N': len(data),
            'Média': data.mean(),
            'Mediana': data.median(),
            'DP': data.std(),
            'Mín': data.min(),
            'Máx': data.max(),
            'CV%': (data.std() / data.mean()) * 100 if data.mean() != 0 else 0
        }
    
    # Diferenças
    diff = df[m1_col] - df[m2_col]
    diff_pct = (diff / df[m2_col]) * 100
    
    stats_dict['Comparação'] = {
        'Viés Médio (Bias)': diff.mean(),
        'DP das Diferenças': diff.std(),
        'Erro % Médio': diff_pct.mean(),
        'Erro % Absoluto Médio (MAPE)': np.abs(diff_pct).mean(),
        'Mediana das Diferenças': diff.median()
    }
    
    return stats_dict, diff

def run_regression(x, y):
    """Executa regressão linear simples."""
    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit()
    intercept = model.params[0]
    slope = model.params[1]
    r2 = model.rsquared
    return model, intercept, slope, r2

# --- Interface Streamlit ---

st.title("🧪 Comparação de Metodologias Analíticas")
st.markdown("""
Esta aplicação permite avaliar a concordância e correlação entre duas metodologias quantitativas 
aplicadas ao mesmo analito em amostras pareadas.
""")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações da Análise")
m1_label = st.sidebar.text_input("Nome da Metodologia 1", "Método A")
m2_label = st.sidebar.text_input("Nome da Metodologia 2", "Método B")
unit = st.sidebar.text_input("Unidade de Medida", "mg/dL")

st.sidebar.divider()
show_bland = st.sidebar.checkbox("Habilitar Bland-Altman", True)
show_bias_pct = st.sidebar.checkbox("Análise de Viés Percentual", True)
remove_outliers = st.sidebar.checkbox("Remover Outliers (±3 DP)", False)

# Upload de Arquivo
uploaded_file = st.file_uploader("Carregue sua base de dados (CSV ou XLSX)", type=["csv", "xlsx"])

if uploaded_file:
    # Leitura dos dados
    if uploaded_file.name.endswith('.csv'):
        sep = detect_delimiter(uploaded_file)
        df_raw = pd.read_csv(uploaded_file, sep=sep)
    else:
        df_raw = pd.read_excel(uploaded_file)
    
    st.subheader("📋 Pré-visualização dos Dados")
    st.dataframe(df_raw.head())
    
    cols = df_raw.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        id_col = st.selectbox("Coluna Identificadora", cols)
    with col2:
        m1_col = st.selectbox(f"Resultados: {m1_label}", cols, index=min(1, len(cols)-1))
    with col3:
        m2_col = st.selectbox(f"Resultados: {m2_label}", cols, index=min(2, len(cols)-1))
    
    group_col = st.selectbox("Coluna de Agrupamento (Opcional)", ["Nenhum"] + cols)

    # Tratamento de Dados
    df = df_raw.copy()
    
    # Converter para numérico
    df[m1_col] = pd.to_numeric(df[m1_col], errors='coerce')
    df[m2_col] = pd.to_numeric(df[m2_col], errors='coerce')
    
    # Limpeza
    initial_count = len(df)
    df = df.dropna(subset=[m1_col, m2_col])
    final_count = len(df)
    
    if initial_count != final_count:
        st.warning(f"Foram removidas {initial_count - final_count} linhas com valores ausentes ou inválidos.")

    if st.button("🚀 Executar Análise Completa"):
        
        # Filtro de Outliers
        if remove_outliers:
            diff = df[m1_col] - df[m2_col]
            mean_diff = diff.mean()
            std_diff = diff.std()
            df = df[(diff >= mean_diff - 3*std_diff) & (diff <= mean_diff + 3*std_diff)]
            st.info(f"Dados após remoção de outliers: {len(df)} amostras.")

        # Cálculos
        stats_data, differences = calculate_stats(df, m1_col, m2_col)
        
        # Tabs de Resultados
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Estatísticas", "📈 Gráficos", "🔍 Análise por Faixas", "📝 Conclusão"])
        
        with tab1:
            st.subheader("Estatística Descritiva")
            res_df = pd.DataFrame({
                "Métrica": ["N", "Média", "Mediana", "DP", "CV%", "Mín", "Máx"],
                m1_label: [stats_data['M1'][k] for k in ["N", "Média", "Mediana", "DP", "CV%", "Mín", "Máx"]],
                m2_label: [stats_data['M2'][k] for k in ["N", "Média", "Mediana", "DP", "CV%", "Mín", "Máx"]]
            })
            st.table(res_df.set_index("Métrica"))
            
            st.subheader("Comparação Pareada")
            comp = stats_data['Comparação']
            c_col1, c_col2 = st.columns(2)
            c_col1.metric("Viés Médio (Bias)", f"{comp['Viés Médio (Bias)']: .4f} {unit}")
            c_col2.metric("MAPE (Erro % Absoluto)", f"{comp['Erro % Absoluto Médio (MAPE)']: .2f}%")
            
            # Testes de Normalidade e Hipótese
            st.divider()
            st.subheader("Testes Estatísticos")
            
            shapiro_stat, shapiro_p = stats.shapiro(differences)
            is_normal = shapiro_p > 0.05
            
            st.write(f"**Teste de Normalidade (Shapiro-Wilk):** p = {shapiro_p:.4f}")
            if is_normal:
                st.success("As diferenças seguem uma distribuição normal. Recomendado: Teste t Pareado.")
                t_stat, t_p = stats.ttest_rel(df[m1_col], df[m2_col])
                st.write(f"**Teste t Pareado:** t = {t_stat:.4f}, p = {t_p:.4f}")
            else:
                st.warning("As diferenças NÃO seguem uma distribuição normal. Recomendado: Teste de Wilcoxon.")
                w_stat, w_p = stats.wilcoxon(df[m1_col], df[m2_col])
                st.write(f"**Teste de Wilcoxon:** W = {w_stat:.4f}, p = {w_p:.4f}")

            # Correlação
            pearson_r, p_p = stats.pearsonr(df[m1_col], df[m2_col])
            spearman_r, p_s = stats.spearmanr(df[m1_col], df[m2_col])
            
            st.write(f"**Correlação de Pearson (r):** {pearson_r:.4f} (p={p_p:.4f})")
            st.write(f"**Correlação de Spearman (ρ):** {spearman_r:.4f} (p={p_s:.4f})")

        with tab2:
            # Gráfico de Dispersão
            st.subheader("Gráfico de Dispersão e Regressão")
            model, inter, slope, r2 = run_regression(df[m2_col], df[m1_col])
            
            fig_scatter = px.scatter(df, x=m2_col, y=m1_col, hover_name=id_col, 
                                     labels={m2_col: f"{m2_label} ({unit})", m1_col: f"{m1_label} ({unit})"},
                                     title=f"Dispersão: {m1_label} vs {m2_label}")
            
            # Linha Identidade
            min_val = min(df[m1_col].min(), df[m2_col].min())
            max_val = max(df[m1_col].max(), df[m2_col].max())
            fig_scatter.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], 
                                             mode='lines', name='Identidade (y=x)', line=dict(dash='dash', color='gray')))
            
            # Linha Regressão
            reg_x = np.array([min_val, max_val])
            reg_y = inter + slope * reg_x
            fig_scatter.add_trace(go.Scatter(x=reg_x, y=reg_y, mode='lines', name=f'Regressão (R²={r2:.3f})', line=dict(color='red')))
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.write(f"**Equação da Reta:** y = {slope:.4f}x + ({inter:.4f})")

            # Bland-Altman
            if show_bland:
                st.subheader("Gráfico de Bland-Altman")
                means = (df[m1_col] + df[m2_col]) / 2
                bias = differences.mean()
                sd_diff = differences.std()
                upper_loa = bias + 1.96 * sd_diff
                lower_loa = bias - 1.96 * sd_diff
                
                fig_ba = px.scatter(x=means, y=differences, hover_name=df[id_col],
                                    labels={'x': 'Média dos Métodos', 'y': f'Diferença ({m1_label} - {m2_label})'},
                                    title="Bland-Altman Plot")
                fig_ba.add_hline(y=bias, line_dash="dash", annotation_text=f"Bias: {bias:.2f}", line_color="blue")
                fig_ba.add_hline(y=upper_loa, line_dash="dot", annotation_text=f"+1.96 SD: {upper_loa:.2f}", line_color="red")
                fig_ba.add_hline(y=lower_loa, line_dash="dot", annotation_text=f"-1.96 SD: {lower_loa:.2f}", line_color="red")
                st.plotly_chart(fig_ba, use_container_width=True)

            # Histogramas e Boxplots
            c1, c2 = st.columns(2)
            with c1:
                fig_hist = px.histogram(differences, title="Distribuição das Diferenças", labels={'value': 'Diferença'})
                st.plotly_chart(fig_hist, use_container_width=True)
            with c2:
                df_melt = df.melt(value_vars=[m1_col, m2_col], var_name='Método', value_name='Resultado')
                fig_box = px.box(df_melt, x='Método', y='Resultado', title="Comparação de Distribuições")
                st.plotly_chart(fig_box, use_container_width=True)

        with tab3:
            st.subheader("Análise por Faixas de Concentração")
            n_bins = st.slider("Número de Faixas", 2, 5, 3)
            df['Faixa'] = pd.qcut(df[m2_col], n_bins)
            
            faixa_stats = df.groupby('Faixa').apply(lambda x: pd.Series({
                'N': len(x),
                'Bias Médio': (x[m1_col] - x[m2_col]).mean(),
                'MAPE %': (np.abs((x[m1_col] - x[m2_col]) / x[m2_col]) * 100).mean(),
                'Correlação': x[m1_col].corr(x[m2_col])
            })).reset_index()
            
            st.dataframe(faixa_stats)
            
            if group_col != "Nenhum":
                st.subheader(f"Análise por Grupo: {group_col}")
                fig_group = px.box(df, x=group_col, y=m1_col, color=group_col, title=f"Distribuição de {m1_label} por {group_col}")
                st.plotly_chart(fig_group, use_container_width=True)

        with tab4:
            st.subheader("Conclusão Automática")
            
            corr_text = "forte" if pearson_r > 0.9 else "moderada" if pearson_r > 0.7 else "fraca"
            bias_text = "significativo" if (is_normal and t_p < 0.05) or (not is_normal and w_p < 0.05) else "não significativo"
            
            conclusao = f"""
            **Resumo da Análise:**
            - Foram analisadas **{len(df)} amostras** pareadas.
            - A correlação entre os métodos é **{corr_text}** (r = {pearson_r:.4f}).
            - O viés médio (Bias) observado foi de **{bias:.4f} {unit}**, o que é estatisticamente **{bias_text}**.
            - O erro percentual absoluto médio (MAPE) foi de **{comp['Erro % Absoluto Médio (MAPE)']: .2f}%**.
            
            **Interpretação:**
            {"Os métodos apresentam alta concordância e podem ser considerados intercambiáveis dependendo dos critérios clínicos." if (pearson_r > 0.95 and bias_text == "não significativo") else "Existem diferenças sistemáticas ou aleatórias que devem ser avaliadas frente aos limites de erro total permitido (TEa)."}
            """
            st.markdown(conclusao)
            
            # Exportação
            st.divider()
            st.subheader("📥 Exportar Resultados")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Baixar Dados Tratados (CSV)", csv, "dados_tratados.csv", "text/csv")
            
            # Gerar resumo para download
            summary_str = res_df.to_csv(index=False) + "\n" + pd.DataFrame([comp]).to_csv(index=False)
            st.download_button("Baixar Resumo Estatístico (CSV)", summary_str.encode('utf-8'), "resumo_analise.csv", "text/csv")

else:
    st.info("Aguardando upload de arquivo para iniciar a análise.")
    # Exemplo de estrutura
    st.write("### Estrutura esperada do arquivo:")
    example_df = pd.DataFrame({
        'ID_Amostra': ['S001', 'S002', 'S003'],
        'Metodo_Referencia': [10.5, 22.1, 15.8],
        'Metodo_Teste': [10.8, 21.9, 16.2]
    })
    st.table(example_df)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido para Análise Laboratorial v1.0")
