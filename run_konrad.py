import konrad
from typhon.plots import profile_p_log
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["legend.facecolor"] = 'k'

def model_run(CO2):

    global atmosphere

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

    if comparison == 'none':
        comparison_atmosphere = None
        comparison_label = None

    elif comparison == 'pi':
        # Load pre-industrial atmosphere for comparison
        # TODO: save data for appropriate comparison runs.
        # TODO: move this to model_run and also use as starting atmosphere.
        comparison_atmosphere = konrad.atmosphere.Atmosphere.from_netcdf(
            ncfile='/home/sally/konrad/tutorials/data/tropical-standard.nc'
        )
        comparison_label = 'pre-industrial'
    elif comparison == 'present':
        # Load present day atmosphere for comparison
        comparison_atmosphere = konrad.atmosphere.Atmosphere.from_netcdf(
            ncfile='/home/sally/konrad/tutorials/data/tropical-standard.nc'
        )
        comparison_label = 'present day'
    return


def create_figure():

    plev = atmosphere['plev'][:]
    T = atmosphere['T'][-1, :]

    fig = plt.figure()
    fig.patch.set_facecolor('k')
    ax = fig.gca()
    ax.patch.set_facecolor('k')
    profile_p_log(plev, T, label='your run')
    try:
        comparison_plev = comparison_atmosphere['plev'][:]
        comparison_T = comparison_atmosphere['T'][-1, :]
        profile_p_log(comparison_plev, comparison_T, label=comparison_label)
    except:
        pass
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    legend = plt.legend()
    plt.setp(legend.get_texts(), color='w')
    plt.xlabel('Temperature [K]')
    return fig
