function [model, schedule, initState, dh] = setup_model(opt)
   gravity on;

   var.Gt                = [];
   var.rock2D            = [];
   var.loops             = [];
   var.loops_bc          = [];
   
   set_formation(opt.formation);
      
   dh = [];
   topo = 'smooth';
   if opt.use_trapping
       dh = computeToptraps(load(opt.subtrap_file), var.Gt, true);
       topo = 'inf_rough';
   end
      
   % Set up input parameters
   initState = setup_initstate();
   ref_p     = mean(initState.pressure);
                                       
   fluid     = makeVEFluid(var.Gt, var.rock2D, ...
       if_else(opt.use_cap_fringe, 'P-scaled table', 'sharp interface') , ...
       'C', opt.c, ...
       'fixedT', caprock_temperature(), ...
       'wat_rho_pvt', [opt.water_compr_val, ref_p], ...
       'wat_rho_ref', opt.water_density, ...
       'pvMult_p_ref', ref_p, ...
       'pvMult_fac', opt.pv_mult, ...
       'residual', [opt.water_residual,  opt.co2_residual], ...
       'dissolution', opt.use_dissolution, ...
       'dis_max', opt.dis_max, ...
       'surf_topo', topo, ...
       'top_trap', dh);
                              
   model     = CO2VEBlackOilTypeModel(var.Gt, var.rock2D, fluid);
   schedule  = setup_schedule();

   semiopen_faces = get_bfaces_of_type(1);
   if ~isempty(semiopen_faces)
       % modifying transmissibilities for semi-open boundary faces

       semiopen_cells = sum(var.Gt.faces.neighbors(semiopen_faces,:), 2); 
       d = var.Gt.cells.centroids(semiopen_cells) - var.Gt.faces.centroids(semiopen_faces);
       d = sqrt(sum(d.^2, 2)); % norm of distance
     
       model.operators.T_all(semiopen_faces) = ...
           model.operators.T_all(semiopen_faces) .* d ./ (d + opt.outside_distance);
  end

   % ============================= LOCAL HELPER FUNCTIONS =============================

   function res = get_bfaces_of_type(type)
      
      res = [];
      for i = 1:numel(var.loops)
         faces = var.loops{i};
         bcs   = var.loops_bc{i};
         res = [res; faces(bcs==type)];%#ok
      end
   end
   
   
   function schedule = setup_schedule()

      schedule = [];
   
      % Create wells 
      W = [];
      wcell_ix = closest_cell(var.Gt, [cell2mat(opt.well_position), 0], 1:var.Gt.cells.num);
      W = addWellVE(W, var.Gt, var.rock2D, wcell_ix , ...
                  'type'   , 'rate'               , ...
                  'val'    , opt.default_rate    , ...
                  'radius' , opt.well_radius      , ...
                  'comp_i' , [0 1]                , ...
                  'name'   , ['I', num2str(1)]);
      W_shut = W;
      for i = 1:numel(W_shut)
         W_shut(i).val = 0;
      end
      
      schedule.control(1).W = W;
      schedule.control(2).W = W_shut;
      
      % Define boundary conditions
      open_faces = [get_bfaces_of_type(1); get_bfaces_of_type(2)];

      schedule.control(1).bc = addBC([], open_faces, ...
                                     'pressure', ...
                                     var.Gt.faces.z(open_faces) * ...
                                     opt.water_density * norm(gravity), ...
                                     'sat', [1 0]);
      schedule.control(2).bc = schedule.control(1).bc;
      
      
      dTi = opt.inj_time / opt.inj_steps;
      dTm = opt.mig_time / opt.mig_steps;
      istepvec = ones(opt.inj_steps, 1) * dTi;
      mstepvec = ones(opt.mig_steps, 1) * dTm;
      
      schedule.step.val = [istepvec; mstepvec];
      schedule.step.control = [ones(opt.inj_steps, 1); ones(opt.mig_steps, 1) * 2];
      
   end

   % ----------------------------------------------------------------------------
   
   function T = caprock_temperature()
      % Return temperature in Kelvin
      T = 273.15 + ...
          opt.seafloor_temp + ...
          (var.Gt.cells.z - opt.seafloor_depth) / 1e3 * opt.temp_gradient;
   end
   
   % ----------------------------------------------------------------------------
   
   function state = setup_initstate()
   
      state.pressure = var.Gt.cells.z * norm(gravity) * opt.water_density;
      state.s = repmat([1 0], var.Gt.cells.num, 1);
      state.sGmax = state.s(:,2);
      
      if opt.use_dissolution
        state.rs = 0 * state.sGmax;
      end
      
   end
      
   % ----------------------------------------------------------------------------

   function set_formation(name)
   
      % Default values, in case values are lacking in model file.
      default_perm = 200 * milli * darcy;
      default_poro = 0.2;
      
      % Load grid and rock, and assure rock values are valid

      [var.Gt, var.rock2D] = getFormationTopGrid(name, opt.grid_coarsening);
      
      if any(isnan(var.rock2D.poro))
         warning('Replacing missing porosity value with default value.');
         var.rock2D.poro = default_poro * ones(size(var.rock2D.poro));
      end
      if any(isnan(var.rock2D.perm))
         warning('Replacing missing permeability value with default value.');
         var.rock2D.perm = default_perm * ones(size(var.rock2D.perm));
      end
      
      var.loops = find_boundary_loops(var.Gt);
      % Setting all boundary conditions to open (2)
      var.loops_bc = cellfun(@(x) 0 * x + 2, var.loops, 'uniformoutput', false);
   end 
end

% ======================= INDEPENDENT HELPER FUNCTIONS =======================

function ix = closest_cell(Gt, pt, candidates)
   
   d = bsxfun(@minus, [Gt.cells.centroids(candidates,:), Gt.cells.z(candidates)], pt);
   d = sum(d.^2, 2);
   [~, ix] = min(d);
   ix = candidates(ix);
end

% ----------------------------------------------------------------------------

function [cix, fix] = boundary_cells_and_faces(Gt)
   
   fix = find(prod(Gt.faces.neighbors, 2) ==0);
   cix = unique(sum(Gt.faces.neighbors(fix, :), 2));
end

% ----------------------------------------------------------------------------

function loops = find_boundary_loops(Gt)

   [~, fix] = boundary_cells_and_faces(Gt); % boundary face indices

   tmp = [fix, Gt.faces.nodes(Gt.faces.nodePos(fix));
          fix, Gt.faces.nodes(Gt.faces.nodePos(fix)+1)];
   tmp = sortrows(tmp, 2);
   tmp = reshape(tmp(:,1), 2, []); % columns now express face neighborships
   
   % defining connectivity matrix
   M = sparse(tmp(1,:), tmp(2,:), 1, Gt.faces.num, Gt.faces.num);
   M = spones(M+M');
   num_loops = 0;
   while nnz(M) > 0
      num_loops = num_loops + 1;
      [loop,~] = find(M, 1);
      next = find(M(loop, :), 1); % find one of the two neighbor faces
      while ~isempty(next)
         M(loop(end), next) = 0; %#ok
         M(next, loop(end)) = 0; %#ok
         loop = [loop; next]; %#ok
         next = find(M(next, :)); 
         assert(numel(next) <= 1);
      end
      assert(loop(1) == loop(end));
      loops{num_loops} = loop(1:end-1); %#ok
   end
end

% ----------------------------------------------------------------------------

function val = if_else(cond, yes, no)
   
   if cond
      val = yes;
   else
      val = no;
   end
   
end
