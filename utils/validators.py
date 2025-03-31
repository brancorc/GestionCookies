def validar_numero(valor_str, tipo='float', permitir_cero=True, permitir_vacio=False):
    """Valida si una cadena puede convertirse a float o int."""
    if permitir_vacio and not str(valor_str).strip():
        return 0.0 if tipo == 'float' else 0
    try:
        valor_str = str(valor_str).strip()
        if tipo == 'float':
            valor = float(valor_str)
        else:  # int
            valor = int(valor_str)

        if not permitir_cero and valor == 0:
            return None
        return valor
    except (ValueError, TypeError):
        return None 