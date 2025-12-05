from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from app import db
from app.models import Event, TelegramUser

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('calendar.html')

@bp.route('/api/events', methods=['GET'])
def get_events():
    start = request.args.get('start')
    end = request.args.get('end')

    query = Event.query

    if start:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        query = query.filter(Event.start_time >= start_date)

    if end:
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        query = query.filter(Event.end_time <= end_date)

    events = query.all()
    return jsonify([event.to_dict() for event in events])

@bp.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()

    try:
        event = Event(
            title=data['title'],
            description=data.get('description', ''),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            telegram_user_id=data.get('telegram_user_id')
        )

        db.session.add(event)
        db.session.commit()

        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'])

        db.session.commit()
        return jsonify(event.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200
