import unittest

import openmdao.api as om
from openmdao.utils.assert_utils import assert_check_partials

from aviary.mission.gasp_based.ode.accel_ode import AccelODE
from aviary.variable_info.options import get_option_defaults
from aviary.utils.test_utils.IO_test_util import check_prob_outputs
from aviary.variable_info.variables import Dynamic
from aviary.subsystems.propulsion.utils import build_engine_deck
from aviary.utils.test_utils.default_subsystems import get_default_mission_subsystems


class AccelerationODETestCase(unittest.TestCase):
    def setUp(self):
        self.prob = om.Problem()

        aviary_options = get_option_defaults()
        default_mission_subsystems = get_default_mission_subsystems(
            'GASP', build_engine_deck(aviary_options))

        self.sys = self.prob.model = AccelODE(num_nodes=2,
                                              aviary_options=aviary_options,
                                              core_subsystems=default_mission_subsystems)

    def test_accel(self):
        """Test both points in GASP Large Single Aisle 1 acceleration segment"""
        self.prob.setup(check=False, force_alloc_complex=True)

        throttle_climb = 0.956
        self.prob.set_val(Dynamic.Mission.ALTITUDE, [500, 500], units="ft")
        self.prob.set_val(
            Dynamic.Mission.THROTTLE, [
                throttle_climb, throttle_climb], units='unitless')
        self.prob.set_val(Dynamic.Mission.VELOCITY, [185, 252], units="kn")
        self.prob.set_val(Dynamic.Mission.MASS, [174974, 174878], units="lbm")

        self.prob.run_model()
        testvals = {
            Dynamic.Mission.LIFT: [174974, 174878],
            Dynamic.Mission.FUEL_FLOW_RATE_NEGATIVE_TOTAL: [
                -13262.73, -13567.53]  # lbm/h
        }
        check_prob_outputs(self.prob, testvals, rtol=1e-6)

        partial_data = self.prob.check_partials(
            method="cs", out_stream=None, excludes=["*params*", "*aero*"]
        )
        assert_check_partials(partial_data, rtol=1e-10)


if __name__ == "__main__":
    unittest.main()
