def calcular_imposto(volume, lucro):
    imposto_normal = lucro * 0.25
    imposto_minimo = volume * 0.01
    
    return max(imposto_normal, imposto_minimo)