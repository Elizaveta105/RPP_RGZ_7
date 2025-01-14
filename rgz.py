from flask import Flask, request, jsonify, render_template
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Ticket

app = Flask(__name__)
# Загрузка конфигураций из объекта Config
app.config.from_object(Config)

# Инициализация базы данных и менеджера логинов
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Загрузка пользователя по его id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Функция создания пользователя с ролью администратора
def create_admin():
    with app.app_context():
        # Проверка наличия администратора
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            hashed_password = generate_password_hash('admin_password', method='pbkdf2:sha256')
            new_admin = User(username='admin', password=hashed_password, role='admin')
            db.session.add(new_admin)
            # Сохранение изменений в базе данных
            db.session.commit()
            print("admin user created successfully!")
        else:
            print("admin user already exists!")


# Маршрут домашней страницы
@app.route('/')
def home():
    return render_template('home.html')


# Маршрут для регистрации нового пользователя
@app.route('/register', methods=['POST'])
def register():
    # Получение данных из запроса
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password, role='user')
    db.session.add(new_user)
    # Сохранение изменений в базе данных
    db.session.commit()
    return jsonify(
        {'message': 'registration was successful!'}), 201


# Маршрут для авторизации зарегистрированного пользователя
@app.route('/login', methods=['POST'])
def login():
    # Получение данных из запроса
    data = request.get_json()
    # Поиск пользователя по имени
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        # Вход пользователя в систему
        login_user(user)
        return jsonify({'message': 'logged in successfully!'}), 200
    return jsonify({'message': 'incorrect login details!'}), 401


# Маршрут для выхода из аккаунта
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged out successfully!'}), 200


# Маршрут для создания новой заявки в техподдержку
@app.route('/tickets', methods=['POST'])
@login_required
def create_ticket():
    data = request.get_json()
    new_ticket = Ticket(title=data['title'], description=data['description'], author=current_user)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(
        {'message': 'ticket created successfully!'}), 201


# Маршрут для получения всех заявок
@app.route('/tickets', methods=['GET'])
@login_required
def get_tickets():
    if current_user.role == 'admin':
        # Получение всех заявок всех пользователей
        tickets = Ticket.query.all()
    else:
        # Получение заявок текущего пользователя
        tickets = Ticket.query.filter_by(author=current_user).all()
    return jsonify([ticket.to_dict() for ticket in tickets]), 200


# Маршрут для получения конкретной заявки
@app.route('/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    # Получение заявки по её id
    ticket = Ticket.query.get(ticket_id)
    if current_user.role == 'admin' or ticket.author == current_user:
        return jsonify(ticket.to_dict()), 200
    return jsonify({'message': 'you do not have access!'}), 403


# Маршрут для обновления данных конкретной заявки
@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    # Получение заявки по её id
    ticket = Ticket.query.get(ticket_id)
    if current_user.role == 'admin' or ticket.author == current_user:
        # Получение данных из запроса
        data = request.get_json()
        # Обновление заголовка заявки, описания и статуса
        ticket.title = data['title']
        ticket.description = data['description']
        ticket.status = data['status']
        db.session.commit()
        return jsonify({'message': 'ticket updated successfully!'}), 200
    return jsonify({'message': 'you do not have access!'}), 403


# Маршрут для удаления конкретной заявки
@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if current_user.role == 'admin' or ticket.author == current_user:
        # Удаление заявки
        db.session.delete(ticket)
        # Сохранение изменений в базе данных
        db.session.commit()
        return jsonify(
            {'message': 'ticket deleted successfully!'}), 200
    return jsonify({'message': 'you do not have access!'}), 403


# Маршрут для получения всех пользователей (доступно только админу)
@app.route('/users', methods=['GET'])
@login_required
def get_users():
    if current_user.role == 'admin':
        # Получение всех пользователей
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    return jsonify({'message': 'you do not have access!'}), 403


# Маршрут для обновления роли пользователя (доступно только админу)
@app.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.role == 'admin':
        # Получение пользователя по id
        user = User.query.get(user_id)
        # Получение данных из запроса
        data = request.get_json()
        # Обновление роли пользователя
        user.role = data['role']
        db.session.commit()
        return jsonify({'message': 'user role updated successfully!'}), 200
    return jsonify({'message': 'you do not have access!'}), 403


# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=False)
