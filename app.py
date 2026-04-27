from flask import Flask, render_template, request
import requests

app = Flask(__name__)

#muutetaan apista saatu maiden data "maa-olioiksi"
def parse_country(country_data):
    # OpenStreetMap korjaus
    osm = country_data.get("maps", {}).get("openStreetMaps")
    if osm and not osm.startswith("http"):
        osm = "https://" + osm

    flags = country_data.get("flags", {})
    flag = flags.get("png") or flags.get("svg")

    area = country_data.get("area") or 0
    population = country_data.get("population") or 0

    return {
        "name": country_data["name"]["common"],
        "flag": flag,
        "population": population,
        "region": country_data.get("region"),
        "subregion": country_data.get("subregion"),
        "capital": country_data.get("capital", {}),
        "area": area,
        "density": population / area if area else None,
        "languages": country_data.get("languages", {}),
        "currencies": country_data.get("currencies", {}),
        "location": osm
    }

#haetaan kaikkien maiden tiedot ja parsitaan ne maa-olioiksi
def fetch_all_countries():
    url = 'https://restcountries.com/v3.1/all?fields=name,flag,population,region,capital,area,density,languages,currencies,location'
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        
        return [parse_country(c) for c in data]
    
    except requests.exceptions.RequestException as e:
        print("API error: ", e)
        return []

#parametrina saadun maalistan mukaan luodaan alueet, irrotetaan alueen nimi ja lasketaan väkiluvut yhteen
def build_region_stats(countries):

    #alustetaan tyhjä dictionary
    regions = {}

    #haetaan jokaisen maan arvot 
    for c in countries:
        region = c["region"]
        population = c["population"]
        area = c.get("area", 0)

        #tarkistetaan, onko region jo olemassa, jos ei lisätään se ja asetetaan alkuarvoksi 0
        if region not in regions:
            regions[region] = {
                "population": 0,
                "area": 0
            }

        #kasvatetaan yhden alueen väkilukua ja areaa
        regions[region]["population"] += population
        regions[region]["area"] += area
    
    for region in regions:
        population = regions[region]["population"]
        area = regions[region]["area"]

        regions[region]["density"] = population / area

    return regions



#flask routing = decorating, binds a function to a URL
@app.route('/')
def countries_top10():
    countries = fetch_all_countries()

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

@app.route('/regions')
def all_regions():
    countries = fetch_all_countries()

    regions_data = build_region_stats(countries)
    
    print(regions_data)

    region_list = [
    {
        "name": region,
        "population": regions_data[region]["population"],
        "area": regions_data[region]["area"],
        "density": regions_data[region]["density"]
    }
    for region in regions_data
]

    print(region_list)

    return render_template('regions.html', region_list=region_list)


@app.route('/countries')
def all_countries():
    countries = fetch_all_countries()
    return render_template('countries.html', countries=countries)

@app.route('/countriesRegion')
def get_countries_by_region():
    region = request.args.get("region")

    if not region:
        return render_template('error.html', message="Region is required")

    url = f"https://restcountries.com/v3.1/region/{region}"
    response = requests.get(url)
    data = response.json()

    countries_region = [parse_country(c) for c in data]

    def get_population(country):
        return country["population"]
    
    countries_by_population = sorted(countries_region, key=get_population, reverse=True)

    def get_density(country):
        return country["density"]
    
    countries_region_by_density = sorted(countries_region, key=get_density, reverse=True)



    return render_template('countriesRegion.html',
                           countries_region = countries_region,
                           countries_by_population=countries_by_population,
                           countries_region_by_density=countries_region_by_density,
                           region=region.capitalize(), 
                           )

@app.route('/country')
def get_country_by_name():
    name = request.args.get("name")

    if not name:
        return render_template('error.html', message="name is required")

    url = f"https://restcountries.com/v3.1/name/{name}"

    try:
        data = requests.get(url).json()
        country = parse_country(data[0])

        return render_template("country.html", country=country)

    except Exception as e:
        print(e)
        return render_template('error.html', message="Country not found")    
        

if __name__ == '__main__':
    app.run(debug=True)


