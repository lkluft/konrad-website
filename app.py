import io
from flask import Flask, url_for, request, render_template, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from run_konrad import model_run, get_comparison, create_figure
app = Flask('/home/sally/Documents/webpages/calc_sst')

# make the WSGI interface available at the top level so wfastcgi can get it
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    UsekonradLink = "<a href='" + url_for('run_konrad') + \
                    "'>Start using konrad</a>"
    LinkRRTMG = "<a href='http://rtweb.aer.com/rrtm_frame.html' " \
                "target='_blank'>RRTMG</a>"
    Linkpython = "<a href='https://www.python.org/' " \
                "target='_blank'>python</a>"
    Linkgithub = "<a href='https://github.com/atmtools/konrad' " \
                 "target='_blank'>our github page</a>"
    Linkclimt = "<a href='https://climt.readthedocs.io/en/latest/index.html' " \
                "target='_blank'>climt</a>"
    return """<html>
                    <head>
                        <title>Welcome to konrad</title>
                        <style>
                            body {background-color: #000000;
                                  color: #f2f2f2;}
                            a:link {color: #99ccff;}
                            a:visited {color: #dd99ff;}
                        </style>
                    </head>
                    <body>
                        <h1>Konrad</h1>
                        <div><font size=5>
                        Konrad is a single column model of the tropical
                        atmosphere, from the surface upwards through the
                        atmosphere.
                        Konrad is a 1D Radiative-Convective Equilibrium (RCE)
                        model, because the main processes involved are
                        radiative transfer (the reflection, absorption,
                        transmission and scattering of light)
                        and convection.
                        Convection only occurs in the lowest part of the
                        atmosphere, known as the troposphere, where
                        clouds form.
                        In konrad, convection simply takes heat
                        energy from the surface and brings it up
                        into the troposphere. </font></div>
                        <br />
                        <div><font size=3>
                        Konrad is written in """ + Linkpython + """ and is
                        available on """ + Linkgithub + """ for anyone to
                        download and use.
                        The radiative transfer scheme used in konrad is
                        """ + LinkRRTMG + """, the development of which started
                        in the 1990s, and the scheme continues to be used in
                        many weather prediction and climate models.
                        """ + LinkRRTMG + """ is written in fortran and made
                        accessible through python by """ + Linkclimt + """.
                        </font>
                        </div>
                        <br />
                        <div><font size=5>
                        """ + UsekonradLink + """
                        </font></div>
                    </body>
                </html>"""


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/run_konrad', methods=['GET', 'POST'])
def run_konrad():
    if request.method == 'GET':
        # send the user the form
        return render_template('UserInput.html')
    elif request.method == 'POST':
        # read form data and check data type
        CO2 = request.form.get('CO2')
        try:
            CO2 = float(CO2)
        except TypeError:
            return render_template('WrongInput.html')
        # input data into model and try to run
        try:
            atmosphere, SST = model_run(CO2)
        except Exception:
            return render_template('WrongInput.html')
        # display result
        comparison = request.form.get('comparison')
        get_comparison(str(comparison))
        return render_template(
            'SurfaceTemperature.html', CO2=CO2, SST=SST)
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
