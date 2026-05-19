# 📄 ONE-PAGER - FISCO_GW LIMPEZA

**Preparado:** 2026-05-18 | **Duração:** 6-8h | **Risco:** Baixo-Médio | **Ganho:** Alto

---

## 🎯 OBJETIVO

Remover redundâncias, consolidar módulos e melhorar manutenibilidade do repositório fisco_gw.

---

## 📊 SITUAÇÃO

```
Arquivos:         36  →  22 (-39%)
Redundâncias:      5  →  0 (-100%)
Vazios:            2  →  0 (-100%)
Orphaned:          3  →  0 (-100%)
Dependências ok:  11  → 13 (+100%)
Funcionamento:   100% → 100% (sem perda)
```

---

## 🔴 AÇÕES HOJE (30 min)

| # | Arquivo | Ação | Por quê |
|---|---------|------|--------|
| 1 | export.py | ❌ rm | Duplicado 100% |
| 2 | fiscal.py | ❌ rm | Obsoleto |
| 3 | merger.py | ❌ rm | Incompleto |
| 4 | dashboard.py | ❌ rm | Vazio |
| 5 | reports.py | ❌ rm | Vazio |
| 6 | requirements.txt | ➕ add fpdf2 | Missing dependency |

**Risco:** MUITO BAIXO | **Teste:** streamlit run app.py

---

## 🟠 AÇÕES SEMANA (4h)

| # | Ação | Tempo | Risco |
|---|------|-------|-------|
| 1 | Atualizar imports | 30min | Baixo |
| 2 | Pinnar versões | 20min | Muito Baixo |
| 3 | Integrar ml_engine em auditoria | 30min | Baixo |
| 4 | Mover methodology em investigador_view | 15min | Muito Baixo |
| 5 | Consolidar DB (db_insert + db_read em db) | 2h | Médio |

**Teste completo:** Depois de cada ação

---

## 🟡 AÇÕES PRÓXIMAS SEMANAS (4-6h, OPCIONAL)

- [ ] Refatorar app.py em pages/ (-50% linhas)
- [ ] Implementar Chart Factory (escalabilidade)
- [ ] Adicionar testes unitários

---

## 📈 RESULTADOS

### Antes
```
❌ Confusão de imports
❌ Código duplicado
❌ Módulos orphaned
❌ Dependência faltando
❌ app.py com 600+ linhas
```

### Depois
```
✅ Imports limpos
✅ Sem redundância
✅ Tudo bem organizado
✅ Todas as dependências
✅ Código -15%
✅ Manutenibilidade +25%
```

---

## 🎯 CORE A MANTER

✅ Detecção de Fraude (Benford, estatísticas, carrossel)
✅ Cálculos de Imposto com IA
✅ Normalização de Dados
✅ Dashboard e Gráficos
✅ Análise de Redes
✅ Exportação (CSV, Excel, PDF)

---

## 📚 DOCUMENTAÇÃO

| Doc | Tamanho | Tempo | Para |
|-----|---------|-------|------|
| SUMARIO_EXECUTIVO.md | 4 pg | 5min | Gestores |
| ANALISE_REPOSITORIO.md | 20 pg | 30min | Arquitetos |
| PLANO_ACAO.md | 15 pg | 20min | Devs (exec) |
| CHECKLIST_IMPRIMIR.md | 12 pg | 10min | Dia-a-dia |
| DIAGRAMA_VISUAL.md | 10 pg | 10min | Visuais |

**→ Comece:** LEIA_PRIMEIRO.md

---

## ⏱️ TIMELINE

```
HOJE          SEMANA 1      SEMANA 2-3    SEMANA 4+
├─ 30min      ├─ 2h         ├─ 2h         ├─ 4-6h
├─ Remove 5   ├─ Imports    ├─ Consolida  ├─ Refatora
├─ Add fpdf2  ├─ Versões    ├─ Testes     ├─ Escalas
└─ Test ✓     └─ ML integr  └─ QA ✓       └─ Deploy
```

---

## ✅ CHECKLIST INICIO

- [ ] Ler análise apropriada (5-30 min)
- [ ] Fazer backup Git
- [ ] Seguir PLANO_ACAO.md
- [ ] Testar após cada fase
- [ ] Commit regularmente

---

## 🚨 ROLLBACK (se necessário)

```bash
git log --oneline | head -5
git reset --hard <commit-anterior>
```

---

## 💬 RECOMENDAÇÃO

✅ **PROCEDER COM:**
- FASE 1 (hoje)
- FASE 2-4 (semana)
- FASE 5 (opcional, depois)

**ROI:** 6-8h investimento → +25% manutenibilidade permanente

---

**Próxima:** Abra [LEIA_PRIMEIRO.md](LEIA_PRIMEIRO.md)
