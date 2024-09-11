import unittest

import numpy as np
import openmdao.api as om
from openmdao.utils.assert_utils import assert_check_partials

from aviary.mission.gasp_based.ode.groundroll_ode import GroundrollODE
from aviary.variable_info.options import get_option_defaults
from aviary.subsystems.propulsion.utils import build_engine_deck
from aviary.utils.test_utils.default_subsystems import get_default_mission_subsystems
from aviary.utils.test_utils.IO_test_util import check_prob_outputs
from aviary.variable_info.variables import Dynamic


class GroundrollODETestCase(unittest.TestCase):
    def setUp(self):
        self.prob = om.Problem()

        aviary_options = get_option_defaults()
        default_mission_subsystems = get_default_mission_subsystems(
            'GASP', build_engine_deck(aviary_options))

        self.prob.model = GroundrollODE(num_nodes=2,
                                        aviary_options=get_option_defaults(),
                                        core_subsystems=default_mission_subsystems)

    def test_groundroll_partials(self):
        """Check partial derivatives"""
        self.prob.setup(check=False, force_alloc_complex=True)

        self.prob.set_val(Dynamic.Mission.VELOCITY, [100, 100], units="kn")
        self.prob.set_val("t_curr", [1, 2], units="s")

        self.prob.run_model()

        testvals = {
            Dynamic.Mission.VELOCITY_RATE: [1413548.36, 1413548.36],
            Dynamic.Mission.FLIGHT_PATH_ANGLE_RATE: [0.0, 0.0],
            Dynamic.Mission.ALTITUDE_RATE: [0.0, 0.0],
            Dynamic.Mission.DISTANCE_RATE: [168.781, 168.781],
            "normal_force": [0.0, 0.0],
            "fuselage_pitch": [0.0, 0.0],
            "dmass_dv": [-5.03252493e-06, -5.03252493e-06],
        }
        check_prob_outputs(self.prob, testvals, rtol=1e-6)

        partial_data = self.prob.check_partials(
            out_stream=None, method="cs", excludes=["*params*", "*aero*"]
        )
        assert_check_partials(partial_data, atol=1e-8, rtol=1e-8)


if __name__ == "__main__":
    unittest.main()
