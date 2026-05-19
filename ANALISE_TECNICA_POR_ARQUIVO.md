# 🔬 ANÁLISE TÉCNICA POR ARQUIVO - FISCO_GW

---

## 📊 MATRIZ DE ANÁLISE

### Legend
- ✅ = Manter
- ❌ = Remover
- ⚠️ = Revisar
- 🔄 = Consolidar
- 🔗 = Integrar em outro

---

## modules/ - 25 Arquivos

### TIER 1: REMOVER (5 arquivos - HOJE)

#### ❌ **export.py** (5 linhas)
```python
def exportar_csv(df):
    return df.to_csv(index=False).encode("utf-8")
```
- **Status:** Redundante 100%
- **Problema:** Exatamente a mesma função em exporter.py
- **Ação:** REMOVER
- **Impacto:** Nenhum (exporter.py é versão completa)
- **Verificar:** grep -r "from modules.export" .
- **Risco:** MUITO BAIXO

#### ❌ **fiscal.py** (5 linhas)
```python
def calcular_imposto(volume, lucro):
    imposto_normal = lucro * 0.25
    imposto_minimo = volume * 0.01
    return max(imposto_normal, imposto_minimo)
```
- **Status:** Obsoleto
- **Problema:** tax_engine.py tem versão muito melhor com IA
- **Ação:** REMOVER, atualizar import em app.py para tax_engine
- **Impacto:** Ganho de lógica inteligente
- **Verificar:** grep -r "from modules.fiscal" . (aparece em app.py linha 16)
- **Risco:** MUITO BAIXO

#### ❌ **merger.py** (10 linhas)
```python
def juntar_ficheiros(df1, df2):
    return pd.concat([df1, df2])

if len(dfs) >= 2:  # ❌ 'dfs' não definido neste módulo
    if st.button("🔗 Juntar ficheiros"):
        ...
```
- **Status:** Incompleto/Fragmentado
- **Problema:** Código UI + lógica misturado, referencia variável global `dfs`
- **Ação:** REMOVER
- **Impacto:** Funcionalidade já existe em app.py
- **Verificar:** Não é importado em lugar nenhum
- **Risco:** MUITO BAIXO

---

### TIER 2: REVISAR / CONSOLIDAR (3 arquivos - ESTA SEMANA)

#### 🔗 **methodology.py** (50 linhas)
```python
def mostrar_metodologia():
    with st.expander("📖 Guia de Interpretação..."):
        st.markdown("""...""")
```
- **Status:** Funcional mas orphaned
- **Problema:** Função é só UI, isolada
- **Ação:** MOVER para investigador_view.py
- **Impacto:** Centralizar UI em um lugar
- **Verificar:** grep -r "mostrar_metodologia" . (não é usado)
- **Risco:** BAIXO
- **Timeline:** ESTA SEMANA

#### 🔗 **ml_engine.py** (80+ linhas)
```python
def prever_anomalias_ml(df):
    # Usa IsolationForest para detectar anomalias
    # Implementação sofisticada
```
- **Status:** Funcional mas nunca importado
- **Problema:** Não é chamado em nenhum lugar
- **Ação:** INTEGRAR em auditoria.py (onde faz sentido)
- **Impacto:** Usar análise ML em auditoria
- **Verificar:** grep -r "ml_engine\|prever_anomalias_ml" . (não está em app.py)
- **Risco:** BAIXO
- **Timeline:** ESTA SEMANA

#### ⚠️ **nlp_engine.py** (50+ linhas)
```python
def limpar_texto(texto):
def extrair_entidades_texto(texto):
def analisar_sentimento_fiscal(texto):
```
- **Status:** Funções úteis mas não importadas
- **Problema:** Poderia ser usado em parser_engine.py para análise de descrições
- **Ação:** INTEGRAR em parser_engine.py OU manter se vai usar
- **Impacto:** Melhorar análise de textos
- **Verificar:** grep -r "nlp_engine" . (não importado)
- **Risco:** BAIXO
- **Timeline:** ESTA SEMANA (se vai usar)

---

### TIER 3: CORE - MANTER ✅ (15 arquivos)

#### ✅ **uploader.py**
- **Função:** Carrega ficheiros Excel/PDF/CSV
- **Imports:** openpyxl, pdfplumber
- **Usado em:** app.py (linha 10)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **cleaner.py**
- **Função:** Normaliza nomes de colunas com IA
- **Imports:** unicodedata, re, difflib
- **Usado em:** parser_engine.py
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 10/10

