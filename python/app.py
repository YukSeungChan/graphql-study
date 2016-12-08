# -*- coding:utf-8 -*-
from schema import schema
from flask_graphql import GraphQLView
from flask import Flask

app = Flask(__name__)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)


@app.route('/schema')
def render_schema():
    return str(schema)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
