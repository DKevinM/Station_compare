from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# Connect to Supabase PostgreSQL
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))

@app.route("/aqhi", methods=["GET"])
def get_aqhi_data():
    station = request.args.get("station")  
    param = request.args.get("param") 
    end = datetime.utcnow()
    start = end - timedelta(days=7)

    if request.args.get("start"):
        start = datetime.fromisoformat(request.args.get("start"))
    if request.args.get("end"):
        end = datetime.fromisoformat(request.args.get("end"))

    try:
        cur = conn.cursor()
        query = """
            SELECT "StationName", "ParameterName", "ReadingDate", "Value"
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
        result = [
            {
                "StationName": row[0],
                "ParameterName": row[1],
                "ReadingDate": row[2].isoformat(),
                "Value": float(row[3])
            }
            for row in rows
        ]

        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
