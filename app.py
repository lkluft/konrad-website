import io
from flask import Flask, url_for, request, render_template, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from run_konrad import model_run, get_comparison, create_figure
app = Flask('/home/sally/Documents/webpages/calc_sst')

# make the WSGI interface available at the top level so wfastcgi can get it
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    createLink = "<a href='" + url_for('run_konrad') + "'>Start using konrad</a>"
    return """<html>
                    <head>
                        <title>Welcome to konrad</title>
                    </head>
                    <body>
                        <h2>Welcome</h2>
                        """ + createLink + """
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
