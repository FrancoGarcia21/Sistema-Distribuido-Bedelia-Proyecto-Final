# Script para vincular materias a la carrera Ingeniería en Sistemas

$BASE_URL = "http://localhost/api"

Write-Host "`n=========================================="
Write-Host "🔗 VINCULANDO MATERIAS A CARRERA"
Write-Host "==========================================`n"

# Login
Write-Host "[1/3] Login..."
$loginResponse = Invoke-RestMethod -Uri "$BASE_URL/usuarios/login" -Method POST -Body (@{
    usuario = "admin_test"
    password = "admin123"
} | ConvertTo-Json) -ContentType "application/json"

$token = $loginResponse.token
Write-Host "✅ Token obtenido`n"

# Obtener ID de la carrera
Write-Host "[2/3] Obteniendo ID de carrera 'Ingeniería en Sistemas'..."
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    # Suponiendo que hay un endpoint para obtener carreras
    # Si no existe, necesitarías crear la carrera primero
    
    Write-Host "⚠️  Nota: Necesitas crear la carrera 'Ingeniería en Sistemas' primero"
    Write-Host "    Endpoint: POST /carreras"
    Write-Host "    Body: { \"nombre\": \"Ingeniería en Sistemas\", \"codigo\": \"ING\", \"duracion_anios\": 5 }"
    
} catch {
    Write-Host "❌ Error: $_"
}

Write-Host "`n=========================================="
Write-Host "ℹ️  ACCIÓN REQUERIDA"
Write-Host "==========================================`n"
Write-Host "Para que el endpoint GET /carreras/{carrera}/materias funcione:"
Write-Host "1. Las materias deben tener un campo 'carrera' o 'id_carrera'"
Write-Host "2. O debe existir una colección de relación carrera-materia"
Write-Host "`nRevisa tu modelo de datos actual."

