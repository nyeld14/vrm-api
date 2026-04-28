import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .db import get_aurora_connection

logger = logging.getLogger(__name__)


class VRMFleetStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            conn = get_aurora_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM fleet_overview")
                rows = cur.fetchall()
            conn.close()
            data = []
            for row in rows:
                item = dict(row)
                if isinstance(item.get('active_alarms'), str):
                    item['active_alarms'] = json.loads(item['active_alarms'])
                for ts_field in ['vrm_last_timestamp', 'updated_at']:
                    if item.get(ts_field):
                        item[ts_field] = item[ts_field].isoformat()
                data.append(item)
            return Response(data)
        except Exception as e:
            logger.error(f"VRM fleet status error: {e}")
            return Response({'error': str(e)}, status=503)


class VRMSiteDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, installation_id):
        hours = int(request.query_params.get('hours', 24))
        try:
            conn = get_aurora_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM fleet_overview WHERE installation_id = %s",
                    (installation_id,)
                )
                site = cur.fetchone()
                if not site:
                    return Response({'error': 'Site not found'}, status=404)
                cur.execute("""
                    SELECT timestamp, soc_percent, battery_voltage_v, battery_power_w,
                        output_power_l1_w, output_power_l2_w, output_power_l3_w,
                        input_power_l1_w, input_power_l2_w, input_power_l3_w,
                        system_state, generator_state, active_alarms
                    FROM inverter_readings
                    WHERE installation_id = %s
                      AND timestamp >= now() - (%s || ' hours')::interval
                    ORDER BY timestamp ASC
                """, (installation_id, hours))
                readings = cur.fetchall()
            conn.close()

            site_data = dict(site)
            for ts_field in ['vrm_last_timestamp', 'updated_at']:
                if site_data.get(ts_field):
                    site_data[ts_field] = site_data[ts_field].isoformat()
            if isinstance(site_data.get('active_alarms'), str):
                site_data['active_alarms'] = json.loads(site_data['active_alarms'])

            readings_data = []
            for r in readings:
                row = dict(r)
                if row.get('timestamp'):
                    row['timestamp'] = row['timestamp'].isoformat()
                if isinstance(row.get('active_alarms'), str):
                    row['active_alarms'] = json.loads(row['active_alarms'])
                readings_data.append(row)

            return Response({'site': site_data, 'readings': readings_data})
        except Exception as e:
            logger.error(f"VRM site detail error: {e}")
            return Response({'error': str(e)}, status=503)
