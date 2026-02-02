"""
UsuarioService - Lógica de negocio para gestión de usuarios
Incluye: CRUD, autenticación, generación JWT
"""

from typing import List, Dict, Any, Optional
from bson import ObjectId

from db.mongo import get_mongo_db
from models.usuario import UsuarioModel
from utils.validators import Validators
from utils.jwt_helper import JWTHelper


class UsuarioService:
    """
    Service para gestión de usuarios y autenticación
    """
    
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.usuarios
    
    def crear_usuario(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un usuario nuevo
        
        Args:
            data: Datos del usuario (usuario, nombre, email, password, rol)
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si los datos son inválidos o el usuario ya existe
        """
        try:
            # Validar email
            if not Validators.validar_email(data.get("email", "")):
                raise ValueError("Email inválido")
            
            # Validar rol
            if not Validators.validar_rol_usuario(data.get("rol", "")):
                raise ValueError("Rol inválido")
            
            # Crear usuario en MongoDB
            id_usuario = UsuarioModel.crear(self.collection, data)
            
            return {
                "id": str(id_usuario),
                "mensaje": "Usuario creado correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear usuario: {e}")
    
    def autenticar(self, usuario: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario y genera JWT
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Diccionario con token JWT y datos del usuario
        
        Raises:
            ValueError: Si las credenciales son incorrectas
        """
        try:
            # Autenticar
            user_doc = UsuarioModel.autenticar(self.collection, usuario, password)
            
            if not user_doc:
                raise ValueError("Credenciales incorrectas")
            
            # Generar JWT
            token = JWTHelper.generar_token(user_doc)
            
            return {
                "token": token,
                "usuario": {
                    "id": str(user_doc["_id"]),
                    "usuario": user_doc["usuario"],
                    "nombre": user_doc["nombre"],
                    "email": user_doc["email"],
                    "rol": user_doc["rol"]
                },
                "expira_en": f"{JWTHelper.EXPIRATION_MINUTES} minutos"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al autenticar: {e}")
    
    def obtener_usuario(self, id_usuario: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por ID (sin password_hash)
        
        Args:
            id_usuario: ID del usuario
        
        Returns:
            Diccionario con datos del usuario o None
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_usuario)
            usuario = UsuarioModel.obtener_por_id(self.collection, obj_id)
            
            if usuario:
                usuario["_id"] = str(usuario["_id"])
            
            return usuario
        
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def listar_por_rol(self, rol: str, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista usuarios por rol
        
        Args:
            rol: Rol a filtrar ("administrador", "profesor", "alumno")
            solo_activos: Si True, solo devuelve usuarios activos
        
        Returns:
            Lista de usuarios
        """
        try:
            usuarios = UsuarioModel.listar_por_rol(self.collection, rol, solo_activos)
            
            # Convertir ObjectIds a strings
            for usuario in usuarios:
                usuario["_id"] = str(usuario["_id"])
            
            return usuarios
        
        except Exception as e:
            print(f"Error al listar usuarios: {e}")
            return []
    
    def actualizar_usuario(self, id_usuario: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un usuario existente
        
        Args:
            id_usuario: ID del usuario
            data: Datos a actualizar (nombre, email, password, rol, activo)
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si el usuario no existe o los datos son inválidos
        """
        try:
            # Validar email si está presente
            if "email" in data and not Validators.validar_email(data["email"]):
                raise ValueError("Email inválido")
            
            # Validar rol si está presente
            if "rol" in data and not Validators.validar_rol_usuario(data["rol"]):
                raise ValueError("Rol inválido")
            
            obj_id = Validators.convertir_a_objectid(id_usuario)
            
            # Actualizar en MongoDB
            UsuarioModel.actualizar(self.collection, obj_id, data)
            
            return {"mensaje": "Usuario actualizado correctamente"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al actualizar usuario: {e}")
    
    def desactivar_usuario(self, id_usuario: str) -> Dict[str, Any]:
        """
        Desactiva un usuario (soft delete)
        
        Args:
            id_usuario: ID del usuario
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_usuario)
            
            # Desactivar en MongoDB
            UsuarioModel.desactivar(self.collection, obj_id)
            
            return {"mensaje": "Usuario desactivado correctamente"}
        
        except Exception as e:
            raise Exception(f"Error al desactivar usuario: {e}")
    
    def cambiar_password(self, id_usuario: str, password_actual: str, password_nueva: str) -> Dict[str, Any]:
        """
        Cambia la contraseña de un usuario
        
        Args:
            id_usuario: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Contraseña nueva
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si la contraseña actual es incorrecta
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_usuario)
            
            # Obtener usuario
            usuario = self.collection.find_one({"_id": obj_id})
            
            if not usuario:
                raise ValueError("Usuario no encontrado")
            
            # Verificar contraseña actual
            import bcrypt
            if not bcrypt.checkpw(password_actual.encode('utf-8'), usuario["password_hash"].encode('utf-8')):
                raise ValueError("Contraseña actual incorrecta")
            
            # Validar nueva contraseña
            if len(password_nueva) < 6:
                raise ValueError("La contraseña nueva debe tener al menos 6 caracteres")
            
            # Actualizar contraseña
            UsuarioModel.actualizar(self.collection, obj_id, {"password": password_nueva})
            
            return {"mensaje": "Contraseña actualizada correctamente"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al cambiar contraseña: {e}")
