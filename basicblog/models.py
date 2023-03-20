from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous import TimestampSigner
from flask import current_app
from basicblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	posts = db.relationship('Post', backref='author', lazy=True)

	def get_reset_token(self):
		secret_key = current_app.config['SECRET_KEY']
		signer = TimestampSigner(secret_key)
		s = URLSafeTimedSerializer(secret_key)
		
		# Generate a token
		payload = {'user_id': self.id}
		token = signer.sign(s.dumps(payload))
		return token

	@staticmethod
	def verify_reset_token(token):
		secret_key = current_app.config['SECRET_KEY']
		signer = TimestampSigner(secret_key)
		s = URLSafeTimedSerializer(secret_key)
		# Verify the token (will return the original payload if the token is valid and has not expired)
		try:
			original_payload = s.loads(signer.unsign(token, max_age=300))
			user_id = original_payload['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"
