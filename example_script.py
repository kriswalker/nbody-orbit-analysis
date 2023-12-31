import numpy as np

from simtools.sim_readers import GadgetSnapshot, GadgetCatalogue

from orbitanalysis.funcs import load_halo_particle_ids_gadget, \
    load_snapshot_obj_gadget
from orbitanalysis.track_orbits import track_orbits
from orbitanalysis.postprocessing import OrbitDecomposition

###############################################################################

snapshot_dir = 'path/to/snapshots'
catalaogue_dir = 'path/to/catalogues'
snapshot_filename = 'snapshot_{}.hdf5'
catalogue_filename = 'fof_subhalo_tab_{}.hdf5'

particle_type = 1  # DM
initial_snapshot_number, final_snapshot_number = 0, 48
groupids_at_snapshot = np.arange(0, 1)

n_radii = 4  # no. of unit radii (R_200 in this case) to track particles out to
mode = 'pericentric'  # use pericentric passages to count orbits

savedir = snapshot_dir + '/orbit_decomposition'
savefile = savedir + '/orbit_decomposition.hdf5'

###############################################################################

final_catalogue = GadgetCatalogue(
    path=catalaogue_dir,
    catalogue_filename=catalogue_filename,
    snapshot_number=final_snapshot_number,
    particle_type=particle_type,
    verbose=True)

haloids_at_final_snapshot = final_catalogue.group['first_subhalo'][
    groupids_at_snapshot]
haloids_at_final_snapshot = haloids_at_final_snapshot[
    haloids_at_final_snapshot > -1]


def regions(catalogue, haloids):
    return catalogue.halo['center_of_mass'][haloids], catalogue.group[
        'R_200crit'][catalogue.halo['group_number'][haloids]]


final_region_positions, final_region_radii = regions(
    final_catalogue, haloids_at_final_snapshot)
final_snapshot = GadgetSnapshot(
    path=snapshot_dir,
    snapshot_filename=snapshot_filename,
    snapshot_number=final_snapshot_number,
    particle_type=particle_type,
    region_positions=final_region_positions,
    region_radii=n_radii * final_region_radii,
    read_mode=1,
    buffer=1.0e-7,
    verbose=True)

track_orbits(load_halo_particle_ids_gadget, load_snapshot_obj_gadget,
             regions, final_snapshot, final_catalogue,
             haloids_at_final_snapshot, n_radii, savefile, mode,
             initial_snapshot_number, verbose=True)

# post-processing
orb_decomp = OrbitDecomposition(savefile)
orb_decomp.correct_counts_and_save_to_file(angle_condition=np.pi/2)
orb_decomp.datafile.close()

# plotting
orb_decomp = OrbitDecomposition(savefile)
orb_decomp.get_halo_decomposition_at_snapshot(
    snapshot_number=48, halo_index=haloids_at_final_snapshot[0],
    use_corrected=True)
orb_decomp.plot_position_space(
    projection='xy', colormap='inferno_r', counts_to_plot='all',
    xlabel=r'$x/R_{200}$', ylabel=r'$y/R_{200}$', display=False,
    savefile=savedir + '/position_space.png')
orb_decomp.plot_phase_space(
    colormap='inferno_r', counts_to_plot='all', radius_label=r'$r/R_{200}$',
    radial_velocity_label=r'$v_r\,\,({\rm km\, s}^{-1})$', display=False,
    savefile=savedir + '/phase_space.png')
orb_decomp.datafile.close()
