function visualSimulation(opt)
   [masses, t, sol, W] = get_simulation_results(opt);

   h2 = figure; plot(1); ax = get(h2, 'currentaxes');

   reports.masses = masses;
   reports.t = t;
   reports.sol = sol;
   reports.W = W;

   plotTrappingDistribution(ax, reports);
   fsize = 16;
   set(get(gca, 'xlabel'), 'fontsize', fsize)
   set(get(gca, 'ylabel'), 'fontsize', fsize)
   set(gca,'fontsize', fsize);
   set(gcf, 'position', [1, 1, 600, 600]);
   