from flask import Blueprint, request, jsonify
import sqlite3

prefs_bp = Blueprint('prefs', __name__)

DATABASE_NAME = 'keyguru.db'

@prefs_bp.route('/api/preferences/columns', methods=['GET'])
def get_column_preferences():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, is_visible, display_order
            FROM column_preferences
            WHERE user_id = ?
            ORDER BY display_order
        """, (1,))  # Hardcoded user_id for now
        
        preferences = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(preferences)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prefs_bp.route('/api/preferences/columns', methods=['PUT'])
def update_column_preferences():
    try:
        data = request.json
        if not isinstance(data, list):
            return jsonify({"error": "Invalid data format"}), 400
            
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        for pref in data:
            cursor.execute("""
                UPDATE column_preferences 
                SET is_visible = ?, display_order = ?
                WHERE user_id = ? AND column_name = ?
            """, (
                pref['is_visible'],
                pref['display_order'],
                1,  # Hardcoded user_id for now
                pref['column_name']
            ))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Preferences updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@prefs_bp.route('/api/preferences/columns/reset', methods=['POST'])
def reset_column_preferences():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Reset to default values
        default_columns = [
            ('job_position', 1, 1),
            ('company', 1, 2),
            ('location', 1, 3),
            ('status', 1, 4),
            ('date_saved', 1, 5),
            ('deadline', 1, 6),
            ('date_applied', 1, 7),
            ('follow_up', 1, 8),
            ('excitement', 1, 9)
        ]
        
        cursor.execute("BEGIN TRANSACTION")
        
        for col_name, is_visible, order in default_columns:
            cursor.execute("""
                UPDATE column_preferences
                SET is_visible = ?, display_order = ?
                WHERE user_id = ? AND column_name = ?
            """, (is_visible, order, 1, col_name))
            
        cursor.execute("COMMIT")
        conn.close()
        return jsonify({"message": "Preferences reset to default"})
    except Exception as e:
        if conn:
            cursor.execute("ROLLBACK")
        return jsonify({"error": str(e)}), 500