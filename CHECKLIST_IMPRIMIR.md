# ✅ CHECKLIST SIMPLES - FISCO_GW

**Objetivo:** Remover redundâncias e consolidar módulos  
**Tempo Total:** 6-8 horas  
**Data de Início:** ___________  
**Responsável:** ___________

---

## FASE 1: LIMPEZA RÁPIDA (30 min) - BAIXO RISCO

### Dia 1 - Manhã

- [ ] **1.1** Backup Git
  ```bash
  git status  # Verificar estado
  git add -A
  git commit -m "BACKUP: Antes da limpeza fisco_gw"
  git branch backup-fisco-2026-05-18
  ```

- [ ] **1.2** Remover export.py
  ```bash
  rm modules/export.py
  # Verificar: Nada quebrou? ✓
  ```

- [ ] **1.3** Remover fiscal.py
  ```bash
  rm modules/fiscal.py
  # Verificar: Nada quebrou? ✓
  ```

- [ ] **1.4** Remover merger.py
  ```bash
  rm modules/merger.py
  ```

- [ ] **1.5** Remover dashboard.py
  ```bash
  rm components/dashboard.py
  ```

- [ ] **1.6** Remover reports.py
  ```bash
  rm components/reports.py
  ```

- [ ] **1.7** Adicionar fpdf2
  ```bash
  echo "fpdf2==2.7.0" >> requirements.txt
  ```

- [ ] **1.8** Testar
  ```bash
  streamlit run app.py
  # ✓ Funciona sem erros?
  # ✓ Upload funciona?
  # ✓ Gráficos renderizam?
  ```

- [ ] **1.9** Commit
  ```bash
  git add -A
  git commit -m "FASE 1: Remove redundâncias (export, fiscal, merger, empty files)"
  ```

---

## FASE 2: ATUALIZAR DEPENDÊNCIAS (20 min) - RISCO MUITO BAIXO

### Dia 1 - Tarde

- [ ] **2.1** Abrir requirements.txt
  
- [ ] **2.2** Verificar versões (ANTES)
  ```
  Atual: Sem versões especificadas
  ```

- [ ] **2.3** Atualizar requirements.txt
  ```txt
  # Copiar este template:
  streamlit==1.35.0
  pandas==2.1.4
  plotly==5.18.0
  numpy==1.26.3
  pyvis==0.3.2
  networkx==3.2
  openpyxl==3.11.0
  pdfplumber==0.10.3
  sqlalchemy==2.0.23
  psycopg2-binary==2.9.9
  scikit-learn==1.3.2
  xlsxwriter==3.1.9
  fpdf2==2.7.0
  ```

- [ ] **2.4** Criar requirements-dev.txt
  ```txt
  pytest==7.4.3
  pytest-cov==4.1.0
  black==23.12.1
  pylint==3.0.3
  ```

- [ ] **2.5** Testar instalação
  ```bash
  pip install -r requirements.txt
  streamlit run app.py
  # ✓ Funciona?
  ```

- [ ] **2.6** Commit
  ```bash
  git add requirements.txt requirements-dev.txt
  git commit -m "FASE 2: Pinnar versões e adicionar fpdf2"
  ```

---

## FASE 3: ATUALIZAR IMPORTS (1-2 horas) - RISCO BAIXO

### Dia 2 - Manhã

- [ ] **3.1** Abrir app.py

- [ ] **3.2** Encontrar imports de módulos removidos
  ```python
  # Procure por:
  # from modules.export import ...  ← REMOVER
  # from modules.fiscal import ...  ← ATUALIZAR
  ```

- [ ] **3.3** Atualizar import de fiscal
  ```python
  # ANTES:
  from modules.fiscal import calcular_imposto
  
  # DEPOIS (escolha uma):
  # Opção A - Alias:
  from modules.tax_engine import calcular_imposto_inteligente as calcular_imposto
  
  # Opção B - Usar direto:
  from modules.tax_engine import calcular_imposto_inteligente
  # (depois substituir uso em app.py)
  ```

