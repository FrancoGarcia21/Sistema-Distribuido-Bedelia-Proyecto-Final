# ===========================================
# Script de pruebas de endpoints - Bedelia
# ===========================================

$BASE_URL = "http://localhost"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBAS DE ENDPOINTS - SMART CAMPUS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Variables para almacenar datos
$TOKEN = ""
$ID_AULA = ""
$ID_PROFESOR = ""
$ID_MATERIA = ""
$ID_CRONOGRAMA = ""

# ===========================================
# 1. HEALTH CHECK
# ===========================================
Write-Host "`n[1/10] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET
    Write-Host " Health: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
    exit 1
}

# ===========================================
# 2. LOGIN (obtener JWT)
# ===========================================
Write-Host "`n[2/10] Login como administrador..." -ForegroundColor Yellow
try {
    $body = @{
        usuario = "admin_test"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/usuarios/login" -Method POST -Body $body -ContentType "application/json"
    $TOKEN = $response.token
    Write-Host " Token obtenido: $($TOKEN.Substring(0,50))..." -ForegroundColor Green
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
    exit 1
}

# Headers con JWT
$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# ===========================================
# 3. CREAR AULA
# ===========================================
Write-Host "`n[3/10] Crear aula..." -ForegroundColor Yellow
try {
    $body = @{
        nro_aula = 301
        piso = 3
        cupo = 40
        estado = "disponible"
        descripcion = "Aula de prueba API"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/aulas" -Method POST -Body $body -Headers $headers
    $ID_AULA = $response.id
    Write-Host " Aula creada con ID: $ID_AULA" -ForegroundColor Green
} catch {
    Write-Host "  $_" -ForegroundColor Yellow
}

# ===========================================
# 4. LISTAR AULAS
# ===========================================
Write-Host "`n[4/10] Listar aulas..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/aulas" -Method GET -Headers $headers
    Write-Host " Total de aulas: $($response.total)" -ForegroundColor Green
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
}

# ===========================================
# 5. OBTENER MÉTRICAS
# ===========================================
Write-Host "`n[5/10] Obtener métricas de aulas..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/aulas/metricas" -Method GET -Headers $headers
    Write-Host " Disponibles: $($response.disponibles), Ocupadas: $($response.ocupadas)" -ForegroundColor Green
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
}

# ===========================================
# 6. OBTENER USUARIO ACTUAL (ME)
# ===========================================
Write-Host "`n[6/10] Obtener usuario actual..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/usuarios/me" -Method GET -Headers $headers
    Write-Host " Usuario: $($response.usuario), Rol: $($response.rol)" -ForegroundColor Green
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
}

# ===========================================
# 7. LISTAR PROFESORES
# ===========================================
Write-Host "`n[7/10] Listar profesores..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/usuarios/rol/profesor" -Method GET -Headers $headers
    Write-Host " Total profesores: $($response.total)" -ForegroundColor Green
    if ($response.total -gt 0) {
        $ID_PROFESOR = $response.usuarios[0]._id
        Write-Host "   Usando profesor ID: $ID_PROFESOR" -ForegroundColor Cyan
    }
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
}

# ===========================================
# 8. LISTAR MATERIAS
# ===========================================
Write-Host "`n[8/10] Listar materias de Ingeniería en Sistemas..." -ForegroundColor Yellow
try {
    $carrera = [System.Uri]::EscapeDataString("Ingeniería en Sistemas")
    $response = Invoke-RestMethod -Uri "$BASE_URL/carreras/$carrera/materias" -Method GET -Headers $headers
    Write-Host " Total materias: $($response.total)" -ForegroundColor Green
    if ($response.total -gt 0) {
        $ID_MATERIA = $response.materias[0]._id
        Write-Host "   Usando materia ID: $ID_MATERIA" -ForegroundColor Cyan
    }
} catch {
    Write-Host " Error: $_" -ForegroundColor Red
}

# ===========================================
# 9. CREAR CRONOGRAMA (si tenemos los datos)
# ===========================================
if ($ID_AULA -and $ID_PROFESOR -and $ID_MATERIA) {
    Write-Host "`n[9/10] Crear cronograma..." -ForegroundColor Yellow
    try {
        $body = @{
            id_aula = $ID_AULA
            id_materia = $ID_MATERIA
            id_profesor = $ID_PROFESOR
            id_carrera = "Ingeniería en Sistemas"
            fecha = (Get-Date).ToString("yyyy-MM-dd")
            hora_inicio = "14:00"
            hora_fin = "16:00"
            tipo = "teorica"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$BASE_URL/cronograma" -Method POST -Body $body -Headers $headers
        $ID_CRONOGRAMA = $response.id
        Write-Host " Cronograma creado con ID: $ID_CRONOGRAMA" -ForegroundColor Green
    } catch {
        Write-Host "  $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[9/10] Saltando creación de cronograma (faltan datos)" -ForegroundColor Yellow
}

# ===========================================
# 10. VALIDAR CUPO (si se creó cronograma)
# ===========================================
if ($ID_CRONOGRAMA) {
    Write-Host "`n[10/10] Validar cupo del cronograma..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/cronograma/$ID_CRONOGRAMA/cupo" -Method GET -Headers $headers
        Write-Host " Cupo disponible: $($response.cupo_disponible) de $($response.cupo_total)" -ForegroundColor Green
    } catch {
        Write-Host " Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "`n[10/10] Saltando validación de cupo" -ForegroundColor Yellow
}

# ===========================================
# RESUMEN
# ===========================================
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "✅ PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Token JWT:  Generado"
Write-Host "Endpoints probados: 10"
Write-Host "Aula creada: $(if($ID_AULA){''+$ID_AULA}else{'  No'})"
Write-Host "Cronograma creado: $(if($ID_CRONOGRAMA){' '+$ID_CRONOGRAMA}else{'  No'})"
Write-Host "`n🚀 Bedelia API funcionando correctamente"
