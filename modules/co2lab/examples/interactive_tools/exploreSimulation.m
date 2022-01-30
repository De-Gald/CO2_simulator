function exploreSimulation()
    rho_cref = 760 * kilogram / meter ^3;

%     opt.default_formation = 'Fensfjordfm';
    opt.formation = 'utsirafm';
    opt.grid_coarsening = 4;
    opt.seafloor_depth    = 100 * meter;
    opt.seafloor_temp     =  7;
    opt.temp_gradient     = 35.6;
    opt.water_density     = 1000;
    opt.dis_max           = (53 * kilogram / meter^3) / rho_cref;
    opt.max_num_wells     = 1;
    opt.default_rate      = 1 * mega * 1e3 / year / rho_cref;
    opt.max_rate          = 10 * mega * 1e3 / year / rho_cref;
    opt.water_compr_val   = 4.3e-5/barsa;
    opt.pv_mult           = 1e-5/barsa;
    opt.water_residual    = 0.11;
    opt.co2_residual      = 0.21;
    opt.inj_time          = 50 * year;
    opt.inj_steps         = 5;
    opt.mig_time          = 100 * year;
    opt.mig_steps         = 5;
    opt.well_radius       = 0.3;
    opt.c                 = 0.1;
    opt.subtrap_file      = 'utsira_subtrap_function_3.mat';
    opt.outside_distance  = 100 * kilo * meter;
    
    opt.use_dissolution   = false;
    opt.use_trapping      = false;
    opt.use_cap_fringe    = false;
    
    opt.well_position          = {487000, 6721000};
    
    visualSimulation(opt);