- [ ] **3.4** Verificar arquivo inteiro por imports orphaned
  ```bash
  grep -n "from modules.export\|from modules.fiscal\|from modules.merger" app.py
  # Deve retornar 0 resultados
  ```

- [ ] **3.5** Verificar imports de components
  ```bash
  grep -n "dashboard\|reports" app.py
  # Deve retornar 0 resultados
  ```

- [ ] **3.6** Teste completo
  ```bash
  streamlit run app.py
  # ✓ Nenhum erro de import?
  # ✓ Todas as funcionalidades ativas?
  # ✓ Dashboard carrega?
  # ✓ Auditoria funciona?
  # ✓ Gráficos renderizam?
  ```

- [ ] **3.7** Commit
  ```bash
  git add app.py
  git commit -m "FASE 3: Atualiza imports (fiscal, export removidos)"
  ```

---

## FASE 4: CONSOLIDAÇÃO (2-3 horas) - RISCO MÉDIO

### Dia 2 - Tarde / Dia 3

**NOTA:** Estas ações requerem teste mais cuidadoso

- [ ] **4.1** Integrar ml_engine em auditoria
  - [ ] 4.1.1 Abrir ml_engine.py
  - [ ] 4.1.2 Copiar função `prever_anomalias_ml()`
  - [ ] 4.1.3 Cola em auditoria.py (fim do arquivo)
  - [ ] 4.1.4 Testar: `from modules.auditoria import prever_anomalias_ml`
  - [ ] 4.1.5 Remover ml_engine.py: `rm modules/ml_engine.py`
  - [ ] 4.1.6 Verificar: grep -r "ml_engine" . (deve ser 0)

- [ ] **4.2** Integrar methodology em investigador_view
  - [ ] 4.2.1 Abrir methodology.py
  - [ ] 4.2.2 Copiar função `mostrar_metodologia()`
  - [ ] 4.2.3 Cola em investigador_view.py (no expander adequado)
  - [ ] 4.2.4 Testar: Abrir "Investigador Inteligente" em app.py
  - [ ] 4.2.5 Remover methodology.py: `rm modules/methodology.py`

- [ ] **4.3** Testar Auditoria
  ```bash
  streamlit run app.py
  # Ir para Análise Fiscal → Auditoria
  # ✓ Funciona sem erros?
  # ✓ Metodologia visível?
  ```

- [ ] **4.4** Commit
  ```bash
  git add modules/auditoria.py components/investigador_view.py
  git commit -m "FASE 4: Integra ml_engine em auditoria, methodology em investigador_view"
  ```

---

## FASE 5: REFATORAÇÃO DB (2-3 horas) - RISCO MÉDIO

### Dia 3 - Tarde / Dia 4

**NOTA:** Esta fase é opcional - considere fazê-la depois

- [ ] **5.1** Ler template de DatabaseManager em PLANO_ACAO.md

- [ ] **5.2** Criar backup de db.py, db_insert.py, db_read.py
  ```bash
  cp modules/db.py modules/db.py.backup
  cp modules/db_insert.py modules/db_insert.py.backup
  cp modules/db_read.py modules/db_read.py.backup
  ```

- [ ] **5.3** Refatorar db.py
  - [ ] Copiar template DatabaseManager
  - [ ] Testar classe: `from modules.db import db_manager`

- [ ] **5.4** Atualizar db_insert.py
  ```python
  # ANTES:
  from modules.db import engine
  df.to_sql(..., engine, ...)
  
  # DEPOIS:
  from modules.db import db_manager
  db_manager.insert("contribuinte", df)
  ```

- [ ] **5.5** Atualizar db_read.py
  ```python
  # ANTES:
  df = pd.read_sql(query, engine)
  
  # DEPOIS:
  df = db_manager.read(query)
  ```

- [ ] **5.6** Atualizar app.py e qualquer outro import de db
  ```bash
  grep -r "from modules.db" . --include="*.py" | grep -v ".backup"
  # Atualizar cada ocorrência
  ```

