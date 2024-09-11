import unittest

import numpy as np
import openmdao.api as om
from openmdao.utils.assert_utils import assert_check_partials, assert_near_equal

from aviary.mission.gasp_based.ode.flight_path_ode import FlightPathODE
from aviary.variable_info.options import get_option_defaults
from aviary.subsystems.propulsion.utils import build_engine_deck
from aviary.utils.test_utils.default_subsystems import get_default_mission_subsystems
from aviary.utils.test_utils.IO_test_util import check_prob_outputs
from aviary.variable_info.variables import Dynamic


class FlightPathODETestCase(unittest.TestCase):
    def setUp(self):
        self.prob = om.Problem()

        aviary_options = get_option_defaults()
        default_mission_subsystems = get_default_mission_subsystems(
            'GASP', build_engine_deck(aviary_options))

        self.fp = self.prob.model = FlightPathODE(num_nodes=2,
                                                  aviary_options=get_option_defaults(),
                                                  core_subsystems=default_mission_subsystems)

    def test_case1(self):
        """
        ground_roll = False (the aircraft is not confined to the ground)
        """
        self.prob.setup(check=False, force_alloc_complex=True)

        self.prob.set_val(Dynamic.Mission.VELOCITY, [100, 100], units="kn")
        self.prob.set_val(Dynamic.Mission.MASS, [100000, 100000], units="lbm")
        self.prob.set_val(Dynamic.Mission.ALTITUDE, [500, 500], units="ft")

        self.prob.run_model()
        testvals = {
            Dynamic.Mission.VELOCITY_RATE: [14.0673, 14.0673],
            Dynamic.Mission.FLIGHT_PATH_ANGLE_RATE: [-0.1429133, -0.1429133],
            Dynamic.Mission.ALTITUDE_RATE: [0.0, 0.0],
            Dynamic.Mission.DISTANCE_RATE: [168.781, 168.781],
            "normal_force": [74910.12, 74910.12],
            "fuselage_pitch": [0.0, 0.0],
            "load_factor": [0.2508988, 0.2508988],
            Dynamic.Mission.ALTITUDE_RATE: [0.0, 0.0],
            Dynamic.Mission.ALTITUDE_RATE_MAX: [-0.01812796, -0.01812796],
        }
        check_prob_outputs(self.prob, testvals, rtol=1e-6)

        tol = 1e-6
        assert_near_equal(
            self.prob[Dynamic.Mission.ALTITUDE_RATE], np.array(
                [0, 0]), tol
        )

        partial_data = self.prob.check_partials(
            out_stream=None, method="cs", excludes=["*USatm*", "*params*", "*aero*"]
        )
        assert_check_partials(partial_data, atol=1e-8, rtol=1e-8)

    def test_case2(self):
        """
        ground_roll = True (the aircraft is confined to the ground)
        """
        self.fp.options["ground_roll"] = True
        self.prob.setup(check=False, force_alloc_complex=True)

        self.prob.set_val(Dynamic.Mission.VELOCITY, [100, 100], units="kn")
        self.prob.set_val(Dynamic.Mission.MASS, [100000, 100000], units="lbm")
        self.prob.set_val(Dynamic.Mission.ALTITUDE, [500, 500], units="ft")

        self.prob.run_model()
        testvals = {
            Dynamic.Mission.VELOCITY_RATE: [13.58489, 13.58489],
            Dynamic.Mission.DISTANCE_RATE: [168.781, 168.781],
            "normal_force": [74910.12, 74910.12],
            "fuselage_pitch": [0.0, 0.0],
            "load_factor": [0.2508988, 0.2508988],
            Dynamic.Mission.ALTITUDE_RATE_MAX: [0.7532356, 0.7532356],
        }
        check_prob_outputs(self.prob, testvals, rtol=1e-6)

        partial_data = self.prob.check_partials(
            out_stream=None, method="cs", excludes=["*USatm*", "*params*", "*aero*"]
        )
        assert_check_partials(partial_data, atol=1e-8, rtol=1e-8)


if __name__ == "__main__":
    unittest.main()
