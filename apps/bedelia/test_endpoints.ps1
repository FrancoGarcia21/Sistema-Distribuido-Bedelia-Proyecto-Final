# ===================================================================
# Script de Pruebas de Endpoints - Bedelia API
# Prueba todos los endpoints principales del sistema
# ===================================================================

$BASE_URL = "http://localhost/"

Write-Host "`n=========================================="
Write-Host "PRUEBAS DE ENDPOINTS - SMART CAMPUS"
Write-Host "==========================================`n"

# Variables para tracking
$endpointsProbados = 0
$endpointsExitosos = 0
$endpointsFallidos = 0

# ========== PASO 1: HEALTH CHECK ==========
$endpointsProbados++
Write-Host "[1/15] Health Check..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost/health" -Method GET -ErrorAction Stop
    Write-Host "   Health: $($health.status)"
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 2: LOGIN ==========
$endpointsProbados++
Write-Host "[2/15] Login como administrador..."
try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/usuarios/login" -Method POST `
        -Body (@{
            usuario = "admin_test"
            password = "admin123"
        } | ConvertTo-Json) `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    $token = $loginResponse.token
    $tokenCorto = $token.Substring(0, 50) + "..."
    Write-Host "   Token obtenido: $tokenCorto"
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
    exit 1
}
Write-Host ""

# ========== PASO 3: CREAR AULA ==========
$endpointsProbados++
Write-Host "[3/15] Crear aula de prueba..."
try {
    $aulaData = @{
        nro_aula = 999
        piso = 9
        cupo = 25
        estado = "disponible"
        descripcion = "Aula de prueba - test_endpoints"
    } | ConvertTo-Json
    
    $aulaResponse = Invoke-RestMethod -Uri "$BASE_URL/aulas" -Method POST `
        -Headers $headers `
        -Body $aulaData `
        -ErrorAction Stop
    
    $idAulaCreada = $aulaResponse.id
    Write-Host "   Aula creada con ID: $idAulaCreada"
    $endpointsExitosos++
} catch {
    try {
        $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "   $($errorMessage.error)"
    } catch {
        Write-Host "   Error desconocido"
    }
    $idAulaCreada = $null
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 4: LISTAR AULAS ==========
$endpointsProbados++
Write-Host "[4/15] Listar aulas..."
try {
    $aulas = Invoke-RestMethod -Uri "$BASE_URL/aulas" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Total de aulas: $($aulas.total)"
    if ($aulas.total -gt 0) {
        Write-Host "   Primeras aulas:"
        $aulas.aulas | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - Aula $($_.nro_aula) | Piso $($_.piso) | Cupo: $($_.cupo) | Estado: $($_.estado)"
        }
    }
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 5: OBTENER AULA ESPECÍFICA ==========
if ($idAulaCreada) {
    $endpointsProbados++
    Write-Host "[5/15] Obtener aula especifica (ID: $idAulaCreada)..."
    try {
        $aula = Invoke-RestMethod -Uri "$BASE_URL/aulas/$idAulaCreada" -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        
        Write-Host "   Aula obtenida: Nro $($aula.nro_aula) - Piso $($aula.piso)"
        $endpointsExitosos++
    } catch {
        Write-Host "   Error: $_"
        $endpointsFallidos++
    }
} else {
    Write-Host "[5/15] Saltando obtencion de aula (no se creo)`n"
}
Write-Host ""

# ========== PASO 6: MÉTRICAS DE AULAS ==========
$endpointsProbados++
Write-Host "[6/15] Obtener metricas de aulas..."
try {
    $metricas = Invoke-RestMethod -Uri "$BASE_URL/aulas/metricas" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Metricas obtenidas:"
    Write-Host "      Total: $($metricas.total_aulas)"
    Write-Host "      Disponibles: $($metricas.disponibles)"
    Write-Host "      Ocupadas: $($metricas.ocupadas)"
    Write-Host "      Deshabilitadas: $($metricas.deshabilitadas)"
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 7: OBTENER USUARIO ACTUAL ==========
$endpointsProbados++
Write-Host "[7/15] Obtener usuario actual..."
try {
    $usuarioActual = Invoke-RestMethod -Uri "$BASE_URL/usuarios/me" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Usuario: $($usuarioActual.usuario)"
    Write-Host "      Rol: $($usuarioActual.rol)"
    Write-Host "      Email: $($usuarioActual.email)"
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 8: LISTAR PROFESORES ==========
$endpointsProbados++
Write-Host "[8/15] Listar profesores..."
try {
    $profesores = Invoke-RestMethod -Uri "$BASE_URL/usuarios/rol/profesor" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Total profesores: $($profesores.usuarios.Count)"
    
    if ($profesores.usuarios.Count -gt 0) {
        $idProfesor = $profesores.usuarios[0]._id
        Write-Host "      Usando profesor ID: $idProfesor"
        Write-Host "      Nombre: $($profesores.usuarios[0].usuario)"
    } else {
        $idProfesor = $null
        Write-Host "      No hay profesores disponibles"
    }
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
    $idProfesor = $null
}
Write-Host ""

# ========== PASO 9: LISTAR MATERIAS DE INGENIERÍA EN SISTEMAS ==========
$endpointsProbados++
Write-Host "[9/15] Listar materias de Ingenieria en Sistemas..."

# IMPORTANTE: Usar el mismo nombre exacto que en el seeding
$nombreCarrera = "Ingenieria en Sistemas"
$carreraEncoded = [uri]::EscapeDataString($nombreCarrera)

try {
    $materias = Invoke-RestMethod -Uri "$BASE_URL/carreras/$carreraEncoded/materias" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Total materias: $($materias.total)"
    
    if ($materias.total -gt 0) {
        Write-Host "   Materias encontradas:"
        $materias.materias | ForEach-Object {
            Write-Host "      - $($_.materia) [$($_.codigo_materia)]"
            Write-Host "        Anio $($_.anio) | Cuatrimestre $($_.cuatrimestre) | $($_.carga_horaria)hs"
        }
        
        # Guardar primera materia para pruebas
        $idMateria = $materias.materias[0]._id
        $nombreMateria = $materias.materias[0].materia
    } else {
        Write-Host "   No hay materias para esta carrera"
        Write-Host "      Ejecuta primero: powershell -ExecutionPolicy Bypass -File .\seed_data.ps1"
        $idMateria = $null
    }
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $idMateria = $null
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 10: OBTENER MATERIA ESPECÍFICA ==========
if ($idMateria) {
    $endpointsProbados++
    Write-Host "[10/15] Obtener materia especifica ($nombreMateria)..."
    try {
        $materia = Invoke-RestMethod -Uri "$BASE_URL/carreras/materias/$idMateria" -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        
        Write-Host "   Materia obtenida:"
        Write-Host "      Carrera: $($materia.carrera)"
        Write-Host "      Materia: $($materia.materia)"
        Write-Host "      Codigo: $($materia.codigo_materia)"
        Write-Host "      Activa: $($materia.activa)"
        $endpointsExitosos++
    } catch {
        Write-Host "   Error: $_"
        $endpointsFallidos++
    }
} else {
    Write-Host "[10/15] Saltando obtencion de materia (no hay materias)`n"
}
Write-Host ""

# ========== PASO 11: LISTAR MATERIAS ASIGNADAS A PROFESOR ==========
if ($idProfesor) {
    $endpointsProbados++
    Write-Host "[11/15] Listar materias asignadas al profesor..."
    try {
        $materiasProfesor = Invoke-RestMethod -Uri "$BASE_URL/carreras/profesor/$idProfesor/materias" -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        
        Write-Host "   Materias asignadas: $($materiasProfesor.total)"
        
        if ($materiasProfesor.total -gt 0) {
            $materiasProfesor.materias | ForEach-Object {
                Write-Host "      - $($_.materia) [$($_.codigo_materia)]"
            }
        }
        $endpointsExitosos++
    } catch {
        Write-Host "   Error: $_"
        $endpointsFallidos++
    }
} else {
    Write-Host "[11/15] Saltando materias de profesor (no hay profesor)`n"
}
Write-Host ""

# ========== PASO 12: CREAR CRONOGRAMA ==========
if ($idAulaCreada -and $idMateria -and $idProfesor) {
    $endpointsProbados++
    Write-Host "[12/15] Crear cronograma..."
    try {
        $fechaInicio = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
        $fechaFin = (Get-Date).AddDays(120).ToString("yyyy-MM-dd")
        
        $cronogramaData = @{
            id_aula = $idAulaCreada
            id_materia = $idMateria
            id_profesor = $idProfesor
            fecha_inicio = $fechaInicio
            fecha_fin = $fechaFin
            hora_inicio = "14:00"
            hora_fin = "18:00"
            dias_semana = @("Lunes", "Miercoles")
            carrera = $nombreCarrera
        } | ConvertTo-Json
        
        $cronogramaResponse = Invoke-RestMethod -Uri "$BASE_URL/cronograma" -Method POST `
            -Headers $headers `
            -Body $cronogramaData `
            -ErrorAction Stop
        
        $idCronograma = $cronogramaResponse.id
        Write-Host "   Cronograma creado: $idCronograma"
        Write-Host "      Fecha: $fechaInicio al $fechaFin"
        Write-Host "      Horario: 14:00 - 18:00"
        Write-Host "      Dias: Lunes, Miercoles"
        $endpointsExitosos++
    } catch {
        try {
            $errorMessage = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "   Error: $($errorMessage.error)"
        } catch {
            Write-Host "   Error desconocido"
        }
        $idCronograma = $null
        $endpointsFallidos++
    }
} else {
    Write-Host "[12/15] Saltando creacion de cronograma (faltan datos)`n"
    $idCronograma = $null
}
Write-Host ""

# ========== PASO 13: LISTAR CRONOGRAMAS ==========
$endpointsProbados++
Write-Host "[13/15] Listar cronogramas..."
try {
    $cronogramas = Invoke-RestMethod -Uri "$BASE_URL/cronograma" -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   Total cronogramas: $($cronogramas.total)"
    
    if ($cronogramas.total -gt 0) {
        Write-Host "   Cronogramas activos:"
        $cronogramas.cronogramas | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - Aula: $($_.id_aula) | Estado: $($_.estado)"
            Write-Host "        $($_.fecha_inicio) al $($_.fecha_fin)"
        }
    }
    $endpointsExitosos++
} catch {
    Write-Host "   Error: $_"
    $endpointsFallidos++
}
Write-Host ""

# ========== PASO 14: VALIDAR CUPO DE CRONOGRAMA ==========
if ($idCronograma) {
    $endpointsProbados++
    Write-Host "[14/15] Validar cupo del cronograma..."
    try {
        $validacionCupo = Invoke-RestMethod -Uri "$BASE_URL/cronograma/$idCronograma/validar-cupo" -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        
        Write-Host "   Validacion de cupo:"
        Write-Host "      Cupo disponible: $($validacionCupo.cupo_disponible)"
        Write-Host "      Capacidad maxima: $($validacionCupo.capacidad_maxima)"
        Write-Host "      Estudiantes inscritos: $($validacionCupo.estudiantes_inscritos)"
        Write-Host "      Puede inscribirse: $($validacionCupo.puede_inscribirse)"
        $endpointsExitosos++
    } catch {
        Write-Host "   Error: $_"
        $endpointsFallidos++
    }
} else {
    Write-Host "[14/15] Saltando validacion de cupo (no hay cronograma)`n"
}
Write-Host ""

# ========== PASO 15: ACTUALIZAR ESTADO DE AULA ==========
if ($idAulaCreada) {
    $endpointsProbados++
    Write-Host "[15/15] Actualizar estado de aula a 'deshabilitada'..."
    try {
        $estadoData = @{
            estado = "deshabilitada"
        } | ConvertTo-Json
        
        $estadoResponse = Invoke-RestMethod -Uri "$BASE_URL/aulas/$idAulaCreada/estado" -Method PATCH `
            -Headers $headers `
            -Body $estadoData `
            -ErrorAction Stop
        
        Write-Host "   $($estadoResponse.mensaje)"
        $endpointsExitosos++
    } catch {
        Write-Host "   Error: $_"
        $endpointsFallidos++
    }
} else {
    Write-Host "[15/15] Saltando actualizacion de estado (no hay aula)`n"
}
Write-Host ""

# ========== RESUMEN FINAL ==========
Write-Host "=========================================="
Write-Host "PRUEBAS COMPLETADAS"
Write-Host "==========================================`n"

$porcentajeExito = [math]::Round(($endpointsExitosos / $endpointsProbados) * 100, 2)

Write-Host "Resumen:"
Write-Host "   Endpoints probados: $endpointsProbados"
Write-Host "   Exitosos: $endpointsExitosos"
Write-Host "   Fallidos: $endpointsFallidos"
Write-Host "   Tasa de exito: $porcentajeExito%"

Write-Host "`nDatos de prueba creados:"
if ($idAulaCreada) {
    Write-Host "   Aula: $idAulaCreada"
}
if ($idCronograma) {
    Write-Host "   Cronograma: $idCronograma"
}

Write-Host "`nEstado del sistema:"
if ($porcentajeExito -ge 80) {
    Write-Host "   Bedelia API funcionando correctamente"
} elseif ($porcentajeExito -ge 50) {
    Write-Host "   Algunos endpoints tienen problemas"
} else {
    Write-Host "   Sistema tiene errores criticos"
}

Write-Host "`nVer logs detallados:"
Write-Host "   docker-compose logs app_bedelia --tail=100"
Write-Host ""