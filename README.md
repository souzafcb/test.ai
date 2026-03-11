# Comparador de Metodologias Analíticas

Esta aplicação foi desenvolvida em Python com Streamlit para facilitar a comparação de resultados entre dois métodos laboratoriais/analíticos.

## Como executar localmente

1. **Certifique-se de ter o Python instalado** (v3.8 ou superior).
2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Execute a aplicação:**
   ```bash
   streamlit run app.py
   ```

## Funcionalidades
- Importação de CSV/Excel.
- Estatística descritiva e pareada.
- Testes de normalidade e significância.
- Gráficos de Dispersão, Regressão e Bland-Altman.
- Análise segmentada por faixas de concentração.
- Exportação de relatórios.
