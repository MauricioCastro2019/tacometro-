import os
import logging
from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager, csrf

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Importar modelos (necesario para que Flask-Migrate los detecte)
    from app import models  # noqa: F401

    # Registrar comandos CLI
    with app.app_context():
        from app import commands  # noqa: F401

    # Registrar blueprints
    from app.main import main as main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.places import places as places_bp
    app.register_blueprint(places_bp, url_prefix='/places')

    from app.reviews import reviews as reviews_bp
    app.register_blueprint(reviews_bp, url_prefix='/reviews')

    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.califica import califica as califica_bp
    app.register_blueprint(califica_bp, url_prefix='/califica')

    # Correr migraciones y setup inicial al arrancar
    with app.app_context():
        _run_migrations()
        _promote_admin_from_env()

    # Manejadores de error
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def too_many_requests(e):
        from flask import render_template
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(e):
        from flask import render_template
        logger.error(f'Error 500: {e}', exc_info=True)
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app


def _run_migrations():
    """Aplica migraciones pendientes al arrancar (seguro: Alembic no re-aplica)."""
    try:
        from flask_migrate import upgrade as db_upgrade
        db_upgrade()
        logger.info('Migraciones aplicadas correctamente.')
    except Exception as e:
        logger.error(f'Error al aplicar migraciones: {e}', exc_info=True)


def _promote_admin_from_env():
    username = os.environ.get('ADMIN_USERNAME', '').strip()
    if not username:
        return
    try:
        from app.models.user import User
        user = User.query.filter_by(username=username).first()
        if user and not user.is_admin:
            user.is_admin = True
            db.session.commit()
    except Exception as e:
        logger.error(f'Error al promover admin: {e}')
