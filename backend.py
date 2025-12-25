from flask import Flask, jsonify, request, Response
import re
import json

app = Flask(__name__)

def load_eczane():
    eczaneler = []
    with open('Eczane.sql', 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'INSERT INTO.*?VALUES\s*\(\s*(\d+)\s*,\s*\'(.*?)\'\s*,\s*\'(.*?)\'\s*,\s*\'(.*?)\''
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        eczaneler.append({
            'id': match[0],
            'ad': match[1],
            'adres': match[2].replace('»', '-'),
            'telefon': match[3]
        })
    
    return eczaneler

eczane_data = load_eczane()

@app.route('/')
def home():
    return "F3 Eczane API - JSON Format"

@app.route('/f3system/api/eczane')
def eczane_api():
    il = request.args.get('il', '')
    eczane_adi = request.args.get('ad', '')
    limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 kayıt
    
    results = []
    for eczane in eczane_data:
        match = True
        
        if il and il.upper() not in eczane['adres'].upper():
            match = False
            
        if eczane_adi and eczane_adi.upper() not in eczane['ad'].upper():
            match = False
            
        if match:
            results.append(eczane)
    
    # JSON response'u düzgün formatla
    response_data = {
        'sorgu': {'il': il, 'ad': eczane_adi},
        'toplam_kayit': len(eczane_data),
        'bulunan': len(results),
        'eczaneler': results[:limit]
    }
    
    # UTF-8 encoding ile döndür
    return Response(
        json.dumps(response_data, ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )

# Yeni endpoint: ID'ye göre ara
@app.route('/f3system/api/eczane/<int:eczane_id>')
def eczane_by_id(eczane_id):
    for eczane in eczane_data:
        if int(eczane['id']) == eczane_id:
            return Response(
                json.dumps(eczane, ensure_ascii=False, indent=2),
                mimetype='application/json; charset=utf-8'
            )
    return jsonify({'error': 'Eczane bulunamadı'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
