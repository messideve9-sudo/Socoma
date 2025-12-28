<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SOCoMA - Suivi des Créances{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">📊 SOCoMA</a>
            {% if current_user.is_authenticated %}
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('liste_creances') }}">Créances</a></li>
                    {% if current_user.is_admin %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_users') }}">Administration</a></li>
                    {% endif %}
                </ul>
                <span class="navbar-text me-3">Connecté en tant que {{ current_user.username }}</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Déconnexion</a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Messages flash -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Contenu principal -->
        {% block content %}{% endblock %}
    </div>

    <footer class="mt-5 py-3 bg-light text-center">
        <div class="container">
            <p class="mb-0">SOCoMA &copy; {{ now.year }} - Suivi des Créances</p>
            <p class="text-muted small">Version 1.0 - Déployé sur Render.com</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>