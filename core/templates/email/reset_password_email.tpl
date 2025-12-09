{% extends "mail_templated/base.tpl" %}

{% block subject %}
Password reset
{% endblock %}

{% block html %}

You requested to reset your password.

Use the link below (or copy the token) within the next hour to set a new password:

http://0.0.0.0:8000/accounts/api/v1/reset-password/confirm/?token={{token}}

{% endblock %}
