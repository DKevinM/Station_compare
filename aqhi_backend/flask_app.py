from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

# Connect to Supabase PostgreSQL
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))

@app.route("/aqhi", methods=["GET"])
def get_aqhi_data():
    start = request.args.get("start")
    end = request.args.get("end")
    station = request.args.get("station")  # Optional
    param = request.args.get("param")      # Optional

    if not start or not end:
        return jsonify({"error": "Missing start or end"}), 400

    try:
        cur = conn.cursor()
        query = """
            SELECT "StationName", "ParameterName", "ReadingDate", "Value", "Latitude", "Longitude"
            FROM aqhi_data
            WHERE "ReadingDate" BETWEEN %s AND %s
        """
        args = [start, end]

        if station:
            query += ' AND "StationName" = %s'
            args.append(station)

        if param:
            query += ' AND "ParameterName" = %s'
            args.append(param)

        query += ' ORDER BY "ReadingDate" ASC LIMIT 5000'
        cur.execute(query, tuple(args))
        rows = cur.fetchall()
        cur.close()

        # Format results
        result = []
        for row in rows:
            result.append({
                "StationName": row[0],
                "ParameterName": row[1],
                "ReadingDate": row[2].isoformat(),
                "Value": float(row[3]),
                "Latitude": float(row[4]),
                "Longitude": float(row[5])
            })

        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
