from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flasklms import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    isTeacher=db.Column(db.Boolean,nullable=False,default=False)
    password = db.Column(db.String(60), nullable=False)
    otp=db.Column(db.Integer , nullable=False , default=123)
    classrooms = db.relationship('ClassRoom', backref='teacher', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class ClassRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroomName = db.Column(db.String(100), nullable=False)
    subject=db.Column(db.String(20),nullable=False)
    time=db.Column(db.String(20),nullable=False)
    daysOfClasses=db.Column(db.String(100),nullable=False,default="Mon Wed Fri")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content= db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ClassRoom('{self.subject}', '{self.date_posted}')"