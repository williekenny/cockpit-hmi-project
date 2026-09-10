class AISynthesisFlightEngine:
    def __init__(self):
        # Scenario repository modeling different tactical operational states
        self.scenarios = {
            "SCENARIO_CONFLICT": {
                "id": "SCENARIO_CONFLICT",
                "name": "Scenario A: ATC Climb vs. Active CDO & RTA",
                "atc_uplink": "CLIMB AND MAINTAIN FL360 DUE TO TRAFFIC",
                "active_4d_state": {
                    "cdo_active": True,
                    "rta_target_fix": "FIX_ALPHA",
                    "current_rta_delta": -14
                },
                "ai_analysis": {
                    "conflict_detected": True,
                    "penalties": {
                        "cdo_impact": "Terminates idle-thrust Continuous Descent Operation",
                        "rta_delta_sec": 22, # Blows past constraint
                        "fuel_penalty_kg": 45
                    },
                    "counter_proposal": "Counter-Proposal: Request level-off at FL340 or delay climb initiation by 2 NM to preserve RTA and idle descent.",
                    "confidence": 0.96
                }
            },
            "SCENARIO_COMPATIBLE": {
                "id": "SCENARIO_COMPATIBLE",
                "name": "Scenario B: Compatible Direct Routing",
                "atc_uplink": "PROCEED DIRECT TO FIX_BETA, MAINTAIN 280 KTS",
                "active_4d_state": {
                    "cdo_active": False,
                    "rta_target_fix": "FIX_BETA",
                    "current_rta_delta": 0
                },
                "ai_analysis": {
                    "conflict_detected": False,
                    "penalties": None,
                    "counter_proposal": "Clearance fully compatible with 4D-TBO profile. Optimal fuel efficiency maintained.",
                    "confidence": 0.99
                }
            }
        }

    def get_scenario_data(self, scenario_id):
        return self.scenarios.get(scenario_id, self.scenarios["SCENARIO_CONFLICT"])