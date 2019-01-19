import matplotlib.pyplot as plt
import mpld3
import numpy as np
from netCDF4 import Dataset


def get_data(CO2, humidity, albedo):

    ds = Dataset('database.nc')
    humidity_options = ds['humidity'][:]
    co2_values = ds['CO2'][:]
    albedo_values = ds['albedo'][:]

    humidity_index = int(np.argwhere(humidity_options == humidity))
    co2_index = int(np.argwhere(co2_values == CO2))
    albedo_index = int(np.argwhere(albedo_values == albedo))

    T = np.hstack((ds['temperature'][co2_index, humidity_index, albedo_index],
                  ds['T'][co2_index, humidity_index, albedo_index, :]))
    z = np.hstack(([0],
                   ds['z'][co2_index, humidity_index, albedo_index, :]*0.001))

    return T, z


def model_run(CO2, humidity, albedo):
    global T, z
    T, z = get_data(CO2, humidity, albedo)
    return T, z


def get_comparison(comparison, humidity, albedo):

    global comparison_T, comparison_z, comparison_label

    if comparison == 'none':
        comparison_T = None
        comparison_z = None
        comparison_label = None

    elif comparison == 'pi':
        comparison_T, comparison_z = get_data(280, humidity, albedo)
        comparison_label = 'pre-industrial'

    elif comparison == 'present':  # CO2 = 400 ppmv
        comparison_T, comparison_z = get_data(400, humidity, albedo)
        comparison_label = 'present day'
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
            label_ref = '<h6>Height: {:.1f} km<br>Temperature: {:.1f} K</h6>'.format(comparison_z[i], comparison_T[i])
            labels_ref.append(label_ref)

        tooltip_ref = mpld3.plugins.PointHTMLTooltip(
            points_ref[0], labels_ref, voffset=10, hoffset=10, css=css)
        comparison = True
    except ValueError:
        comparison = False
        pass

    points = ax.plot(T, z, marker='o', ms=5, label='your run', c='#ff3300')
    plt.xlabel('Temperature [K]')
    plt.ylabel('Height [km]')
    plt.ylim(0, np.max(z))
    leg = plt.legend()
    leg.get_frame().set_edgecolor('white')

    labels = []
    for i in range(z.size):
        label = '<h5>Height: {:.1f} km<br>Temperature: {:.1f} K</h5>'.format(z[i], T[i])
        labels.append(label)

    tooltip_user = mpld3.plugins.PointHTMLTooltip(
        points[0], labels, voffset=10, hoffset=10, css=css)

    if comparison:
        mpld3.plugins.connect(fig, tooltip_user, tooltip_ref)
    else:
        mpld3.plugins.connect(fig, tooltip_user)

    return mpld3.fig_to_html(fig)