#### ✅ **parser_engine.py**
- **Função:** Pipeline inteligente de parsing
- **Imports:** schema_detector, cleaner, tax_engine
- **Usado em:** app.py (linha 12)
- **Status:** CRITICAL
- **Ação:** MANTER
- **Score:** 10/10

#### ✅ **exporter.py**
- **Função:** Export em CSV, Excel, PDF
- **Imports:** pandas, io, xlsxwriter, fpdf
- **Usado em:** app.py (linha 13)
- **Status:** ESSENCIAL
- **Ação:** MANTER + USAR em vez de export.py
- **Score:** 10/10

#### ✅ **analyzer.py**
- **Função:** Análises básicas (volume, clientes, fornecedores)
- **Imports:** pandas
- **Usado em:** app.py (linha 14)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

#### ✅ **relationships.py**
- **Função:** Calcula relações cliente-fornecedor
- **Imports:** pandas
- **Usado em:** app.py (linha 15)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

#### ✅ **tax_engine.py**
- **Função:** Cálculos de imposto com IA
- **Imports:** fiscal_rules, ai_classifier
- **Usado em:** parser_engine.py
- **Status:** CRÍTICA
- **Ação:** MANTER (é a versão inteligente)
- **Score:** 10/10

#### ✅ **fiscal_rules.py**
- **Função:** Define regras de IVA
- **Imports:** -
- **Usado em:** tax_engine.py
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **ai_classifier.py**
- **Função:** Classificação de regime fiscal por IA
- **Imports:** re
- **Usado em:** tax_engine.py
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **schema_detector.py**
- **Função:** Detecta tipo de declaração
- **Imports:** -
- **Usado em:** parser_engine.py
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **fraud.py**
- **Função:** Detecção de fraude (Benford, outliers, duplicatas)
- **Imports:** pandas, numpy, plotly
- **Usado em:** app.py (linha 45+)
- **Status:** CRÍTICA
- **Ação:** MANTER
- **Score:** 10/10

#### ✅ **auditoria.py**
- **Função:** Funções de auditoria
- **Imports:** -
- **Usado em:** app.py (linha 27)
- **Status:** CRÍTICA
- **Ação:** MANTER (vai absorver ml_engine)
- **Score:** 10/10

#### ✅ **risk.py**
- **Função:** Calcula score de risco
- **Imports:** pandas
- **Usado em:** app.py (linha 18)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **network.py**
- **Função:** Análise de redes/grafos e fraude carrossel
- **Imports:** networkx
- **Usado em:** app.py (linha 19)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **mapper.py**
- **Função:** Extrai entidades (clientes, fornecedores)
- **Imports:** pandas
- **Usado em:** app.py (linha 20)
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

#### ✅ **db.py**
- **Função:** Gerencia conexão com DB (PostgreSQL + SQLite fallback)
- **Imports:** sqlalchemy
- **Usado em:** db_insert.py, db_read.py
- **Status:** ESSENCIAL
- **Ação:** MANTER (consolidar db_insert + db_read depois)
- **Score:** 10/10

#### ✅ **db_insert.py**
- **Função:** Insere contribuintes na DB
- **Imports:** pandas, db
- **Usado em:** app.py (linha 21)
- **Status:** ESSENCIAL
- **Ação:** MANTER (CONSOLIDAR em db.py depois)
- **Score:** 8/10

#### ✅ **db_read.py**
- **Função:** Lê contribuintes da DB
- **Imports:** pandas, db
- **Usado em:** app.py (linha 22)
- **Status:** ESSENCIAL
- **Ação:** MANTER (CONSOLIDAR em db.py depois)
- **Score:** 8/10

---

## components/ - 11 Arquivos

### TIER 1: REMOVER (2 arquivos - HOJE)

#### ❌ **dashboard.py** (0 linhas)
- **Status:** Vazio
- **Problema:** Arquivo vazio, sem conteúdo
- **Ação:** REMOVER
- **Impacto:** Nenhum
- **Verificar:** cat components/dashboard.py (deve estar vazio)
- **Risco:** MUITO BAIXO

#### ❌ **reports.py** (0 linhas)
- **Status:** Vazio
- **Problema:** Arquivo vazio, sem conteúdo
- **Ação:** REMOVER
- **Impacto:** Nenhum
- **Verificar:** cat components/reports.py (deve estar vazio)
- **Risco:** MUITO BAIXO

---

### TIER 2: CORE - MANTER ✅ (9 arquivos)

