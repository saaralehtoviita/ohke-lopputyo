from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_all_countries():
    url = 'https://restcountries.com/v3.1/all?fields=name,population,region'
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        
        countries = []

        for country in data: 
            countries.append({
                "name": country["name"]["common"],
                "population": country["population"],
                "region": country["region"]
        })
        return countries
    
    except requests.exceptions.RequestException as e:
        print("API error: ", e)
        return []



#flask routing = decorating, binds a function to a URL
@app.route('/')
def countries_top10():
    countries = get_all_countries()

    countries = [country for country in countries if country["population"] > 0]

    def get_population(country):
        return country["population"]
    
    # suurimmat
    countries_sorted_desc = sorted(countries, key=get_population, reverse=True)
    countriestop10 = countries_sorted_desc[:10]

    # pienimmät
    countries_sorted_asc = sorted(countries, key=get_population)
    countrieslowest10 = countries_sorted_asc[:10]

    return render_template('index.html', countriestop10=countriestop10, countrieslowest10=countrieslowest10)

@app.route('/countries')
def all_countries():
    countries = get_all_countries()
    return render_template('countries.html', countries=countries)

@app.route('/countriesRegion')
def get_countries_by_region():
    region = request.args.get("region")

    if not region:
        return render_template('error.html', message="Region is required")

    url = f"https://restcountries.com/v3.1/region/{region}"
    response = requests.get(url)
    data = response.json()

    countries_region = []

    for country in data:
        countries_region.append({
            "name": country["name"]["common"],
            "population": country["population"]
        })
    
    def get_population(country):
        return country["population"]
    
    countries_region.sort(key=get_population, reverse=True)

    return render_template('countriesRegion.html', 
                           countries_region=countries_region, 
                           region=region.capitalize()
                           )

@app.route("/countriesGraph")
def graph_test():
    data = [
        ("01-01-2020", 1597),
        ("02-02-2020", 1456),
        ("03-01-2020", 1908),
        ("04-01-2020", 896),
        ("05-01-2020", 755),
        ("06-01-2020", 453),
        ("07-01-2020", 1100),
        ("08-01-2020", 1235),
        ("09-01-2020", 1478),
    ]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template("countriesGraph.html", labels=labels, values=values)

@app.route('/countriesEurope')
def countriesEurope():

    countries = get_all_countries()


    #empty list
    countries_europe = []

    for country in countries:
        if country["region"] == "Europe":
            countries_europe.append({
                countries_europe.append(country)
            })
    return render_template('countriesEurope.html', countries_europe=countries_europe)

@app.route('/country')
def get_country_by_name():
    name = request.args.get("name")
    
    if not name:
        render_template('error.html', message="name is required")

    url = f"https://restcountries.com/v3.1/name/{name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if len(data) > 0:
            country_data = data[0]
            return render_template('country.html', country_data=country_data)
        
    except requests.exceptions.RequestException as e:
        print("API error: ", e)
    
        return render_template('error.html', message="Country not found")

    
        

if __name__ == '__main__':
    app.run(debug=True)