- [ ] **5.7** Teste completo de DB
  ```bash
  streamlit run app.py
  # Ir para Sistema MER
  # ✓ Contribuintes carregam?
  # ✓ Upload + insert funciona?
  ```

- [ ] **5.8** Se tudo OK: Commit
  ```bash
  git add modules/db.py modules/db_insert.py modules/db_read.py app.py
  git commit -m "FASE 5: Consolida DB operations em DatabaseManager"
  ```

- [ ] **5.9** Se algo quebrou: Rollback
  ```bash
  git restore modules/db.py modules/db_insert.py modules/db_read.py
  rm *.backup
  ```

---

## VERIFICAÇÃO FINAL

### Dia 4 - Manhã

- [ ] **6.1** Verificar arquivos deletados
  ```bash
  ls modules/*.py | wc -l  # Antes: 25, Depois: ~20-22
  ls components/*.py | wc -l  # Antes: 11, Depois: 9
  ```

- [ ] **6.2** Verificar imports
  ```bash
  python -c "import sys; sys.path.insert(0, '.'); 
  from modules import *
  from components import *
  print('✓ OK')"
  ```

- [ ] **6.3** Teste de funcionalidade
  ```bash
  streamlit run app.py
  ```
  - [ ] Upload de ficheiro
  - [ ] Análise Fiscal (Dashboard, Auditoria, Dados, Rede, Explorar)
  - [ ] Investigador Inteligente
  - [ ] Sistema MER
  - [ ] Investigação
  - [ ] Exportar em CSV, Excel, PDF

- [ ] **6.4** Verificar requirements
  ```bash
  pip install -r requirements.txt
  python -c "import fpdf; import streamlit; print('✓ OK')"
  ```

- [ ] **6.5** Contar redundâncias
  ```bash
  # Antes: 5 redundâncias (export, fiscal, merger, dashboard, reports)
  # Depois: 0 redundâncias
  # Verificar: ✓
  ```

- [ ] **6.6** Relatório Final
  - [ ] Redundâncias: 5 → 0 ✓
  - [ ] Arquivos vazios: 2 → 0 ✓
  - [ ] Módulos orphaned: 2-3 → 0 ✓
  - [ ] Dependências faltando: 1 → 0 ✓
  - [ ] Funcionamento: 100% ✓

---

## GIT COMMITS ESPERADOS

```bash
1. git log --oneline | head -10

FASE 1: Remove redundâncias
FASE 2: Pinnar versões e adicionar fpdf2
FASE 3: Atualiza imports
FASE 4: Integra ml_engine em auditoria
FASE 5: Consolida DB operations
...
```

---

## MÉTRICAS ANTES → DEPOIS

|  | ANTES | DEPOIS | ✓ |
|---|---|---|---|
| Arquivos Python | 36 | ~22 | |
| Redundâncias | 5 | 0 | ✓ |
| Vazios | 2 | 0 | ✓ |
| Orphaned | 3 | 0 | ✓ |
| Dep. Faltando | 1 | 0 | ✓ |
| LOC app.py | 600+ | 300-400 | |
| Funcionamento | 100% | 100% | ✓ |

---

## ROLLBACK RÁPIDO (Se precisar)

```bash
# Se algo correr muito mal:
git log --oneline | head -5
git reset --hard <commit-anterior>

# Se só um arquivo:
git restore <arquivo>

# Restaurar backup:
cp modules/db.py.backup modules/db.py
```

---

## ASSINATURA

**Data Início:** ___________  
**Data Conclusão:** ___________  
**Responsável:** ___________  
**Verificado por:** ___________  
**Status:** [ ] COMPLETO [ ] INCOMPLETO [ ] COM PROBLEMAS

**Problemas encontrados:**
```
_________________________________________________________________

_________________________________________________________________
```

**Próximas ações:**
```
_________________________________________________________________

_________________________________________________________________
```

---

**Impresso:** ___________  
**Versão:** 1.0  
**Data:** 2026-05-18
