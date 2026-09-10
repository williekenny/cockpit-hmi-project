class RTAOptimizationEngine:
    def __init__(self):
        self.target_fix = "FIX_ALPHA"
        self.target_time_utc = "14:25:00 UTC"

    def evaluate_rta_options(self, current_time_error_sec):
        """
        Models trade-off options based on the RTA time error.
        current_time_error_sec: Negative = Ahead of schedule, Positive = Behind
        """
        options = []
        
        if current_time_error_sec < 0: # Ahead of schedule (e.g., -14 seconds)
            abs_error = abs(current_time_error_sec)
            options = [
                {
                    "id": "OPT-1",
                    "strategy": "Speed Management",
                    "description": f"Reduce speed by 12 KTS for next 4 minutes to absorb {abs_error}s error.",
                    "fuel_delta_kg": -18, # Negative delta means fuel savings/cost efficiency
                    "time_delta_sec": abs_error,
                    "recommended": True
                },
                {
                    "id": "OPT-2",
                    "strategy": "Lateral Offset",
                    "description": "Request a 2 NM lateral offset arc around weather/congestion to lengthen path.",
                    "fuel_delta_kg": +25, # Extra fuel burn due to distance extension
                    "time_delta_sec": abs_error,
                    "recommended": False
                }
            ]
        else: # Behind schedule
            options = [
                {
                    "id": "OPT-1",
                    "strategy": "Speed Acceleration",
                    "description": f"Increase speed by 10 KTS to catch up by {current_time_error_sec}s.",
                    "fuel_delta_kg": +35,
                    "time_delta_sec": -current_time_error_sec,
                    "recommended": True
                },
                {
                    "id": "OPT-2",
                    "strategy": "Direct-To Routing",
                    "description": "Bypass minor intermediate waypoint via Direct-To clearance.",
                    "fuel_delta_kg": -10,
                    "time_delta_sec": -current_time_error_sec,
                    "recommended": False
                }
            ]

        return {
            "target_fix": self.target_fix,
            "time_error_sec": current_time_error_sec,
            "trade_off_options": options
        }