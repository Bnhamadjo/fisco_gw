# 🎓 SISTEMA ADAPTATIVO DE CAMPOS - MANUAL DE TREINAMENTO

## Visão Geral

O FISCO-GW foi treinado com um **Sistema Adaptativo de Campos** que permite que o aplicativo funcione com qualquer estrutura de arquivo fiscal, sem falhar quando campos específicos estão ausentes.

## Como Funciona

### 1. **Detecção Automática de Campos**

Quando um arquivo é carregado, o sistema:

```
1. Examina todas as colunas disponíveis
2. Usa "Fuzzy Matching" para encontrar equivalências
3. Mapeia campos reais → campos esperados
4. Atribui scores de confiança (0-100%)
```

**Exemplo:**
```
Coluna no arquivo        →  Campo Detectado    →  Confiança
"NIF Do Declarante"      →  nif_cliente        →  95%
"Valor da Fatura"        →  valor              →  87%
"Nome Empresa"           →  cliente            →  72%
(coluna ausente)         →  fornecedor         →  ❌ N/A
```

### 2. **Adaptação de Análises**

O sistema avalia quais análises podem ser realizadas:

```
✅ Pode fazer (todos os campos)
 - Lei de Benford
 - Detecção de Outliers
 - Valores Inválidos

⚠️ Pode fazer (campos parciais)
 - Análise Temporal (se tiver "data")
 - Rede (se tiver "cliente" E "fornecedor")

❌ Não pode fazer (faltam campos críticos)
 - Análise Bilateral (requer cliente+fornecedor+valor)
 - Matriz de Fluxos (requer cliente+fornecedor)
```

### 3. **Fallbacks Automáticos**

Se um campo não for encontrado, o sistema:

- **Tenta alternativas**: "valor" → "montante" → "amount"
- **Reduz escopo da análise**: Procura por padrões sem o campo faltando
- **Mantém funcionalidade**: Análises críticas continuam funcionando

**Exemplo:**
```python
# Sem campo "cliente":
Top valores → apenas mostra os valores (sem nome do cliente)

# Sem campo "data":
Análise temporal → desabilitada automaticamente
```

## Campos Esperados

### Primários (Críticos)
- `nif_cliente` - NIF do declarante/comprador
- `nif_fornecedor` - NIF do fornecedor/prestador  
- `valor` - Valor da transação (campo mais importante!)
- `data` - Data da transação

### Secundários (Análises Avançadas)
- `cliente` - Nome da entidade compradora
- `fornecedor` - Nome da entidade vendedora
- `fatura` - Número do documento
- `iva_suportado` - IVA dedutível
- `iva_liquidado` - IVA cobrado

## Equivalências Automáticas

O sistema reconhece automaticamente:

```
Campo Esperado      |  Variações Reconhecidas
==========================================
nif_cliente         |  NIF do declarante, NIF cliente, NIF do cliente,
                    |  NIF comprador, 01.nif

nif_fornecedor      |  NIF do fornecedor, NIF fornecedor,
                    |  NIF prestador, 3.1 nif

valor               |  Base tributável, valor total, montante,
                    |  valor sem iva, valor da fatura

data                |  Data da fatura, data emissão,
                    |  data da factura, data

cliente             |  Nome do declarante, nome cliente,
                    |  cliente name, comprador, entidade

fornecedor          |  Nome do fornecedor, nome prestador,
                    |  fornecedor name, vendedor
```

## Fluxo de Processamento

```
┌─────────────────────┐
│  Arquivo Carregado  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ FieldAdapter Criado │  ← Detecta campos
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Normaliza Colunas   │  ← Renomeia para padrão
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Avalia Análises     │  ← Quais funcionam?
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Exibe Diagnóstico   │  ← Mostra campos encontrados
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Executa Análises    │  ← Usa fallbacks se necessário
│ Disponíveis         │
└─────────────────────┘
```

## Diagnóstico no Dashboard

Quando carrega um arquivo, o usuário vê:

```
🔍 Diagnóstico Automático de Campos

✅ Campos Detectados:
  - nif_cliente → NIF Do Declarante (95%)
  - valor → Valor da Fatura (87%)
  - data → Data da Fatura (90%)
  - cliente → Nome Empresa (72%)

📈 Análises Recomendadas:
  ✅ Lei de Benford
  ✅ Outliers Estatísticos
  ❌ Rede (falta: fornecedor)

⚠️ Campos não detectados: fornecedor, iva_suportado
   O sistema funcionará com análises adaptadas
```

## Exemplos de Uso

### Cenário 1: Arquivo com Campos Completos
```
┌─────────────────────────────────────┐
│ NIF Cliente | NIF Fornecedor | Valor│
│   123456789 |   987654321    | 1000 │
└─────────────────────────────────────┘

Resultado: ✅ Todas as análises habilitadas
```

### Cenário 2: Arquivo sem Fornecedor
```
┌─────────────────────────┐
│ NIF Cliente | Valor     │
│   123456789 | 1000      │
└─────────────────────────┘

Resultado: ⚠️ Análises de rede desabilitadas
          ✅ Análises de valor funcionam
```

### Cenário 3: Arquivo com Nomes Diferentes
```
┌──────────────────────┐
│ Montante | Data Emit │
│   1000   | 2024-05-19│
└──────────────────────┘

Resultado: ✅ Sistema mapeia automaticamente
          "Montante" → valor
          "Data Emit" → data
```

## Configuração Avançada

### Adicionar Novas Variações

Editar `modules/field_adapter.py`:

```python
PRIMARY_FIELDS = {
    "valor": [
        "base tributavel",      # Existentes
        "seu_campo_novo",       # Novo!
        "outra_variacao"        # Novo!
    ]
}
```

### Ajustar Scores de Confiança

```python
def _detect_fields(self):
    # Aumentar threshold mínimo de 60 para 70
    if score > 70:  # Era: > 60
        self.available_fields[field_name] = best_match
```

## Tratamento de Erros

### Se nenhum campo for detectado:
```
⚠️ Estrutura de dados limitada - Análise básica apenas
→ Sistema carrega dados como estão
→ Filtragem simples disponível
→ Exportação funciona normalmente
```

### Se valor não for encontrado:
```
❌ Campo crítico faltando: "valor"
→ Nenhuma análise fiscal pode ser realizada
→ Apenas visualização de dados disponível
```

## Benefícios

✅ **Compatibilidade**: Funciona com qualquer estrutura de arquivo
✅ **Robustez**: Não falha com campos faltando
✅ **Inteligência**: Fuzzy matching encontra campos com nomes diferentes
✅ **Transparência**: Diagnóstico mostra exatamente o que foi detectado
✅ **Fallbacks**: Análises adaptadas ao que está disponível

## Limitações Conhecidas

- ⚠️ Sem campo "valor": nenhuma análise fiscal é possível
- ⚠️ Sem "cliente" + "fornecedor": análise de rede desabilitada
- ⚠️ Sem "data": análise temporal desabilitada
- ⚠️ Campo detectado incorretamente: usuário pode inverter manualmente

## Próximos Passos

1. ✅ Sistema implementado
2. 🔄 Testar com arquivos reais variados
3. 📊 Ajustar scores de detecção conforme necessário
4. 🚀 Documentar casos especiais

---

**Versão:** 1.1  
**Data:** 2026-05-19  
**Status:** ✅ Em Produção
