from flask import Flask, jsonify, render_template_string
import redis
import time

app = Flask(__name__)

HOST = '157.151.165.209'
PORT = 6380
PASSWORD = 'Secreta123'

def get_db():
    return redis.Redis(host=HOST, port=PORT, password=PASSWORD, decode_responses=True, socket_timeout=1)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Demostración HA y PITR - Equipo B</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom scrollbar for terminal look */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
        /* Animaciones para la arquitectura */
        .flow-line {
            position: relative;
            overflow: hidden;
        }
        .flow-line::after {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
            animation: flow 1.5s infinite;
        }
        @keyframes flow {
            100% { left: 100%; }
        }
        .pulse-error { animation: pulseError 1s infinite; }
        @keyframes pulseError {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; color: #ef4444; }
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans p-6 min-h-screen">
    
    <header class="max-w-6xl mx-auto text-center mb-10">
        <div class="inline-block bg-white px-10 py-5 rounded-2xl border border-slate-200 shadow-sm">
            <h1 class="text-4xl font-extrabold text-slate-800 mb-2">
                Clúster de Alta Disponibilidad <span class="text-red-600">Redis</span>
            </h1>
            <h2 class="text-xl font-semibold text-slate-500">Equipo B | Proyecto OCI</h2>
        </div>
    </header>

    <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">

        <div class="bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden flex flex-col md:col-span-2">
            <div class="bg-slate-100 border-b border-slate-200 p-4">
                <h3 class="text-xl font-bold text-slate-800 flex items-center">
                    <span class="mr-2 text-blue-600">⚡</span> Demo 1: Alta Disponibilidad & Arquitectura
                </h3>
            </div>
            
            <div class="p-6 flex-grow flex flex-col md:flex-row gap-6">
                <div class="flex-1 border-r border-slate-100 pr-6">
                    <p class="text-xs font-bold text-slate-400 mb-4 uppercase tracking-wider">Flujo de Datos en Vivo</p>
                    
                    <div class="flex flex-col items-center justify-center space-y-4 py-4">
                        <div class="bg-blue-50 border-2 border-blue-200 text-blue-700 px-6 py-2 rounded-lg font-bold shadow-sm z-10 w-48 text-center">
                            Aplicación Web
                        </div>
                        
                        <div id="arrow-1" class="h-8 w-1 bg-blue-300 flow-line transition-colors duration-300"></div>
                        
                        <div class="bg-orange-50 border-2 border-orange-200 text-orange-700 px-6 py-2 rounded-lg font-bold shadow-sm z-10 w-48 text-center flex items-center justify-center">
                            <span class="mr-2">⚖️</span> HAProxy
                        </div>
                        
                        <div id="arrow-2" class="h-8 w-1 bg-green-400 flow-line transition-colors duration-300"></div>
                        
                        <div class="flex space-x-4 w-full justify-center">
                            <div id="node-master" class="bg-green-50 border-2 border-green-500 text-green-700 px-4 py-3 rounded-lg font-bold shadow-md w-32 text-center transition-all duration-300 transform scale-105">
                                Maestro
                                <div class="text-xs font-normal mt-1">Activo</div>
                            </div>
                            <div id="node-slave" class="bg-slate-50 border-2 border-slate-300 text-slate-500 px-4 py-3 rounded-lg font-semibold w-32 text-center transition-all duration-300">
                                Réplicas
                                <div class="text-xs font-normal mt-1">Standby</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex-1 flex flex-col">
                    <div class="mb-4 flex justify-between items-end bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div>
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Estado HAProxy</p>
                            <div id="status-box" class="font-bold text-lg text-green-600 transition-colors duration-300">
                                ✅ CONECTADO
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">RTO</p>
                            <div class="text-2xl font-mono text-slate-800 font-bold" id="rto-timer">0.00s</div>
                        </div>
                    </div>

                    <div class="flex-grow flex flex-col">
                        <p class="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Log de Transacciones</p>
                        <div class="flex-grow h-40 overflow-y-auto bg-slate-900 p-4 rounded-xl text-sm font-mono text-slate-300 border border-slate-800 shadow-inner" id="log-ha">
                            Inicializando conexión con el clúster...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-6">
            
            <div class="bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden flex flex-col flex-1">
                <div class="bg-slate-100 border-b border-slate-200 p-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <span class="mr-2 text-purple-600">🛡️</span> Demo 2: PITR
                    </h3>
                </div>
                <div class="p-5 flex-grow flex flex-col">
                    <div class="mb-4">
                        <p class="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Dato Crítico (Memoria)</p>
                        <div id="pitr-data" class="p-3 bg-slate-900 border-l-4 border-purple-500 rounded text-center font-mono text-emerald-400 shadow-inner min-h-[60px] flex items-center justify-center text-sm transition-all duration-300">
                            Cargando...
                        </div>
                    </div>

                    <div class="flex-grow flex flex-col justify-end space-y-2 mt-2">
                        <button onclick="actionPITR('escribir')" class="w-full bg-white hover:bg-slate-50 border border-blue-200 text-blue-700 py-2.5 rounded-lg font-bold transition-colors shadow-sm text-sm">
                            1. Insertar Dato Crítico
                        </button>
                        <button onclick="actionPITR('borrar')" class="w-full bg-white hover:bg-red-50 border border-red-200 text-red-600 py-2.5 rounded-lg font-bold transition-colors shadow-sm text-sm">
                            2. Simular Desastre (DEL)
                        </button>
                        <button onclick="actionPITR('leer')" class="w-full bg-purple-600 hover:bg-purple-700 text-white shadow-md py-2.5 rounded-lg font-bold transition-colors mt-2 text-sm">
                            3. Consultar DB
                        </button>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden flex flex-col">
                <div class="bg-slate-100 border-b border-slate-200 p-4">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center">
                        <span class="mr-2 text-orange-500">📊</span> Demo 3: Monitoreo
                    </h3>
                </div>
                <div class="p-5">
                    <a href="http://129.80.10.240:3000" target="_blank" class="w-full flex items-center justify-center bg-orange-500 hover:bg-orange-600 text-white shadow-md py-3 px-4 rounded-xl font-bold transition-colors group">
                        Abrir Dashboard Grafana 
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                </div>
            </div>

        </div>
    </div>

    <script>
        // Lógica de Alta Disponibilidad (RTO) y Animación de Arquitectura
        let caidaInicio = null;
        
        setInterval(() => {
            fetch('/api/heartbeat')
                .then(res => res.json())
                .then(data => {
                    const box = document.getElementById('status-box');
                    const log = document.getElementById('log-ha');
                    
                    // Elementos de la arquitectura
                    const arrow1 = document.getElementById('arrow-1');
                    const arrow2 = document.getElementById('arrow-2');
                    const masterNode = document.getElementById('node-master');
                    const slaveNode = document.getElementById('node-slave');
                    
                    if(data.status === 'ok') {
                        if(caidaInicio) {
                            let rto = ((new Date() - caidaInicio) / 1000).toFixed(2);
                            document.getElementById('rto-timer').innerText = rto + 's';
                            caidaInicio = null;
                        }
                        
                        // Estado UI
                        box.innerText = '✅ TRÁFICO ENRUTADO (OK)';
                        box.className = 'font-bold text-lg text-green-600 transition-colors duration-300';
                        log.innerHTML = `<div><span class="text-green-400">[WRITE]</span> Tx ID: ${data.val} -> Master</div>` + log.innerHTML;
                        
                        // Animación de flujo normal
                        arrow1.className = 'h-8 w-1 bg-blue-300 flow-line transition-colors duration-300';
                        arrow2.className = 'h-8 w-1 bg-green-400 flow-line transition-colors duration-300';
                        
                        masterNode.className = 'bg-green-50 border-2 border-green-500 text-green-700 px-4 py-3 rounded-lg font-bold shadow-md w-32 text-center transition-all duration-300 transform scale-105';
                        masterNode.innerHTML = 'Maestro<div class="text-xs font-normal mt-1">Activo</div>';
                        
                        slaveNode.className = 'bg-slate-50 border-2 border-slate-300 text-slate-500 px-4 py-3 rounded-lg font-semibold w-32 text-center transition-all duration-300';
                        slaveNode.innerHTML = 'Réplicas<div class="text-xs font-normal mt-1">Standby</div>';

                    } else {
                        if(!caidaInicio) caidaInicio = new Date();
                        
                        // Estado UI Error
                        box.innerText = '⚠️ FAILOVER EN CURSO...';
                        box.className = 'font-bold text-lg text-red-600 transition-colors duration-300 pulse-error';
                        log.innerHTML = `<div class="text-red-400"><span class="font-bold">[ERROR]</span> Pérdida de nodo. Sentinel negociando...</div>` + log.innerHTML;
                        
                        // Animación de arquitectura rota
                        arrow1.className = 'h-8 w-1 bg-red-300 transition-colors duration-300 pulse-error';
                        arrow2.className = 'h-8 w-1 bg-red-400 transition-colors duration-300 pulse-error';
                        
                        masterNode.className = 'bg-red-50 border-2 border-red-500 text-red-700 px-4 py-3 rounded-lg font-bold shadow-md w-32 text-center transition-all duration-300 pulse-error';
                        masterNode.innerHTML = 'Maestro<div class="text-xs font-normal mt-1">CAÍDO</div>';
                        
                        slaveNode.className = 'bg-orange-50 border-2 border-orange-400 text-orange-700 px-4 py-3 rounded-lg font-semibold w-32 text-center transition-all duration-300 transform scale-105';
                        slaveNode.innerHTML = 'Réplicas<div class="text-xs font-normal mt-1 animate-pulse">Votando...</div>';
                    }
                }).catch(() => {
                    if(!caidaInicio) caidaInicio = new Date();
                });
        }, 1000);

        // Lógica de PITR
        function actionPITR(accion) {
            const display = document.getElementById('pitr-data');
            display.innerText = "Procesando...";
            display.classList.add('opacity-50');

            fetch('/api/pitr/' + accion)
                .then(res => res.json())
                .then(data => {
                    display.classList.remove('opacity-50');
                    if(data.valor) {
                        display.innerText = data.valor;
                        display.className = 'p-3 bg-slate-900 border-l-4 border-emerald-500 rounded text-center font-mono text-emerald-400 shadow-inner min-h-[60px] flex items-center justify-center text-sm transition-all duration-300';
                    } else {
                        display.innerText = "(nil) - Tabla Vacía";
                        display.className = 'p-3 bg-slate-900 border-l-4 border-red-500 rounded text-center font-mono text-red-400 shadow-inner min-h-[60px] flex items-center justify-center text-sm transition-all duration-300';
                    }
                });
        }
        
        // Leer al cargar
        actionPITR('leer');
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/heartbeat')
def heartbeat():
    try:
        r = get_db()
        val = r.incr('equipo_b_ha_counter')
        return jsonify({"status": "ok", "val": val})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

@app.route('/api/pitr/<accion>')
def pitr_action(accion):
    try:
        r = get_db()
        key = "tabla_importante"
        if accion == 'escribir':
            r.set(key, "Datos Críticos del Proyecto (Protegidos)")
        elif accion == 'borrar':
            r.delete(key)
        
        # Siempre leer el valor final
        val = r.get(key)
        return jsonify({"status": "ok", "valor": val})
    except Exception as e:
        return jsonify({"status": "error", "valor": "Error de conexión"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)