import pytest
from app.services import gastos as gastos_service
from app.services.gastos import LimiteExcedidoError, CategoriaInvalidaError


class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
        gasto_dict = {
            "id": len(self._gastos) + 1,
            "descripcion": descripcion,
            "monto": monto,
            "categoria": categoria,
        }
        # Registro interno con usuario_id para soporte de aislamiento multiusuario
        self._gastos.append({**gasto_dict, "usuario_id": usuario_id})
        return gasto_dict

    def listar(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        propios = [
            {"id": g["id"], "descripcion": g["descripcion"], "monto": g["monto"], "categoria": g["categoria"]}
            for g in self._gastos
            if g.get("usuario_id") == usuario_id or g.get("usuario_id") is None
        ]
        return propios[skip: skip + limit]

    def total_por_categoria(self, db, usuario_id: int, categoria: str) -> float:
        return self._total_inicial + sum(
            g["monto"]
            for g in self._gastos
            if g["categoria"] == categoria and (g.get("usuario_id") == usuario_id or g.get("usuario_id") is None)
        )


def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto(None, 1, "Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar(None, 1) == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", -5.0, "comida", repo=RepositorioFalso())

    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", 0.0, "comida", repo=RepositorioFalso())

    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "", 10.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto(None, 1, "Cine", 20.0, "categoria-inventada", repo=RepositorioFalso())


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto(None, 1, "Cena cara", 50.0, "comida", repo=repo)


def test_listar_gastos_con_repositorio_falso():
    repo = RepositorioFalso()
    gastos_service.registrar_gasto(None, 1, "Almuerzo", 12.50, "comida", repo=repo)
    gastos_service.registrar_gasto(None, 1, "Cena", 25.00, "comida", repo=repo)

    gastos = gastos_service.listar_gastos(None, 1, skip=0, limit=10, repo=repo)
    assert len(gastos) == 2
