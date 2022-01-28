function reports = get_simulation_results(initial_params)
    gravity on;
    
    [model, schedule, initState, dh] = setup_model(initial_params);
    [~, states] = simulateScheduleAD(initState, model, schedule);

    opt.trapstruct = trapAnalysis(model.G, false);

    reports = makeReports(model.G, [{initState}; states], model.rock, ...
        model.fluid, schedule, [model.fluid.res_water, ...
        model.fluid.res_gas], opt.trapstruct, dh);