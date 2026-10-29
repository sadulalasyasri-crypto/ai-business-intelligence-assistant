from flask import Flask, jsonify, render_template, request
from database import initialize_database, get_connection
from analytics import answer_question
from ai_interpreter import interpret_question

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/api/ask')
def ask():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get('question'), str):
        return jsonify({'error': 'Send JSON with a string field named question.'}), 400
    question = payload['question'].strip()
    if not question:
        return jsonify({'error': 'Question cannot be empty.'}), 400
    try:
        intent = interpret_question(question)
        result = answer_question(intent, question)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        app.logger.exception('Unexpected error while answering question')
        return jsonify({'error': 'An unexpected error occurred. Check the application log.'}), 500

@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})

# Initialize the SQLite database when the app starts.
initialize_database()

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
