from flask import Flask
from flask_restful import Api, Resource

from twitter import get_timeseries

app = Flask(__name__)
api = Api(app)

class TwitterSentiment(Resource):
    def get(self, keyword):
        return get_timeseries(keyword)

api.add_resource(TwitterSentiment, "/<string:keyword>")

if __name__ == "__main__":
    app.run(debug=True)