"""Preserve legacy URL building while controllers move into Blueprints."""
from werkzeug.routing import Rule


def register_compat(app, blueprint, namespace):
    app.register_blueprint(blueprint)
    prefix = blueprint.name + '.'
    for rule in list(app.url_map.iter_rules()):
        if rule.endpoint.startswith(prefix):
            legacy = rule.endpoint[len(prefix):]
            app.url_map.add(Rule(rule.rule, endpoint=legacy, methods=rule.methods, build_only=True))
            app.view_functions[legacy] = app.view_functions[rule.endpoint]
            namespace[legacy] = app.view_functions[rule.endpoint]
