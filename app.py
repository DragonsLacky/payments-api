import connexion
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def hello_world(name: str) -> str:
    return 'Hello World! {name}'.format(name=name)


connexion_app = connexion.App(__name__, specification_dir="config/")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")


if __name__ == '__main__':
    connexion_app.run(port=5000, debug=True)
