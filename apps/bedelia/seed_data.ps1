# ===========================================
# Script para crear datos de prueba
# ===========================================

$BASE_URL = "http://localhost"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🌱 SEEDING DATOS DE PRUEBA - BEDELIA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# ===========================================
# 1. LOGIN
# ===========================================
Write-Host "`n[1/4] Login..." -ForegroundColor Yellow
$body = @{
    usuario = "admin_test"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BASE_URL/usuarios/login" -Method POST -Body $body -ContentType "application/json"
$TOKEN = $response.token
Write-Host "✅ Token obtenido" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# ===========================================
# 2. CREAR MATERIAS
# ===========================================
Write-Host "`n[2/4] Creando materias..." -ForegroundColor Yellow

$materias = @(
    @{
        carrera = "Ingeniería en Sistemas"
        materia = "Sistemas Distribuidos"
        codigo_materia = "ING-401"
        anio = 4
        cuatrimestre = 1
        carga_horaria = 6
    },
    @{
        carrera = "Ingeniería en Sistemas"
        materia = "Bases de Datos II"
        codigo_materia = "ING-402"
        anio = 4
        cuatrimestre = 1
        carga_horaria = 6
    },
    @{
        carrera = "Ingeniería en Sistemas"
        materia = "Inteligencia Artificial"
        codigo_materia = "ING-501"
        anio = 5
        cuatrimestre = 1
        carga_horaria = 8
    }
)

$IDS_MATERIAS = @()

foreach ($mat in $materias) {
    try {
        $body = $mat | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BASE_URL/carreras/materias" -Method POST -Body $body -Headers $headers
        $IDS_MATERIAS += $response.id
        Write-Host "   ✅ $($mat.materia) - ID: $($response.id)" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  $($mat.materia) - $_" -ForegroundColor Yellow
    }
}

# ===========================================
# 3. ASIGNAR PROFESOR A MATERIAS
# ===========================================
Write-Host "`n[3/4] Obteniendo profesor..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/usuarios/rol/profesor" -Method GET -Headers $headers
$ID_PROFESOR = $response.usuarios[0]._id
Write-Host "✅ Profesor ID: $ID_PROFESOR" -ForegroundColor Green

Write-Host "`n[4/4] Asignando profesor a materias..." -ForegroundColor Yellow
foreach ($id_mat in $IDS_MATERIAS) {
    try {
        $body = @{
            id_profesor = $ID_PROFESOR
            id_materia = $id_mat
            carrera = "Ingeniería en Sistemas"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$BASE_URL/carreras/materias/asignar-profesor" -Method POST -Body $body -Headers $headers
        Write-Host "   ✅ Materia asignada: $id_mat" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  $_" -ForegroundColor Yellow
    }
}

# ===========================================
# RESUMEN
# ===========================================
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "✅ SEEDING COMPLETADO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Materias creadas: $($IDS_MATERIAS.Count)"
Write-Host "Asignaciones profesor-materia: $($IDS_MATERIAS.Count)"
Write-Host "`n🚀 Ahora puedes ejecutar test_endpoints.ps1 completo"
