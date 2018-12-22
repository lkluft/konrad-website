import konrad
from typhon.plots import profile_p_log
import matplotlib.pyplot as plt
import mpld3
import numpy as np


def model_run(CO2):

    global atmosphere
    global surface

    atmosphere = konrad.atmosphere.Atmosphere.from_netcdf(
        ncfile='/home/sally/konrad/tutorials/data/tropical-standard.nc',
    )
    #atmosphere.tracegases_rcemip()
    p = atmosphere['plev'][:]
    atmosphere['CO2'][:] = CO2*10**-6
    surface = konrad.surface.SurfaceHeatCapacity()
    rce = konrad.RCE(
        atmosphere,
        surface=surface,
        radiation=konrad.radiation.RRTMG(),  # Use RRTMG radiation scheme.
        cloud=konrad.cloud.ClearSky(z=p),
        convection=konrad.convection.HardAdjustment(),  # Perform a hard convective adjustment.
        lapserate=konrad.lapserate.MoistLapseRate(),  # Adjust towards a moist adiabat.
        timestep='16h',  # Set timestep in model time.
        max_duration='200d',  # Set maximum runtime.
    )
    rce.run()

    return atmosphere, surface['temperature'][-1]


def get_comparison(comparison):

    global comparison_atmosphere
    global comparison_label
    global comparison_surface

    if comparison == 'none':
        comparison_atmosphere = None
        comparison_label = None
        comparison_surface = None

    elif comparison == 'pi':
        # Load pre-industrial atmosphere for comparison
        # TODO: save data for appropriate comparison runs.
        # TODO: move this to model_run and also use as starting atmosphere.
        comparison_atmosphere = konrad.atmosphere.Atmosphere.from_netcdf(
            ncfile='/home/sally/konrad/tutorials/data/tropical-standard.nc'
        )
        comparison_label = 'pre-industrial'
        comparison_surface = konrad.surface.SurfaceHeatCapacity.from_atmosphere(comparison_atmosphere)
    elif comparison == 'present':
        # Load present day atmosphere for comparison
        comparison_atmosphere = konrad.atmosphere.Atmosphere.from_netcdf(
            ncfile='/home/sally/konrad/tutorials/data/tropical-standard.nc'
        )
        comparison_label = 'present day'
        comparison_surface = konrad.surface.SurfaceHeatCapacity.from_atmosphere(comparison_atmosphere)
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

    T = np.hstack((surface['temperature'][-1], atmosphere['T'][-1, :]))
    z = np.hstack(([0], atmosphere['z'][-1, :] * 0.001))

    fig = plt.figure(figsize=(5, 7))
    ax = fig.gca()
    try:  # plot comparison if requested
        comparison_z = np.hstack(([0],
                                  comparison_atmosphere['z'][-1, :] * 0.001))
        comparison_T = np.hstack((comparison_surface['temperature'][-1],
                                  comparison_atmosphere['T'][-1, :]))
        points_ref = ax.plot(comparison_T, comparison_z, marker='o', ms=5,
                             label=comparison_label, c='#0099ff')

        labels_ref = []
        for i in range(comparison_z.size):
            label_ref = '<h6>Height: {:.1f} km<br>Temperature: {:.1f} K</h6>'.format(comparison_z[i], comparison_T[i])
            labels_ref.append(label_ref)

        tooltip_ref = mpld3.plugins.PointHTMLTooltip(
            points_ref[0], labels_ref, voffset=10, hoffset=10, css=css)
    except TypeError:
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

    try:
        mpld3.plugins.connect(fig, tooltip_user, tooltip_ref)
    except:
        mpld3.plugins.connect(fig, tooltip_user)

    return mpld3.fig_to_html(fig)
