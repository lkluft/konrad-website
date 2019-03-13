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


@app.route('/co2_exp', methods=['GET', 'POST'])
def co2_exp():
    if request.method == 'GET':
        state = {'exp1': 'co2x2', 'exp2': '', 'output': 'T'}
        # send the user the form
        return render_template('CO2exp.html', state=state)
    elif request.method == 'POST':
        # read form data and check data type
        exp1 = request.form.get('exp1')
        exp2 = request.form.get('exp2')
        print(exp1, exp2, type(exp2))
        output = request.form.get('output')
        T, z, xlabel, xunits = model_run(exp1+exp2, output)
        SST0 = get_comparison(output, SST=True)
        mpld3_html = plot_interactive_png()
        state = {'exp1': exp1, 'exp2': exp2, 'output': output}
        if output == 'T':
            return render_template(
                'SurfaceTemperature.html', SST_diff=T[0]-SST0, plot=mpld3_html,
                state=state
            )
        else:
            return render_template(
                'CO2Output.html', plot=mpld3_html, state=state
            )

    else:
        return "<h2>Invalid request</h2>"


def one_experiment(templatename='OzoneExp.html', outputname='OzoneOutput.html',
                   codename='ozone'):
    if request.method == 'GET':
        state = {'output': 'T'}
        return render_template(templatename, state=state)
    elif request.method == 'POST':
        output = request.form.get('output')
        T, z, xlabel, xunits = model_run(codename, output)
        get_comparison(output)
        mpld3_html = plot_interactive_png()
        state = {'output': output}
        return render_template(
            outputname, plot=mpld3_html, state=state
        )
    else:
        return "<h2>Invalid request</h2>"


@app.route('/ozone_exp', methods=['GET', 'POST'])
def ozone_exp():
    return one_experiment()


@app.route('/convection_exp', methods=['GET', 'POST'])
def convection_exp():
    return one_experiment('ConvExp.html', 'ConvOutput.html', 'noconv')


@app.route('/experiments', methods=['GET'])
def experiments():
    if request.method == 'GET':
        return render_template('Experiments.html')
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


@app.route('/all_models_are_wrong', methods=['GET'])
def all_models_are_wrong():
    if request.method == 'GET':
        return render_template('all_models_are_wrong.html')
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
