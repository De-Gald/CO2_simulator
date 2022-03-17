function [masses, t, sol, W] = get_simulation_results(initial_params)
    initial_params.use_dissolution   = false;
    initial_params.use_trapping      = false;
    initial_params.use_cap_fringe    = false;

    gravity on;
    
    [model, schedule, initState, dh] = setup_model(initial_params);
    [~, states] = simulateScheduleAD(initState, model, schedule);

    opt.trapstruct = trapAnalysis(model.G, false);

    [masses, t, sol, W] = makeReports(model.G, [{initState}; states], model.rock, ...
        model.fluid, schedule, [model.fluid.res_water, ...
        model.fluid.res_gas], opt.trapstruct, dh);