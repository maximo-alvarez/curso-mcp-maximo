from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.usuario import Usuario
from app.models.gasto import Gasto


def test_modelo_usuario_creacion_e_indice():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = Usuario(email="usuario1@test.com", hashed_password="hashed_pw_123")
    session.add(user)
    session.commit()

    saved_user = session.query(Usuario).filter_by(email="usuario1@test.com").first()
    assert saved_user is not None
    assert saved_user.id == 1
    assert saved_user.email == "usuario1@test.com"
    assert saved_user.hashed_password == "hashed_pw_123"

    session.close()


def test_modelo_gasto_fk_usuario():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = Usuario(email="dueno@test.com", hashed_password="hash")
    session.add(user)
    session.commit()

    gasto = Gasto(descripcion="Almuerzo", monto=15.50, categoria="comida", usuario_id=user.id)
    session.add(gasto)
    session.commit()

    saved_gasto = session.query(Gasto).filter_by(id=gasto.id).first()
    assert saved_gasto is not None
    assert saved_gasto.usuario_id == user.id
    assert saved_gasto.monto == 15.50
    assert saved_gasto.categoria == "comida"

    session.close()
