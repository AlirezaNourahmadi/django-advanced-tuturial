{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account activation 
{% endblock %}

{%block html%}

{{token}}

{%endblock%}
