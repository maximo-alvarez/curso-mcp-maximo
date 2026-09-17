from app.utils.validadores import categoria_valida, CATEGORIAS_PERMITIDAS


def test_validador_categorias_permitidas():
    assert "comida" in CATEGORIAS_PERMITIDAS
    assert "transporte" in CATEGORIAS_PERMITIDAS
    assert "entretenimiento" in CATEGORIAS_PERMITIDAS
    assert "otros" in CATEGORIAS_PERMITIDAS

    for cat in CATEGORIAS_PERMITIDAS:
        assert categoria_valida(cat) is True

    assert categoria_valida("categoria-inventada") is False
    assert categoria_valida("") is False
    assert categoria_valida("COMIDA") is False
