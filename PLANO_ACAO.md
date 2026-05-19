# 🔧 PLANO DE AÇÃO - FISCO_GW

## ✅ CHECKLIST DE LIMPEZA

### FASE 1: REMOÇÃO IMEDIATA (Risco: MUITO BAIXO)

- [ ] **1.1 Remover export.py**
  - Arquivo: `modules/export.py`
  - Razão: Completamente duplicado por exporter.py
  - Verificar: Nenhuma importação em app.py
  - Comando: `rm modules/export.py`
  
- [ ] **1.2 Remover fiscal.py**
  - Arquivo: `modules/fiscal.py`
  - Razão: Versão antiga, supersedida por tax_engine.py
  - Verificar: app.py importa `calcular_imposto` - ATUALIZAR para tax_engine
  - Ação: Atualizar linha 16 de app.py

- [ ] **1.3 Remover merger.py**
  - Arquivo: `modules/merger.py`
  - Razão: Código incompleto, faz referência a variáveis globais
  - Verificar: Não é importado
  - Comando: `rm modules/merger.py`

- [ ] **1.4 Remover dashboard.py**
  - Arquivo: `components/dashboard.py`
  - Razão: Arquivo completamente vazio
  - Verificar: Não é importado
  - Comando: `rm components/dashboard.py`

- [ ] **1.5 Remover reports.py**
  - Arquivo: `components/reports.py`
  - Razão: Arquivo completamente vazio
  - Verificar: Não é importado
  - Comando: `rm components/reports.py`

---

### FASE 2: CORRIGIR DEPENDÊNCIAS (Risco: MUITO BAIXO)

- [ ] **2.1 Adicionar fpdf2 em requirements.txt**
  - Motivo: exporter.py usa `from fpdf import FPDF`
  - Status: Não está em requirements.txt
  - Ação: Adicionar `fpdf2==2.7.0`
  - Teste: `pip install fpdf2`

- [ ] **2.2 Pinnar versões em requirements.txt**
  - Motivo: Melhor prática para reprodutibilidade
  - Ação: Adicionar versões específicas (veja template abaixo)

- [ ] **2.3 Criar requirements-dev.txt**
  - Motivo: Separar dependências de desenvolvimento
  - Incluir: pytest, black, pylint

---

### FASE 3: ATUALIZAR IMPORTS (Risco: BAIXO)

- [ ] **3.1 Atualizar app.py**
  ```python
  # LINHA 16 - ANTES:
  from modules.fiscal import calcular_imposto
  
  # LINHA 16 - DEPOIS:
  from modules.tax_engine import calcular_imposto_inteligente as calcular_imposto
  # OU usar calcular_imposto_inteligente diretamente
  ```

- [ ] **3.2 Remover import de export.py se existir**
  ```python
  # Se houver em algum lugar:
  # from modules.export import ...
  # Remover (usar exporter.py em seu lugar)
  ```

---

### FASE 4: CONSOLIDAÇÃO (Risco: MÉDIO)

- [ ] **4.1 Integrar ml_engine.py em auditoria.py**
  - Mover: `prever_anomalias_ml()` de ml_engine.py
  - Para: auditoria.py
  - Atualizar: Nenhum import precisa mudar (nunca foi usado)
  - Remover: ml_engine.py depois

- [ ] **4.2 Mover methodology.py para investigador_view.py**
  - Mover: `mostrar_metodologia()` para investigador_view.py
  - Contexto: Função é só UI, faz sentido estar perto da UI
  - Remover: methodology.py depois

- [ ] **4.3 Avaliar nlp_engine.py**
  - Status: Funções existem mas nunca importadas
  - Decisão:
    - ❌ Se não vai usar: rm modules/nlp_engine.py
    - ✅ Se vai usar: Integrar em parser_engine.py
  - Sugestão: INTEGRAR - as funções são úteis

---

### FASE 5: REFATORAÇÃO ESTRUTURAL (Risco: ALTO)

