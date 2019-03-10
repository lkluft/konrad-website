import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
import numpy as np
from netCDF4 import Dataset


def get_data(exp, output):

    ds = Dataset('database_new.nc')
    experiments = ds['exp'][:]

    exp_index = int(np.argwhere(experiments == exp))

    z = ds['z'][exp_index, :]*0.001
    if 'T' in output:
        z = np.hstack(([0], z))
        T = np.hstack((ds['temperature'][exp_index],
                  ds['T'][exp_index, :]))
        xlabel = 'Temperature'
        xunits = 'K'
        if output == 'T_C':
            T -= 273.15
            xunits = 'Celcius'
    elif output == 'radlw':
        T = ds['radlw'][exp_index, :]
        xlabel = 'Longwave heating'
        xunits = 'K / day'
    elif output == 'radsw':
        T = ds['radsw'][exp_index, :]
        xlabel = 'Shortwave heating'
        xunits = 'K / day'
    elif output == 'conv':
        T = ds['conv'][exp_index, :]
        xlabel = 'Convective heating'
        xunits = 'K / day'

    return z, T, xlabel, xunits


def model_run(exp, output):
    global T, z, xlabel, xunits
    z, T, xlabel, xunits = get_data(exp, output)
    return T, z, xlabel, xunits


def get_comparison(output):

    global comparison_T, comparison_z, comparison_label

    comparison_z, comparison_T, xlabel, xunits = get_data('standard', output)
    comparison_label = 'standard'
    return


def create_interactive_figure():
    css = """
    h6
    {
      font-size: 1.5em;
      margin-top: 0.83em;
      margin-bottom: 0.83em;
      margin-left: 0.83em;
      margin-right: 0.83em;
      color: #0099ff;
      background-color: rgba(255,255,255,0.8);
    }
    h5
    {
      font-size: 1.5em;
      margin-top: 0.83em;
      margin-bottom: 0.83em;
      margin-left: 0.83em;
      margin-right: 0.83em;
      color: #ff3300;
      background-color: rgba(255,255,255,0.8);
    }
    """

    fig = plt.figure(figsize=(5, 7))
    ax = fig.gca()
    try:  # plot comparison if requested
        points_ref = ax.plot(comparison_T, comparison_z, marker='o', ms=5,
                             label=comparison_label, c='#0099ff')

        labels_ref = []
        for i in range(comparison_z.size):
            label_ref = '<h6>Height: {:.1f} km<br>{}: {:.1f} {}</h6>'.format(comparison_z[i], xlabel, comparison_T[i], xunits)
            labels_ref.append(label_ref)

        tooltip_ref = mpld3.plugins.PointHTMLTooltip(
            points_ref[0], labels_ref, voffset=10, hoffset=10, css=css)
        comparison = True
    except ValueError:
        comparison = False
        pass

    points = ax.plot(T, z, marker='o', ms=5, label='your run', c='#ff3300')
    plt.xlabel(f'{xlabel} [{xunits}]')
    plt.ylabel('Height [km]')
    plt.ylim(0, np.max(z))
    leg = plt.legend()
    leg.get_frame().set_edgecolor('white')

    labels = []
    for i in range(z.size):
        label = '<h5>Height: {:.1f} km<br>{}: {:.1f} {}</h5>'.format(z[i], xlabel, T[i], xunits)
        labels.append(label)

    tooltip_user = mpld3.plugins.PointHTMLTooltip(
        points[0], labels, voffset=10, hoffset=10, css=css)

    if comparison:
        mpld3.plugins.connect(fig, tooltip_user, tooltip_ref)
    else:
        mpld3.plugins.connect(fig, tooltip_user)

    return mpld3.fig_to_html(fig)
