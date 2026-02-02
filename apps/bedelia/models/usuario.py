"""
Modelo: Usuario
Gestiona usuarios (administrador, profesor, alumno)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import bcrypt


class UsuarioModel:
    """
    Modelo de Usuario con autenticación y roles
    """
    
    ROLES_VALIDOS = ["administrador", "profesor", "alumno"]
    
    @staticmethod
    def validar_datos(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de entrada para crear/actualizar un usuario
        
        Args:
            data: Diccionario con los datos del usuario
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado y sanitizado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        # Validaciones obligatorias para creación
        if not es_actualizacion:
            if "usuario" not in data or not data["usuario"].strip():
                errores.append("Campo 'usuario' es obligatorio")
            
            if "nombre" not in data or not data["nombre"].strip():
                errores.append("Campo 'nombre' es obligatorio")
            
            if "email" not in data or not data["email"].strip():
                errores.append("Campo 'email' es obligatorio")
            elif "@" not in data["email"]:
                errores.append("'email' debe ser válido")
            
            if "password" not in data or len(data["password"]) < 6:
                errores.append("'password' debe tener al menos 6 caracteres")
            
            if "rol" not in data:
                errores.append("Campo 'rol' es obligatorio")
        
        # Validación de rol (si está presente)
        if "rol" in data:
            if data["rol"] not in UsuarioModel.ROLES_VALIDOS:
                errores.append(f"'rol' debe ser uno de: {', '.join(UsuarioModel.ROLES_VALIDOS)}")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        # Construir documento validado
        documento = {}
        
        if not es_actualizacion:
            # Hash de contraseña
            password_hash = bcrypt.hashpw(
                data["password"].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            documento = {
                "usuario": data["usuario"].strip().lower(),
                "nombre": data["nombre"].strip(),
                "email": data["email"].strip().lower(),
                "password_hash": password_hash,
                "rol": data["rol"],
                "activo": data.get("activo", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            # Actualización parcial
            if "nombre" in data:
                documento["nombre"] = data["nombre"].strip()
            if "email" in data:
                if "@" not in data["email"]:
                    raise ValueError("'email' debe ser válido")
                documento["email"] = data["email"].strip().lower()
            if "password" in data:
                if len(data["password"]) < 6:
                    raise ValueError("'password' debe tener al menos 6 caracteres")
                documento["password_hash"] = bcrypt.hashpw(
                    data["password"].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
            if "rol" in data:
                if data["rol"] not in UsuarioModel.ROLES_VALIDOS:
                    raise ValueError(f"'rol' debe ser uno de: {', '.join(UsuarioModel.ROLES_VALIDOS)}")
                documento["rol"] = data["rol"]
            if "activo" in data:
                documento["activo"] = bool(data["activo"])
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices(coleccion):
        """
        Crea los índices necesarios para la colección usuarios
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único para usuario
        coleccion.create_index(
            [("usuario", 1)],
            unique=True,
            name="idx_usuario_unique"
        )
        
        # Índice único para email
        coleccion.create_index(
            [("email", 1)],
            unique=True,
            name="idx_email_unique"
        )
        
        # Índice para búsquedas por rol
        coleccion.create_index(
            [("rol", 1)],
            name="idx_rol"
        )
        
        # Índice compuesto para usuarios activos por rol
        coleccion.create_index(
            [("rol", 1), ("activo", 1)],
            name="idx_rol_activo"
        )
    
    @staticmethod
    def crear(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Crea un usuario en la base de datos
        
        Args:
            coleccion: Colección MongoDB
            data: Datos del usuario
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos
            DuplicateKeyError: Si ya existe el usuario o email
        """
        documento = UsuarioModel.validar_datos(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError as e:
            if "usuario" in str(e):
                raise ValueError(f"El usuario '{data['usuario']}' ya existe")
            elif "email" in str(e):
                raise ValueError(f"El email '{data['email']}' ya está registrado")
            else:
                raise ValueError("Ya existe un usuario con esos datos")
    
    @staticmethod
    def autenticar(coleccion, usuario: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario por usuario y contraseña
        
        Args:
            coleccion: Colección MongoDB
            usuario: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Documento del usuario si las credenciales son correctas, None si no
        """
        user_doc = coleccion.find_one({
            "usuario": usuario.strip().lower(),
            "activo": True
        })
        
        if not user_doc:
            return None
        
        # Verificar contraseña
        if bcrypt.checkpw(password.encode('utf-8'), user_doc["password_hash"].encode('utf-8')):
            return user_doc
        
        return None
    
    @staticmethod
    def obtener_por_id(coleccion, id_usuario: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID
        
        Args:
            coleccion: Colección MongoDB
            id_usuario: ObjectId del usuario
            
        Returns:
            Documento del usuario (sin password_hash) o None si no existe
        """
        return coleccion.find_one(
            {"_id": id_usuario},
            {"password_hash": 0}  # Excluir hash de contraseña
        )
    
    @staticmethod
    def obtener_por_usuario(coleccion, usuario: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por nombre de usuario
        
        Args:
            coleccion: Colección MongoDB
            usuario: Nombre de usuario
            
        Returns:
            Documento del usuario (sin password_hash) o None si no existe
        """
        return coleccion.find_one(
            {"usuario": usuario.strip().lower()},
            {"password_hash": 0}
        )
    
    @staticmethod
    def listar_por_rol(coleccion, rol: str, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista usuarios por rol
        
        Args:
            coleccion: Colección MongoDB
            rol: Rol a filtrar
            solo_activos: Si True, solo devuelve usuarios activos
            
        Returns:
            Lista de usuarios (sin password_hash)
        """
        query = {"rol": rol}
        if solo_activos:
            query["activo"] = True
        
        return list(coleccion.find(query, {"password_hash": 0}).sort("nombre", 1))
    
    @staticmethod
    def actualizar(coleccion, id_usuario: ObjectId, data: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario existente
        
        Args:
            coleccion: Colección MongoDB
            id_usuario: ObjectId del usuario
            data: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si los datos no son válidos o el usuario no existe
        """
        documento = UsuarioModel.validar_datos(data, es_actualizacion=True)
        
        resultado = coleccion.update_one(
            {"_id": id_usuario},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró el usuario con ID {id_usuario}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def desactivar(coleccion, id_usuario: ObjectId) -> bool:
        """
        Desactiva un usuario (soft delete)
        
        Args:
            coleccion: Colección MongoDB
            id_usuario: ObjectId del usuario
            
        Returns:
            True si se desactivó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_usuario},
            {
                "$set": {
                    "activo": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return resultado.modified_count > 0
