import konrad

def model_run(CO2):

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
    return surface['temperature'][-1]
