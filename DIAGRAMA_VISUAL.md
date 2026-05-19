# 📐 DIAGRAMA VISUAL - FISCO_GW

## Estrutura ATUAL vs PROPOSTA

```
ESTRUTURA ATUAL (COM PROBLEMAS)
═══════════════════════════════════════════════════════════

modules/
├── ❌ export.py                    [DUPLICADO: exporter.py faz melhor]
├── ❌ fiscal.py                    [OBSOLETO: tax_engine.py supera]
├── ❌ merger.py                    [INCOMPLETO: código fragmentado]
│
├── CORE (MANTER)
│   ├── uploader.py                 ✅ Carrega ficheiros
│   ├── cleaner.py                  ✅ Normaliza colunas
│   ├── parser_engine.py            ✅ Parse inteligente
│   └── exporter.py                 ✅ Export completo
│
├── FISCAL (MANTER)
│   ├── tax_engine.py               ✅ Cálculos + IA
│   ├── fiscal_rules.py             ✅ Regras de IVA
│   ├── ai_classifier.py            ✅ Classificação
│   └── schema_detector.py          ✅ Detecta tipo
│
├── ANALYSIS (MANTER)
│   ├── auditoria.py                ✅ Auditoria
│   ├── fraud.py                    ✅ Detecção fraude
│   ├── risk.py                     ✅ Score risco
│   ├── network.py                  ✅ Grafo análise
│   └── ml_engine.py                ⚠️ NÃO IMPORTADO
│
├── DATABASE (MANTER)
│   ├── db.py                       ✅ Engine + fallback
│   ├── db_insert.py                ✅ Insere dados
│   └── db_read.py                  ✅ Lê dados
│
├── UTILS (MANTER)
│   ├── mapper.py                   ✅ Extrai entidades
│   ├── relationships.py            ✅ Relações
│   ├── nlp_engine.py               ⚠️ NÃO IMPORTADO
│   └── methodology.py              ⚠️ Só UI, pode mover

components/
├── ❌ dashboard.py                 [VAZIO: 0 linhas]
├── ❌ reports.py                   [VAZIO: 0 linhas]
│
├── CORE (MANTER)
│   ├── charts.py                   ✅ Gráficos
│   ├── filters.py                  ✅ Filtros sidebar
│   ├── network_chart.py            ✅ Visualizar grafo
│   ├── query_builder.py            ✅ Queries avançadas
│   ├── contributor_view.py         ✅ Análise por contribuinte
│   ├── entity_relationship.py      ✅ Relações
│   ├── investigador_view.py        ✅ UI investigação
│   ├── time_analysis.py            ✅ Análise temporal
│   └── fiscal_compare.py           ✅ Comparação


ESTRUTURA PROPOSTA (OTIMIZADA)
═══════════════════════════════════════════════════════════

modules/
├── core/
│   ├── uploader.py
│   ├── cleaner.py
│   ├── parser_engine.py
│   └── exporter.py
│
├── fiscal/
│   ├── tax_engine.py
│   ├── fiscal_rules.py
│   └── ai_classifier.py
│
├── analysis/
│   ├── auditoria.py                  (+ ml_engine integrado)
│   ├── fraud.py
│   ├── risk.py
│   └── network.py
│
├── database/
│   └── db.py                         (consolidado com insert + read)
│
├── utils/
│   ├── mapper.py
│   ├── relationships.py
│   ├── schema_detector.py
│   └── nlp_engine.py                 (integrado em parser_engine)

components/
├── charts.py
├── filters.py
├── network_chart.py
├── query_builder.py
├── contributor_view.py
├── entity_relationship.py
├── investigador_view.py              (+ methodology integrado)
├── time_analysis.py
└── fiscal_compare.py

pages/                                 (NOVO - refatoração app.py)
├── analise_fiscal.py
├── investigador.py
├── mer_system.py
└── investigacao.py


FLUXO DE DADOS ATUAL
═══════════════════════════════════════════════════════════

                    ┌─────────────────┐
                    │   app.py (UI)   │  600+ linhas
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  UPLOAD FILES   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    uploader.py        get_excel_sheets()    load_file()
        │
        └────────────────────┬────────────────────┐
                             │                    │
                    ┌────────▼────────┐           │
                    │ PARSING SMART   │           │
                    │ parser_engine   │           │
                    └────────┬────────┘           │
                             │                    │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    schema_det()        normalize()         tax_engine()
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  DATAFRAME OK   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┬─────────────┐
        │                    │                    │             │
        ▼                    ▼                    ▼             ▼
    AUDIT            VISUALIZATION          DATABASE      EXPORT
    ├─ fraud()       ├─ charts.py            ├─ insert()    ├─ csv
    ├─ risk()        ├─ network.py           └─ read()      ├─ excel
    ├─ benford()     └─ filters.py                          └─ pdf
    └─ anomalies()


FLUXO DE DADOS PROPOSTO (Melhorado)
═══════════════════════════════════════════════════════════

                ┌─────────────────┐
                │   app.py        │  300-400 linhas (orchestration)
                │   (limpo)       │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    pages/          components/      modules/
  (4 páginas)      (9 comps)        (18-20 mods)
   ├─ análise
   ├─ investig
   ├─ mer
   └─ rede


MAPA DE DEPENDÊNCIAS ATUAL
═══════════════════════════════════════════════════════════

app.py
├── modules.exporter              ✅
├── modules.cleaner               ✅
├── modules.parser_engine         ✅
├── modules.uploader              ✅
├── modules.analyzer              ✅
├── modules.relationships         ✅
├── modules.fiscal                ✅ (REMOVER)
├── modules.risk                  ✅
├── modules.network               ✅
├── modules.mapper                ✅
├── modules.db_insert             ✅ (consolidar)
├── modules.db_read               ✅ (consolidar)
├── modules.tax_engine            ❌ (só em tax_engine direto)
├── modules.fraud                 ✅
├── modules.auditoria             ✅
├── components.charts             ✅
├── components.filters            ✅
├── components.network_chart      ✅
├── components.query_builder      ✅
├── components.contributor_view   ✅
├── components.entity_relationship ✅
├── components.investigador_view  ✅
├── components.time_analysis      ✅
└── components.fiscal_compare     ✅


MATRIZ DE REDUNDÂNCIA
═══════════════════════════════════════════════════════════

┌──────────────────┬──────────────────┬────────┬──────────┐
│ Módulo A         │ Módulo B          │ Razão  │ Ação     │
├──────────────────┼──────────────────┼────────┼──────────┤
│ export.py        │ exporter.py      │ DUPLIC │ REMOVER  │
│ fiscal.py        │ tax_engine.py    │ DUPLIC │ REMOVER  │
│ merger.py        │ (nenhum)         │ INCOMP │ REMOVER  │
│ ml_engine.py     │ auditoria.py     │ ORPHAN │ INTEGRAR │
│ methodology.py   │ investig_view.py │ ORPHAN │ MOVER    │
│ nlp_engine.py    │ parser_engine.py │ ORPHAN │ INTEGRAR │
│ dashboard.py     │ (vazio)          │ EMPTY  │ REMOVER  │
│ reports.py       │ (vazio)          │ EMPTY  │ REMOVER  │
│ db_insert.py     │ db.py            │ FRAG   │ CONSOLIDAR│
│ db_read.py       │ db.py            │ FRAG   │ CONSOLIDAR│
└──────────────────┴──────────────────┴────────┴──────────┘


IMPACTO VISUAL
═══════════════════════════════════════════════════════════

ANTES (Caótico)
    export.py ─┐
    fiscal.py  ├─→ CONFUSÃO
    merger.py  │
    empty .py  │
    orphan.py  └────┐
                    ▼
          [36 arquivos]
          [3 redundâncias]
          [2 vazios]
          [2+ orphaned]
          [1 dependência falta]

DEPOIS (Organizado)
    core/
      ├─ uploader
      ├─ cleaner
      ├─ parser
      └─ exporter
    fiscal/
      ├─ tax_engine
      ├─ rules
      └─ classifier
    analysis/
      ├─ auditoria*
      ├─ fraud
      ├─ risk
      └─ network
    database/
      └─ db*
    utils/
      ├─ mapper
      ├─ relationships
      └─ schema
                    │
                    ▼
          [20-22 arquivos]
          [0 redundâncias]
          [0 vazios]
          [0 orphaned]
          [0 dependências falta]
          
    * = consolidado


CRONOGRAMA VISUAL
═══════════════════════════════════════════════════════════

HOJE                    SEMANA 1                SEMANA 2-4
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ 30 min       │      │ 3-4 horas    │      │ 6-8 horas    │
│              │      │              │      │              │
│ ✓ Remove 5   │      │ ✓ DB refactor│      │ ✓ app.py     │
│ ✓ Add fpdf2  │      │ ✓ ML integr  │      │ ✓ Factory    │
│ ✓ Test OK    │  →   │ ✓ NLP integr │  →   │ ✓ Testes     │
│ RISK: VERY   │      │ RISK: MEDIUM │      │ RISK: HIGH   │
│ LOW          │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
     FASE 1               FASE 4                 FASE 5
  (Go now!)        (Esta semana)          (Próximas semanas)


COMPARAÇÃO ANTES vs DEPOIS
═══════════════════════════════════════════════════════════

MÉTRICA                          ANTES        DEPOIS        MELHORIA
────────────────────────────────────────────────────────────────────
Arquivos Python                    36           22            -39%
Redundâncias                        3            0            -100%
Arquivos vazios                     2            0            -100%
Módulos orphaned                    3            0            -100%
Linhas app.py                      600          300           -50%
LOC total (core)                 3500         3000           -14%
Dependências faltando               1            0            -100%
Manutenibilidade                   --            +25%
Onboarding novo dev                --           -40% tempo
Complexidade (Cyclomatic)          --           -20%
Test coverage                      --           +30%
```

---

## 🎨 Legenda

| Símbolo | Significado |
|---------|------------|
| ✅ | Funcionando, manter |
| ❌ | Remover |
| ⚠️ | Revisar, decidir ação |
| * | Consolidado/Alterado |
| DUPLIC | Exatamente o mesmo que outro |
| ORPHAN | Não é importado/usado |
| FRAG | Fragmentado, pode consolidar |
| EMPTY | Arquivo vazio |
| INCOMP | Código incompleto |

---

**Versão:** 1.0  
**Data:** 2026-05-18