#### ✅ **charts.py**
- **Funções:** grafico_clientes(), grafico_risco()
- **Status:** ESSENCIAL
- **Ação:** MANTER (considerar factory pattern depois)
- **Score:** 9/10

#### ✅ **filters.py**
- **Funções:** aplicar_filtros()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **network_chart.py**
- **Funções:** visualizar_grafo()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **query_builder.py**
- **Funções:** query_builder()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

#### ✅ **contributor_view.py**
- **Funções:** analisar_contribuinte()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **entity_relationship.py**
- **Funções:** analisar_relacao()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

#### ✅ **investigador_view.py**
- **Funções:** investigador_inteligente()
- **Status:** CRÍTICA (UI principal)
- **Ação:** MANTER (vai absorver methodology.py)
- **Score:** 10/10

#### ✅ **time_analysis.py**
- **Funções:** analise_temporal()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 9/10

#### ✅ **fiscal_compare.py**
- **Funções:** cruzamento_fiscal()
- **Status:** ESSENCIAL
- **Ação:** MANTER
- **Score:** 8/10

---

## requirements.txt - 12 Dependências

### ✅ VALIDADAS

| Pacote | Versão | Usado em | Score | Status |
|--------|--------|----------|-------|--------|
| streamlit | ? | app.py, all | 10/10 | ✅ |
| pandas | ? | all | 10/10 | ✅ |
| plotly | ? | components/charts | 10/10 | ✅ |
| numpy | ? | fraud.py, ml_engine | 9/10 | ✅ |
| pyvis | ? | network_chart | 9/10 | ✅ |
| networkx | ? | network.py | 9/10 | ✅ |
| openpyxl | ? | uploader.py | 9/10 | ✅ |
| pdfplumber | ? | uploader.py | 8/10 | ✅ |
| sqlalchemy | ? | db.py | 10/10 | ✅ |
| psycopg2-binary | ? | db.py | 9/10 | ✅ |
| scikit-learn | ? | ml_engine.py | 8/10 | ✅ |
| xlsxwriter | ? | exporter.py | 10/10 | ✅ |

### ❌ FALTANDO

| Pacote | Usado em | Ação |
|--------|----------|------|
| fpdf2 | exporter.py | ➕ ADICIONAR |

---

## app.py - 600+ Linhas

### 📊 Análise

| Aspecto | Valor |
|---------|-------|
| Linhas | 600+ |
| Imports | 50+ |
| Funções | ~0 (tudo inline) |
| Abas/Páginas | 4 principais |
| Complexidade | Alta (tudo em um arquivo) |
| Status | ⚠️ PODE REFATORAR |

### 🔄 Oportunidade (FASE 5 - próximas semanas)

```
ANTES:
  app.py (600+ linhas)
  └─ Tudo inline

DEPOIS:
  app.py (300-400 linhas, só orchestration)
  ├─ pages/analise_fiscal.py
  ├─ pages/investigador.py
  ├─ pages/mer_system.py
  └─ pages/investigacao.py
```

**Ganho:** -50% linhas, melhor manutenibilidade

---

## 📊 Resumo Numérico

### REMOVER
```
- export.py (5 linhas)
- fiscal.py (5 linhas)
- merger.py (10 linhas)
- dashboard.py (0 linhas)
- reports.py (0 linhas)
TOTAL: 20 linhas, 5 arquivos
```

### CONSOLIDAR
```
- ml_engine.py → auditoria.py
- methodology.py → investigador_view.py
- nlp_engine.py → parser_engine.py (opcional)
- db_insert.py + db_read.py → db.py
TOTAL: 4 consolidações
```

### MANTER
```
- Core: 15 módulos
- UI: 9 componentes
- DB: 3 operações (consolidar depois)
TOTAL: 27 arquivos essenciais
```

---

## 🎯 Ações Resumidas

```
HOJE (30 min):
  ❌ rm export.py
  ❌ rm fiscal.py
  ❌ rm merger.py
  ❌ rm dashboard.py
  ❌ rm reports.py
  ➕ add fpdf2 em requirements.txt

ESTA SEMANA (3-4 h):
  🔗 ml_engine → auditoria
  🔗 methodology → investigador_view
  🔗 nlp_engine → parser_engine (opcional)
  🔄 Consolidar DB

PRÓXIMAS SEMANAS (4-6 h - OPCIONAL):
  🔄 app.py → pages/
  🔄 Charts → factory
  📝 Testes
```

---

**Versão:** 1.0  
**Data:** 2026-05-18  
**Próximo:** Use PLANO_ACAO.md para implementar
