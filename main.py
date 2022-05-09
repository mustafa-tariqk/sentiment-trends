from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class TwitterSentiment(Resource):
    def get(self):
        return {"hello": "world"}

api.add_resource(TwitterSentiment, '/')

if __name__ == "__main__":
    app.run(debug=True)