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
    if request.method == 'GET':
        state = {'exp': 'co2x2', 'output': 'T'}
        # send the user the form
        return render_template('UserInput.html',
                               state=state)
    elif request.method == 'POST':
        # read form data and check data type
        exp = request.form.get('exp')
        output = request.form.get('output')
        T, z, xlabel, xunits = model_run(exp, output)
        get_comparison(output)
        mpld3_html = plot_interactive_png()
        state = {'exp': exp, 'output': output}
        if output == 'T':
            return render_template(
                'SurfaceTemperature.html', SST=T[0], plot=mpld3_html,
                state=state
            )
        else:
            return render_template(
                'ModelOutput.html', plot=mpld3_html, state=state
            )

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
