from vibe_coding.validators import (
    validar_contrasena,
    validar_email,
    registrar_usuario,
    listar_usuarios,
    usuarios,
)
from vibe_coding.api import app, start

def main() -> None:
    print("=== Registro y Gestión de Usuarios ===")
    
    # Intentos de registro
    candidatos = [
        ("ana@correo.com", "Password123!", False),
        ("admin@empresa.org", "123", True),          # Admin con contraseña débil permitida
        ("superadmin@empresa.org", "", True),         # Admin sin contraseña permitida
        ("carlos@empresa.org", "12345", False),       # Usuario estándar con contraseña débil (falla)
    ]

    for email, pwd, es_admin in candidatos:
        rol = "Admin" if es_admin else "Estándar"
        print(f"\nIntentando registrar [{rol}]: {email} / '{pwd}'")
        res = registrar_usuario(email, pwd, es_admin=es_admin)
        if res["exito"]:
            print(f"  ✅ Registrado exitosamente: {res['usuario']['email']} (Admin: {res['usuario']['es_admin']})")
        else:
            print("  ❌ Error al registrar:")
            for err in res["errores"]:
                print(f"    - {err}")

    # Mostrar lista completa de usuarios
    print("\n" + "=" * 45)
    print("=== Lista Completa de Usuarios Registrados ===")
    lista = listar_usuarios()
    if not lista:
        print("No hay usuarios registrados.")
    else:
        for idx, u in enumerate(lista, 1):
            rol_str = "👑 Admin" if u["es_admin"] else "👤 Usuario"
            print(f"{idx}. [{rol_str}] Email: {u['email']} | Password: '{u['password']}'")

if __name__ == "__main__":
    main()
