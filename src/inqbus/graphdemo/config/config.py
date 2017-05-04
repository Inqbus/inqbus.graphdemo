from inqbus.graphdemo.constants import DEBUG_MODE, DATABASE, UPLOAD_PATH


def configure_app(app):
    app.config['DEBUG'] = DEBUG_MODE
    app.config['SECRET_KEY'] = 'super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE

    # This is the path to the upload directory
    app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
    # These are the extension that we are accepting to be uploaded
    app.config['ALLOWED_EXTENSIONS'] = set(['h5'])
