from flask import Blueprint, render_template, request, jsonify
from MySQLdb.cursors import DictCursor
from app import mysql
from datetime import datetime, timedelta
import json

main = Blueprint('main', __name__)

def is_harvester_online(last_heartbeat):
    if last_heartbeat is None:
        return False
    return datetime.now() - last_heartbeat < timedelta(minutes=5)

@main.route('/')
def dashboard():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
        SELECT h.*, COUNT(nd.id) as devices_count
        FROM harvesters h
        LEFT JOIN network_devices nd ON nd.harvester_id = h.id
        GROUP BY h.id
    """)
    harvesters = cursor.fetchall()
    cursor.close()
    return render_template('dashboard.html', 
                         harvesters=harvesters, 
                         is_harvester_online=is_harvester_online)

@main.route('/api/harvester/data', methods=['POST'])
def receive_harvester_data():
    try:
        # Récupération des données avec plusieurs méthodes pour plus de robustesse
        if request.is_json:
            data = request.get_json()
        else:
            # Pour les requêtes avec Content-Type: application/x-www-form-urlencoded
            data = request.form.to_dict()
            if 'scan_results' in data:
                try:
                    data['scan_results'] = json.loads(data['scan_results'])
                except:
                    pass

        # Validation des données requises
        required_fields = ['ip_address', 'hostname', 'status', 'scan_results']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Champs manquants: {', '.join(missing_fields)}",
                "received_data": data
            }), 400

        # Traitement de la latence WAN
        wan_latency = data.get('wan_latency', 'N/A')
        if isinstance(wan_latency, str):
            if 'WAN Latency:' in wan_latency:
                wan_latency = wan_latency.split('WAN Latency:')[-1].strip()
            wan_latency = wan_latency.replace('WAN', '').strip()

        # Conversion des devices connectés
        try:
            connected_devices = int(data.get('connected_devices', 0))
        except (ValueError, TypeError):
            connected_devices = 0

        cursor = mysql.connection.cursor(DictCursor)

        # Insertion/Mise à jour du harvester
        cursor.execute("""
            INSERT INTO harvesters 
            (name, ip_address, status, connected_devices, last_activity, last_heartbeat, wan_latency, scan_results)
            VALUES (%s, %s, %s, %s, NOW(), NOW(), %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                status = VALUES(status),
                connected_devices = VALUES(connected_devices),
                last_activity = NOW(),
                last_heartbeat = NOW(),
                wan_latency = VALUES(wan_latency),
                scan_results = VALUES(scan_results)
        """, (
            data['hostname'],
            data['ip_address'],
            data['status'],
            connected_devices,
            wan_latency,
            data['scan_results']
        ))

        # Récupération de l'ID
        if cursor.lastrowid:
            harvester_id = cursor.lastrowid
        else:
            cursor.execute("SELECT id FROM harvesters WHERE ip_address = %s", (data['ip_address'],))
            harvester_id = cursor.fetchone()['id']

        # Traitement des résultats de scan
        parse_scan_results(cursor, harvester_id, data['scan_results'])

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Données enregistrées avec succès",
            "harvester_id": harvester_id
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}",
            "error_details": str(e),
            "received_data": data if 'data' in locals() else None
        }), 500

def parse_scan_results(cursor, harvester_id, scan_text):
    devices = []
    current_device = None
    
    for line in scan_text.split('\n'):
        line = line.strip()
        if line.startswith(('• Machine:', 'â€¢ Machine:', '* Machine:')):
            if current_device:
                devices.append(current_device)
            parts = line.split('(')
            ip_part = parts[0].replace('• Machine:', '').replace('â€¢ Machine:', '').replace('* Machine:', '').strip()
            ip = ip_part.split(':')[-1].strip() if ':' in ip_part else ip_part
            name = parts[1].replace(')', '').strip() if len(parts) > 1 else 'Inconnu'
            current_device = {'ip': ip, 'name': name, 'ports': []}
        elif line.startswith(('- Port', '* Port')):
            if current_device:
                port_part = line.replace('- Port', '').replace('* Port', '').strip()
                port_info = [p.strip() for p in port_part.split(':', 1)]
                if len(port_info) == 1:
                    port_info.append('unknown')
                current_device['ports'].append({'port': port_info[0], 'service': port_info[1]})
    
    if current_device:
        devices.append(current_device)
    
    for device in devices:
        try:
            cursor.execute("""
                INSERT INTO network_devices (harvester_id, ip_address, hostname)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE hostname = VALUES(hostname)
            """, (harvester_id, device['ip'], device['name']))
            
            device_id = cursor.lastrowid
            
            for port in device['ports']:
                try:
                    port_num = int(port['port'])
                    cursor.execute("""
                        INSERT INTO open_ports (device_id, port_number, service_name)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE service_name = VALUES(service_name)
                    """, (device_id, port_num, port['service']))
                except ValueError:
                    continue
        except Exception as e:
            print(f"Erreur traitement appareil {device.get('ip')}: {str(e)}")
            continue

@main.route('/harvester/<harvester_id>')
def harvester_details(harvester_id):
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute("SELECT * FROM harvesters WHERE id = %s OR ip_address = %s", (harvester_id, harvester_id))
        harvester = cursor.fetchone()
        
        if not harvester:
            return "Harvester non trouvé", 404
        
        cursor.execute("""
            SELECT nd.*, 
                   GROUP_CONCAT(CONCAT(op.port_number, ':', op.service_name) SEPARATOR '|') as ports_str
            FROM network_devices nd
            LEFT JOIN open_ports op ON op.device_id = nd.id
            WHERE nd.harvester_id = %s
            GROUP BY nd.id
        """, (harvester['id'],))
        
        network_devices = []
        for device in cursor.fetchall():
            ports = []
            if device['ports_str']:
                for port_str in device['ports_str'].split('|'):
                    port, service = port_str.split(':', 1)
                    ports.append({'port_number': port, 'service_name': service})
            device['ports'] = ports
            network_devices.append(device)
        
        return render_template('harvester_details.html',
                            harvester=harvester,
                            network_devices=network_devices)
    finally:
        cursor.close()