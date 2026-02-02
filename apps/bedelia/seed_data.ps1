$BASE_URL = "http://localhost/"

Write-Host "`n=========================================="
Write-Host "SEEDING DATOS DE PRUEBA - BEDELIA"
Write-Host "==========================================`n"

# ========== PASO 1: LOGIN ==========
Write-Host "[1/5] Login como administrador..."
try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/usuarios/login" -Method POST `
        -Body (@{
            usuario = "admin_test"
            password = "admin123"
        } | ConvertTo-Json) `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    $token = $loginResponse.token
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    Write-Host "Token obtenido`n"
} catch {
    Write-Host "Error en login: $_"
    exit 1
}

# ========== PASO 2: CREAR AULAS ==========
Write-Host "[2/5] Creando aulas de prueba..."

$aulas = @(
    @{
        nro_aula = 101
        piso = 1
        cupo = 40
        estado = "disponible"
        descripcion = "Aula de teoria con proyector"
    },
    @{
        nro_aula = 201
        piso = 2
        cupo = 30
        estado = "disponible"
        descripcion = "Aula de teoria estandar"
    },
    @{
        nro_aula = 301
        piso = 3
        cupo = 25
        estado = "disponible"
        descripcion = "Laboratorio de computacion"
    }
)

$aulasCreadas = @()

foreach ($aula in $aulas) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/aulas" -Method POST `
            -Headers $headers `
            -Body ($aula | ConvertTo-Json) `
            -ErrorAction Stop
        
        $aulasCreadas += $response.id
        Write-Host "   Aula $($aula.nro_aula) creada - ID: $($response.id)"
    } catch {
        try {
            $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "   Aula $($aula.nro_aula) - $($errorMessage.error)"
        } catch {
            Write-Host "   Aula $($aula.nro_aula) - Error desconocido"
        }
    }
}

Write-Host ""

# ========== PASO 3: CREAR MATERIAS ==========
Write-Host "[3/5] Creando materias..."

# IMPORTANTE: El campo 'carrera' debe ser EXACTO para que la busqueda funcione
$nombreCarrera = "Ingenieria en Sistemas"

$materias = @(
    @{
        carrera = $nombreCarrera
        materia = "Sistemas Distribuidos"
        codigo_materia = "ING-401"
        anio = 4
        cuatrimestre = 1
        carga_horaria = 6
        activa = $true
    },
    @{
        carrera = $nombreCarrera
        materia = "Bases de Datos II"
        codigo_materia = "ING-302"
        anio = 3
        cuatrimestre = 2
        carga_horaria = 6
        activa = $true
    },
    @{
        carrera = $nombreCarrera
        materia = "Inteligencia Artificial"
        codigo_materia = "ING-501"
        anio = 5
        cuatrimestre = 1
        carga_horaria = 8
        activa = $true
    },
    @{
        carrera = $nombreCarrera
        materia = "Arquitectura de Software"
        codigo_materia = "ING-402"
        anio = 4
        cuatrimestre = 2
        carga_horaria = 6
        activa = $true
    },
    @{
        carrera = $nombreCarrera
        materia = "Seguridad Informatica"
        codigo_materia = "ING-403"
        anio = 4
        cuatrimestre = 1
        carga_horaria = 4
        activa = $true
    }
)

$materiasCreadas = @()

foreach ($materia in $materias) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/carreras/materias" -Method POST `
            -Headers $headers `
            -Body ($materia | ConvertTo-Json) `
            -ErrorAction Stop
        
        $materiasCreadas += @{
            id = $response.id
            nombre = $materia.materia
            codigo = $materia.codigo_materia
        }
        Write-Host "   $($materia.materia) - ID: $($response.id)"
    } catch {
        try {
            $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "   $($materia.materia) - $($errorMessage.error)"
        } catch {
            Write-Host "   $($materia.materia) - Error desconocido"
        }
    }
}

Write-Host ""

# ========== PASO 4: OBTENER PROFESOR ==========
Write-Host "[4/5] Obteniendo profesor de prueba..."

try {
    $profesores = Invoke-RestMethod -Uri "$BASE_URL/usuarios/rol/profesor" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    if ($profesores.usuarios.Count -gt 0) {
        $idProfesor = $profesores.usuarios[0]._id
        Write-Host "Profesor encontrado - ID: $idProfesor`n"
    } else {
        Write-Host "No hay profesores disponibles. Crea uno primero.`n"
        $idProfesor = $null
    }
} catch {
    Write-Host "Error obteniendo profesores: $_`n"
    $idProfesor = $null
}

# ========== PASO 5: ASIGNAR PROFESOR A MATERIAS ==========
if ($idProfesor -and $materiasCreadas.Count -gt 0) {
    Write-Host "[5/5] Asignando profesor a materias..."
    
    $asignacionesExitosas = 0
    
    foreach ($materia in $materiasCreadas) {
        try {
            $body = @{
                id_profesor = $idProfesor
                id_materia = $materia.id
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "$BASE_URL/carreras/materias/asignar-profesor" -Method POST `
                -Headers $headers `
                -Body $body `
                -ErrorAction Stop
            
            Write-Host "   $($materia.nombre) asignada al profesor"
            $asignacionesExitosas++
        } catch {
            try {
                $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
                Write-Host "   $($materia.nombre) - $($errorMessage.error)"
            } catch {
                Write-Host "   $($materia.nombre) - Error desconocido"
            }
        }
    }
    
    Write-Host ""
} else {
    Write-Host "[5/5] Saltando asignacion de profesor (no hay profesor o materias)`n"
    $asignacionesExitosas = 0
}

# ========== RESUMEN ==========
Write-Host "=========================================="
Write-Host "SEEDING COMPLETADO"
Write-Host "==========================================`n"

Write-Host "Resumen:"
Write-Host "   Aulas creadas: $($aulasCreadas.Count)"
Write-Host "   Materias creadas: $($materiasCreadas.Count)"
Write-Host "   Asignaciones profesor-materia: $asignacionesExitosas"
Write-Host "   Carrera: $nombreCarrera"

if ($materiasCreadas.Count -gt 0) {
    Write-Host "`nMaterias creadas:"
    foreach ($materia in $materiasCreadas) {
        Write-Host "   - $($materia.nombre) [$($materia.codigo)]"
    }
}

Write-Host "`nAhora puedes ejecutar test_endpoints.ps1"
Write-Host "   powershell -ExecutionPolicy Bypass -File .\test_endpoints.ps1"
Write-Host ""