**ATENÇÃO: Estas ações são maiores e requerem testes.**

- [ ] **5.1 Consolidar DB Operations**
  - Atualmente: 3 arquivos (db.py, db_insert.py, db_read.py)
  - Proposto: Classe DatabaseManager em db.py
  - Veja código refatorado abaixo

- [ ] **5.2 Refatorar app.py em páginas**
  - Dividir app.py em:
    - `app.py` (orchestration)
    - `pages/analise_fiscal.py`
    - `pages/investigador.py`
    - `pages/mer_system.py`
    - `pages/investigacao.py`
  - Tempo: 4-6 horas

- [ ] **5.3 Implementar Chart Factory**
  - Centralizar lógica de gráficos
  - Facilitar adição de novos gráficos
  - Veja código refatorado abaixo

---

## 📝 TEMPLATES DE REFATORAÇÃO

### Template 1: requirements.txt Otimizado

```txt
# Core
streamlit==1.35.0
pandas==2.1.4
numpy==1.26.3

# Visualização
plotly==5.18.0
pyvis==0.3.2
networkx==3.2

# Dados
openpyxl==3.11.0
pdfplumber==0.10.3
xlsxwriter==3.1.9
fpdf2==2.7.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Machine Learning
scikit-learn==1.3.2
```

### Template 2: DatabaseManager Consolidado

```python
# modules/db.py (REFATORADO)

from sqlalchemy import create_engine
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerencia todas as operações de banco de dados."""
    
    def __init__(self):
        self.engine = self._init_engine()
    
    def _init_engine(self):
        """Inicializa engine com fallback SQLite."""
        try:
            database_url = os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:123456@localhost:5432/fiscal_db"
            )
            engine = create_engine(database_url, echo=False)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("✓ PostgreSQL conectado")
            return engine
        except Exception as e:
            logger.warning(f"PostgreSQL falhou: {e}")
            sqlite_url = "sqlite:///fiscal_db.db"
            engine = create_engine(sqlite_url, echo=False)
            logger.info("✓ SQLite (fallback) conectado")
            return engine
    
    def insert(self, table_name: str, df: pd.DataFrame) -> bool:
        """Insere dados em uma tabela."""
        try:
            df.to_sql(table_name, self.engine, if_exists="append", index=False)
            logger.info(f"✓ Inseridos {len(df)} registos em {table_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir: {e}")
            return False
    
    def read(self, query: str) -> pd.DataFrame:
        """Lê dados com query SQL."""
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Erro ao ler: {e}")
            return pd.DataFrame()
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Lê tabela inteira."""
        return self.read(f"SELECT * FROM {table_name}")

# Instância global
db_manager = DatabaseManager()

# Backward compatibility
def get_engine():
    return db_manager.engine

engine = get_engine()
```

**Uso Novo:**
```python
# Em vez de:
# from modules.db_insert import inserir_contribuintes
# from modules.db_read import listar_contribuintes

# Usar:
from modules.db import db_manager

db_manager.insert("contribuinte", df)
listar = db_manager.read_table("contribuinte")
```

### Template 3: Chart Factory

```python
# components/chart_factory.py (NOVO)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class ChartFactory:
    """Factory centralizada para todos os gráficos."""
    
    @staticmethod
    def criar_cliente_chart(df: pd.DataFrame):
        """Gráfico de clientes por volume."""
        if "cliente" not in df.columns or "valor" not in df.columns:
            return px.bar(title="Dados insuficientes")
        
        resumo = df.groupby("cliente")["valor"].sum().reset_index()
        return px.bar(
            resumo, 
            x="cliente", 
            y="valor", 
            title="Volume por Cliente",
            color_discrete_sequence=['#00d2ff']
        )
    
    @staticmethod
    def criar_risco_chart(df: pd.DataFrame):
        """Gráfico de risco."""
        if "cliente" not in df.columns or "score_risco" not in df.columns:
            return px.bar(title="Dados de risco insuficientes")
        
        return px.bar(
            df.sort_values(by="score_risco", ascending=False).head(10),
            x="cliente",
            y="score_risco",
            color="nivel_risco",
            title="Top 10 Contribuintes por Risco",
            color_discrete_map={
                "🔴 Alto Risco": "#ef4444",
                "🟡 Médio Risco": "#f59e0b",
                "🟢 Baixo Risco": "#10b981"
            }
        )
    
    @staticmethod
    def criar_benford_chart(df: pd.DataFrame, column: str = "valor"):
        """Gráfico de análise Benford."""
        # ... implementação ...
        pass

# Uso em app.py:
# from components.chart_factory import ChartFactory
# fig = ChartFactory.criar_cliente_chart(df)
```

