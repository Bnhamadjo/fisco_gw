"""
Field Adapter - Sistema Inteligente de Adaptação de Campos
============================================================
Detecta automaticamente campos disponíveis e adapta análises
sem falhar quando campos são omitidos.
"""

import pandas as pd
import difflib
import unicodedata
import re
from typing import Dict, List, Tuple, Optional

class FieldAdapter:
    """
    Adaptador inteligente de campos que:
    1. Detecta campos disponíveis no arquivo
    2. Mapeia para campos esperados (fuzzy matching)
    3. Indica quais análises podem ser realizadas
    4. Fornece fallbacks para campos faltando
    """
    
    # Campos primários esperados (em ordem de importância)
    PRIMARY_FIELDS = {
        "nif_cliente": ["nif do declarante", "nif cliente", "nif do cliente", "nif comprador", "01.nif", "nif"],
        "nif_fornecedor": ["nif do fornecedor", "nif fornecedor", "nif prestador", "3.1 nif"],
        "valor": ["base tributavel", "valor total", "total base", "valor sem iva", "montante liquido", "valor"],
        "data": ["data da fatura", "data da factura", "data de emissao", "data emissao", "data"],
        "fatura": ["numero de fatura", "numero fatura", "fatura numero", "fatura n", "fatura"],
        "cliente": ["nome do declarante", "nome cliente", "cliente name", "cliente", "comprador"],
        "fornecedor": ["nome do fornecedor", "nome fornecedor", "fornecedor name", "fornecedor"],
        "iva_suportado": ["iva suportado", "iva dedutivel", "iva debito", "3.7 iva suportado"],
        "iva_liquidado": ["iva liquidado", "iva credito"],
    }
    
    # Análises e seus requisitos
    ANALYSES_REQUIREMENTS = {
        "benford": {"required": ["valor"], "optional": []},
        "outliers": {"required": ["valor"], "optional": []},
        "duplicates": {"required": ["valor"], "optional": ["cliente", "fornecedor"]},
        "suspicious_top": {"required": ["valor"], "optional": ["cliente"]},
        "invalid_values": {"required": ["valor"], "optional": []},
        "network": {"required": ["cliente", "fornecedor"], "optional": ["valor"]},
        "risk_score": {"required": ["valor"], "optional": ["cliente"]},
        "temporal": {"required": ["data", "valor"], "optional": []},
        "bilateral": {"required": ["cliente", "fornecedor", "valor"], "optional": []},
        "flow_matrix": {"required": ["cliente", "fornecedor", "valor"], "optional": []},
    }
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o adaptador com um dataframe"""
        self.df = df
        self.original_columns = list(df.columns)
        self.available_fields = {}
        self.field_mapping = {}
        self.available_analyses = {}
        self.confidence_scores = {}
        
        # Executar análise
        self._detect_fields()
        self._evaluate_analyses()
    
    @staticmethod
    def _clean_string(s: str) -> str:
        """Normaliza string para comparação"""
        if not isinstance(s, str):
            return str(s)
        # Remove acentos
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        s = s.lower().strip()
        # Remove caracteres especiais
        s = re.sub(r'[^a-z0-9\s]', ' ', s)
        return ' '.join(s.split())
    
    def _detect_fields(self):
        """Detecta campos disponíveis com fuzzy matching"""
        available_cols = [self._clean_string(col) for col in self.original_columns]
        used_indices = set()
        
        # Para cada campo esperado, encontrar melhor match
        for field_name, keywords in self.PRIMARY_FIELDS.items():
            best_match = None
            best_score = 0
            best_idx = -1
            
            for idx, col in enumerate(available_cols):
                if idx in used_indices:
                    continue
                
                for keyword in keywords:
                    clean_kw = self._clean_string(keyword)
                    
                    # Exact match
                    if col == clean_kw:
                        score = 100
                    # Contains
                    elif clean_kw in col or col in clean_kw:
                        score = 80
                    # Fuzzy matching
                    else:
                        ratio = difflib.SequenceMatcher(None, clean_kw, col).ratio()
                        score = ratio * 70
                    
                    if score > best_score and score > 60:
                        best_score = score
                        best_match = self.original_columns[idx]
                        best_idx = idx
            
            if best_match:
                self.field_mapping[field_name] = best_match
                self.available_fields[field_name] = best_match
                self.confidence_scores[field_name] = best_score
                used_indices.add(best_idx)
    
    def _evaluate_analyses(self):
        """Avalia quais análises podem ser realizadas"""
        for analysis_name, requirements in self.ANALYSES_REQUIREMENTS.items():
            required = requirements.get("required", [])
            optional = requirements.get("optional", [])
            
            # Verificar se todos os campos obrigatórios estão disponíveis
            has_all_required = all(field in self.available_fields for field in required)
            
            if has_all_required:
                self.available_analyses[analysis_name] = {
                    "available": True,
                    "missing": [],
                    "optional_missing": [f for f in optional if f not in self.available_fields]
                }
            else:
                missing = [f for f in required if f not in self.available_fields]
                self.available_analyses[analysis_name] = {
                    "available": False,
                    "missing": missing,
                    "reason": f"Faltam campos: {', '.join(missing)}"
                }
    
    def can_analyze(self, analysis_name: str) -> Tuple[bool, str]:
        """
        Verifica se uma análise pode ser realizada
        
        Returns:
            (pode_realizar, mensagem)
        """
        if analysis_name not in self.ANALYSES_REQUIREMENTS:
            return False, f"Análise desconhecida: {analysis_name}"
        
        info = self.available_analyses.get(analysis_name, {})
        
        if info.get("available", False):
            optional_missing = info.get("optional_missing", [])
            if optional_missing:
                msg = f"✅ Pode realizar (sem {', '.join(optional_missing)})"
            else:
                msg = "✅ Pode realizar com todos os campos"
            return True, msg
        else:
            reason = info.get("reason", "Campos faltando")
            return False, f"❌ {reason}"
    
    def get_field(self, field_name: str, default=None) -> Optional[str]:
        """Obtém o nome real da coluna para um campo esperado"""
        return self.available_fields.get(field_name, default)
    
    def get_available_fields(self) -> Dict[str, str]:
        """Retorna mapa de campos disponíveis"""
        return self.available_fields.copy()
    
    def get_summary(self) -> str:
        """Gera sumário do que foi detectado"""
        summary = "📊 **Análise de Campos Detectados**\n\n"
        
        if self.available_fields:
            summary += "✅ **Campos Detectados:**\n"
            for field, col in self.available_fields.items():
                conf = self.confidence_scores.get(field, 0)
                summary += f"- `{field}` → `{col}` ({conf:.0f}%)\n"
        else:
            summary += "⚠️ **Nenhum campo específico detectado**\n"
        
        summary += "\n📈 **Análises Disponíveis:**\n"
        available_count = sum(1 for a in self.available_analyses.values() if a.get("available"))
        total_count = len(self.available_analyses)
        
        for analysis, info in self.available_analyses.items():
            if info.get("available"):
                summary += f"- ✅ {analysis}\n"
            else:
                summary += f"- ❌ {analysis} ({info.get('reason')})\n"
        
        summary += f"\n**{available_count}/{total_count}** análises disponíveis\n"
        
        return summary
    
    def adapt_dataframe(self) -> pd.DataFrame:
        """
        Retorna dataframe com campos normalizados (apenas os detectados)
        """
        df = self.df.copy()
        
        # Renomear colunas detectadas para nomes padrão
        rename_map = {}
        for field_name, original_col in self.available_fields.items():
            if original_col in df.columns:
                rename_map[original_col] = field_name
        
        df = df.rename(columns=rename_map)
        
        # Adicionar metadados
        df.attrs['field_adapter'] = {
            'detected_fields': self.available_fields,
            'available_analyses': self.available_analyses,
            'confidence_scores': self.confidence_scores
        }
        
        return df
    
    def get_analysis_recommendation(self) -> str:
        """Recomenda análises prioritárias"""
        recommendations = []
        
        if self.can_analyze("benford")[0]:
            recommendations.append("🔢 **Lei de Benford** - Detecta manipulação de dados")
        
        if self.can_analyze("outliers")[0]:
            recommendations.append("📉 **Outliers Estatísticos** - Identifica valores anormais")
        
        if self.can_analyze("network")[0]:
            recommendations.append("🕸️ **Rede de Transações** - Detecta fraude carrossel")
        
        if self.can_analyze("temporal")[0]:
            recommendations.append("⏰ **Tendências Temporais** - Analisa evolução no tempo")
        
        if not recommendations:
            recommendations.append("⚠️ Estrutura de dados limitada - Análise básica apenas")
        
        return "\n".join(recommendations)


# Função helper para usar facilmente
def create_field_adapter(df: pd.DataFrame) -> FieldAdapter:
    """Factory function para criar adaptador"""
    return FieldAdapter(df)
