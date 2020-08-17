import json
from jinja2 import Template

def jinja_to_json(template_path, data):
    jinja_template = Template(open(template_path).read())
    return json.loads(jinja_template.render(data))