### Template 4: Integração ml_engine em auditoria

```python
# modules/auditoria.py (ADICIONAR ISTO NO FIM)

from modules.ml_engine import prever_anomalias_ml

def detectar_anomalias_ml(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper para manter compatibilidade."""
    return prever_anomalias_ml(df)

# Depois remover ml_engine.py
```

---

## 🧪 TESTE E VALIDAÇÃO

### Teste 1: Importações Básicas
```python
# test_imports.py
import sys
sys.path.insert(0, '/path/to/fisco_gw')

try:
    from modules.exporter import exportar_csv, exportar_excel
    from modules.tax_engine import calcular_imposto_inteligente
    from modules.auditoria import detectar_valores_invalidos
    from components.charts import grafico_clientes
    print("✓ Todos os imports funcionam")
except ImportError as e:
    print(f"✗ Erro: {e}")
```

### Teste 2: Funcionalidade do app.py
```bash
# No terminal
streamlit run app.py

# Verificar:
# 1. Carrega sem erros
# 2. Upload funciona
# 3. Abas todas acessíveis
# 4. Gráficos renderizam
# 5. Análises executam
```

### Teste 3: Remover e Validar
```bash
# Remover export.py e testar
rm modules/export.py
streamlit run app.py
# Se funciona, confirma que não era necessário

# Remover fiscal.py e testar
rm modules/fiscal.py
streamlit run app.py
# Se funciona, confirma que tax_engine.py é suficiente
```

---

## 📋 ORDEM DE EXECUÇÃO RECOMENDADA

```
1. HOJE (30 min)
   └─ FASE 1: Remover 5 arquivos
   └─ FASE 2.1: Adicionar fpdf2
   └─ Testar: streamlit run app.py

2. AMANHÃ (2-3 horas)
   └─ FASE 3: Atualizar imports
   └─ FASE 2.2: Pinnar versões
   └─ Testar novamente

3. ESTA SEMANA (3-4 horas)
   └─ FASE 4: Consolidações
   └─ Testes unitários
   └─ Commit no Git

4. PRÓXIMAS SEMANAS
   └─ FASE 5: Refatoração grande
   └─ QA em staging
   └─ Deploy
```

---

## 📊 MÉTRICAS DE SUCESSO

Depois da limpeza, você deve ter:

- ✅ 0 erros de import
- ✅ 0 arquivos vazios
- ✅ 0 módulos orphaned
- ✅ Todas as dependências em requirements.txt
- ✅ streamlit run app.py executa sem erros
- ✅ Todas as funcionalidades funcionam igual
- ✅ Código -15% (menos redundância)

---

## 🚨 ROLLBACK (Se algo correr mal)

Se após limpeza encontrar problemas:

```bash
# Ver histórico Git
git log --oneline | head -20

# Reverter para versão anterior
git revert <commit-hash>

# Ou restaurar arquivo específico
git restore modules/export.py
```

**Importante:** Sempre faça commit ANTES de cada fase!

```bash
git add -A
git commit -m "FASE 1: Remove redundâncias (export, fiscal, merger, dashboard, reports)"

git add -A
git commit -m "FASE 2: Adiciona fpdf2 e pinnas versões"

# ... etc
```

---

**Versão:** 1.0  
**Data:** 2026-05-18  
**Pronto para usar!**
