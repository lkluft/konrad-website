import numpy as np
from flask import Flask, url_for, request, render_template, Response
from run_konrad import model_run, get_comparison, create_interactive_figure
app = Flask('/home/sally/Documents/webpages/calc_sst')

# make the WSGI interface available at the top level so wfastcgi can get it
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    return render_template('Hello.html')


@app.route('/plot_interactive.png')
def plot_interactive_png():
    return create_interactive_figure()


@app.route('/run_konrad', methods=['GET', 'POST'])
def run_konrad():
    co2_options = np.arange(280, 601, 20)
    if request.method == 'GET':
        state = {'co2': 400, 'humidity': 'rh', 'albedo': 0.2,
                 'comparison': 'pi'}
        # send the user the form
        return render_template('UserInput.html', co2_options=co2_options,
                               state=state)
    elif request.method == 'POST':
        # read form data and check data type
        humidity = request.form.get('humidity')
        co2 = int(request.form.get('CO2'))
        albedo = round(float(request.form.get('albedo')), 2)
        # get T and z corresponding to the selected input
        T, z = model_run(co2, humidity, albedo)
        # display result
        comparison = request.form.get('comparison')
        get_comparison(str(comparison), humidity, albedo)
        mpld3_html = plot_interactive_png()
        state = {'co2': co2, 'albedo': albedo, 'comparison': comparison,
                 'humidity': humidity}
        return render_template(
            'SurfaceTemperature.html', co2_options=co2_options, SST=T[0],
            plot=mpld3_html, state=state)
    else:
        return "<h2>Invalid request</h2>"


@app.route('/about_us', methods=['GET'])
def about_us():
    if request.method == 'GET':
        return render_template('AboutUs.html')
    else:
        return "<h2>Invalid request</h2>"


@app.route('/read_about_konrad', methods=['GET'])
def read_about_konrad():
    if request.method == 'GET':
        return render_template('ModelDetails.html')
    else:
        return "<h2>Invalid request</h2>"


# Launching our server
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, threaded=True)
