from flask import Flask, render_template
import requests

app = Flask(__name__)

#flask routing = decorating, binds a function to a URL
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/country')
def about():
    url = 'https://restcountries.com/v3.1/all?fields=name,population,region'
    response = requests.get(url)
    data = response.json()

    #empty list
    countries_europe = []

    for country in data:
        if country["region"] == "Europe":
            countries_europe.append({
                "name": country["name"]["common"],
                "population": country["population"]
            })
    return render_template('country.html', countries_europe=countries_europe)

if __name__ == '__main__':
    app.run(debug=True)


